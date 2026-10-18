"""One mechanical step of orchestration, without a language model; plus the orchestrator heartbeat and tool limits.

  python .agentflow/tools/tick.py run [--dry-run] [--even-if-live]   act on every open task once; writes tick.json
  python .agentflow/tools/tick.py heartbeat --holder <name>   claim or refresh orchestration (exit 1: someone else holds it)
  python .agentflow/tools/tick.py release [--holder <name>]   the Orchestrator ends its session cleanly
  python .agentflow/tools/tick.py status                      live Orchestrator and limited tools; exit 0 live, 1 not
  python .agentflow/tools/tick.py next-orchestrator           first orchestrator tool that is not limited ('' if none)
  python .agentflow/tools/tick.py limit <tool> "<message>" [--group g]    record a usage limit from a tool's own message
  python .agentflow/tools/tick.py limit-migrate <tool> <group>            move a tool-wide hold under '<tool>:<group>'

Rules: .agentflow/docs/ai-handoff-protocol.md, section "Autonomous orchestration". `run` does by itself only what
needs no judgment: accept a tester whose Verdict is pass, accept a developer whose tester is done or whose independent
check is none, launch a ready task whose dependencies are done and whose tool is not limited. Everything else becomes
a "need" in tick.json for an Orchestrator session. Acceptance and launch go through accept.py and run-task.ps1, so
every gate still applies. While an Orchestrator is live (fresh heartbeat), `run` only reports: one actor at a time.
`AGENTFLOW_SHARED_DISPATCHER=shadow` adds a read-only cross-project preview; `active` requires a shared grant before each automatic worker launch. Both modes preserve the existing acceptance gate.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT  # noqa: E402
import gate  # noqa: E402
import ledger  # noqa: E402
import limit_detection  # noqa: E402
import machine_capacity  # noqa: E402
import quota_groups  # noqa: E402
import route  # noqa: E402
import dispatch  # noqa: E402
import run_task  # noqa: E402

TOOLS = FLOW_ROOT / "tools"
RT = FLOW_ROOT / "tasks" / ".runtime"
HEARTBEAT = RT / "orchestrator.json"
LIMITS = RT / "tool-limits.json"
TICK = RT / "tick.json"
LOCK = RT / "tick.lock"
LAUNCHABLE = ("codex", "claude", "agy", "devin")
# A tool can be temporarily unusable because its quota is exhausted or because
# account access is disabled. Both cases must hand orchestration to the next
# configured tool. With no reset time in the message record_limit() retries the
# preferred tool after one hour instead of removing it from the configured list.
# Whether log wording is a real provider limit: limit_detection.py, shared with
# run_task.py and conductor.ps1.


def orchestrators():
    return [t.strip() for t in os.environ.get("AGENTFLOW_ORCHESTRATORS", "claude,codex,devin,agy").split(",") if t.strip()]


def stale_minutes():
    return int(os.environ.get("AGENTFLOW_ORCHESTRATOR_STALE_MINUTES", "20"))


def now():
    return datetime.now(timezone.utc)


def iso(t):
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


class StateError(Exception):
    """Malformed or unreadable runtime state: fail closed, never pretend the record does not exist."""
    pass


def read(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return default
    except (OSError, ValueError) as e:
        raise StateError(f"cannot read {p.name}: {e}")


def read_map(p):
    """A runtime object file (orchestrator heartbeat, tool limits): a wrong shape fails closed too."""
    m = read(p, {})
    if not isinstance(m, dict):
        raise StateError(f"{p.name} is not a JSON object")
    return m


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


# --- tool limits -------------------------------------------------------------------------------------------------
def parse_reset(text, at=None):
    """When a limited tool is usable again, from its own message; one hour later when the message does not say."""
    at = at or now()
    if m := re.search(r"resets?\s+in\s+(?:(\d+)\s*d)?\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?", text, re.I):
        d, h, mi = (int(x or 0) for x in m.groups())
        if d or h or mi:
            return at + timedelta(days=d, hours=h, minutes=mi)
    if m := re.search(r"(?:resets?|try again)\s+(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*([ap]m)", text, re.I):
        hour, minute = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0), int(m.group(2) or 0)
        local = at.astimezone()
        t = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if t <= local:
            t += timedelta(days=1)
        return t.astimezone(timezone.utc)
    return at + timedelta(hours=1)


def read_limits():
    """The tool-limits map; a wrong shape fails closed (StateError): 'no limits' is never inferred from
    a bad file. '_seen' is internal metadata, not a limit record, and is tolerated as-is."""
    try:
        return ledger.check_limits(read(LIMITS, {}))
    except ValueError as e:
        raise StateError(f"cannot read {LIMITS.name}: {e}")


def record_limit(tool, text, at=None, seen=None, group=None):
    lim = read_limits()
    until = parse_reset(text, at)
    key = machine_capacity._limit_key(tool, group)
    lim[key] = {"until": iso(until), "reason": " ".join(text.split())[-200:], "at": iso(at or now())}
    if seen:
        seen_map = lim.setdefault("_seen", {})
        if not isinstance(seen_map, dict):
            seen_map = lim["_seen"] = {}
        seen_map[seen] = iso(at or now())
    write(LIMITS, lim)
    machine_capacity.record_limit(tool, until, group)
    return lim[key]


def limit_end(tool, group=None):
    """Latest recorded hold end applying to <tool> on <group>: the tool-wide hold plus its group's."""
    ends = []
    lim = read_limits()
    for key in {tool, machine_capacity._limit_key(tool, group)} if group else {tool}:
        local = lim.get(key)
        if local:
            try:
                ends.append(parse_iso(local["until"]))
            except ValueError as e:
                raise StateError(f"{LIMITS.name}: bad 'until' for {key}: {e}")
    global_end = machine_capacity.limit_until(tool, group)
    if global_end:
        ends.append(global_end)
    return max(ends, default=None)


def limited(tool, group=None, at=None):
    end = limit_end(tool, group)
    return bool(end) and end > (at or now())


def migrate_limit(tool, group):
    """Move an existing tool-wide hold under '<tool>:<group>' in the local file and the shared
    machine registry, preserving its reset time. For a hold known to belong to one quota group
    only (a legacy record from before quota groups); the later of two ends wins. Returns the
    report lines; nothing else in either store changes."""
    out = []
    lim = read_limits()
    if tool in lim:
        key = machine_capacity._limit_key(tool, group)
        entry = lim.pop(tool)
        if key in lim and parse_iso(lim[key]["until"]) > parse_iso(entry["until"]):
            entry = lim[key]
        lim[key] = entry
        write(LIMITS, lim)
        out.append(f"local {tool} -> {key} until {entry['until']}")
    end = machine_capacity.move_limit(tool, group)
    if end:
        out.append(f"machine {tool} -> {tool}:{group} until "
                   f"{datetime.fromtimestamp(end, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return out


def active_limits():
    """Recorded holds still in force, keyed '<tool>' or '<tool>:<group>'."""
    return {k: v["until"] for k, v in read_limits().items()
            if k != "_seen" and parse_iso(v["until"]) > now()}


def tool_group(tool, model=None):
    """The quota group a session on <tool>/<model> consumes (None: only tool-wide holds apply)."""
    return quota_groups.group_for(tool, model)


def launch_group(tid, tool):
    """The quota group of the session this ready task would run (its Model, or the tool default)."""
    try:
        return tool_group(tool, gate.parse(tid).get("model"))
    except (gate.TaskError, OSError):
        return None


# --- declared quota policy ------------------------------------------------------------------------------------------
# An operator's declared expectation of remaining quota - a wish, never a measurement of the provider's
# counter. Only a fresh reading can fire an action; without one every policy reports 'unknown' and the
# launch budgets in run_task.py remain the bound. A malformed file fails closed: StateError, not silence.
POLICY_FILE = FLOW_ROOT / "docs" / "quota-policy.json"
SAMPLE_MAX_AGE = 1800  # seconds; a reading older than this never justifies a policy action
_ACTIONS = ("pause", "switch", "report")


def _policy_path():
    raw = os.environ.get("AGENTFLOW_QUOTA_POLICY")
    if raw == "off":
        return None
    return Path(raw) if raw else POLICY_FILE


def quota_policy_states(at=None):
    """One entry per declared policy: [{tool, group, key, action, threshold, state, detail}]. state is
    'ok' | 'below' | 'unknown'; only 'below' may fire an action. Readings come from quota-samples.json
    next to the policy file (AGENTFLOW_QUOTA_SAMPLES overrides), keyed '<tool>' or '<tool>:<group>' -
    the same limit-key shape the observed-limits machinery uses."""
    p = _policy_path()
    if p is None or not p.exists():
        return []
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise StateError(f"cannot read {p.name}: {e}")
    if not isinstance(doc, dict) or not isinstance(doc.get("policies"), list):
        raise StateError(f"{p.name}: expected an object with a 'policies' list")
    sp = Path(os.environ.get("AGENTFLOW_QUOTA_SAMPLES") or p.parent / "quota-samples.json")
    samples = {}
    if sp.exists():
        try:
            samples = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise StateError(f"cannot read {sp.name}: {e}")
        if not isinstance(samples, dict):
            raise StateError(f"{sp.name}: expected an object of readings")
    return [_policy_state(pol, i, samples, at or now(), p.name, sp.name) for i, pol in enumerate(doc["policies"])]


def _policy_state(pol, i, samples, at, fname, sfile):
    if not isinstance(pol, dict) or not isinstance(pol.get("tool"), str) or not pol["tool"].strip():
        raise StateError(f"{fname}: policy #{i + 1} needs a 'tool'")
    if pol.get("group") is not None and not isinstance(pol["group"], str):
        raise StateError(f"{fname}: policy #{i + 1}: 'group' must be a string")
    rem = pol.get("remaining")
    if not isinstance(rem, dict) or not isinstance(rem.get("percent_below"), (int, float)) \
            or isinstance(rem["percent_below"], bool):
        raise StateError(f"{fname}: policy #{i + 1} needs 'remaining': {{\"percent_below\": <n>}}")
    action = pol.get("action") or "pause"
    if action not in _ACTIONS:
        raise StateError(f"{fname}: policy #{i + 1}: unknown action '{action}' (pause | switch | report)")
    group = pol.get("group") or None
    key = machine_capacity._limit_key(pol["tool"], group)
    st = {"tool": pol["tool"], "group": group, "key": key, "action": action,
          "threshold": rem["percent_below"], "state": "unknown", "reading": None, "detail": ""}
    s = samples.get(key)
    if s is None:
        st["detail"] = f"no reading for {key} ({sfile})"
        return st
    if not isinstance(s, dict) or not isinstance(s.get("remaining_percent"), (int, float)) \
            or isinstance(s["remaining_percent"], bool) or not isinstance(s.get("at"), str):
        raise StateError(f"quota-samples.json: the reading for '{key}' needs 'at' and 'remaining_percent'")
    try:
        sat = parse_iso(s["at"])
    except ValueError as e:
        raise StateError(f"quota-samples.json: bad 'at' for {key}: {e}")
    if s.get("resets_at") is not None:
        try:
            reset = parse_iso(s["resets_at"])
        except ValueError as e:
            raise StateError(f"quota-samples.json: bad 'resets_at' for {key}: {e}")
        if reset <= at:
            st["detail"] = f"the reading for {key} is past its reset ({s['resets_at']} <= now)"
            return st
    max_age = pol.get("sample_max_age_seconds", SAMPLE_MAX_AGE)
    if not isinstance(max_age, (int, float)) or isinstance(max_age, bool) or max_age <= 0:
        raise StateError(f"{fname}: policy #{i + 1}: 'sample_max_age_seconds' must be a positive number")
    if at - sat > timedelta(seconds=max_age):
        st["detail"] = f"stale reading for {key}: taken {s['at']}, older than {max_age}s"
        return st
    if sat - at > timedelta(seconds=max_age):
        raise StateError(f"quota-samples.json: the reading for '{key}' is dated in the future ({s['at']})")
    st["reading"] = s["remaining_percent"]
    if s["remaining_percent"] < rem["percent_below"]:
        st["state"] = "below"
        st["detail"] = f"{key} at {s['remaining_percent']}% remaining, below the declared " \
                       f"{rem['percent_below']}% threshold (read {s['at']})"
    else:
        st["state"] = "ok"
        st["detail"] = f"{key} at {s['remaining_percent']}% remaining (read {s['at']})"
    return st


def policy_hold(tool, group=None, at=None):
    """The first declared policy holding (tool, group) now: a fresh below-threshold reading under a
    'pause' or 'switch' action. 'report' only informs, and an 'unknown' or 'ok' state holds nothing."""
    want = {tool, machine_capacity._limit_key(tool, group)} if group else {tool}
    for st in quota_policy_states(at):
        if st["state"] == "below" and st["action"] in ("pause", "switch") and st["key"] in want:
            return st
    return None


def next_orchestrator(at=None, skip=()):
    return next((t for t in orchestrators() if t not in skip
                 and not limited(t, quota_groups.default_group(t), at)
                 and not policy_hold(t, quota_groups.default_group(t), at)
                 and machine_capacity.has_capacity(t, FLOW_ROOT.parent, at,
                                                   group=quota_groups.default_group(t))), "")


# --- heartbeat ---------------------------------------------------------------------------------------------------
def heartbeat(holder, force=False):
    """Claim or refresh orchestration. Refused (returns the other holder) while a different holder is live.
    A malformed heartbeat file blocks the claim - it may hide a live holder and is never silently
    overwritten; --force takes over anyway (the human's own session)."""
    try:
        other = live_orchestrator()
    except StateError:
        if not force:
            raise
        other = None
    if other and other.get("holder") != holder and not force:
        return other
    write(HEARTBEAT, {"holder": holder, "at": iso(now())})
    return None


def release(holder=None):
    hb = read_map(HEARTBEAT)
    if hb and (holder is None or hb.get("holder") == holder):
        HEARTBEAT.unlink(missing_ok=True)


def live_orchestrator(at=None):
    if not HEARTBEAT.exists():
        return None
    hb = read_map(HEARTBEAT)
    if not isinstance(hb.get("holder"), str) or not hb["holder"] or not isinstance(hb.get("at"), str):
        raise StateError(f"{HEARTBEAT.name}: malformed heartbeat record (needs holder and at)")
    try:
        at_hb = parse_iso(hb["at"])
    except ValueError as e:
        raise StateError(f"{HEARTBEAT.name}: bad heartbeat timestamp: {e}")
    return hb if (at or now()) - at_hb < timedelta(minutes=stale_minutes()) else None


# --- worker processes --------------------------------------------------------------------------------------------
def alive(pid, pid_start=None):
    """The worker process still runs - the same identity rule the launcher uses (run_task.alive):
    a recorded start must re-measure equal, so a reused pid can impersonate a live worker nowhere."""
    return run_task.alive(pid, pid_start)


def log_tail(att, n=4000):
    p = Path(att.get("log") or "")
    try:
        return p.read_text(encoding="utf-8", errors="replace")[-n:] if p.is_file() else ""
    except OSError:
        return ""


def limit_detail(att):
    """(phrase, kind) of the attempt's provider limit: 'quota' scopes to the attempt's quota
    group, 'account' holds the whole tool. A launcher-flagged limit without a readable log
    keeps the kind the launcher recorded, else tool-wide 'account' (pre-quota-groups attempts)."""
    if att.get("status") in ("exited", "error") and att.get("log"):
        detail = limit_detection.detect_detail_file(att["log"], att.get("exitCode"))
        if detail:
            return detail
    if att.get("limitHit"):
        return (att.get("limitPhrase") or "flagged by the launcher", att.get("limitKind") or "account")
    return None


def hit_limit(att):
    return bool(limit_detail(att))


# --- decisions ---------------------------------------------------------------------------------------------------
def testers_of(dev_id, rows):
    """(tester id, ledger status) of every tester task that checks this developer task."""
    out = []
    for k, r in rows.items():
        if r.get("Role") != "tester" or r.get("Status") in ("rejected", "cancelled"):
            continue
        try:
            if gate.parse(k)["checked"]["id"] == dev_id:
                out.append((k, r.get("Status")))
        except (gate.TaskError, OSError):
            continue
    return out


def decide(rows, at=None):
    """[(task, action, detail)], action: accept | launch | wait | need. Reads files, changes nothing."""
    out = []
    done = {k for k, r in rows.items() if r.get("Status") == "done"}
    for tid, r in rows.items():
        st = r.get("Status")
        if st == "blocked" and (r.get("Notes") or "").startswith("awaiting approval"):
            out.append((tid, "wait", "awaiting the human's approval of the plan (ledger.py approve)"))
            continue
        if st in ("done", "rejected", "cancelled", "blocked"):
            continue
        try:
            t = gate.parse(tid)
        except (gate.TaskError, OSError) as e:
            out.append((tid, "need", f"Task File: {e}"))
            continue
        try:
            att = gate.last_attempt(tid)
        except gate.TaskError as e:
            out.append((tid, "need", f"runtime state: {e}"))
            continue
        running = bool(att) and att.get("status") == "running"
        if running and not att.get("manual"):
            if run_task.attempt_alive(att):
                out.append((tid, "wait", f"{att.get('tool')} is working (attempt {att.get('n')})"))
            elif run_task.attempt_uncertain(att):
                out.append((tid, "need", f"attempt {att.get('n')}: pid {att['pid']} is alive but its start "
                                         "identity is unconfirmed (a possibly reused pid) - the task stays "
                                         "locked; verify and stop it with run_task.py --stop"))
            else:
                strays, members = run_task.leftover_processes(tid, att)
                if strays or members:
                    shown = ", ".join(map(str, strays[:5])) or f"{members} process(es) in the worker's job"
                    out.append((tid, "need", f"attempt {att.get('n')}: the worker process is gone but "
                                             f"managed process(es) still run ({shown}) - end them "
                                             "before a successor"))
                else:
                    out.append((tid, "need", "the worker process is gone without a final state (dead attempt): recover it"))
            continue
        if running:
            out.append((tid, "wait", f"{att.get('tool')} is working (attempt {att.get('n')})"))
            continue
        if st == "ready":
            deps = [d for d in t["depends"] if d not in done]
            tool = (r.get("Tool") or "").strip()
            if deps:
                out.append((tid, "wait", f"depends on {', '.join(deps)}"))
            elif tool not in LAUNCHABLE:
                out.append((tid, "need", f"Tool '{tool}' cannot be started automatically: route it or start it by hand"))
            elif limited(tool, group := tool_group(tool, t.get("model")), at):
                scope = f" group {group}" if group else ""
                out.append((tid, "need", f"its tool {tool}{scope} is limited until {iso(limit_end(tool, group))}: move it to another tool or wait"))
            elif (hold := policy_hold(tool, tool_group(tool, t.get("model")), at)):
                if hold["action"] == "switch":
                    out.append((tid, "need", f"quota policy: {hold['detail']} - the declared action is to "
                                             "switch this task to another tool"))
                else:
                    out.append((tid, "wait", f"quota policy: {hold['detail']} - the declared action pauses "
                                             "launches on it until a fresh reading shows headroom"))
            else:
                out.append((tid, "launch", tool))
            continue
        if not att:
            out.append((tid, "need", f"status '{st}' without any attempt"))
            continue
        if hit_limit(att):
            out.append((tid, "need", f"{att.get('tool')} hit a usage limit in attempt {att.get('n')}: relaunch on a fallback tool"))
            continue
        outcome = gate.result_field(t, "Outcome")
        if t["role"] == "tester":
            verdict = gate.result_field(t, "Verdict")
            if outcome == "completed" and verdict == "pass":
                out.append((tid, "accept", "tester, Verdict pass"))
            else:
                out.append((tid, "need", f"tester Outcome {outcome or 'missing'}, Verdict {verdict or 'missing'}: decide on {t['checked']['id']}"))
        elif t["role"] == "developer":
            if outcome != "completed":
                out.append((tid, "need", f"developer Outcome {outcome or 'missing'} (attempt {att.get('status')}): decide"))
            elif (t["independent"] or "").lower().startswith("none"):
                out.append((tid, "accept", "developer, no independent check"))
            elif testers := testers_of(tid, rows):
                if any(s == "done" for _, s in testers):
                    out.append((tid, "accept", "developer, its tester is done"))
                else:
                    out.append((tid, "wait", f"its tester {', '.join(k for k, _ in testers)} is not done"))
            else:
                out.append((tid, "need", "developer completed: write its tester task"))
        else:
            out.append((tid, "need", f"{t['role']} task: closed by the Orchestrator"))
    return out


# --- acting ------------------------------------------------------------------------------------------------------
def learn_limits(rows):
    """Record limits from finished attempts once, so later launches and the conductor skip those tools."""
    seen = read_limits().get("_seen", {})
    if not isinstance(seen, dict):
        seen = {}
    for tid in rows:
        try:
            att = gate.last_attempt(tid)
        except gate.TaskError:
            continue  # unreadable runtime: decide() surfaces it as a need
        if not att or att.get("tool") in (None, "manual") or not hit_limit(att):
            continue
        key = f"{tid}#{att.get('n')}"
        if key not in seen:
            detail = limit_detail(att)
            group = att.get("quotaGroup") if detail and detail[1] == "quota" else None
            record_limit(att["tool"], log_tail(att, 1500), at=parse_iso(att["finishedAt"]) if att.get("finishedAt") else None,
                         seen=key, group=group)


def py(*args):
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout + p.stderr).strip()


def do_accept(tid):
    code, out = py(TOOLS / "accept.py", tid)
    return code == 0, (out.splitlines() or [""])[-1]


def do_launch(tid, tool, grant=None):
    ps = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
    args = [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(TOOLS / "run-task.ps1"), tid, tool]
    if grant:
        args.extend(["-DispatchGrant", grant])
    p = subprocess.run(args,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout + p.stderr).strip()
    if p.returncode:
        return False, out[-300:]
    return True, tool  # the launcher owns the transition, including direct/manual starts


def use_backup(tid, current_tool):
    """Switch one unstarted ready task to Jev's saved backup when the primary has no slot."""
    if gate.last_attempt(tid):
        return False, "task has an attempt; its header cannot be changed"
    task = gate.parse(tid)
    path = Path(task["file"])
    original = path.read_text(encoding="utf-8-sig")
    head = gate.header(original)
    backup = gate.field(head, "Backup Tool")
    if not backup or backup not in LAUNCHABLE or backup == current_tool:
        return False, "no usable backup is recorded"
    model, effort = gate.parse_model(gate.field(head, "Backup Model"))
    group = tool_group(backup, model)
    if limited(backup, group) or not machine_capacity.has_capacity(backup, FLOW_ROOT.parent, group=group):
        return False, f"backup {backup} has no free slot"
    route.set_header(path, backup, model, effort)
    code, output = py(TOOLS / "ledger.py", "set", tid, "--tool", backup)
    if code:
        path.write_text(original, encoding="utf-8", newline="\n")
        return False, f"backup update failed: {output[-200:]}"
    try:
        route._log(tid, {"event": "backup-selected", "at": iso(now()), "primaryTool": current_tool,
                         "tool": backup, "model": model, "effort": effort, "reason": "primary unavailable"})
    except (OSError, ValueError):
        pass  # the ledger and Task File are authoritative for launch; a missing metric cannot block it
    return True, backup


def lock():
    """One tick at a time (the conductor and a background Orchestrator may both call run). Stale after 30 minutes."""
    RT.mkdir(parents=True, exist_ok=True)
    try:
        if LOCK.exists() and now().timestamp() - LOCK.stat().st_mtime > 1800:
            LOCK.unlink()
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def run(dry=False, even_if_live=False, accept=do_accept, launch=do_launch):
    live = live_orchestrator()
    report_only = dry or (live is not None and not even_if_live)
    if not report_only and not lock():
        return {"at": iso(now()), "skipped": "another tick is running"}
    try:
        rows = gate.ledger_rows()
        if not dry:
            learn_limits(rows)
        shadow = None
        dispatch_mode = os.environ.get("AGENTFLOW_SHARED_DISPATCHER", "off")
        if dispatch_mode == "shadow":
            try:
                shadow = dispatch.plan()
            except (OSError, ValueError, TimeoutError) as error:
                shadow = {"mode": "shadow", "error": f"{type(error).__name__}: {error}"}
        acted, failed, busy = [], [], []
        if not report_only:
            for _ in range(len(rows) + 1):  # accept until nothing changes: a tester accepted can unlock its developer
                todo = [(t, d) for t, a, d in decide(rows) if a == "accept" and t not in {f["task"] for f in failed}]
                if not todo:
                    break
                for tid, detail in todo:
                    ok, msg = accept(tid)
                    (acted if ok else failed).append({"task": tid, "action": "accept", "detail": msg if ok else f"accept stopped: {msg}"})
                rows = gate.ledger_rows()
            if os.environ.get("AGENTFLOW_BACKUP_ROUTING", "off") == "on":
                for tid, row in rows.items():
                    if row.get("Status") != "ready":
                        continue
                    tool = (row.get("Tool") or "").strip()
                    group = launch_group(tid, tool)
                    if tool not in LAUNCHABLE or (not limited(tool, group) and
                                                  machine_capacity.has_capacity(tool, FLOW_ROOT.parent, group=group)):
                        continue
                    switched, detail = use_backup(tid, tool)
                    if switched:
                        acted.append({"task": tid, "action": "backup", "detail": f"{tool} -> {detail}"})
                    elif detail != "no usable backup is recorded":
                        busy.append({"task": tid, "detail": detail})
                rows = gate.ledger_rows()
            launches = [(tid, tool) for tid, action, tool in decide(rows) if action == "launch"]
            if dispatch_mode == "active":
                dispatch.register(FLOW_ROOT.parent, launches)
            for tid, a, tool in decide(rows):
                if a == "launch":
                    grant = None
                    if dispatch_mode == "active":
                        grant, reason = dispatch.request(FLOW_ROOT.parent, tid, tool)
                        if not grant:
                            busy.append({"task": tid, "detail": reason})
                            continue
                    try:
                        ok, msg = launch(tid, tool, grant) if grant else launch(tid, tool)
                    finally:
                        if grant:
                            dispatch.release(grant)
                    if not ok and ("running session(s) on this machine" in msg or "machine capacity wait:" in msg):
                        busy.append({"task": tid, "detail": f"{tool} has no free slot (project rule parallel)"})
                        continue
                    (acted if ok else failed).append({"task": tid, "action": "launch", "detail": msg if ok else f"launch refused: {msg}"})
            rows = gate.ledger_rows()
        plan = decide(rows)
        failed_ids = {f["task"] for f in failed}
        needs = failed + [{"task": t, "action": "need", "detail": d} for t, a, d in plan if a == "need" and t not in failed_ids]
        report = {"at": iso(now()), "reportOnly": report_only, "live": live, "acted": acted,
                  "would": [{"task": t, "action": a, "detail": d} for t, a, d in plan if a in ("accept", "launch")] if report_only else [],
                  "needs": needs, "waits": busy + [{"task": t, "detail": d} for t, a, d in plan if a == "wait"],
                  "nextOrchestrator": next_orchestrator(),
                  "limited": active_limits(),
                  "quotaPolicy": quota_policy_states()}
        if dispatch_mode == "active":
            report["dispatchMode"] = "active"
        if shadow is not None:
            report["dispatchShadow"] = shadow
        if not dry:
            write(TICK, report)
        return report
    finally:
        if not report_only:
            LOCK.unlink(missing_ok=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--even-if-live", action="store_true", help="act although an Orchestrator heartbeat is fresh")
    r.add_argument("--json", action="store_true", help="print the report as JSON")
    hp = sub.add_parser("heartbeat")
    hp.add_argument("--holder", default="orchestrator")
    hp.add_argument("--force", action="store_true", help="take over from another live holder (the human's session)")
    sub.add_parser("release").add_argument("--holder", help="release only if this holder has it")
    sub.add_parser("status")
    no = sub.add_parser("next-orchestrator")
    no.add_argument("--skip", default="", help="comma-separated tools whose atomic claim just lost a race")
    lp = sub.add_parser("limit")
    lp.add_argument("tool")
    lp.add_argument("text")
    lp.add_argument("--group", help="quota group the hold applies to (default: detected from the message)")
    mv = sub.add_parser("limit-migrate")
    mv.add_argument("tool")
    mv.add_argument("group")
    a = ap.parse_args()
    try:
        return dispatch_cmd(a)
    except StateError as e:
        print(f"tick: {e}", file=sys.stderr)
        return 1


def dispatch_cmd(a):
    if a.cmd == "run":
        rep = run(a.dry_run, a.even_if_live)
        if a.json:
            print(json.dumps(rep, indent=2, ensure_ascii=False))
            return 0
        if rep.get("skipped"):
            print(f"skipped: {rep['skipped']}")
            return 0
        if rep["reportOnly"] and rep["live"]:
            print(f"report only: Orchestrator {rep['live']['holder']} is live (heartbeat {rep['live']['at']})")
        for x in rep["acted"]:
            print(f"{x['action']:7} {x['task']}: {x['detail']}")
        for x in rep["would"]:
            print(f"would {x['action']} {x['task']}: {x['detail']}")
        for x in rep["needs"]:
            print(f"need    {x['task']}: {x['detail']}")
        for x in rep["waits"]:
            print(f"wait    {x['task']}: {x['detail']}")
        for k, v in rep["limited"].items():
            print(f"limited {k} until {v}")
        for s in rep.get("quotaPolicy") or []:
            if s["state"] != "ok":
                scope = f"{s['tool']}:{s['group']}" if s.get("group") else s["tool"]
                print(f"policy  {scope} {s['state']} ({s['action']}): {s['detail']}")
        if shadow := rep.get("dispatchShadow"):
            print(f"dispatcher shadow: {len(shadow.get('selected', []))} would launch, "
                  f"{len(shadow.get('waits', []))} would wait"
                  + (f"; error: {shadow['error']}" if shadow.get("error") else ""))
        return 0
    if a.cmd == "heartbeat":
        if other := heartbeat(a.holder, a.force):
            print(f"refused: {other['holder']} holds orchestration (heartbeat {other['at']}); read, do not act")
            return 1
        return 0
    if a.cmd == "release":
        release(a.holder)
        return 0
    if a.cmd == "status":
        hb = live_orchestrator()
        print(f"orchestrator: {hb['holder']} (heartbeat {hb['at']})" if hb else "orchestrator: none live")
        lim = read_limits()
        for k, v in active_limits().items():
            print(f"limited: {k} until {v} - {((lim.get(k) or {}).get('reason') or '')[-80:]}")
        for s in quota_policy_states():
            print(f"quota policy: {s['key']} is {s['state']} ({s['action']}): {s['detail']}")
        return 0 if hb else 1
    if a.cmd == "next-orchestrator":
        print(next_orchestrator(skip={x for x in a.skip.split(",") if x}))
        return 0
    if a.cmd == "limit":
        group = a.group
        if group is None:
            detail = limit_detection.detect_detail(a.text, 1)  # a limit message arrives as failure evidence
            if detail and detail[1] == "quota":
                group = quota_groups.default_group(a.tool)
        e = record_limit(a.tool, a.text, group=group)
        scope = f" group {group}" if group else ""
        print(f"{a.tool}{scope} limited until {e['until']}")
        return 0
    if a.cmd == "limit-migrate":
        for line in migrate_limit(a.tool, a.group):
            print(line)
        return 0


if __name__ == "__main__":
    sys.exit(main())
