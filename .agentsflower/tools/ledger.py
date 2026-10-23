#!/usr/bin/env python3
"""Edit the Task Ledger (.agentflow/state/tasks.md) without one-off scripts.

  python .agentflow/tools/ledger.py add T-007 --title "Fix login" --stage 2 --role developer \
      --tool codex --depends "T-006" --notes "..."      # a planned task: blocked, "awaiting approval"
  python .agentflow/tools/ledger.py approve T-007 T-008                   # the human approved the plan: ready
  python .agentflow/tools/ledger.py add T-009 ... --status ready          # needs no approval (successor, tester task)
  python .agentflow/tools/ledger.py set T-007 --status review
  python .agentflow/tools/ledger.py set T-007 --status done --commit abc1234      # acceptance: needs a passing gate.py verify on that SHA
  python .agentflow/tools/ledger.py set T-007 --status rejected --notes "-> T-012: <why>"
  python .agentflow/tools/ledger.py show [T-007]

Only the Orchestrator (or a Single Mode session) runs this. Transitions follow .agentflow/docs/ai-handoff-protocol.md,
"Task lifecycle". A '|' inside a value is replaced with '/'. Task IDs are never reused.
A direct `set` keeps the same gates a launch does: an awaiting-approval row accepts only `approve`, a terminal
`rejected`/`cancelled`, or a `--notes` update that keeps the prefix; `in progress` requires a running attempt
recorded by the launcher (claims go through .agentflow/tools/run_task.py / run-task.ps1, not this CLI).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from paths import FLOW_ROOT, REPO_ROOT

COLS = ["ID", "Title", "Stage", "Role", "Tool", "Status", "Depends on", "Commit / artifact", "Notes", "Updated"]
FIELD = {  # CLI option -> column
    "title": "Title", "stage": "Stage", "role": "Role", "tool": "Tool", "status": "Status",
    "depends": "Depends on", "commit": "Commit / artifact", "notes": "Notes",
}
NEXT = {  # allowed status transitions; done, rejected, cancelled are final
    "ready": {"in progress", "blocked", "cancelled"},
    "in progress": {"review", "blocked", "rejected", "cancelled"},
    "review": {"done", "rejected", "in progress", "blocked"},
    "blocked": {"ready", "in progress", "review", "cancelled"},
    "done": set(), "rejected": set(), "cancelled": set(),
}
NEEDS_NOTES = {"rejected", "cancelled"}
AWAITING = "awaiting approval"  # Notes prefix of a planned task the human has not approved: nothing launches it
PLACEHOLDER = re.compile(r"^\s*No tasks yet\.?\s*$", re.I)
HEAD = "# Task Ledger\n\nWritten only through `python .agentflow/tools/ledger.py`. Statuses: .agentflow/docs/ai-handoff-protocol.md, \"Task lifecycle\".\n\n"


def root() -> Path:
    return FLOW_ROOT


def ledger_path() -> Path:
    return root() / "state" / "tasks.md"


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def join_row(cells: list[str]) -> str:
    return "| " + " | ".join(c.replace("|", "/").replace("\n", " ") for c in cells) + " |"


def _write_atomic(path: Path, text: str):
    """tasks.md is a single-writer file, but a crash mid-write must not leave it truncated:
    temp file + os.replace, the same pattern the runtime JSON writers use."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)  # never strand a half-written temp next to the ledger


def load(path: Path):
    """-> lines, columns (COLS), rows (padded to COLS), header index, end index. Older ledgers gain new columns."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(path, HEAD + join_row(COLS) + "\n" + "|---" * len(COLS) + "|\n")
    lines = path.read_text(encoding="utf-8-sig").split("\n")
    head = next((i for i, l in enumerate(lines) if l.startswith("| ID ")), None)
    if head is None:
        sys.exit(f"{path}: table header '| ID | ...' not found")
    old = split_row(lines[head])
    end = head + 2  # header + separator
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    rows = []
    for l in lines[head + 2:end]:
        cells = dict(zip(old, split_row(l)))
        rows.append([cells.get(c, "") for c in COLS])
    return lines, COLS, rows, head, end


def save(path: Path, lines, head, end, rows):
    out = lines[:head] + [join_row(COLS), "|---" * len(COLS) + "|"] + [join_row(r) for r in rows] + lines[end:]
    if rows:  # drop the "No tasks yet." placeholder once there is a row
        out = [l for l in out if not PLACEHOLDER.match(l)]
    _write_atomic(path, "\n".join(out))


# --- Task File requirements hash (shared with gate.py; the verify record binds it) ----------------------------------
def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def header(text):
    """Everything above "## Result": the worker must not change it. Trailing blank lines do not count:
    a worker that adds the missing "## Result" heading after an empty line changes nothing above it."""
    return re.sub(r"(?ms)^## Result[ \t]*$.*\Z", "", text.replace("\r\n", "\n")).rstrip() + "\n"


def task_header_hash(tid: str):
    """The requirements hash of the task's current Task File, or None when there is none."""
    hits = sorted((root() / "tasks").glob(f"{tid}-*.md"))
    return sha256(header(hits[0].read_text(encoding="utf-8-sig"))) if hits else None


# --- runtime state schema (shared with gate.py and run_task.py) -----------------------------------------------------
ATTEMPT_STATES = ("running", "exited", "error")


def check_runtime(rt, tid=None):
    """Structural validity of tasks/.runtime/T-NNN.json; raises ValueError. The file must name its task and
    hold an attempts list (every launcher writes both), and each attempt that names a task must name this
    one - an attempt without `taskId` is legacy evidence bound to the file it lives in. Records with extra
    or newer fields pass: only the shape a reader depends on is required, so older and newer records coexist."""
    if not isinstance(rt, dict):
        raise ValueError("runtime state is not an object")
    if not isinstance(rt.get("attempts"), list):
        raise ValueError("runtime state has no attempts list")
    if tid and rt.get("taskId") != tid:
        raise ValueError(f"runtime state is for {rt.get('taskId') or 'no task'}, not {tid}")
    for a in rt["attempts"]:
        if not isinstance(a, dict) or not isinstance(a.get("n"), int) or isinstance(a.get("n"), bool) \
                or a.get("status") not in ATTEMPT_STATES:
            raise ValueError("malformed attempt record (needs n:int and status running|exited|error)")
        if tid and a.get("taskId") not in (None, tid):
            raise ValueError(f"attempt {a['n']} is for {a.get('taskId')}, not {tid}")
    return rt


def check_verify(recs):
    """Structural validity of T-NNN.verify.json: a list of record objects; raises ValueError. `ok` must be
    a real bool and the binding fields (sha, attempt, taskId, headerHash) must be of their types when present -
    a wrong-shaped record is diagnosed, never read as 'no evidence' and never trusted by a truthy string."""
    if not isinstance(recs, list) or any(not isinstance(r, dict) for r in recs):
        raise ValueError("verify records are not a list of objects")
    for r in recs:
        if not isinstance(r.get("ok"), bool):
            raise ValueError("malformed verify record (needs ok: bool)")
        for key, typ in (("sha", str), ("taskId", str), ("headerHash", str)):
            if r.get(key) is not None and not isinstance(r[key], typ):
                raise ValueError(f"malformed verify record ({key} must be a string)")
        for key in ("base", "shas", "criteria"):
            if r.get(key) is not None and not isinstance(r[key], dict):
                raise ValueError(f"malformed verify record ({key} must be an object)")
        if r.get("attempt") is not None and (not isinstance(r["attempt"], int) or isinstance(r["attempt"], bool)):
            raise ValueError("malformed verify record (attempt must be an int)")
    return recs


def check_limits(lim):
    """Structural validity of tool-limits.json: a map of tool -> record with an 'until' timestamp string;
    raises ValueError. '_seen' is internal metadata, not a limit record, and is tolerated as-is."""
    if not isinstance(lim, dict):
        raise ValueError("tool limits are not a JSON object")
    for tool, rec in lim.items():
        if tool == "_seen":
            continue
        if not isinstance(rec, dict) or not isinstance(rec.get("until"), str):
            raise ValueError(f"malformed limit record for {tool}")
    return lim


def _last_attempt(tid: str):
    """The task's last recorded attempt, or None (missing file or no attempts). A corrupt file is a
    diagnosable refusal, never a silent 'no attempt'."""
    p = root() / "tasks" / ".runtime" / f"{tid}.json"
    if not p.exists():
        return None
    try:
        rt = check_runtime(json.loads(p.read_text(encoding="utf-8-sig")), tid)
    except (OSError, ValueError) as e:
        sys.exit(f"{tid}: cannot read runtime state {p.name}: {e}")
    return rt["attempts"][-1] if rt["attempts"] else None


def claimed(tid: str):
    """The launcher's recorded running attempt for this task, or None: a claim exists only while a real
    attempt runs. A missing file is no claim; a corrupt one is a diagnosable refusal, never a silent yes."""
    a = _last_attempt(tid)
    return a if a and a.get("status") == "running" else None


def _git(repo: str, *args):
    """stdout of a git call in one repository ('' = the repository holding .agentflow/), or None."""
    d = REPO_ROOT / repo if repo else REPO_ROOT
    r = subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip() if r.returncode == 0 else None


def _base_current(rec) -> bool:
    """The base a verify record was produced against is still current: per repository the recorded base
    equals the main-branch HEAD, or HEAD is this task's own merge (first parent = that base, second =
    the record's artifact). A moved base invalidates the bound evidence; a record without `base` binds
    only the artifact (the documented legacy rule)."""
    base = rec.get("base")
    if not isinstance(base, dict):
        return True
    shas = rec.get("shas") if isinstance(rec.get("shas"), dict) else {}
    for repo, b in base.items():
        if not isinstance(b, str):
            continue
        if _git(repo, "rev-parse", "HEAD") == b:
            continue
        parents = (_git(repo, "rev-list", "--parents", "-n", "1", "HEAD") or "").split()
        if not (isinstance(shas.get(repo), str) and parents[1:] == [b, shas[repo]]):
            return False
    return True


def verified(tid: str, sha: str):
    """Why no `gate.py verify` PASS accepts `sha` for this task, or None when one does (protocol: Acceptance).

    A current record binds task id, the last attempt number, the Task File header hash (requirements), the
    full artifact SHA(s) and the base SHA(s) the evidence was produced against; every binding field a record
    carries must match - a stale PASS from an earlier attempt, stale requirements, a moved base or a
    different artifact never satisfies acceptance. Legacy records stay valid evidence under an explicit rule:
    a record without `taskId` belongs to the file it lives in, and a missing `attempt`/`headerHash`/`base`
    binds only the artifact. Either way the task's last attempt must be `exited`: acceptance never runs
    beside a live or dead-but-unrecovered worker."""
    if not sha:
        return "no commit given"
    att = _last_attempt(tid)
    if not att or att.get("status") != "exited":
        return f"the last attempt is '{att.get('status') if att else 'missing'}', needs 'exited'"
    p = root() / "tasks" / ".runtime" / f"{tid}.verify.json"
    if not p.exists():
        return "no verify records"
    try:
        recs = check_verify(json.loads(p.read_text(encoding="utf-8")))
    except (OSError, ValueError) as e:
        sys.exit(f"{tid}: cannot read verify records {p.name}: {e}")
    hh = task_header_hash(tid)
    stale = False
    for r in recs:
        if r.get("taskId") not in (None, tid) or r.get("ok") is not True:
            continue
        rs = r["sha"] if isinstance(r.get("sha"), str) else ""
        if not rs or not (rs.startswith(sha) or sha.startswith(rs)):
            continue
        if r.get("attempt") in (None, att["n"]) and r.get("headerHash") in (None, hh) and _base_current(r):
            return None
        stale = True
    return (f"verify records name the artifact but none is bound to attempt {att['n']}, the current "
            "Task File and the current base (stale evidence): run gate.py verify again" if stale
            else "no passing verify record names this artifact")


def main() -> None:
    # ledger text is UTF-8 (emoji, Cyrillic); a cp1251/cp866 console or pipe must not crash the print
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("add", "set"):
        p = sub.add_parser(name)
        p.add_argument("id")
        for opt in FIELD:
            p.add_argument(f"--{opt}")
    apv = sub.add_parser("approve", help="the human approved these planned tasks: blocked -> ready")
    apv.add_argument("ids", nargs="+")
    sh = sub.add_parser("show")
    sh.add_argument("id", nargs="?")
    a = ap.parse_args()

    path = ledger_path()
    lines, cols, rows, head, end = load(path)
    idx = {r[0]: i for i, r in enumerate(rows)}

    if a.cmd == "show":
        for r in rows:
            if a.id is None or r[0] == a.id:
                print(" | ".join(r))
        return

    if a.cmd == "approve":
        st, nt = cols.index("Status"), cols.index("Notes")
        bad = [t for t in a.ids if t not in idx or rows[idx[t]][st] != "blocked" or not rows[idx[t]][nt].startswith(AWAITING)]
        if bad:
            sys.exit(f"not awaiting approval: {', '.join(bad)} (only planned tasks added without --status are)")
        for t in a.ids:
            r = rows[idx[t]]
            r[st], r[nt] = "ready", r[nt][len(AWAITING):].lstrip(" ;")
            r[cols.index("Updated")] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        save(path, lines, head, end, rows)
        for t in a.ids:
            print(join_row(rows[idx[t]]))
        return

    if not re.fullmatch(r"T-\d+", a.id):
        sys.exit(f"bad task id: {a.id} (expected T-NNN)")
    if a.status and a.status not in NEXT:
        sys.exit(f"bad status: {a.status}; allowed: {', '.join(NEXT)}")

    if a.cmd == "add":
        if a.id in idx:
            sys.exit(f"{a.id} already exists (IDs are never reused)")
        if (a.status or "ready") not in ("ready", "blocked"):
            sys.exit("a new task starts as ready or blocked")
        row = [""] * len(cols)
        row[0], row[cols.index("Status")] = a.id, "ready"
        if a.status is None:  # a planned task waits for the human's approval (protocol: Task lifecycle, Flow)
            a.status = "blocked"
            a.notes = AWAITING + (f"; {a.notes}" if a.notes else "")
        rows.append(row)
        i = len(rows) - 1
    else:
        if a.id not in idx:
            sys.exit(f"{a.id} not in ledger")
        i = idx[a.id]
        cur = rows[i][cols.index("Status")]
        notes = rows[i][cols.index("Notes")]
        if notes.startswith(AWAITING) and a.status not in ("cancelled", "rejected") and (
                (a.status and a.status != "blocked")
                or (a.notes is not None and not a.notes.startswith(AWAITING))):
            sys.exit(f"{a.id} awaits the human's approval of the plan: ledger.py approve {a.id} "
                     "(only approve, a terminal status, or --notes keeping the prefix is allowed)")
        if a.status and a.status != cur and cur in NEXT and a.status not in NEXT[cur]:
            sys.exit(f"{a.id}: {cur} -> {a.status} is not allowed; from {cur}: {', '.join(sorted(NEXT[cur])) or 'final'}")
        if a.status == "in progress" and cur != "in progress" and not claimed(a.id):
            sys.exit(f"{a.id}: 'in progress' needs a running attempt recorded by the launcher "
                     "(.agentflow/tools/run_task.py, run-task.ps1 on Windows). Nothing was changed")
        if a.status in NEEDS_NOTES and not a.notes:
            sys.exit(f"{a.status} needs --notes (reason; for rejected also the successor task)")
        if a.status == "done":
            sha = a.commit or rows[i][cols.index("Commit / artifact")]
            if reason := verified(a.id, sha):
                sys.exit(f"{a.id}: cannot accept on commit '{sha}': {reason}. "
                         f"Run: python .agentflow/tools/gate.py verify {a.id}")

    for opt, col in FIELD.items():
        v = getattr(a, opt)
        if v is not None:
            rows[i][cols.index(col)] = v
    rows[i][cols.index("Updated")] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    save(path, lines, head, end, rows)
    print(join_row(rows[i]))


if __name__ == "__main__":
    main()
