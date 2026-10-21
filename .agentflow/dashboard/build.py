#!/usr/bin/env python3
"""Builds .agentflow/dashboard/out/index.html and out/graph.html from .agentflow/state/tasks.md, .agentflow/tasks/T-*.md and git history.

Run from anywhere: python .agentflow/dashboard/build.py        (real project data)
                   python .agentflow/dashboard/build.py --demo (deterministic DEMO DATA fixture, no project reads)
The project is read-only; output goes only to .agentflow/dashboard/out/ (git-ignored). Data contract: .agentflow/dashboard/README.md.
Dashboard source snapshots: .agentflow/dashboard/snapshot.py.
"""
import copy, hashlib, json, os, re, subprocess, sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from paths import FLOW_ROOT, REPO_ROOT
import route_report

ROOT = REPO_ROOT
OUT = HERE / "out"
LEDGER = FLOW_ROOT / "state" / "tasks.md"
TASKS = FLOW_ROOT / "tasks"
PLAN = FLOW_ROOT / "docs" / "project-plan.md"
RUNTIME = TASKS / ".runtime"
LEDGER_REL = LEDGER.relative_to(ROOT).as_posix()
TASKS_REL = TASKS.relative_to(ROOT).as_posix()
PLAN_REL = PLAN.relative_to(ROOT).as_posix()
RUNTIME_REL = RUNTIME.relative_to(ROOT).as_posix()
PROJECT = ROOT.name
SCHEMA_VERSION = 1

STATUS_EN = {  # ledger machine status -> English display label
    "ready": "Ready", "in progress": "In progress", "review": "In review",
    "done": "Done", "rejected": "Rejected", "blocked": "Blocked", "cancelled": "Cancelled",
}
LEGACY_STATUS = {"failed": "Rejected", "partial": "In review", "rework": "In progress"}  # 1.x ledger vocabulary
ST_VALUES = set(STATUS_EN.values())
FINAL = {"Done", "Rejected", "Cancelled"}
RESULT_EN = {  # Result section in a Task File: old `Status:` and current `Outcome:`
    "done": "Completed by worker", "completed": "Completed by worker", "partial": "Partially done",
    "blocked": "Worker blocked", "failed": "Worker failed", "rolled back": "Deploy rolled back",
}
ROLE_EN = {"developer": "Developer", "tester": "Tester", "deployer": "Deployer"}
VERDICTS = {"pass", "partial", "fail", "unverified"}


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def tool_family(raw):
    """worker agent (not a role): Claude Code / Codex / Antigravity"""
    s = raw.lower()
    if "→" in s:  # handover: keep the one who finished
        s = s.split("→")[-1]
    if "claude" in s: return "Claude Code"
    if "codex" in s: return "Codex"
    if "antigravity" in s or "agy" in s: return "Antigravity"
    return raw.strip() or "not set"


def field(text, name):
    m = re.search(rf"^{re.escape(name)}:[ \t]*(.*?)[ \t]*(?:<!--.*)?$", text, re.M)
    return m.group(1).strip() if m else ""


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def header(text):
    """Task File header: everything before the first '## ' section."""
    return text.split("\n## ", 1)[0]


def git_dates():
    """file -> (first commit, last commit) over .agentflow/tasks/*.md"""
    out = subprocess.run(["git", "log", "--format=@%aI", "--name-only", "--", TASKS_REL, "tasks"],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    first, last, cur = {}, {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            cur = line[1:]
        elif line.strip() and cur:
            f = line.strip()
            if f.startswith("tasks/"):
                f = ".agentflow/" + f
            last.setdefault(f, cur)  # log runs newest to oldest
            first[f] = cur
    return first, last


def short(s, n):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def parse_deps(s):
    return sorted(set(re.findall(r"T-\d{3}", s)))


def norm_status(raw):
    k = raw.strip().lower()
    return STATUS_EN.get(k) or LEGACY_STATUS.get(k) or raw.strip()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout


def ledger_rows(text):
    lines = text.split("\n")
    head = next((i for i, l in enumerate(lines) if l.startswith("| ID ")), None)
    if head is None:
        return {}
    cols = split_row(lines[head])
    out = {}
    for l in lines[head + 2:]:
        if not l.startswith("| T-"):
            break
        r = dict(zip(cols, split_row(l)))
        out[r["ID"]] = r
    return out


def history():
    """Replays the git history of .agentflow/state/tasks.md: statuses and dependencies over time."""
    log = git("log", "--reverse", "--format=%H\t%aI\t%s", "--", LEDGER_REL, "state/tasks.md").strip().splitlines()
    timeline, edges, open_edges, commits = {}, [], {}, []
    prev_status, prev_deps = {}, {}
    for l in log:
        h, ts, subj = l.split("\t", 2)
        commits.append([ts, subj])
        text = git("show", f"{h}:{LEDGER_REL}") or git("show", f"{h}:state/tasks.md")
        cur = ledger_rows(text)
        for tid, r in cur.items():
            st = norm_status(r.get("Status", ""))
            if prev_status.get(tid) != st:
                timeline.setdefault(tid, []).append([ts, st])
                prev_status[tid] = st
            deps = set(re.findall(r"T-\d{3}", r.get("Depends on", ""))) - {tid}
            old = prev_deps.get(tid, set())
            for d in deps - old:
                open_edges[(d, tid)] = ts
            for d in old - deps:
                edges.append({"from": d, "to": tid, "kind": "dep", "t0": open_edges.pop((d, tid), ts), "t1": ts})
            prev_deps[tid] = deps
    for (d, tid), t0 in open_edges.items():
        edges.append({"from": d, "to": tid, "kind": "dep", "t0": t0, "t1": None})
    return timeline, edges, commits


def successor_edges(tasks):
    """dead task -> its successor: `-> T-xxx` in the dead task's Notes, or 'successor/rework of T-xxx' on the new one"""
    pairs = set()
    for t in tasks.values():
        if t["status"] in ("Rejected", "Cancelled"):
            for m in re.findall(r"(?:->|→)\s*(T-\d{3})", t["notes"]):
                if m in tasks and m != t["id"]:
                    pairs.add((t["id"], m))
        for m in re.findall(r"(?:преемник|successor of|replaces|rework of|повтор|перевыдан\w*)\s*(?:of\s*)?`?(T-\d{3})", t["title"] + " " + t["notes"], re.I):
            if m in tasks and m != t["id"] and tasks[m]["status"] in ("Rejected", "Cancelled"):
                pairs.add((m, t["id"]))
    return [{"from": a, "to": b, "kind": "succ"} for a, b in sorted(pairs)]


def check_edges(tasks):
    """tester task -> checked task, taken from the Task File `Verifies:` field (not a title guess)."""
    out = []
    for t in tasks.values():
        if t["role"] == "Tester" and t.get("verifies") and t["verifies"]["task"] in tasks:
            out.append({"from": t["id"], "to": t["verifies"]["task"], "kind": "check",
                        "sha": t["verifies"]["sha"], "stale": t["verifies"]["stale"]})
    return out


def verifies_of(body):
    """`Verifies: T-xxx @ <sha>` from a tester Task File header -> {'task', 'sha'} or None."""
    m = re.match(r"^(T-\d+)\s*@\s*(\S+)", field(header(body), "Verifies") or "")
    return {"task": m.group(1), "sha": m.group(2)} if m else None


def sha_matches(a, b):
    """Two SHAs refer to the same commit when either is a prefix of the other (>= 7 chars)."""
    a, b = (a or "").lower(), (b or "").lower()
    return bool(a and b) and (a.startswith(b[:7]) or b.startswith(a[:7]))


def chains(tasks, succ):
    parent = {i: i for i in tasks}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for e in succ:
        parent[find(e["from"])] = find(e["to"])
    return {i: find(i) for i in tasks}


def terminal_end(tl):
    """time of entering the trailing run of final statuses; None when the task is not closed"""
    if not tl or tl[-1][1] not in FINAL:
        return None
    i = len(tl) - 1
    while i > 0 and tl[i - 1][1] in FINAL:
        i -= 1
    return tl[i][0]


OWN_RE = re.compile(
    r"(замечани\w+|баги|просьб\w+|ревью)\s+(от\s+)?владельц\w+"
    r"|владелец\s+(\d{4}-\d\d-\d\d\s+)?(хочет|просит|попросил|выбрал|отметил|увидел|видел|сообщил|заметил|потребовал|назвал|указал|написал)"
    r"|(по|от)\s+(просьб\w+|требовани\w+)\s+владельц\w+|owner\s+(request|report|remark|bugs?|asked|wants|found|noticed|chose)|owner-reported|owner review",
    re.I)


def origins(tasks, goal_text):
    """Who set the task — estimate from text: tester/deployer (link to their report) > owner (their remark) > orchestrator."""
    for t in tasks.values():
        txt = t["title"] + " " + t["notes"]
        why = None
        if t["role"] != "Tester":
            for ref in sorted(set(re.findall(r"T-\d{3}", txt))):
                r = tasks.get(ref)
                if r and r["id"] != t["id"] and r["role"] in ("Tester", "Deployer") and r["c0"] < t["c0"]:
                    t["origin"], why = r["role"], f"found in {ref} ({r['role'].lower()} report)"
                    break
        if why is None:
            m = OWN_RE.search(txt + " " + goal_text.get(t["id"], ""))
            if m:
                t["origin"], why = "Owner", '"' + m.group(0).strip() + '"'
        if why is None:
            t["origin"], why = "Orchestrator", "default: the Task File is written by the Orchestrator"
        t["originWhy"] = why


SKIP_RE = re.compile(r"package-lock\.json|\.lock$|\.lockb$|\.(png|jpe?g|gif|webp|svg|ico|mp4|webm|pdf|woff2?|zip)$", re.I)  # lock files and binaries are not counted
DOC_RE = re.compile(r"^\.agentflow/|^(docs|tasks|state|runbook|screenshots)/|\.md$", re.I)


def sizes():
    """change size from worker commits (subject starts with [T-NNN]); code = everything except docs/tasks/state/runbook/screenshots and *.md"""
    out = git("log", "--all", "--numstat", "--format=@%H|%s")
    res, cur = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            subj = line[1:].split("|", 1)[1] if "|" in line else ""
            m = re.match(r"\[(T-\d{3})\]", subj)
            cur = res.setdefault(m.group(1), {"commits": 0, "files": set(), "codeFiles": set(), "add": 0, "del": 0, "codeAdd": 0, "codeDel": 0}) if m else None
            if cur is not None:
                cur["commits"] += 1
        elif cur is not None and line.count("\t") >= 2:
            a, d, path = line.split("\t", 2)
            if SKIP_RE.search(path):
                continue
            a = int(a) if a.isdigit() else 0
            d = int(d) if d.isdigit() else 0
            cur["files"].add(path); cur["add"] += a; cur["del"] += d
            if not DOC_RE.search(path):
                cur["codeFiles"].add(path); cur["codeAdd"] += a; cur["codeDel"] += d
    for v in res.values():
        v["files"] = len(v["files"]); v["codeFiles"] = len(v["codeFiles"])
    return res


def size_class(z):
    if not z or not z["files"]:
        return "—"
    n = z["codeAdd"] + z["codeDel"]
    return "docs" if n == 0 else "S" if n < 50 else "M" if n < 300 else "L" if n < 1000 else "XL"


COMMIT_LINE = re.compile(r"^[ \t]*(?:[-*][ \t]+)?(Commit|Change)[ \t]*:[ \t]*(.+?)[ \t]*$", re.M)
SHA_RE = re.compile(r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")


def report_commit(res):
    """Commit the worker explicitly named on a `Commit:` or `Change:` line of the report.
    Used only when all such lines name exactly one hash; otherwise (none or several) there is no value."""
    clean = re.sub(r"<!--.*?-->", "", res, flags=re.S)
    found, first = [], None
    for label, rest in COMMIT_LINE.findall(clean):
        lead = re.match(r"[`'\"]?([0-9a-f]{7,40})", rest)          # hash right after the label: all-digit hashes allowed
        for sha in ([lead.group(1)] if lead else []) + SHA_RE.findall(rest):
            if sha not in found:
                found.append(sha)
            first = first or (label, rest)
    if len(found) != 1:
        return None
    return {"sha": found[0], "label": first[0] + ":", "line": first[1][:200]}


def build_tasks(rows, files, first, last):
    tasks, goal_text = {}, {}
    for r in rows:
        tid = r["ID"]
        p = files.get(tid)
        body = p.read_text(encoding="utf-8-sig") if p else ""
        res = section(body, "Result")
        res_raw = (field(res, "Outcome") or field(res, "Status")).lower()
        res_key = next((k for k in RESULT_EN if res_raw.startswith(k)), "")
        ind_raw = field(body, "Independent check").lower()
        ind = "tester" if ind_raw.startswith("tester") else "none" if ind_raw.startswith("none") else ""
        status = STATUS_EN.get(r["Status"].lower(), r["Status"])
        rel = p.relative_to(ROOT).as_posix() if p else ""
        file_href = os.path.relpath(p, OUT).replace(os.sep, "/") if p else ""
        upd = r.get("Updated", "")
        created = first.get(rel, "")[:10]
        t = {
            "id": tid, "title": r["Title"], "stage": r["Stage"] or "—",
            "role": ROLE_EN.get(r["Role"], r["Role"]), "roleKey": r["Role"], "tool": tool_family(r["Tool"]),
            "toolRaw": r["Tool"],
            "status": status, "statusKey": r["Status"].lower(), "final": status in FINAL,
            "result": RESULT_EN.get(res_key, "No report"),
            "outcomeSrc": "Outcome" if field(res, "Outcome") else ("Status" if field(res, "Status") else ""),
            "outcomeRaw": (field(res, "Outcome") or field(res, "Status"))[:240],
            "reportCommit": report_commit(res),
            "ind": ind, "verdict": field(res, "Verdict").lower().split()[0] if field(res, "Verdict") else "",
            "verifies": verifies_of(body) if r["Role"] == "tester" else None,
            "deps": parse_deps(r.get("Depends on", "")), "commit": r.get("Commit / artifact", ""),
            "notes": r.get("Notes", ""), "file": rel, "fileHref": file_href,
            "created": created or (upd[:10] if upd else ""),
            "updated": upd[:10] or (last.get(rel, "")[:10]),
            "goal": short(section(body, "Goal"), 900),
            "goalFull": re.sub(r"<!--.*?-->", "", section(body, "Goal"), flags=re.S).strip(),
            "resultFull": re.sub(r"<!--.*?-->", "", res, flags=re.S).strip(),
            "body": re.sub(r"[ \t]+", " ", body),
            "resultText": short(res, 1200),
            "attemptsHint": body.count("Attempt "),
        }
        t["c0"] = 0
        goal_text[tid] = body.split("## Result")[0][:2500]
        tasks[tid] = t
    return tasks, goal_text


def link_checks(tasks):
    """checkedBy per developer task: tester tasks whose `Verifies:` names it, with the checked SHA and a stale flag."""
    for t in tasks.values():
        if t["verifies"]:
            checked = tasks.get(t["verifies"]["task"])
            current = None
            if checked:
                current = (checked["reportCommit"] or {}).get("sha") or checked["commit"].split(",")[0].strip() or None
            t["verifies"]["stale"] = bool(current and not sha_matches(t["verifies"]["sha"], current))
    verdicts = {}
    for t in tasks.values():
        if t["role"] == "Tester" and t["verifies"] and t["verifies"]["task"] in tasks:
            verdicts.setdefault(t["verifies"]["task"], []).append(
                {"id": t["id"], "verdict": t["verdict"], "status": t["status"],
                 "sha": t["verifies"]["sha"], "stale": t["verifies"]["stale"]})
    for t in tasks.values():
        t["checkedBy"] = verdicts.get(t["id"], [])
        if t["role"] != "Developer":
            t["check"] = "—"
        elif t["checkedBy"]:
            vs = [c["verdict"] for c in t["checkedBy"] if c["status"] != "Cancelled"]
            stale = any(c["stale"] for c in t["checkedBy"])
            if "fail" in vs: t["check"] = "Tester: fail"
            elif "partial" in vs or "unverified" in vs: t["check"] = "Tester: partial"
            elif "pass" in vs: t["check"] = "Tester: pass"
            else: t["check"] = "Tester assigned"
            if stale: t["check"] += " (stale link)"
        elif t["ind"] == "tester": t["check"] = "Tester required, no report"
        elif t["ind"] == "none": t["check"] = "No independent check"
        else: t["check"] = "Not set (legacy task)"
        t["blockedBy"] = [d for d in t["deps"] if d in tasks and not tasks[d]["final"] and tasks[d]["status"] != "Done"]
        t["blocks"] = []
        t["waitsOwner"] = (not t["final"]) and bool(re.search(r"владел|owner", t["notes"], re.I)) and t["status"] in ("Blocked", "Ready", "In review")
    for t in tasks.values():
        for d in t["deps"]:
            if d in tasks:
                tasks[d]["blocks"].append(t["id"])


def finish_graph(tasks, goal_text, dep_edges, commits, pings, succ, metrics=None, demo=False,
                 stages=None, diagnostics=None, provenance=None):
    origins(tasks, goal_text)
    ch = chains(tasks, succ)
    for t in tasks.values():
        t["chain"] = ch[t["id"]]
        t.setdefault("attempts", None)
        t.setdefault("routing", None)
        t.setdefault("verifications", None)
    graph = {"project": PROJECT, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
             "now": datetime.now().astimezone().isoformat(timespec="seconds"),
             "schemaVersion": SCHEMA_VERSION,
             "tasks": list(tasks.values()), "edges": dep_edges + succ + check_edges(tasks),
             "stages": stages if stages is not None else [],
             "diagnostics": diagnostics or {"sources": [], "warnings": [], "gaps": [],
                                            "unmappedTaskIds": [], "freshnessNote": ""},
             "provenance": provenance or {},
             "commits": commits, "pings": pings, "metrics": metrics, "demo": demo}
    return graph


# --- Roadmap layer: project-plan.md stages joined with ledger/runtime evidence ---
# Field contract: dashboard/README.md ("Roadmap data"). Everything here is additive
# to the task payload under SCHEMA_VERSION; task fields are unchanged.

DECLARED_EN = {"planned": "Planned", "current": "Current", "closed": "Closed"}
STATUS_BUCKET = {"done": "accepted", "in progress": "active", "review": "review",
                 "blocked": "blocked", "ready": "ready", "rejected": "rejected",
                 "cancelled": "cancelled"}
EVIDENCE_STATES = {"pass", "fail", "stale", "pending", "unknown"}
STAGE_HEAD = re.compile(r"^#{1,3}\s+stage\s+(\S+)\s*[.:\-–—]\s*(.+?)\s*$", re.I)
STAGE_IDONLY = re.compile(r"^#{1,3}\s+stage\s+(\S+?)\s*$", re.I)
STAGE_WORD = re.compile(r"^#{1,3}\s+stage\b", re.I)
HEADING = re.compile(r"^(#{1,6})\s")
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
LABEL = re.compile(r"^[ \t]*(status|exit criteria|recurring|references)\s*:\s*(.*?)\s*$", re.I)
CRIT_BULLET = re.compile(r"^\s*-\s*([A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*)\s*:\s*(\S.*?)\s*$")
EVIDENCE_LINE = re.compile(r"^\s*evidence\s*:\s*(.*?)\s*$", re.I)
BULLET = re.compile(r"^\s*-\s*(\S.*?)\s*$")
KV_PAIR = re.compile(r"^\s*([A-Za-z][\w-]*)\s*=\s*(.*?)\s*$", re.S)
SCHEME = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*):")
ATTEMPT_KEEP = {"n", "taskId", "tool", "role", "manual", "status", "exitCode",
                "startedAt", "finishedAt", "requestedModel", "requestedEffort",
                "effectiveModel", "effectiveEffort", "toolVersion", "limitHit",
                "stopReason", "workerTimeout", "deadline", "target", "note"}
VERIFY_KEEP = {"n", "at", "attempt", "role", "ok", "sha", "shas", "base", "criteria",
               "problems", "target", "headerHash", "checksHash", "taskId",
               "checksTouchedByTask"}
CHECK_KEEP = {"cmd", "exit"}
ROUTE_ASSESS_KEEP = {"event", "schemaVersion", "task", "at", "source", "status", "error",
                     "applied", "tool", "model", "effort", "jevChoice", "choice",
                     "jevEffort", "resolvedEffort", "band", "complexity", "confidence",
                     "required", "recommended", "floor", "excluded", "inadequate",
                     "adequateHeld", "blocked", "eligibleOptions", "backupChoice",
                     "backupTool", "backupModel", "backupEffort", "requirementsHash",
                     "escalation", "role", "prefer", "selected", "selectionReason",
                     "complexityConfidence", "effortConfidence", "optionConfidence",
                     "backupProbability", "availability"}
ROUTE_EVENT_KEEP = {"event", "task", "at", "source", "admitted", "deviation", "reason",
                    "requirementsHash", "note"}
ROUTE_NESTED_KEEP = {"admitted": {"tool", "model", "effort", "tier", "option"},
                     "required": {"effort", "complexity"},
                     "floor": {"option", "tool", "model", "effort", "resolvedModel", "resolvedTier"},
                     "selected": {"option", "tool", "model", "effort", "resolvedModel",
                                  "resolvedEffort", "resolvedTier"},
                     "availability": {"at", "source"}}


def split_kv(text):
    """';'-separated parts; double quotes shield a ';' inside a value."""
    parts, buf, quoted = [], [], False
    for ch in text:
        if ch == '"':
            quoted = not quoted
        elif ch == ";" and not quoted:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    return [p for p in parts if p.strip()]


def kv_pairs(parts):
    """-> (dict, malformed parts). Values may be quoted; keys lowercased."""
    out, bad = {}, []
    for p in parts:
        m = KV_PAIR.match(p)
        if not m:
            bad.append(p.strip())
            continue
        v = m.group(2)
        if len(v) >= 2 and v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        out[m.group(1).lower()] = v
    return out, bad


def parse_plan(text):
    """project-plan.md -> (stage records in source order, problems).

    A stage section runs from a `### Stage <id><sep> <title>` heading to the next
    level-1..3 heading; deeper headings stay inside the stage body. Fenced code
    blocks are opaque. Inside a stage, `Status:`/`Exit criteria:`/`Recurring:`/
    `References:` label lines open a paragraph block that ends at a blank line,
    a heading or another label. Raw text is kept verbatim.
    """
    stages, problems = [], []
    cur, block, fence = None, None, None

    def close_block():
        nonlocal block
        if cur is not None and block is not None:
            cur["blocks"].append(block)
        block = None

    for i, raw in enumerate(text.split("\n")):
        fm = FENCE.match(raw)
        if fence:
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= fence[1]:
                fence = None
            continue
        if fm:
            fence = (fm.group(1)[0], len(fm.group(1)))
            continue
        hm = HEADING.match(raw)
        if hm and len(hm.group(1)) <= 3:
            close_block()
            sm = STAGE_HEAD.match(raw)
            if sm:
                cur = {"id": sm.group(1), "title": sm.group(2), "line": i + 1, "blocks": []}
                stages.append(cur)
            else:
                im = STAGE_IDONLY.match(raw)
                cur = None
                if im:
                    cur = {"id": im.group(1), "title": None, "line": i + 1, "blocks": []}
                    stages.append(cur)
                    problems.append(f"stage '{im.group(1)}' at line {i + 1}: heading has no title")
                elif STAGE_WORD.match(raw):
                    problems.append(f"line {i + 1}: unrecognized stage heading {raw.strip()!r} - not parsed")
            continue
        if hm:
            close_block()
            continue
        lm = LABEL.match(raw)
        if cur is not None and lm:
            close_block()
            block = {"label": lm.group(1).lower(), "line": i + 1, "lines": [raw]}
            continue
        if block is not None:
            if raw.strip():
                block["lines"].append(raw)
            else:
                close_block()
    close_block()
    return stages, problems


def block_body(block):
    """text after the `Label:` of the first line, plus verbatim continuation lines."""
    first = LABEL.match(block["lines"][0]).group(2)
    return "\n".join([first] + block["lines"][1:]).strip()


def block_text(block):
    return "\n".join(block["lines"]).strip()


def check_ref(ref, check_fs=True):
    """Validate one authored evidence ref. Returns {kind, ...}: url | file | invalid.
    Local paths must stay under the project root (traversal and symlink escapes
    rejected); only http/https URL refs pass, and nothing is ever fetched."""
    s = ref.strip()
    m = SCHEME.match(s)
    if m:
        if m.group(1).lower() in ("http", "https"):
            return {"kind": "url"}
        return {"kind": "invalid", "reason": f"URL scheme '{m.group(1).lower()}' is not allowed"}
    parts = [p for p in s.replace("\\", "/").split("/") if p not in ("", ".")]
    if s.startswith(("/", "~")) or ".." in parts:
        return {"kind": "invalid", "reason": "path escapes the project root"}
    if not check_fs:
        return {"kind": "file", "exists": None, "href": None}  # demo: no filesystem reads
    try:
        rp = (ROOT / s).resolve()
    except (OSError, ValueError) as e:
        return {"kind": "invalid", "reason": f"path does not resolve: {e}"}
    if not rp.is_relative_to(ROOT.resolve()):
        return {"kind": "invalid", "reason": "path escapes the project root"}
    exists = rp.exists()
    try:
        href = os.path.relpath(rp, OUT).replace(os.sep, "/") if exists else None
    except ValueError:
        href = None  # no relative link across drives
    return {"kind": "file", "exists": exists, "href": href}


def evidence_of(parts, where, problems, check_fs):
    """`key=value` pairs of an authored `evidence:` line -> evidence record."""
    kv, bad = kv_pairs(parts)
    for b in bad:
        problems.append(f"{where}: malformed evidence item {b!r} (expected key=value)")
    known = {"state", "label", "provenance", "recorded", "artifact", "ref",
             "external", "supersededby"}
    for k in kv:
        if k not in known:
            problems.append(f"{where}: unknown evidence key '{k}' - ignored")
    state = kv.get("state", "unknown").lower()
    if state not in EVIDENCE_STATES:
        problems.append(f"{where}: evidence state '{state}' is not recognized - shown as unknown")
        state = "unknown"
    ev = {"state": state}
    for k, name in (("label", "label"), ("provenance", "provenance"), ("recorded", "recorded"),
                    ("artifact", "artifact"), ("supersededby", "supersededBy")):
        if k in kv:
            ev[name] = kv[k]
    if kv.get("external", "").lower() in ("true", "yes", "1"):
        ev["external"] = True
    if "ref" in kv:
        r = check_ref(kv["ref"], check_fs)
        ev["ref"] = kv["ref"]
        ev["refKind"] = r["kind"]
        if r["kind"] == "url":
            ev["external"] = True  # external refs are references, never fetched
        elif r["kind"] == "file":
            ev["refExists"] = r["exists"]
            if r.get("href"):
                ev["refHref"] = r["href"]
            if r["exists"] is False:
                problems.append(f"{where}: evidence ref '{kv['ref']}' not found under the project root - shown as text")
        else:
            problems.append(f"{where}: evidence ref rejected - {r['reason']}")
    return ev


def parse_criteria(lines, where, problems, check_fs):
    """`- <ID>: <text>` bullets inside an Exit criteria block -> criteria records.
    An ID must contain a digit or -/_ so plain `- word: ...` bullets stay text.
    Indented `evidence:` lines attach to the last criterion."""
    crits = None
    for ln in lines[1:]:
        em = EVIDENCE_LINE.match(ln)
        cm = CRIT_BULLET.match(ln)
        if em:
            if crits:
                crits[-1]["evidence"] = evidence_of(split_kv(em.group(1)), where, problems, check_fs)
            else:
                problems.append(f"{where}: evidence line without a criterion - ignored")
        elif cm and (re.search(r"\d", cm.group(1)) or re.search(r"[-_]", cm.group(1))):
            if crits is None:
                crits = []
            crits.append({"id": cm.group(1), "text": cm.group(2), "evidence": None})
    for c in crits or []:
        if c["evidence"] is None:
            c["evidence"] = {"state": "unknown", "provenance": "declared criterion; no evidence line authored"}
    return crits


def parse_recurring(block, where, problems, check_fs):
    """Recurring: <kind> line, non-bullet continuations -> note, `- <id>: <result>; key=value...` -> cycles."""
    first = LABEL.match(block["lines"][0]).group(2)
    note, cycles = None, []
    for ln in block["lines"][1:]:
        bm = BULLET.match(ln)
        if not bm:
            note = (note + "\n" + ln.strip()) if note else ln.strip()
            continue
        segs = split_kv(bm.group(1))
        m = re.match(r"^(.+?)\s*:\s*(.+)$", segs[0], re.S)
        cyc = {"id": m.group(1).strip() if m else None,
               "result": (m.group(2) if m else segs[0]).strip() or None}
        kv, bad = kv_pairs(segs[1:])
        for b in bad:
            problems.append(f"{where}: malformed cycle item {b!r} (expected key=value)")
        for k in ("recorded", "note"):
            if k in kv:
                cyc[k] = kv[k]
        if "ref" in kv:
            r = check_ref(kv["ref"], check_fs)
            cyc["ref"], cyc["refKind"] = kv["ref"], r["kind"]
            if r["kind"] == "file":
                cyc["refExists"] = r["exists"]
                if r.get("href"):
                    cyc["refHref"] = r["href"]
                if r["exists"] is False:
                    problems.append(f"{where}: cycle ref '{kv['ref']}' not found under the project root - shown as text")
            elif r["kind"] == "invalid":
                problems.append(f"{where}: cycle ref rejected - {r['reason']}")
        cycles.append(cyc)
    return {"kind": first or None, "note": note, "cycles": cycles}


def parse_references(block):
    """References: `- <label>; note="..."` bullets - display text, never resolved."""
    refs = []
    for ln in block["lines"][1:]:
        bm = BULLET.match(ln)
        if bm:
            segs = split_kv(bm.group(1))
            kv, _ = kv_pairs(segs[1:])
            refs.append({"label": segs[0].strip(), "note": kv.get("note")})
    return refs or None


def stage_fields(st, problems, check_fs):
    """labeled blocks -> declared status, exit criteria, criteria, recurring, references."""
    by_label = {}
    for b in st.pop("blocks"):
        if b["label"] in by_label:
            problems.append(f"stage '{st['id']}': duplicate '{b['label']}:' block at line {b['line']} - first kept")
        else:
            by_label[b["label"]] = b
    where = f"stage '{st['id']}'"
    st["declaredRaw"] = st["declared"] = st["declaredKey"] = None
    if "status" in by_label:
        st["declaredRaw"] = block_body(by_label["status"]) or None
        word = re.match(r"[A-Za-z-]+", st["declaredRaw"] or "")
        key = word.group(0).lower() if word else ""
        if key in DECLARED_EN:
            st["declaredKey"], st["declared"] = key, DECLARED_EN[key]
        elif st["declaredRaw"]:
            problems.append(f"{where}: declared status '{short(st['declaredRaw'], 60)}' is not a known stage state - shown raw")
    else:
        st["diagnostics"].append("no Status: block - declared status unknown")
    st["exitCriteria"] = block_text(by_label["exit criteria"]) if "exit criteria" in by_label else None
    if "exit criteria" not in by_label:
        st["diagnostics"].append("no Exit criteria: block")
    st["criteria"] = (parse_criteria(by_label["exit criteria"]["lines"], where, problems, check_fs)
                      if "exit criteria" in by_label else None)
    st["recurring"] = (parse_recurring(by_label["recurring"], where, problems, check_fs)
                       if "recurring" in by_label else None)
    st["historicalRefs"] = parse_references(by_label["references"]) if "references" in by_label else None


def current_sha(t):
    """the task's current artifact hash: explicit report Commit/Change line, else the ledger cell."""
    return (t.get("reportCommit") or {}).get("sha") or (t.get("commit") or "").split(",")[0].strip() or None


def counts_of(ts):
    ts = list(ts)
    c = {k: 0 for k in STATUS_BUCKET.values()}
    other = {}
    for t in ts:
        b = STATUS_BUCKET.get(t["statusKey"])
        if b:
            c[b] += 1
        else:
            other[t["statusKey"] or "?"] = other.get(t["statusKey"] or "?", 0) + 1
    c["other"], c["total"] = other, len(ts)
    return c


def join_stages(parsed, problems, tasks, check_fs=True):
    """stage fields + task join -> (stages, unmapped task ids). Duplicate ids are
    never resolved silently: both records are flagged and their tasks stay unmapped."""
    seen = {}
    for st in parsed:
        seen.setdefault(st["id"], []).append(st)
        st["diagnostics"] = []
    for sid, group in seen.items():
        if len(group) > 1:
            lines = ", ".join(f"line {g['line']}" for g in group)
            problems.append(f"duplicate stage id '{sid}' in the plan ({lines}) - not resolved; "
                            f"its tasks stay in the Unmapped group")
            for g in group:
                g["duplicate"] = True
                g["diagnostics"].append(f"duplicate id - also declared at {lines}")
        else:
            group[0]["duplicate"] = False
    try:
        plan_href = os.path.relpath(PLAN, OUT).replace(os.sep, "/")
    except ValueError:
        plan_href = PLAN_REL  # no relative link across drives - the repo path as text
    for i, st in enumerate(parsed):
        st["ordinal"] = i
        st["source"] = PLAN_REL
        st["sourceRef"] = f"plan §Stage {st['id']}"
        st["sourceHref"] = plan_href
        stage_fields(st, problems, check_fs)
    valid = {st["id"] for st in parsed if not st["duplicate"]}
    by_stage, unmapped = {sid: [] for sid in valid}, []
    for t in tasks.values():
        sval = t["stage"].strip()
        if sval and sval != "—" and sval in valid:
            by_stage[sval].append(t["id"])
        else:
            unmapped.append(t["id"])
    for st in parsed:
        st["taskIds"] = by_stage.get(st["id"], [])
        st["counts"] = counts_of(tasks[i] for i in st["taskIds"])
        if st["criteria"] is None:
            st["coverage"] = {"kind": "unstructured"}
        else:
            states = {}
            for c in st["criteria"]:
                s = (c.get("evidence") or {}).get("state", "unknown")
                states[s] = states.get(s, 0) + 1
            st["coverage"] = {"kind": "authored", "total": len(st["criteria"]), "states": states}
        c = st["counts"]
        unfinished = c["active"] + c["review"] + c["blocked"] + c["ready"]
        if st["declaredKey"] == "planned" and c["total"]:
            problems.append(f"stage '{st['id']}' is declared 'planned' but the ledger lists "
                            f"{c['total']} task(s) ({unfinished} unfinished) - both facts shown as recorded")
            st["diagnostics"].append("declared status disagrees with the ledger")
        elif st["declaredKey"] == "closed" and unfinished:
            problems.append(f"stage '{st['id']}' is declared 'closed' but has {unfinished} unfinished task(s) "
                            f"- declaration and ledger disagree")
            st["diagnostics"].append("declared status disagrees with the ledger")
    for t in tasks.values():
        for chk in t.get("checkedBy", []):
            if chk.get("stale"):
                cur = current_sha(t) or "no current commit"
                problems.append(f"{chk['id']} verifies {t['id']} @ {chk['sha']} but the task reports {cur} "
                                f"- stale link, not current evidence")
    dup = sorted(sid for sid, g in seen.items() if len(g) > 1)
    unmapped_stages = sorted({t["stage"].strip() for t in tasks.values()
                              if t["id"] in unmapped and t["stage"].strip() not in ("", "—")})
    if unmapped_stages:
        problems.append(f"stage(s) {', '.join(unmapped_stages)} appear in the ledger but not in the plan - "
                        f"affected tasks stay in the Unmapped group")
    dup_tasks = [i for i in unmapped if tasks[i]["stage"].strip() in dup]
    if dup_tasks:
        problems.append(f"tasks naming duplicated stage id(s) {', '.join(dup)} are unmapped: "
                        + ", ".join(dup_tasks))
    no_stage = [i for i in unmapped if tasks[i]["stage"].strip() in ("", "—")]
    if no_stage:
        problems.append(f"{len(no_stage)} task(s) have no Stage value - kept in the Unmapped group: "
                        + ", ".join(no_stage))
    return parsed, unmapped


def rel_ref(value):
    """a recorded absolute path -> repo-relative when under the project root, else the file name."""
    try:
        rp = Path(value).resolve()
        return rp.relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        return Path(str(value)).name


def attempt_view(a):
    v = {k: a[k] for k in ATTEMPT_KEEP if k in a}
    if a.get("log"):
        v["logRef"] = rel_ref(a["log"])
    return v


def verify_view(v, t):
    out = {k: v[k] for k in VERIFY_KEEP if k in v}
    if isinstance(v.get("checks"), list):
        out["checks"] = [{k: c[k] for k in CHECK_KEEP if k in c} for c in v["checks"] if isinstance(c, dict)]
    if v.get("log"):
        out["logRef"] = rel_ref(v["log"])
    cur = current_sha(t)
    if out.get("sha"):
        out["stale"] = bool(cur and not sha_matches(out["sha"], cur))
    return out


def routing_view(records):
    """route.json entries -> allowlisted assessments and admission/exception events.
    Pre-event-schema records (no `event`) count as assessments when they carry a
    routing choice; unknown event kinds are not exported."""
    assess, events = [], []
    for e in records if isinstance(records, list) else []:
        if not isinstance(e, dict):
            continue
        if e.get("event") == "assessment" or (e.get("event") is None and (e.get("jevChoice") or e.get("choice"))):
            v = {k: e[k] for k in ROUTE_ASSESS_KEEP if k in e}
            kind = "assess"
        elif e.get("event") in ("admission", "human-exception"):
            v = {k: e[k] for k in ROUTE_EVENT_KEEP if k in e}
            kind = "event"
        else:
            continue
        for k, keep in ROUTE_NESTED_KEEP.items():
            if isinstance(v.get(k), dict):
                v[k] = {kk: vv for kk, vv in v[k].items() if kk in keep}
        (assess if kind == "assess" else events).append(v)
    return {"assessments": assess, "events": events}


def read_runtime_json(name, problems):
    """one .runtime file -> parsed JSON, or None (absent, unreadable or malformed)."""
    p = RUNTIME / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        problems.append(f"runtime record {name} is unreadable ({e}) - shown as not recorded")
        return None


def attach_runtime(tasks, problems):
    """attempts, routing and verify records per task - allowlisted fields only;
    raw argv/env/log contents, credentials and quota data are never exported."""
    missing = not RUNTIME.is_dir()
    for tid, t in tasks.items():
        t["attempts"] = t["routing"] = t["verifications"] = None
        if missing:
            continue
        rec = read_runtime_json(f"{tid}.json", problems)
        if isinstance(rec, dict) and isinstance(rec.get("attempts"), list):
            t["attempts"] = [attempt_view(a) for a in rec["attempts"] if isinstance(a, dict)]
        rec = read_runtime_json(f"{tid}.route.json", problems)
        if rec is not None:
            t["routing"] = routing_view(rec)
        rec = read_runtime_json(f"{tid}.verify.json", problems)
        if isinstance(rec, list):
            t["verifications"] = [verify_view(v, t) for v in rec if isinstance(v, dict)]
    return missing


def file_source(path, rel):
    """diagnostics.sources entry: build-time mtime + content fingerprint."""
    if not path.exists():
        return {"file": rel, "status": "missing", "mtime": None, "fingerprint": None}
    try:
        data = path.read_bytes()
        return {"file": rel, "status": "read",
                "mtime": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds"),
                "fingerprint": "sha256:" + hashlib.sha256(data).hexdigest()[:8]}
    except OSError as e:
        return {"file": rel, "status": "unreadable", "mtime": None, "fingerprint": None, "detail": str(e)}


def read_plan(problems):
    try:
        return PLAN.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        problems.append(f"{PLAN_REL} is missing - no stage records; every task falls in the Unmapped group")
    except (OSError, ValueError) as e:
        problems.append(f"{PLAN_REL} is unreadable ({e}) - no stage records; every task falls in the Unmapped group")
    return None


def runtime_source(missing):
    if missing:
        return {"file": RUNTIME_REL + "/", "status": "absent", "mtime": None, "fingerprint": None}
    n = len([p for p in RUNTIME.glob("T-*.json") if re.fullmatch(r"T-\d+\.json", p.name)])
    return {"file": RUNTIME_REL + "/", "status": "read", "mtime": None, "fingerprint": None,
            "detail": f"{n} attempt records"}


def real_graph():
    text = LEDGER.read_text(encoding="utf-8-sig")
    head = next(i for i, l in enumerate(text.split("\n")) if l.startswith("| ID "))
    lines = text.split("\n")
    cols = split_row(lines[head])
    rows = []
    for l in lines[head + 2:]:
        if not l.startswith("| T-"):
            break
        rows.append(dict(zip(cols, split_row(l))))

    files = {p.name.split("-")[0] + "-" + p.name.split("-")[1]: p for p in TASKS.glob("T-*.md")}
    first, last = git_dates()
    tasks, goal_text = build_tasks(rows, files, first, last)
    link_checks(tasks)

    problems = []
    for tid in sorted(set(r["ID"] for r in rows) - set(files)):
        problems.append(f"{tid}: ledger row has no Task File under {TASKS_REL} - ledger data only")
    plan_text = read_plan(problems)
    parsed = []
    if plan_text is not None:
        parsed, plan_problems = parse_plan(plan_text)
        problems += plan_problems
        if not parsed:
            problems.append(f"{PLAN_REL} holds no '### Stage <id>.' sections - malformed or empty plan")
    stages, unmapped = join_stages(parsed, problems, tasks)
    rt_missing = attach_runtime(tasks, problems)
    git_ok = bool(git("rev-parse", "--is-inside-work-tree").strip())

    timeline, dep_edges, commits = history()
    for t in tasks.values():
        tl = timeline.get(t["id"]) or [[datetime.fromisoformat(t["created"] or datetime.now().strftime("%Y-%m-%d")).astimezone().isoformat(), t["status"]]]
        t["timeline"] = tl
        t["createdAt"] = min([tl[0][0]] + ([first[t["file"]]] if t["file"] in first else []), key=lambda x: datetime.fromisoformat(x))
        t["endAt"] = terminal_end(tl)
    for t in tasks.values():
        t["c0"] = datetime.fromisoformat(t["createdAt"]).timestamp()
    succ = successor_edges(tasks)
    allc = [l.split("|", 1) for l in git("log", "--all", "--format=%aI|%s").splitlines() if "|" in l]
    pings = sorted(ts for ts, _ in allc)
    work = {}  # worker commits: subject starts with [T-NNN]
    for ts, subj in allc:
        m = re.match(r"\[(T-\d{3})\]", subj)
        if m:
            work.setdefault(m.group(1), []).append(ts)
    for t in tasks.values():
        t["work"] = sorted(work.get(t["id"], []))
    sz = sizes()
    for t in tasks.values():
        t["size"] = sz.get(t["id"]) if sz.get(t["id"], {}).get("files") else None
        t["sizeCls"] = size_class(t["size"])
        t["sizeN"] = (t["size"]["codeAdd"] + t["size"]["codeDel"]) if t["size"] else 0

    plan_source = file_source(PLAN, PLAN_REL)
    if plan_text is None and plan_source["status"] == "read":
        plan_source["status"] = "unreadable"  # bytes fingerprinted, but the text did not decode
        plan_source["detail"] = "not decodable as UTF-8 text"
    sources = [plan_source, file_source(LEDGER, LEDGER_REL),
               {"file": TASKS_REL + "/T-*.md", "status": "read" if files else "missing",
                "mtime": None, "fingerprint": None, "detail": f"{len(files)} files read"},
               runtime_source(rt_missing),
               {"file": "git history", "status": "read" if git_ok else "absent",
                "mtime": None, "fingerprint": None}]
    gaps = []
    if plan_text is None:
        gaps.append(f"project plan ({PLAN_REL}) unavailable - stage data absent")
    if rt_missing:
        gaps.append(f"no attempt records ({RUNTIME_REL}/ absent) - attempts, routing and gate evidence are 'not recorded'")
    elif not any(t["attempts"] is not None for t in tasks.values()):
        gaps.append(f"no attempt records in {RUNTIME_REL}/ - attempts are 'not recorded'")
    if not git_ok:
        gaps.append("git history unavailable - commit dates, sizes and status timelines are unknown")
    unstructured = sorted({st["id"] for st in stages if st["coverage"]["kind"] == "unstructured"})
    if unstructured:
        gaps.append(f"stage(s) {', '.join(unstructured)} have unstructured exit criteria - "
                    f"per-criterion coverage is unknown")
    diagnostics = {"sources": sources, "warnings": problems, "gaps": gaps,
                   "unmappedTaskIds": sorted(unmapped),
                   "freshnessNote": "Sources were read at build time; mtimes and fingerprints show "
                                    "their state then - a static page cannot watch for later changes."}
    provenance = {"plan": PLAN_REL, "ledger": LEDGER_REL, "taskFiles": TASKS_REL + "/T-*.md",
                  "runtime": RUNTIME_REL + "/", "git": "git log at the repository root",
                  "payload": f"schemaVersion {SCHEMA_VERSION} - dashboard/README.md data contract",
                  "synthetic": False}
    graph = finish_graph(tasks, goal_text, dep_edges, commits, pings, succ,
                         metrics=route_report.metrics(),
                         stages=stages, diagnostics=diagnostics, provenance=provenance)
    return graph, len(dep_edges), len(succ)


DEMO_PLAN = """# Project Plan

Project: demo-project (DEMO DATA).

## Roadmap

### Stage 6. Public release

Status: current.

Exit criteria:
- S6-E1: packaged zero-dependency core CLI
  evidence: state=pass; label="recorded pass: install checks"; provenance="gate verify record"; recorded=2026-10-16; artifact=a1b2c3d; ref=demo/install.md
- S6-E2: CI on three OSes
  evidence: state=fail; external=true; label="external run failed on windows-latest"; provenance="external CI report - reference only, never fetched"; recorded=2026-10-17; ref=https://ci.invalid/run/42
- S6-E3: human push and publication
  evidence: state=pending; external=true; label="not yet performed"; provenance="declared in plan; no run recorded"

### Stage 1. Team layer and launcher

Status: closed.

Exit criteria: roles, Task Files, ledger, launcher with preflight on a live project (1.2.0).

References:
- release 1.2.0; note="recorded before the ledger kept task rows"

### Stage 2. Enforcement, states, template vs project

Status: closed.

Exit criteria: audit findings committed; the branch is merged by the human.

### Stage 4. Upstream sync

Status: current.

Recurring: periodic drift review
a completed cycle never closes the stage
- cycle-2026-10-15: completed; recorded=2026-10-15; ref=https://ci.invalid/decision-note; note="bounded review"

Exit criteria: drift reports from every installed project are reviewed periodically.

### Stage 3. Pilot 2.0.0

Status: closed.

Exit criteria: one real project updated with the Update procedure; findings recorded.

References:
- pilot ledger; note="outside this repository - reference only"

### Stage 5. Reliability and efficient project practices

Status: planned.

Exit criteria: the scenario suite passes; migration preserves open tasks.

### Stage 3. Pilot 2.0.0 (redeclared)

Status: closed.

Exit criteria: a duplicated stage id - a parser diagnostic, never resolved silently.
"""

DEMO_ATTEMPTS = {
    "T-103": [
        {"n": 1, "tool": "devin", "role": "developer", "manual": False,
         "requestedModel": "swe-2-high", "requestedEffort": "high",
         "effectiveModel": "swe-2-high", "effectiveEffort": "high",
         "status": "exited", "exitCode": 0,
         "startedAt": "2026-10-12T09:00:00Z", "finishedAt": "2026-10-12T09:41:00Z",
         "limitHit": False, "stopReason": "completed", "workerTimeout": 1200,
         "deadline": "2026-10-12T09:20:00Z", "logRef": ".agentflow/tasks/.runtime/T-103.1.log"},
        {"n": 2, "tool": "devin", "role": "developer", "manual": False,
         "requestedModel": "swe-2-high", "requestedEffort": "high",
         "effectiveModel": "unknown", "effectiveEffort": "unknown",
         "status": "running", "startedAt": "2026-10-12T11:08:00Z",
         "limitHit": False, "workerTimeout": 1200}],
}

DEMO_ROUTING = {
    "T-103": {"assessments": [
        {"event": "assessment", "schemaVersion": 1, "task": "T-103",
         "at": "2026-10-12T08:59:00Z", "source": "jev", "status": "ok",
         "tool": "devin", "model": "swe-2-high", "resolvedEffort": "high",
         "required": {"effort": "high", "complexity": 0.4},
         "recommended": ["devin-swe-2", "devin-gpt-6-sol"],
         "applied": True}],
        "events": [
        {"event": "admission", "task": "T-103", "at": "2026-10-12T08:59:05Z",
         "source": "jev",
         "admitted": {"tool": "devin", "model": "swe-2-high", "effort": None,
                      "tier": "high", "option": "devin-swe-2"},
         "deviation": False}]},
}

DEMO_VERIFY = {
    "T-102": [
        {"n": 1, "at": "2026-10-12T09:55:00Z", "attempt": 1, "role": "tester",
         "ok": True, "sha": "abc1234", "criteria": {"V-01": "pass"}, "problems": [],
         "checks": [{"cmd": "python -m unittest discover -s .agentflow/tests -p test_demo.py",
                     "exit": 0}],
         "logRef": ".agentflow/tasks/.runtime/T-102.verify.1.log"}],
}


def demo_graph():
    """Deterministic DEMO DATA fixture: fixed timestamps, no reads of ledger, Task Files, runtime or git."""
    base = datetime.fromisoformat("2026-10-10T09:00:00+00:00").timestamp()
    rows = [
        ("T-101", "Launcher parity fix", "6", "developer", "codex", "done", "abc1234", "done", "completed", None, "none - local change"),
        ("T-102", "Verify launcher parity", "6", "tester", "devin", "done", "def5678", "done", "completed", ("T-101", "abc1234"), "tester"),
        ("T-103", "Honest metrics dashboard", "5", "developer", "devin", "review", "9f00dc1", "done", "completed", None, "tester"),
        ("T-104", "Verify metrics dashboard", "5", "tester", "codex", "in progress", "", "in progress", "", ("T-103", "deadbeef"), "tester"),
        ("T-105", "Old probe cleanup", "5", "developer", "agy", "rejected", "", "blocked", "", None, "none - superseded"),
        ("T-106", "Successor probe cleanup", "5", "developer", "codex", "in progress", "", "in progress", "", None, "none - rework of T-105"),
        ("T-107", "Deploy staging update", "5", "deployer", "claude", "blocked", "", "", "", None, "none - waits for T-103, owner decision"),
        ("T-108", "Cancelled experiment", "9", "developer", "codex", "cancelled", "", "", "", None, "none - owner cancelled"),
    ]
    days = lambda n: (datetime.fromtimestamp(base + n * 86400).astimezone().isoformat(timespec="seconds"))
    tasks, goal_text = {}, {}
    for i, (tid, title, stage, role, tool, st, commit, outcome, verdict, verifies, ind) in enumerate(rows):
        c0, c1 = days(i), days(i + 2)
        status = STATUS_EN[st]
        tl = [[c0, "Ready"], [days(i + 0.5), "In progress"]]
        if st in ("done", "rejected", "cancelled", "review"):
            tl.append([c1, "In review" if st == "review" else status])
        if st == "in progress":
            tl[-1] = [c0, "In progress"]
        res = f"Outcome: {outcome}\nVerdict: {verdict}" if outcome else ""
        t = {"id": tid, "title": title, "stage": stage,
             "role": ROLE_EN[role], "roleKey": role, "tool": tool_family(tool), "toolRaw": tool,
             "status": status, "statusKey": st, "final": status in FINAL,
             "result": RESULT_EN.get(outcome.split()[0] if outcome else "", "No report"),
             "outcomeSrc": "Outcome" if outcome else "", "outcomeRaw": outcome,
             "reportCommit": {"sha": commit, "label": "Change:", "line": f"Change: {commit}"} if commit else None,
             "ind": ind.split(" ")[0], "verdict": verdict,
             "verifies": {"task": verifies[0], "sha": verifies[1], "stale": False} if verifies else None,
             "deps": [], "commit": commit, "notes": "DEMO DATA row",
             "file": f".agentflow/tasks/{tid}-demo.md", "fileHref": "#",
             "created": c0[:10], "updated": c1[:10], "goal": "Demo goal text.", "goalFull": "Demo goal text.",
             "resultFull": res, "body": res, "resultText": res, "attemptsHint": 0,
             "timeline": tl, "createdAt": c0, "endAt": c1 if status in FINAL else None, "c0": base + i * 86400,
             "work": [days(i + 0.4), days(i + 0.9)] if role == "developer" else [],
             "size": {"commits": 2, "files": 5, "codeFiles": 3, "add": 80, "del": 20, "codeAdd": 60, "codeDel": 15},
             "sizeCls": "S", "sizeN": 75}
        goal_text[tid] = t["goalFull"]
        tasks[tid] = t
    tasks["T-106"]["deps"] = ["T-105"]
    tasks["T-107"]["deps"] = ["T-103"]
    link_checks(tasks)
    for tid, t in tasks.items():
        t["attempts"] = copy.deepcopy(DEMO_ATTEMPTS.get(tid))
        t["routing"] = copy.deepcopy(DEMO_ROUTING.get(tid))
        t["verifications"] = copy.deepcopy(DEMO_VERIFY.get(tid))
    problems = []
    parsed, plan_problems = parse_plan(DEMO_PLAN)
    problems += plan_problems
    stages, unmapped = join_stages(parsed, problems, tasks, check_fs=False)
    unstructured = sorted({st["id"] for st in stages if st["coverage"]["kind"] == "unstructured"})
    gaps = ["runtime/routing/verify evidence is embedded in the fixture - no canonical memory is read"]
    if unstructured:
        gaps.append(f"stage(s) {', '.join(unstructured)} have unstructured exit criteria - "
                    f"per-criterion coverage is unknown")
    diagnostics = {"sources": [{"file": n, "status": "synthetic", "mtime": None, "fingerprint": None}
                               for n in ("embedded demo plan", "embedded demo ledger",
                                         "embedded demo task files", "embedded demo runtime")],
                   "warnings": problems, "gaps": gaps, "unmappedTaskIds": sorted(unmapped),
                   "freshnessNote": "Deterministic fixture - no source files are read, "
                                    "so there is no freshness to measure."}
    provenance = {"plan": "embedded demo plan", "ledger": "embedded demo ledger",
                  "taskFiles": "embedded demo task files", "runtime": "embedded demo runtime",
                  "payload": f"schemaVersion {SCHEMA_VERSION} - dashboard/README.md data contract",
                  "synthetic": True, "fixture": "build.py demo fixture"}
    dep_edges = [{"from": "T-105", "to": "T-106", "kind": "dep", "t0": days(5), "t1": None},
                 {"from": "T-103", "to": "T-107", "kind": "dep", "t0": days(4), "t1": None}]
    succ = [{"from": "T-105", "to": "T-106", "kind": "succ"}]
    commits = [[days(i), f"demo ledger update {i}"] for i in range(9)]
    pings = [days(i * 0.3) for i in range(24)]
    metrics = {"definitions": route_report.DEFINITIONS,
               "firstPassGateRate": [{"role": "developer", "tool": "codex", "tasks": 2, "firstVerifyPass": 1},
                                      {"role": "tester", "tool": "devin", "tasks": 1, "firstVerifyPass": 1}],
               "tasksWithoutEvidence": 5,
               "leadSeconds": [{"role": "developer", "tool": "codex", "tasks": 2, "median": 5400.0, "min": 3600.0, "max": 7200.0}],
               "testerVerdicts": {"pass": 1, "none-recorded": 1}, "cost": None,
               "note": "DEMO fixture; not real project evidence."}
    graph = finish_graph(tasks, goal_text, dep_edges, commits, pings, succ, metrics=metrics, demo=True,
                         stages=stages, diagnostics=diagnostics, provenance=provenance)
    graph["project"] = "demo-project"
    graph["generated"] = "2026-10-17 12:00"
    graph["now"] = days(9)
    return graph, len(dep_edges), len(succ)


def main(argv=None):
    demo = "--demo" in (argv if argv is not None else sys.argv[1:])
    graph, n_deps, n_succ = demo_graph() if demo else real_graph()
    payload = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")  # both pages get the same data
    OUT.mkdir(exist_ok=True)
    for tpl_name, out_name in (("graph_template.html", "graph.html"), ("template.html", "index.html")):
        page = render(tpl_name).replace("__PROJECT__", graph["project"]).replace("__DATA__", payload)
        (OUT / out_name).write_text(page, encoding="utf-8")
    print(f"{len(graph['tasks'])} tasks, {len(graph['stages'])} stages, {n_deps} dependencies, "
          f"{n_succ} successors, {len(graph['pings'])} commits -> {OUT}"
          + (" [DEMO DATA]" if demo else ""))


def render(name):
    """page template with shared CSS/JS inlined: each page is one self-contained file"""
    page = (HERE / name).read_text(encoding="utf-8")
    for marker, src in (("/*FILTERBAR_CSS*/", "filterbar.css"), ("/*FILTERBAR_JS*/", "filterbar.js"),
                        ("/*COMMON_CSS*/", "common.css"), ("/*COMMON_JS*/", "common.js")):
        page = page.replace(marker, (HERE / src).read_text(encoding="utf-8"))
    return page


if __name__ == "__main__":
    sys.exit(main())
