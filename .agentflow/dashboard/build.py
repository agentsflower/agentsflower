#!/usr/bin/env python3
"""Builds .agentflow/dashboard/out/index.html and out/graph.html from .agentflow/state/tasks.md, .agentflow/tasks/T-*.md and git history.

Run from anywhere: python .agentflow/dashboard/build.py        (real project data)
                   python .agentflow/dashboard/build.py --demo (deterministic DEMO DATA fixture, no project reads)
The project is read-only; output goes only to .agentflow/dashboard/out/ (git-ignored). Data contract: .agentflow/dashboard/README.md.
Dashboard source snapshots: .agentflow/dashboard/snapshot.py.
"""
import json, os, re, subprocess, sys
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
LEDGER_REL = LEDGER.relative_to(ROOT).as_posix()
TASKS_REL = TASKS.relative_to(ROOT).as_posix()
PROJECT = ROOT.name

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


def finish_graph(tasks, goal_text, dep_edges, commits, pings, succ, metrics=None, demo=False):
    origins(tasks, goal_text)
    ch = chains(tasks, succ)
    for t in tasks.values():
        t["chain"] = ch[t["id"]]
    graph = {"project": PROJECT, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
             "now": datetime.now().astimezone().isoformat(timespec="seconds"),
             "tasks": list(tasks.values()), "edges": dep_edges + succ + check_edges(tasks),
             "commits": commits, "pings": pings, "metrics": metrics, "demo": demo}
    return graph


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
    graph = finish_graph(tasks, goal_text, dep_edges, commits, pings, succ, metrics=route_report.metrics())
    return graph, len(dep_edges), len(succ)


def demo_graph():
    """Deterministic DEMO DATA fixture: fixed timestamps, no reads of ledger, Task Files, runtime or git."""
    base = datetime.fromisoformat("2026-10-10T09:00:00+00:00").timestamp()
    rows = [
        ("T-101", "Launcher parity fix", "1", "developer", "codex", "done", "abc1234", "done", "completed", None, "none - local change"),
        ("T-102", "Verify launcher parity", "1", "tester", "devin", "done", "def5678", "done", "completed", ("T-101", "abc1234"), "tester"),
        ("T-103", "Honest metrics dashboard", "2", "developer", "devin", "review", "9f00dc1", "done", "completed", None, "tester"),
        ("T-104", "Verify metrics dashboard", "2", "tester", "codex", "in progress", "", "in progress", "", ("T-103", "deadbeef"), "tester"),
        ("T-105", "Old probe cleanup", "2", "developer", "agy", "rejected", "", "blocked", "", None, "none - superseded"),
        ("T-106", "Successor probe cleanup", "2", "developer", "codex", "in progress", "", "in progress", "", None, "none - rework of T-105"),
        ("T-107", "Deploy staging update", "2", "deployer", "claude", "blocked", "", "", "", None, "none - waits for T-103, owner decision"),
        ("T-108", "Cancelled experiment", "1", "developer", "codex", "cancelled", "", "", "", None, "none - owner cancelled"),
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
    graph = finish_graph(tasks, goal_text, dep_edges, commits, pings, succ, metrics=metrics, demo=True)
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
    print(f"{len(graph['tasks'])} tasks, {n_deps} dependencies, {n_succ} successors, "
          f"{len(graph['pings'])} commits -> {OUT}" + (" [DEMO DATA]" if demo else ""))


def render(name):
    """page template with shared CSS/JS inlined: each page is one self-contained file"""
    page = (HERE / name).read_text(encoding="utf-8")
    for marker, src in (("/*FILTERBAR_CSS*/", "filterbar.css"), ("/*FILTERBAR_JS*/", "filterbar.js"),
                        ("/*COMMON_CSS*/", "common.css"), ("/*COMMON_JS*/", "common.js")):
        page = page.replace(marker, (HERE / src).read_text(encoding="utf-8"))
    return page


if __name__ == "__main__":
    sys.exit(main())
