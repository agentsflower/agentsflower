"""Coordinate AgentFlow sessions across projects on one machine.

The registry is shared by all projects of the current OS user. A short OS file lock
serializes claims, so two launchers cannot both take the last tool slot or PORT.
Leases follow worker PIDs and are removed after normal exit or when the process dies.
Capacity, temporary tool unavailability, and dispatch grants live here; task memory stays local.
"""
import argparse
import ctypes
import json
import os
import re
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

TOOLS = ("codex", "claude", "devin", "agy")
DEFAULT_CAPACITY = {"codex": 1}
PENDING_SECONDS = 600
READY_SECONDS = 600
GRANT_SECONDS = 60
GROUP = r"[A-Za-z0-9_.-]+"


def _limit_key(tool, group=None):
    """Registry key for a provider hold: '<tool>' tool-wide, '<tool>:<group>' one quota group."""
    if group:
        if not re.fullmatch(GROUP, str(group)):
            raise ValueError(f"bad quota group: {group!r}")
        return f"{tool}:{group}"
    return tool


def _limit_end(state, tool, group=None):
    """Latest hold timestamp applying to <tool> on <group>: the tool-wide hold plus its group's."""
    lim = state.get("limits", {})
    end = lim.get(tool, 0)
    if group:
        end = max(end, lim.get(_limit_key(tool, group), 0))
    return end

# Windows transient replace failures (a scanner or indexer briefly holds registry.json):
# ERROR_ACCESS_DENIED=5, ERROR_SHARING_VIOLATION=32. Anything else, and exhaustion, fails closed.
REPLACE_ATTEMPTS = 10
REPLACE_DELAY = 0.05


def _replace_retry(temp, path):
    """One atomic os.replace, retried with a short bounded backoff only while Windows reports a transient
    sharing/access failure; a permanent failure leaves the previous registry untouched and raises."""
    for left in range(REPLACE_ATTEMPTS, 0, -1):
        try:
            os.replace(temp, path)
            return
        except OSError as error:
            if getattr(error, "winerror", None) not in (5, 32) or left == 1:
                raise
            time.sleep(REPLACE_DELAY)


def state_dir():
    override = os.environ.get("AGENTFLOW_MACHINE_STATE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_STATE_HOME")
    return Path(base).expanduser().resolve() / "AgentFlow" / "machine" if base else Path.home() / ".agentflow-machine"


def _pid_start(pid):
    """Process start as .NET ticks - the same measurement run_task.pid_start makes for attempt records,
    duplicated here because this standalone tool cannot import the launcher. Windows: GetProcessTimes.
    Linux: /proc jiffies -> epoch -> ticks. Elsewhere: `ps -o lstart=` -> ticks, or None (not measurable)."""
    if os.name == "nt":
        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return None
        try:
            times = [ctypes.c_ulonglong() for _ in range(4)]
            if kernel.GetProcessTimes(handle, *(ctypes.byref(x) for x in times)):
                return times[0].value + 504911232000000000  # FILETIME (1601) -> .NET ticks (0001)
            return None
        finally:
            kernel.CloseHandle(handle)
    try:
        clk = os.sysconf("SC_CLK_TCK")
        btime = next(int(line.split()[1]) for line in Path("/proc/stat").read_text().splitlines()
                     if line.startswith("btime"))
        stat = Path(f"/proc/{int(pid)}/stat").read_text().rsplit(")", 1)[1].split()
        epoch = btime + int(stat[19]) / clk  # field 22 (starttime) after "pid (comm)" is removed
        return int(epoch * 10_000_000) + 504911232000000000
    except (OSError, IndexError, ValueError, StopIteration):
        pass
    try:
        out = subprocess.run(["ps", "-p", str(int(pid)), "-o", "lstart="], capture_output=True, text=True,
                             env={**os.environ, "LC_ALL": "C"}, timeout=10).stdout.strip()
        epoch = datetime.strptime(out, "%a %b %d %H:%M:%S %Y").replace(tzinfo=timezone.utc).timestamp()
        return int(epoch * 10_000_000) + 504911232000000000
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _alive(pid, started=None):
    """The lease holder still runs - the same identity rule as run_task.alive on every platform: a recorded
    start must re-measure equal, so a reused pid cannot impersonate a live worker, and an unmeasurable or
    failed identity check is never 'alive'. Without a recorded start only the pid itself can be checked."""
    if not pid:
        return False
    if os.name == "nt":
        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != 259:
                return False
            if started is not None:
                times = [ctypes.c_ulonglong() for _ in range(4)]
                if not kernel.GetProcessTimes(handle, *(ctypes.byref(x) for x in times)):
                    return False  # alive but identity unverifiable: not the recorded lease holder
                return times[0].value + 504911232000000000 == int(started)
            return True
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    if started is not None:
        return _pid_start(pid) == int(started)
    return True


@contextmanager
def _locked():
    directory = state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / "registry.lock"
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            for _ in range(100):
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
            else:
                raise TimeoutError("machine capacity registry is busy")
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            path = directory / "registry.json"
            try:
                state = json.loads(path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                state = {"leases": [], "limits": {}}
            state.setdefault("leases", [])
            state.setdefault("limits", {})
            state.setdefault("projects", {})
            state.setdefault("dispatch", {"ready": {}, "grants": [], "last_served": {}})
            yield state
            temp = directory / f"registry.{os.getpid()}.{uuid.uuid4().hex}.tmp"
            try:
                temp.write_text(json.dumps(state, indent=2), encoding="utf-8")
                _replace_retry(temp, path)
            finally:
                temp.unlink(missing_ok=True)
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _clean(state):
    now = time.time()
    state["leases"] = [lease for lease in state["leases"] if
                       (_alive(lease.get("pid"), lease.get("pidStart")) if lease.get("active") else
                        now - lease.get("created", 0) < PENDING_SECONDS or
                        _alive(lease.get("pid"), lease.get("pidStart")))]
    state["limits"] = {tool: end for tool, end in state["limits"].items() if end > now}
    state["projects"] = {p: t for p, t in state.get("projects", {}).items()
                         if Path(p).is_dir() or now - t < PENDING_SECONDS}
    dispatch = state.setdefault("dispatch", {"ready": {}, "grants": [], "last_served": {}})
    dispatch["ready"] = {p: entry for p, entry in dispatch.get("ready", {}).items()
                         if now - entry.get("at", 0) < READY_SECONDS and Path(p).is_dir()}
    dispatch["grants"] = [grant for grant in dispatch.get("grants", []) if grant.get("until", 0) > now]
    dispatch.setdefault("last_served", {})


def project_capacity(tool, project):
    """Project-specific cap, or zero when the project did not set one."""
    root = Path(project)
    value = 0
    rules = (root / ".agentflow" / "docs" / "engineering-rules.md",
             root / ".agentflow" / "docs" / "project-rules.md", root / "AGENTS.md")
    for path in rules:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            marker = f"- parallel: {tool}="
            if line.strip().startswith(marker):
                project_value = int(line.strip()[len(marker):].strip("` "))
                if project_value < 1:
                    raise ValueError("project parallel capacity must be positive")
                value = min(value, project_value) if value else project_value
    return value


def capacity(tool, project=None):
    if tool not in TOOLS:
        raise ValueError(f"unknown tool: {tool}")
    raw = os.environ.get(f"AGENTFLOW_MACHINE_{tool.upper()}_MAX")
    value = DEFAULT_CAPACITY.get(tool, 0) if raw is None else int(raw)
    if value < 0:
        raise ValueError("machine capacity must be zero or positive")
    if project:
        project_value = project_capacity(tool, project)
        if project_value:
            value = min(value, project_value) if value else project_value
    return value


def has_capacity(tool, project, at=None, group=None):
    """A read-only scheduling hint; claim() is still the atomic final decision."""
    requested = capacity(tool, project)
    with _locked() as state:
        _clean(state)
        if _limit_end(state, tool, group) > (at.timestamp() if at else time.time()):
            return False
        current = [lease for lease in state["leases"] if lease["tool"] == tool]
        grants = [grant for grant in state["dispatch"]["grants"] if grant["tool"] == tool]
        if os.environ.get("AGENTFLOW_SHARED_DISPATCHER") == "active":
            machine_limit = capacity(tool)
            local_limit = project_capacity(tool, project)
            same_project = sum(item["project"] == str(Path(project).resolve()) for item in current + grants)
            return (not machine_limit or len(current) + len(grants) < machine_limit) and (
                not local_limit or same_project < local_limit)
        active_caps = [lease["cap"] for lease in current if lease.get("cap")]
        effective = min([x for x in [requested, *active_caps] if x], default=0)
        return not effective or len(current) + len(grants) < effective


def claim(tool, project, owner, port=None, cap=None, pid=None, pid_start=None, grant=None, group=None):
    requested = capacity(tool, project) if cap is None else cap
    if requested < 0:
        raise ValueError("machine capacity must be zero or positive")
    with _locked() as state:
        _clean(state)
        end = _limit_end(state, tool, group)
        if end > time.time():
            scope = "globally" if state["limits"].get(tool, 0) >= end else f"group '{group}'"
            return None, f"{tool} is {scope} limited until {datetime.fromtimestamp(end, timezone.utc).isoformat()}"
        current = [lease for lease in state["leases"] if lease["tool"] == tool]
        grants = state["dispatch"]["grants"]
        selected = next((item for item in grants if item["token"] == grant), None) if grant else None
        if grant and (not selected or (selected["tool"], selected["project"], selected["task"]) !=
                      (tool, str(Path(project).resolve()), owner)):
            return None, "dispatch grant is missing, expired, or belongs to another task"
        others = [item for item in grants if item["tool"] == tool and item is not selected]
        if selected:
            machine_limit = capacity(tool)
            local_limit = project_capacity(tool, project)
            occupied = len(current) + len(others)
            same_project = sum(lease["project"] == str(Path(project).resolve()) for lease in current)
            same_project += sum(item["project"] == str(Path(project).resolve()) for item in others)
            if machine_limit and occupied >= machine_limit:
                return None, f"{tool} has no free machine slot ({occupied}/{machine_limit})"
            if local_limit and same_project >= local_limit:
                return None, f"{tool} has no free project slot ({same_project}/{local_limit})"
        else:
            active_caps = [lease["cap"] for lease in current if lease.get("cap")]
            effective = min([x for x in [requested, *active_caps] if x], default=0)
            if effective and len(current) + len(others) >= effective:
                return None, f"{tool} has no free machine slot ({len(current) + len(others)}/{effective})"
        if port and any(str(lease.get("port")) == str(port) for lease in state["leases"]):
            return None, f"PORT={port} is reserved by another AgentFlow project"
        token = uuid.uuid4().hex
        if selected:
            grants.remove(selected)
        state["projects"][str(Path(project).resolve())] = time.time()
        state["leases"].append({"token": token, "tool": tool, "project": str(Path(project).resolve()),
                                "owner": owner, "port": str(port) if port else None, "cap": requested,
                                "pid": int(pid or os.getpid()), "pidStart": int(pid_start) if pid_start else None,
                                "active": False, "created": time.time()})
        return token, ""


def activate(token, pid, pid_start=None):
    with _locked() as state:
        for lease in state["leases"]:
            if lease["token"] == token:
                lease.update(pid=int(pid), pidStart=int(pid_start) if pid_start else None, active=True)
                return True
    return False


def release(token):
    with _locked() as state:
        state["leases"] = [lease for lease in state["leases"] if lease["token"] != token]


def record_limit(tool, until, group=None):
    with _locked() as state:
        state["limits"][_limit_key(tool, group)] = until.timestamp()


def limit_until(tool, group=None):
    with _locked() as state:
        _clean(state)
        end = _limit_end(state, tool, group)
    return datetime.fromtimestamp(end, timezone.utc) if end else None


def move_limit(tool, group):
    """Move a tool-wide hold under '<tool>:<group>', keeping its reset time; the later of two ends wins.

    Legacy holds recorded before quota groups stay tool-wide until an explicit migration; other
    limits, leases and projects are untouched. Returns the moved timestamp, or None."""
    with _locked() as state:
        _clean(state)
        end = state["limits"].pop(tool, None)
        if end is None:
            return None
        key = _limit_key(tool, group)
        state["limits"][key] = max(end, state["limits"].get(key, 0))
        return end


def known_projects():
    """Project roots that claimed a slot or were installed here (existing AgentFlow installs only)."""
    with _locked() as state:
        projects = dict(state.get("projects", {}))
    return sorted(p for p in projects if (Path(p) / ".agentflow").is_dir())


def register_project(project):
    """Remember a project root without claiming a slot (install.py calls this)."""
    with _locked() as state:
        _clean(state)
        state["projects"][str(Path(project).resolve())] = time.time()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    take = sub.add_parser("claim")
    take.add_argument("tool", choices=TOOLS)
    take.add_argument("project")
    take.add_argument("owner")
    take.add_argument("--port")
    take.add_argument("--max", type=int, dest="cap")
    take.add_argument("--pid", type=int)
    take.add_argument("--pid-start", type=int)
    take.add_argument("--grant")
    take.add_argument("--group", help="quota group the session consumes; its group holds also apply")
    active = sub.add_parser("activate")
    active.add_argument("token")
    active.add_argument("pid", type=int)
    active.add_argument("--pid-start", type=int)
    sub.add_parser("status")
    sub.add_parser("projects")
    done = sub.add_parser("release")
    done.add_argument("token")
    mv = sub.add_parser("move-limit", help="move a tool-wide hold under '<tool>:<group>', keeping the reset time")
    mv.add_argument("tool", choices=TOOLS)
    mv.add_argument("group")
    args = parser.parse_args()
    try:
        if args.command == "claim":
            token, reason = claim(args.tool, args.project, args.owner, args.port, args.cap, args.pid, args.pid_start,
                                  args.grant, args.group)
            if token:
                print(token)
            else:
                print(reason, file=sys.stderr)
                return 4  # busy: wait for a shared resource, do not create an Orchestrator need
        elif args.command == "activate":
            return 0 if activate(args.token, args.pid, args.pid_start) else 1
        elif args.command == "release":
            release(args.token)
        elif args.command == "move-limit":
            end = move_limit(args.tool, args.group)
            if end:
                print(f"{args.tool} -> {_limit_key(args.tool, args.group)} until "
                      f"{datetime.fromtimestamp(end, timezone.utc).isoformat()}")
            else:
                print(f"no active {args.tool} limit to move")
        elif args.command == "status":
            with _locked() as state:
                _clean(state)
                print(json.dumps(state, indent=2))
        elif args.command == "projects":
            for project in known_projects():
                print(project)
    except (OSError, ValueError, TimeoutError) as error:
        print(f"machine capacity: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
