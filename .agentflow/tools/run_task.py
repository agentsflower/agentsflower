#!/usr/bin/env python3
"""Launch one worker attempt for one task and track its process state.

  python .agentflow/tools/run_task.py T-007 codex          # launch a developer or tester task
  python .agentflow/tools/run_task.py T-007 --manual       # same gate and preparation, no process: a human starts the tool
  python .agentflow/tools/run_task.py --status             # process state of the last attempt of every task
  python .agentflow/tools/run_task.py T-007 --stop         # kill a hung worker (whole process tree), release the lock
  python .agentflow/tools/run_task.py T-007 --mark-finished# a manual attempt has finished
  python .agentflow/tools/run_task.py T-007 --recheck      # rerun the end check for an attempt that exited 0 but failed it
  python .agentflow/tools/run_task.py --watchdog           # stop non-manual workers past their recorded deadline

.agentflow/tools/run-task.ps1 is a thin compatibility wrapper: it translates the old parameter names and delegates
here, preserving the exit code. Existing callers (tick.py, conductor.ps1, humans) keep working on Windows; on
macOS/Linux this script is the launcher and needs no PowerShell.

Rules: .agentflow/docs/ai-handoff-protocol.md, sections "Runtime state" and "Launching workers".
Task File parsing, preflight and end-of-attempt checks: .agentflow/tools/gate.py. This script does the side effects:
worktrees and checkouts, environment, processes, tasks/.runtime/T-NNN.json (attempt history).

Tool command lines below are defaults: verify them once against your installed versions.
Machine settings are environment variables, not edits:
  AGENTFLOW_CODEX          codex executable; wildcards allowed, the newest match wins
  AGENTFLOW_CODEX_ARGS     extra codex exec arguments, space-separated (for example: -m <model>)
  AGENTFLOW_CLAUDE, AGENTFLOW_AGY, AGENTFLOW_DEVIN   other tool executables (same rules as AGENTFLOW_CODEX)
  AGENTFLOW_CLAUDE_ARGS, AGENTFLOW_AGY_ARGS, AGENTFLOW_DEVIN_ARGS   extra arguments for those tools
A Task File line `Model: <model>[, effort=<level>]` adds the tool's model and reasoning-effort flags for that task
(codex: -m / -c model_reasoning_effort; claude and agy: --model / --effort; devin: --model, with effort
encoded in its model id).
  AGENTFLOW_PYTHON         Python 3 executable for gate.py/ledger.py and the worker process (default: this interpreter)
  AGENTFLOW_WORKER_PYTHON  Python executable only for the worker process (default: AGENTFLOW_PYTHON, then this interpreter)
  AGENTFLOW_<TOOL>_PROBE   free account/model-access check: extra arguments for the tool executable (exit 0 =
                           access), or `off` to declare the check unsupported (unattended launches are refused).
                           Account access alone is not proof that the task's selected model can run inference;
                           custom account/catalog probes stay at this level and are never model evidence.
  AGENTFLOW_<TOOL>_MODEL_PROBE   selected-model inference check, explicit opt-in (a real call may cost tokens):
                           `on` selects the built-in audited check for the tool. No other value is accepted -
                           custom argv is not inference evidence and fails closed. Unset/`off`: nothing proves
                           the model, so an unattended launch is refused - use --manual. The check runs without
                           repository tools or writes (empty temp directory, stdin closed) under its own strict
                           timeout. A success is recorded as model access at a point in time, never as a
                           remaining-quota figure.
  AGENTFLOW_PROBE_TIMEOUT, AGENTFLOW_MODEL_PROBE_TIMEOUT   probe bounds in seconds (defaults 45/60; invalid
                           values fall back to the default - a probe is never unbounded). On expiry the probe's
                           whole process tree is killed.

Bounded autonomy (protocol: Runtime state). Every attempt record stores the requested `Model:`/effort
(`requestedModel`/`requestedEffort`, null when the Task File requests none), the resolved launch argv in safe
form (`launch.argv`: the prompt is `<prompt>` and each machine-args token is `<env arg>`, so a secret in
AGENTFLOW_<TOOL>_ARGS can never enter runtime state), the tool CLI's `--version` first line when it answers
within AGENTFLOW_VERSION_TIMEOUT (default 15s), and the model/effort the tool itself reported in the session
log (`effectiveModel`/`effectiveEffort`). Identity the tool never reported stays "unknown" - never guessed.
New attempts are bounded by configurable caps, each overridable per machine, each refusing the launch with a
diagnosable reason and no new attempt (the preserved records and recovery checkpoints stay untouched):
  AGENTFLOW_MAX_ATTEMPTS            attempts per task (default 8)
  AGENTFLOW_TASK_TIMEOUT            wall-clock seconds since attempt 1's start (default 14400 = 4h); a running
                                    worker also stops when the remaining budget is tighter than its own timeout
  AGENTFLOW_MAX_IDENTICAL_FAILURES  consecutive identical failures - same stop reason, exit code and normalized
                                    note - before a new attempt is refused (default 3)
  AGENTFLOW_MAX_TOOL_SWITCHES       distinct worker platforms a task may touch; another one is refused
                                    (default 3; a manual attempt is the human's own session, not a switch)
Nested sessions: every managed session carries AGENTFLOW_ATTEMPT=<task>#<attempt> and AGENTFLOW_ATTEMPT_ROOT=
the worker's checkout root in its environment. A launch whose own project root equals that marker is a nested
helper of a running worker: refused unless a project Preflight rule says `- delegate: on` (default: zero
helpers). Delegation never bypasses the budgets above or the machine capacity claim.

Permission and isolation matrix (a missing combination refuses the launch; the launcher never downgrades silently):

  tool    role        flags                                        isolation
  codex   developer   exec --sandbox danger-full-access            preventive (CLI sandbox)
  codex   tester      exec --sandbox workspace-write + network     preventive (CLI sandbox)
  claude  developer   -p --dangerously-skip-permissions            post-execution (end check)
  claude  tester      -p --allowedTools Read,Grep,Glob,Bash,Edit   post-execution (end check)
  agy     developer   -p --dangerously-skip-permissions            post-execution (end check)
  agy     tester      -p --output-format stream-json               post-execution (end check)
  devin   developer   -p --permission-mode dangerous               post-execution (end check)
  devin   tester      -p --permission-mode dangerous               post-execution (end check)

Review isolation for a tester comes from the disposable checkout plus the end-of-attempt check; only codex adds a
preventive sandbox on top. A tester on a CLI whose mode is not listed here is refused rather than run unsandboxed.

Before a worker starts the launcher checks: the executable exists, a free account-access probe (built-in default or
AGENTFLOW_<TOOL>_PROBE; `off` = unsupported, refuses an unattended launch), an opted-in selected-model inference
probe (AGENTFLOW_<TOOL>_MODEL_PROBE), observed quota/access limits (machine_capacity.py registry and
tasks/.runtime/tool-limits.json), and machine capacity (slot + PORT claim). What was checked, from where, and when
is recorded in the attempt's `resourceCheck` as safe metadata only (observation source and time, the selected
model, the outcome, and a hash of operator-supplied probe arguments); built-in probe arguments are recorded
verbatim because they are constants of this file. User-supplied argv and probe output are never serialized
into runtime files or diagnostics, and no remaining-quota percentage is ever claimed.
Observed limits are records of what a tool reported, not an enforceable time or attempt budget: when a tool's
remaining quota is unknown it stays unknown, and the bound on one worker is a wall clock the launcher enforces
itself - AGENTFLOW_WORKER_TIMEOUT seconds (default 1200 = 20 minutes; an invalid, zero or missing value keeps
the default - a managed worker is never unbounded). On expiry the launcher kills the managed process tree,
records a timeout error and releases the machine lease. The resolved bound and its absolute deadline are
persisted on the attempt record (`workerTimeout`/`deadline`), and an external pass - `--watchdog`, run by the
conductor every round - stops an overdue non-manual attempt from the outside through the same guarded path as
--stop (classified `timeout`, initiator `watchdog`); an attempt recorded before the field existed gets the
bounded fallback `startedAt + workerTimeout`. While that bounded worker runs on Windows it also holds a
thread-scoped execution request against automatic idle system sleep (power_guard.py): the OS cannot idle-sleep
mid-attempt, the request never keeps the display on, never asks for away mode, yields to an explicit user
sleep/lid action, and dies with the worker; POSIX is a no-op and a failed request is recorded, not hidden.
All tools above run non-interactively, so every worker obeys this bound; an interactive session is a --manual
attempt and is never touched by the watchdog.

Recovery (protocol: Recovery). Every attempt classifies its end in `stopReason` (completed, limit, timeout,
stopped, dead, environment, implementation, verification) from launcher facts - never from free text alone.
An explicit stop records `stoppedBy` - initiator (`watchdog` for a deadline stop, `cli` for the --stop
command line - invoked by a human or a script, the record claims no more), a safe fixed reason and the time;
raw argv, environment and secrets are never recorded. An attempt that did not complete also carries a
bounded `recovery` record: per checkout the branch, HEAD, tracked modifications and untracked paths
(paths/status only - file contents never enter runtime state), so a
successor launched on the same Task File continues from the preserved draft instead of starting blind, and the
record includes whether a Result exists. A new attempt is refused while a managed child of the previous worker
still runs (the worker's descendants by parent chain plus, on POSIX, processes still in the recorded tool
session): a possibly-live writer blocks the handover with a diagnosable error, never a concurrent write.
`Resume: <sha>` keeps the worktree and its drafts and requires the commit to be an ancestor of its HEAD;
`Resume: start fresh` discards only that worktree's draft state.
"""
import argparse
import ctypes
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
import ledger  # noqa: E402
import limit_detection  # noqa: E402
import machine_capacity  # noqa: E402
import power_guard  # noqa: E402
import quota_groups  # noqa: E402
from paths import FLOW_ROOT, REPO_ROOT  # noqa: E402

ROOT = REPO_ROOT
RT_DIR = FLOW_ROOT / "tasks" / ".runtime"
GATE = FLOW_ROOT / "tools" / "gate.py"
LEDGER = FLOW_ROOT / "tools" / "ledger.py"
MACHINE = FLOW_ROOT / "tools" / "machine_capacity.py"
LIMITS_FILE = RT_DIR / "tool-limits.json"
TOOLS = ("codex", "claude", "agy", "devin")

# Whether a session log shows the tool's own provider/account limit: limit_detection.py, shared with
# tick.py and conductor.ps1. Strong provider-directed phrases count at any exit code; weak quota/status
# words need failure evidence (nonzero exit, an error-prefixed line, an outer error event); quoted
# subject matter is skipped. The former local LIMIT_RE regex is superseded by it.

# Free model-access checks (extra args for the tool exe; exit 0 = authenticated). `agy models` lists account models.
# CLI help or --version alone is not proof of model access, so those are never used here.
PROBE_ARGS = {"codex": ["login", "status"], "claude": ["auth", "status"],
              "agy": ["models"], "devin": ["auth", "status"]}
PROBE_TIMEOUT = 45

# Opt-in selected-model inference checks (AGENTFLOW_<TOOL>_MODEL_PROBE=on). They may cost tokens, so they never run
# unless the operator opts in, and only these audited built-ins count as model evidence - custom argv cannot be
# told apart from an auth/catalog check, so it fails closed. Built-ins are minimal noninteractive calls that
# request no repository tools and write nothing (they run in an empty temp cwd with stdin closed).
MODEL_PROBE_ARGS = {"codex": ["exec", "--sandbox", "read-only", "--skip-git-repo-check",
                             "reply with the single word ok"],
                    "claude": ["-p", "reply with the single word ok", "--allowedTools", ""],
                    "agy": ["-p", "reply with the single word ok", "--output-format", "stream-json"],
                    "devin": ["-p", "reply with the single word ok", "--respect-workspace-trust", "false",
                              "--permission-mode", "auto"]}
MODEL_PROBE_TIMEOUT = 60

# Evidence stores safe metadata only: an operator-supplied probe argv can carry a secret anywhere (a flag value,
# a bare positional), so it is recorded as a hash, never verbatim, and never inside diagnostics. Built-in probe
# argv is a constant of this file and may be recorded as-is. Probe stdout/stderr is never serialized.
def argv_hash(argv):
    return hashlib.sha256("\x00".join(argv).encode("utf-8")).hexdigest()[:16]


def env_seconds(name, default):
    """A positive bound from the environment; missing or invalid values keep the default."""
    try:
        v = int(os.environ.get(name) or "")
    except ValueError:
        v = 0
    return v if v > 0 else default


def selected_model(tool, model):
    """The concrete model the worker would use: the task's Model line, else the one inside AGENTFLOW_<TOOL>_ARGS."""
    if model:
        return model
    args = split_args(os.environ.get(f"AGENTFLOW_{tool.upper()}_ARGS"))
    for i, a in enumerate(args):
        if a in ("-m", "--model") and i + 1 < len(args):
            return args[i + 1]
        m = re.match(r"^(?:-m|--model)=(.+)$", a)
        if m:
            return m.group(1)
    return None

# Wall-clock limit for one worker, enforced by the launcher itself (see the docstring): the tool process tree is
# killed, the attempt recorded as a timeout error and the lease released. AGENTFLOW_WORKER_TIMEOUT overrides it
# in seconds; an invalid, zero or missing value keeps the default - a managed worker is never unbounded.
WORKER_TIMEOUT = 1200

KILL_TIMEOUT = 30       # taskkill itself is bounded: a hung kill must not wedge an external stop
POST_KILL_WAIT = 30     # waiting on a just-killed direct child is bounded too
STOP_LOCK_WAIT = 15     # an external stop waits this long for an in-flight launch under launch.lock

# tool -> roles the launcher will start (see the permission matrix in the docstring). Anything else refuses.
PERMISSIONS = {t: ("developer", "tester") for t in TOOLS}


class LaunchError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def resolve_exe(name, override):
    """Machine override; wildcards allowed, the newest match wins."""
    if not override:
        return name
    hits = glob.glob(override)
    if hits:
        return max(hits, key=lambda p: os.path.getmtime(p))
    return override


def python_cmd():
    """Interpreter for gate.py/ledger.py: AGENTFLOW_PYTHON override, else this interpreter."""
    return [resolve_exe("python", os.environ.get("AGENTFLOW_PYTHON"))] if os.environ.get("AGENTFLOW_PYTHON") \
        else [sys.executable]


def worker_python_cmd():
    """Interpreter for the worker process: AGENTFLOW_WORKER_PYTHON, then AGENTFLOW_PYTHON, then this one."""
    own = os.environ.get("AGENTFLOW_WORKER_PYTHON")
    return [resolve_exe("python", own)] if own else python_cmd()


def split_args(value):
    return [a for a in (value or "").strip().split() if a]


def remove_overridden(args, model, effort):
    """The task's Model line wins over machine defaults (kept in step with the former PowerShell loop)."""
    out, skip = [], False
    for i, a in enumerate(args):
        if skip:
            skip = False
            continue
        nxt = args[i + 1] if i + 1 < len(args) else ""
        if model and a in ("-m", "--model"):
            skip = True
            continue
        if model and re.match(r"^(-m|--model)=", a):
            continue
        if effort and a == "--effort":
            skip = True
            continue
        if effort and re.match(r"^--effort=", a):
            continue
        if effort and a == "-c" and re.match(r"^model_reasoning_effort=", nxt):
            skip = True
            continue
        out.append(a)
    return out


def model_args(tool, model, effort):
    """The task's Model line as tool flags; the tool's machine args are filtered separately."""
    extra = []
    if model:
        extra += ["-m" if tool == "codex" else "--model", model]
    if effort:
        if tool == "codex":
            extra += ["-c", f"model_reasoning_effort={effort}"]
        elif tool in ("claude", "agy"):
            extra += ["--effort", effort]
        else:
            print(f"warning: {tool} takes no separate effort flag; put the level in the model name "
                  f"(Model: {model})", file=sys.stderr)
    return extra


def env_args(tool, model, effort):
    """AGENTFLOW_<TOOL>_ARGS, filtered so the task's Model line wins."""
    return remove_overridden(split_args(os.environ.get(f"AGENTFLOW_{tool.upper()}_ARGS")), model, effort)


def tool_argv(tool, role, prompt, model, effort, masked=False):
    """Full argv after the executable, in the same order the PowerShell launcher built it. With
    masked=True the record-safe shape is produced instead: the prompt becomes '<prompt>' and every
    AGENTFLOW_<TOOL>_ARGS token becomes '<env arg>' (count and position preserved), so a secret in
    machine arguments can never be written into runtime state."""
    def eargs(t):
        args = env_args(t, model, effort)
        return ["<env arg>"] * len(args) if masked else args
    if masked:
        prompt = "<prompt>"
    if tool == "codex":
        base = ["exec"] + eargs("codex")
        if role == "developer":
            base += ["--sandbox", "danger-full-access", prompt]
        else:
            base += ["--sandbox", "workspace-write", "--add-dir", str(FLOW_ROOT / "tasks"),
                     "-c", "sandbox_workspace_write.network_access=true", prompt]
        extra = model_args("codex", model, effort)
        return [base[0]] + extra + base[1:] if extra else base
    if tool == "claude":
        base = ["-p", prompt, "--dangerously-skip-permissions"] if role == "developer" \
            else ["-p", prompt, "--allowedTools", "Read,Grep,Glob,Bash,Edit"]
    elif tool == "agy":
        base = ["-p", prompt, "--dangerously-skip-permissions", "--output-format", "stream-json"] \
            if role == "developer" else ["-p", prompt, "--output-format", "stream-json"]
    else:  # devin
        base = ["-p", prompt, "--permission-mode", "dangerous", "--respect-workspace-trust", "false"]
    return base + eargs(tool) + model_args(tool, model, effort)


def tool_exe(tool):
    return resolve_exe(tool, os.environ.get(f"AGENTFLOW_{tool.upper()}"))


VERSION_TIMEOUT = 15  # <tool> --version is a fact, not a probe: bounded, output-only, never stored raw


def tool_version(exe):
    """First line of `<exe> --version`, or 'unknown' when the tool does not answer cheaply. A version
    string is runtime metadata; a CLI that fails or stalls reports 'unknown', never a guess."""
    try:
        code, out = run_capture([exe, "--version"],
                                timeout=env_seconds("AGENTFLOW_VERSION_TIMEOUT", VERSION_TIMEOUT))
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    line = next((ln.strip() for ln in out.splitlines() if ln.strip()), "")
    return line[:120] if code == 0 and line else "unknown"


# What a tool may report about itself: structured stream-json init/config events and plain header lines.
# Anything else (assistant prose, file content, prompts) is subject matter, not runtime identity.
_IDENTITY_EVENTS = ("init", "session", "config")
_MODEL_LINE = re.compile(r"^model\s*:\s*([A-Za-z0-9][\w./-]*)$", re.I)
_EFFORT_LINE = re.compile(r"^(?:reasoning[ _-]?effort|effort)\s*:\s*([A-Za-z0-9._-]+)$", re.I)


def effective_identity(log):
    """(model, effort) the tool reported itself in this session log, else (None, None): a 'model'/'effort'
    field of a structured init/session/config event, or a 'model:'/'reasoning effort:' header line. An
    assistant message's content never counts; absence is reported by the caller as 'unknown'."""
    try:
        head = Path(log).read_text(encoding="utf-8", errors="replace")[:65536] if log else ""
    except OSError:
        return None, None
    model = effort = None
    for s in (ln.strip() for ln in head.splitlines()):
        if s.startswith("{") and s.endswith("}"):
            try:
                ev = json.loads(s)
            except ValueError:
                ev = None
            if isinstance(ev, dict):
                kind = f"{ev.get('type', '')}:{ev.get('subtype', '')}".lower()
                if any(k in kind for k in _IDENTITY_EVENTS):
                    if model is None and isinstance(ev.get("model"), str):
                        model = ev["model"]
                    eff = ev.get("effort") or ev.get("reasoning_effort") or ev.get("reasoningEffort")
                    if effort is None and isinstance(eff, str):
                        effort = eff
                continue
        if model is None and (m := _MODEL_LINE.match(s)):
            model = m.group(1)
        if effort is None and (m := _EFFORT_LINE.match(s)):
            effort = m.group(1)
        if model and effort:
            break
    return model, effort


# --- process identity ---------------------------------------------------------------------------------------------
def pid_start(pid):
    """Process start as .NET ticks (the format the attempt record and tick.py/machine_capacity.py compare).
    Windows: GetProcessTimes. Linux: /proc jiffies -> epoch -> ticks. Elsewhere: None (start not measurable)."""
    if os.name == "nt":
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return None
        try:
            ft = [ctypes.c_ulonglong() for _ in range(4)]
            if k.GetProcessTimes(h, *(ctypes.byref(x) for x in ft)):
                return ft[0].value + 504911232000000000  # FILETIME (1601) -> .NET ticks (0001)
            return None
        finally:
            k.CloseHandle(h)
    try:
        clk = os.sysconf("SC_CLK_TCK")
        btime = next(int(line.split()[1]) for line in Path("/proc/stat").read_text().splitlines()
                     if line.startswith("btime"))
        stat = Path(f"/proc/{int(pid)}/stat").read_text().rsplit(")", 1)[1].split()
        epoch = btime + int(stat[19]) / clk  # field 22 (starttime) after "pid (comm)" is removed
        return int(epoch * 10_000_000) + 504911232000000000
    except (OSError, IndexError, ValueError, StopIteration):
        pass
    # macOS and other non-/proc systems: `ps -o lstart=` reports the same absolute start time ps prints.
    # Without it a recorded start identity could never be confirmed and a reused pid could not be told apart.
    try:
        out = subprocess.run(["ps", "-p", str(int(pid)), "-o", "lstart="], capture_output=True, text=True,
                             env={**os.environ, "LC_ALL": "C"}, timeout=10).stdout.strip()
        epoch = datetime.strptime(out, "%a %b %d %H:%M:%S %Y").replace(tzinfo=timezone.utc).timestamp()
        return int(epoch * 10_000_000) + 504911232000000000
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def alive(pid, start=None):
    """The process still runs. When a start identity was recorded and is measurable, it must match: a pid that was
    reused by another process is not ours, and an unkillable-by-mistake answer beats a wrong kill."""
    if not pid:
        return False
    if os.name == "nt":
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, int(pid))
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            if not k.GetExitCodeProcess(h, ctypes.byref(code)) or code.value != 259:  # STILL_ACTIVE
                return False
            if start is not None:
                ft = [ctypes.c_ulonglong() for _ in range(4)]
                if not k.GetProcessTimes(h, *(ctypes.byref(x) for x in ft)):
                    return False  # alive but identity unverifiable: do not treat as ours
                return ft[0].value + 504911232000000000 == int(start)
            return True
        finally:
            k.CloseHandle(h)
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    if start is not None:
        # A recorded identity must be re-measurable: a pid whose start cannot be confirmed is not ours,
        # and no kill is sent to it (it may have been reused).
        return pid_start(pid) == int(start)
    return True


def _proc_table():
    """Live process table as pid -> (ppid, pgid, sid); {} when it cannot be measured. POSIX reads /proc or
    falls back to `ps`; Windows walks a Toolhelp32 snapshot (process groups and sessions do not exist there,
    so those positions are None)."""
    if os.name == "nt":
        kernel = ctypes.windll.kernel32
        snap = kernel.CreateToolhelp32Snapshot(0x2, 0)  # TH32CS_SNAPPROCESS
        if snap in (-1, ctypes.c_void_p(-1).value):
            return {}
        try:
            class PROCESSENTRY32(ctypes.Structure):
                _fields_ = [("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong),
                            ("th32ProcessID", ctypes.c_ulong), ("th32DefaultHeapID", ctypes.c_void_p),
                            ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
                            ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long),
                            ("dwFlags", ctypes.c_ulong), ("szExeFile", ctypes.c_wchar * 260)]
            table = {}
            entry = PROCESSENTRY32()
            entry.dwSize = ctypes.sizeof(entry)
            ok = kernel.Process32First(snap, ctypes.byref(entry))
            while ok:
                table[int(entry.th32ProcessID)] = (int(entry.th32ParentProcessID), None, None)
                ok = kernel.Process32Next(snap, ctypes.byref(entry))
            return table
        finally:
            kernel.CloseHandle(snap)
    proc = Path("/proc")
    if proc.is_dir():
        table = {}
        for d in proc.iterdir():  # Linux: /proc/<pid>/stat holds ppid, pgrp and sid after the comm field
            if not d.name.isdigit():
                continue
            try:
                stat = (d / "stat").read_text().rsplit(")", 1)[1].split()
                table[int(d.name)] = (int(stat[1]), int(stat[2]), int(stat[3]))
            except (OSError, IndexError, ValueError):
                continue
        return table
    table = {}
    try:
        out = subprocess.run(["ps", "-eo", "pid=,ppid=,pgid=,sid="], capture_output=True, text=True,
                             timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return table
    for line in out.splitlines():
        f = line.split()
        if len(f) == 4:
            try:
                table[int(f[0])] = (int(f[1]), int(f[2]), int(f[3]))
            except ValueError:
                continue
    return table


def tree_pgroups(pid):
    """Process-group ids of the tree rooted at pid: the root's group plus the group of every live
    descendant, so a managed child that leads its own session is reached too."""
    groups = set()
    try:
        groups.add(os.getpgid(int(pid)))
    except OSError:
        pass
    kids = {}
    for child, (ppid, grp, _sid) in _proc_table().items():
        kids.setdefault(ppid, []).append((child, grp))
    stack, seen = [int(pid)], {int(pid)}
    while stack:
        for child, grp in kids.pop(stack.pop(), []):
            if child not in seen:
                seen.add(child)
                stack.append(child)
                if grp is not None:
                    groups.add(grp)
    return groups


def descendants(pid):
    """Live descendants of pid by parent chain; the pid itself is not included. On POSIX an orphaned
    grandchild is reparented and leaves the chain - the tool-session scan covers those."""
    kids = {}
    for child, (ppid, _grp, _sid) in _proc_table().items():
        kids.setdefault(ppid, []).append(child)
    out, stack, seen = [], [int(pid)], {int(pid)}
    while stack:
        for child in kids.pop(stack.pop(), []):
            if child not in seen:
                seen.add(child)
                stack.append(child)
                out.append(child)
    return out


# Windows job objects: the worker is assigned to a job named after its pid at spawn. Children of job
# members inherit membership, so even an orphaned grandchild (whose parent chain is already broken)
# still counts against the job - that is the Windows equivalent of the POSIX session scan below.
def _job_name(pid):
    return rf"Local\AgentFlow-Worker-{pid}"


def _job_assign(pid):
    """Assign the worker process to its named job; best-effort (an already-exited process or a Windows
    that disallows nesting simply leaves the parent-chain scan as the fallback)."""
    if os.name != "nt":
        return
    k = ctypes.windll.kernel32
    job = k.CreateJobObjectW(None, _job_name(pid))
    if not job:
        return
    handle = k.OpenProcess(0x0100 | 0x0001, False, int(pid))  # PROCESS_SET_QUOTA | PROCESS_TERMINATE
    if handle:
        k.AssignProcessToJobObject(job, handle)
        k.CloseHandle(handle)
    k.CloseHandle(job)  # the object persists while any member process lives


def _job_active(pid):
    """Members still alive in the worker's job, or None when there is no job for this pid."""
    if os.name != "nt" or not pid:
        return None
    k = ctypes.windll.kernel32
    job = k.OpenJobObjectW(0x0004, False, _job_name(pid))  # JOB_OBJECT_QUERY
    if not job:
        return None
    try:
        class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
            _fields_ = [("TotalUserTime", ctypes.c_ulonglong), ("TotalKernelTime", ctypes.c_ulonglong),
                        ("ThisPeriodTotalUserTime", ctypes.c_ulonglong),
                        ("ThisPeriodTotalKernelTime", ctypes.c_ulonglong),
                        ("TotalPageFaultCount", ctypes.c_ulong), ("TotalProcesses", ctypes.c_ulong),
                        ("ActiveProcesses", ctypes.c_ulong), ("TotalTerminatedProcesses", ctypes.c_ulong)]
        info = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        if k.QueryInformationJobObject(job, 1, ctypes.byref(info), ctypes.sizeof(info), None):
            return int(info.ActiveProcesses)
        return None
    finally:
        k.CloseHandle(job)


def _job_terminate(pid):
    """End every process in the worker's job, including orphans that left the parent chain."""
    if os.name != "nt":
        return
    k = ctypes.windll.kernel32
    job = k.OpenJobObjectW(0x0001, False, _job_name(pid))  # JOB_OBJECT_TERMINATE
    if job:
        k.TerminateJobObject(job, 1)
        k.CloseHandle(job)


def _tool_session_path(tid):
    return RT_DIR / f"{tid}.toolsession.json"


def write_tool_session(tid, pid):
    """Record the tool process the worker spawned: takeover checks read it after the worker is gone.
    POSIX: the tool leads its own session, and orphaned grandchildren keep that session id after
    reparenting, so a stray writer is still found when the parent chain is broken."""
    sid = None
    if os.name != "nt":
        try:
            sid = os.getsid(int(pid))
        except OSError:
            sid = None
    p = _tool_session_path(tid)
    tmp = p.parent / (p.name + ".tmp")
    tmp.write_text(json.dumps({"pid": int(pid), "sid": sid}), encoding="utf-8")
    os.replace(tmp, p)


def read_tool_session(tid):
    try:
        data = json.loads(_tool_session_path(tid).read_text(encoding="utf-8"))
        return data if isinstance(data.get("pid"), int) and not isinstance(data.get("pid"), bool) else None
    except (OSError, ValueError):
        return None


def leftover_processes(tid, a, grace=0.0):
    """(stray pids, job members) of a dead or stopped attempt: the worker's descendants by parent chain
    plus, on POSIX, every process still in the recorded tool session (orphans keep their session id after
    reparenting); on Windows the worker's job reports members that already left the parent chain.
    `grace` seconds lets a just-killed tree finish dying before the answer counts. Identity is
    best-effort: an unrelated process sitting on a reused pid is a diagnosable block for the operator,
    never a kill target."""
    deadline = time.time() + grace
    while True:
        out = set()
        pid = a.get("pid")
        if pid:
            out.update(descendants(pid))
        meta = read_tool_session(tid)
        if meta:
            tpid = meta.get("pid")
            if tpid:
                if alive(tpid):
                    out.add(tpid)
                out.update(descendants(tpid))
            sid = meta.get("sid")
            if sid is not None and os.name != "nt":
                for p, (_ppid, _grp, s) in _proc_table().items():
                    if s == sid:
                        out.add(p)
        out.discard(pid)
        members = _job_active(pid) if os.name == "nt" else 0
        if (not out and not members) or time.time() >= deadline:
            return sorted(out), members or 0
        time.sleep(0.1)


def _leftover_error(tid, strays, members=0, what="a new attempt"):
    shown = ", ".join(str(p) for p in strays[:5])
    if len(strays) > 5:
        shown += f" (+{len(strays) - 5} more)"
    if not shown:
        shown = "no visible pid"
    if members:
        shown += f"; {members} member(s) in the worker's job"
    return LaunchError(f"{tid}: managed processes of the previous worker still run ({shown}) - they "
                       f"may still write the worktree, so {what} is refused. Verify they belong to this "
                       "task (a reused pid can imitate one) and end them, then retry.")


def kill_tree(pid):
    """Kill the worker and its managed descendants (the tool process and what it spawned)."""
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                           timeout=env_seconds("AGENTFLOW_KILL_TIMEOUT", KILL_TIMEOUT))
        except (OSError, subprocess.SubprocessError):
            pass  # a hung or failed taskkill is covered by the job-object terminate below
        _job_terminate(pid)  # orphans that already left the parent chain still belong to the job
        return
    # Only the tree rooted at pid is signalled: the tool leads its own group, so the caller's group
    # (which is also the worker's) is never targeted.
    groups = tree_pgroups(pid)
    for g in groups:
        try:
            os.killpg(g, 15)
        except OSError:
            pass
    if not groups:
        return
    for _ in range(20):
        if not alive(pid):
            return
        time.sleep(0.1)
    for g in groups:
        try:
            os.killpg(g, 9)
        except OSError:
            pass


# --- runtime state (tasks/.runtime/T-NNN.json; attempts appended, never overwritten) --------------------------------
def read_rt(tid):
    """The task's attempt history, or None. Malformed or structurally invalid state fails closed:
    a corrupt file is a diagnosable error, never 'no active work'."""
    p = RT_DIR / f"{tid}.json"
    if not p.exists():
        return None
    try:
        return ledger.check_runtime(json.loads(p.read_text(encoding="utf-8-sig")), tid)
    except (OSError, ValueError) as e:
        raise LaunchError(f"cannot read runtime state {p.name}: {e}")


def write_rt(tid, obj):
    p = RT_DIR / f"{tid}.json"
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    os.replace(tmp, p)


def last_attempt(rt):
    return rt["attempts"][-1] if rt and rt.get("attempts") else None


def attempt_alive(a):
    """Confirmed live: the attempt runs and a live process sits on its recorded pid whose start identity
    matches the recorded one. Anything less is not proof the worker is alive."""
    return bool(a) and a.get("status") == "running" and bool(a.get("pid")) \
        and a.get("pidStart") is not None and alive(a["pid"], a["pidStart"])


def attempt_uncertain(a):
    """A live process occupies the recorded pid but its identity cannot be confirmed (no start was recorded,
    or it cannot be re-measured now): the pid may be the worker or a reused one. This is a diagnosable block,
    never 'dead' and never a kill target - the task stays locked."""
    return bool(a) and a.get("status") == "running" and bool(a.get("pid")) \
        and not attempt_alive(a) and alive(a["pid"])


def attempt_held(a):
    return bool(a) and a.get("status") == "running" and (a.get("manual") or not a.get("pid")
                                                       or attempt_alive(a) or attempt_uncertain(a))


def live_tasks():
    out = []
    if not RT_DIR.is_dir():
        return out
    for p in sorted(RT_DIR.glob("T-*.json")):
        if not re.match(r"^T-\d+\.json$", p.name):
            continue
        try:
            rt = ledger.check_runtime(json.loads(p.read_text(encoding="utf-8-sig")), p.stem)
        except (OSError, ValueError) as e:
            raise LaunchError(f"cannot read active runtime state {p.name}: {e}")  # corrupted state fails closed
        if attempt_held(last_attempt(rt)):
            out.append(rt.get("taskId") or p.stem)
    return out


# --- helpers on the other tools ------------------------------------------------------------------------------------
def invoke_gate(cmd, tid, more=()):
    """tools/gate.py -> object; exit >= 2 or a missing --out file is a gate error."""
    out = RT_DIR / f"{tid}.gate.json"
    r = subprocess.run(python_cmd() + [str(GATE), cmd, tid, *more, "--out", str(out)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode >= 2 or not out.exists():
        raise LaunchError(f"gate.py {cmd} {tid}: {(r.stdout + r.stderr).strip()}")
    try:
        return json.loads(out.read_text(encoding="utf-8"))
    finally:
        out.unlink(missing_ok=True)


def cmd_argv(argv):
    """Windows cannot exec .cmd/.bat directly: run them through cmd /c with the outer-quote rule."""
    if os.name == "nt" and argv and re.search(r"\.(cmd|bat)$", argv[0], re.I):
        return f'{os.environ.get("COMSPEC", "cmd.exe")} /d /s /c "{subprocess.list2cmdline(argv)}"'
    return argv


def run_capture(argv, timeout=None, cwd=None):
    """Bounded probe execution: output is returned, never stored. On timeout the probe's whole process tree is
    killed (its own session/group), not only the direct child."""
    kw = {"cwd": cwd, "stdin": subprocess.DEVNULL, "stdout": subprocess.PIPE,
          "stderr": subprocess.STDOUT, "text": True, "encoding": "utf-8", "errors": "replace"}
    if os.name == "nt":
        kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    p = subprocess.Popen(cmd_argv(argv), **kw)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_tree(p.pid)
        try:
            p.wait(timeout=POST_KILL_WAIT)
        except subprocess.TimeoutExpired:
            pass   # the probe's direct child outlived its kill; the timeout is still raised
        raise
    return p.returncode, out.strip()


# --- worktrees, checkouts, Setup ------------------------------------------------------------------------------------
def remove_setup_links(t, base):
    """Unlink `Setup - link:` junctions/symlinks without following them: `git worktree remove` and a recursive
    delete would empty the target (the main folder's copy, such as node_modules)."""
    if not base:
        return
    for s in t.get("setup") or []:
        if s.get("kind") != "link":
            continue
        p = Path(base) / s["path"]
        try:
            st = p.lstat()
        except OSError:
            continue
        if not (p.is_symlink() or getattr(st, "st_file_attributes", 0) & 0x400):  # FILE_ATTRIBUTE_REPARSE_POINT
            continue
        if p.is_symlink():
            p.unlink()
        else:
            p.rmdir()


def remove_checkout(t):
    """Tester checkouts are disposable: one per repository (gate.py 'checkouts')."""
    if t.get("role") != "tester":
        return
    remove_setup_links(t, t.get("workdir"))
    for c in t.get("checkouts") or []:
        if not Path(c["path"]).exists():
            continue
        remove_setup_links(t, c["path"])
        r = subprocess.run(["git", "-C", c["repo"], "worktree", "remove", "--force", c["path"]],
                           capture_output=True, text=True)
        if r.returncode and Path(c["path"]).exists():
            try:
                shutil.rmtree(c["path"])
                subprocess.run(["git", "-C", c["repo"], "worktree", "prune"], capture_output=True)
            except OSError as e:
                print(f"warning: could not remove tester checkout {c['path']}: {e}", file=sys.stderr)
    wd = t.get("workdir")
    if wd and Path(wd).is_dir() and not any(Path(wd).iterdir()):
        Path(wd).rmdir()  # the empty folder that held a workspace tester's checkouts


def make_link(src, dst):
    if os.name == "nt":
        r = subprocess.run(f'{os.environ.get("COMSPEC", "cmd.exe")} /d /s /c mklink /J '
                           + subprocess.list2cmdline([str(dst), str(src)]), capture_output=True, text=True)
        if r.returncode:
            raise LaunchError(f"mklink /J failed for {dst}: {(r.stdout + r.stderr).strip()}")
    else:
        os.symlink(str(src), str(dst))


def init_workdir(t):
    """Worktrees (developer) or disposable checkouts (tester), then Setup links and copies."""
    if t["role"] == "developer":
        for c in t.get("checkouts") or []:
            if Path(c["path"]).exists():
                cur = subprocess.run(["git", "-C", c["path"], "rev-parse", "--abbrev-ref", "HEAD"],
                                     capture_output=True, text=True).stdout.strip()
                if cur != c["branch"]:
                    raise LaunchError(f"worktree {c['path']} is on branch '{cur}', task needs '{c['branch']}'. "
                                      "Not this task's: stop.")
                apply_resume(t, c)
                print(f"worktree {c['path']} exists on {c['branch']}: resume")
            else:
                Path(c["path"]).parent.mkdir(parents=True, exist_ok=True)
                exists = subprocess.run(["git", "-C", c["repo"], "rev-parse", "--verify", "--quiet",
                                         f"refs/heads/{c['branch']}"], capture_output=True).returncode == 0
                args = ["git", "-C", c["repo"], "worktree", "add", c["path"]] + ([] if exists else ["-b"]) + [c["branch"]]
                if subprocess.run(args, capture_output=True).returncode:
                    raise LaunchError(f"git worktree add failed for {c['path']}")
    if t["role"] == "tester":
        remove_checkout(t)
        for c in t.get("checkouts") or []:
            Path(c["path"]).parent.mkdir(parents=True, exist_ok=True)
            if subprocess.run(["git", "-C", c["repo"], "worktree", "add", "--detach", c["path"], c["sha"]],
                              capture_output=True).returncode:
                raise LaunchError(f"git worktree add (tester checkout) failed for {c['path']}")
        (RT_DIR / f"{t['id']}.evidence").mkdir(parents=True, exist_ok=True)
    for s in t.get("setup") or []:
        src, dst = ROOT / s["path"], Path(t["workdir"]) / s["path"]
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if s["kind"] == "link":
            make_link(src, dst)
        elif src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def worker_env(t):
    e = dict(t.get("env") or {})
    e["AGENTFLOW_TARGET"] = t["target"]  # after the Task File env: production is never opted into by a task
    if t["role"] == "tester":
        e["AGENTFLOW_EVIDENCE"] = str(RT_DIR / f"{t['id']}.evidence")
    return e


# --- launch budgets (bounded autonomy): every cap is an AGENTFLOW_* setting with a documented default;
# --- a refused launch creates no attempt and leaves every earlier record and checkpoint untouched --------
MAX_ATTEMPTS = 8
MAX_IDENTICAL_FAILURES = 3
MAX_TOOL_SWITCHES = 3
TASK_TIMEOUT = 4 * 3600  # wall-clock budget of the whole task, counted from attempt 1's start

# stopReason classes that count as a repeated identical failure. "stopped" is the human's decision,
# "limit" is a provider hold handled by the limits machinery, "completed" is not a failure at all.
_FAILURE_REASONS = {"environment", "verification", "implementation", "timeout", "dead"}


def _same_root(path):
    try:
        return os.path.normcase(str(Path(path).resolve())) == os.path.normcase(str(ROOT.resolve()))
    except OSError:
        return False


def nested_check():
    """A launch inside a managed worker session is a nested helper: detectable by the attempt markers
    the launcher sets in the worker's environment (its checkout root). Refused unless a project
    Preflight rule delegates sub-agent launches; delegation never bypasses the budgets or machine caps."""
    marker = os.environ.get("AGENTFLOW_ATTEMPT_ROOT")
    if not marker or not _same_root(marker):
        return
    if gate.delegation_allowed():
        return
    who = os.environ.get("AGENTFLOW_ATTEMPT") or "a worker"
    raise LaunchError(f"nested launch refused: this session already belongs to {who} of this project, and "
                      "the project's Preflight rules do not delegate sub-agent launches "
                      "('- delegate: on' would allow it; the launch budgets and machine capacity still apply). "
                      "Nothing was started.")


def failure_signature(a):
    """What 'the same failure again' means: stop reason, exit code and the note with volatile numbers
    normalized out. Attempts that are still running, were stopped by hand or completed carry no signature."""
    if a.get("status") == "running" or a.get("stopReason") not in _FAILURE_REASONS:
        return None
    note = re.sub(r"\s+", " ", re.sub(r"\d+", "#", (a.get("note") or "").lower()))[:160]
    return a["stopReason"], a.get("exitCode"), note


def budget_stop(rt, tool):
    """The budget a new attempt would exceed, or None. Attempts, overall task duration (from attempt 1's
    start), a trailing run of identical failures, and distinct worker platforms are all capped."""
    attempts = rt.get("attempts") or []
    cap = env_seconds("AGENTFLOW_MAX_ATTEMPTS", MAX_ATTEMPTS)
    if len(attempts) >= cap:
        return (f"attempt budget exhausted: {len(attempts)} attempt(s) on this task, cap "
                f"AGENTFLOW_MAX_ATTEMPTS={cap}")
    if attempts and attempts[0].get("startedAt"):
        try:
            started = datetime.strptime(attempts[0]["startedAt"], "%Y-%m-%dT%H:%M:%SZ") \
                .replace(tzinfo=timezone.utc)
        except ValueError:
            started = None
        span = env_seconds("AGENTFLOW_TASK_TIMEOUT", TASK_TIMEOUT)
        if started and datetime.now(timezone.utc) - started > timedelta(seconds=span):
            return (f"task duration budget exhausted: attempt 1 started {attempts[0]['startedAt']}, cap "
                    f"AGENTFLOW_TASK_TIMEOUT={span}s")
    chain, sig0 = 0, None
    for old in reversed(attempts):
        sig = failure_signature(old)
        if sig is None:
            break
        if sig0 is None:
            sig0 = sig
        elif sig != sig0:
            break
        chain += 1
    cap = env_seconds("AGENTFLOW_MAX_IDENTICAL_FAILURES", MAX_IDENTICAL_FAILURES)
    if sig0 is not None and chain >= cap:
        return (f"identical failures budget exhausted: the last {chain} attempt(s) all failed as "
                f"'{sig0[0]}' (exit {sig0[1]}) the same way, cap AGENTFLOW_MAX_IDENTICAL_FAILURES={cap}")
    if tool:
        used = {old.get("tool") for old in attempts} - {"manual", None}
        cap = env_seconds("AGENTFLOW_MAX_TOOL_SWITCHES", MAX_TOOL_SWITCHES)
        if tool not in used and len(used) >= cap:
            return (f"platform switch budget exhausted: this task already ran on {sorted(used)}, cap "
                    f"AGENTFLOW_MAX_TOOL_SWITCHES={cap}; '{tool}' would be another platform")
    return None


def worker_bound(rt, att):
    """(seconds, bound-name): the wall clock a managed worker obeys. AGENTFLOW_WORKER_TIMEOUT resolves
    like every positive bound here - an invalid, zero or missing value keeps the default, so a managed
    worker is never unbounded - and the task's own duration budget (from attempt 1's start) clamps it
    further when tighter."""
    timeout, bound = env_seconds("AGENTFLOW_WORKER_TIMEOUT", WORKER_TIMEOUT), "AGENTFLOW_WORKER_TIMEOUT"
    first = (rt.get("attempts") or [att])[0]
    try:
        started = parse_ts(first.get("startedAt") or "")
        remaining = (started + timedelta(seconds=env_seconds("AGENTFLOW_TASK_TIMEOUT", TASK_TIMEOUT))
                     - datetime.now(timezone.utc)).total_seconds()
    except ValueError:
        remaining = None
    if remaining is not None:
        if remaining <= 0:
            raise LaunchError("task duration budget exhausted before the tool started "
                              f"(AGENTFLOW_TASK_TIMEOUT={env_seconds('AGENTFLOW_TASK_TIMEOUT', TASK_TIMEOUT)}s)")
        if remaining < timeout:
            timeout, bound = remaining, "AGENTFLOW_TASK_TIMEOUT"
    return timeout, bound


def attempt_deadline(a):
    """The attempt's wall-clock deadline (UTC): the launch-persisted value, else startedAt + the resolved
    worker bound for records written before the field existed - a bounded fallback, never 'no deadline'.
    None only when neither can be read: the attempt is left locked for diagnosis, never killed on an
    unprovable deadline."""
    if a.get("deadline"):
        try:
            return parse_ts(a["deadline"])
        except (TypeError, ValueError):
            pass  # an unreadable field falls back to the same bound a legacy record gets
    try:
        return parse_ts(a.get("startedAt") or "") + timedelta(
            seconds=env_seconds("AGENTFLOW_WORKER_TIMEOUT", WORKER_TIMEOUT))
    except (TypeError, ValueError):
        return None


# --- resource and permission checks before a worker start -----------------------------------------------------------
def limit_until(tool, group=None):
    """Observed quota/access limits applying to <tool> on quota <group>, project file and shared machine
    registry; earliest expiry wins. A hold on the bare tool key stays tool-wide, a hold on '<tool>:<group>'
    blocks only that group. A malformed project record fails closed: 'no limits known' is never inferred
    from a bad file."""
    ends = []
    if LIMITS_FILE.exists():
        try:
            lim = ledger.check_limits(json.loads(LIMITS_FILE.read_text(encoding="utf-8-sig")))
        except (OSError, ValueError) as e:
            raise LaunchError(f"cannot read observed limits {LIMITS_FILE.name}: {e}")
        keys = [tool, machine_capacity._limit_key(tool, group)] if group else [tool]
        for key in keys:
            rec = lim.get(key)
            if rec:
                try:
                    ends.append(datetime.strptime(rec["until"], "%Y-%m-%dT%H:%M:%SZ")
                                .replace(tzinfo=timezone.utc))
                except ValueError as e:
                    raise LaunchError(f"cannot read observed limits {LIMITS_FILE.name}: "
                                      f"bad 'until' for {key}: {e}")
    machine = machine_capacity.limit_until(tool, group)
    if machine:
        ends.append(machine)
    return max(ends) if ends else None


def resource_check(tool, model=None):
    """Executable, authenticated access, selected-model inference, observed limits (scoped to the quota
    group the session would consume). Raises LaunchError with an actionable diagnostic; returns what was
    observed (freshness + source, no secrets, no quota figures)."""
    check = {"at": now(), "exe": None, "probe": None, "probeSource": None}
    exe = tool_exe(tool)
    found = shutil.which(exe) or (str(Path(exe).resolve()) if Path(exe).exists() else None)
    if not found:
        raise LaunchError(f"{tool} executable not found: '{exe}'. Set AGENTFLOW_{tool.upper()} to its path "
                          "(wildcards allowed, the newest match wins).")
    check["exe"] = found

    group = quota_groups.group_for(tool, selected_model(tool, model))
    check["quotaGroup"] = group
    end = limit_until(tool, group)
    if end and end > datetime.now(timezone.utc):
        # Name the hold that actually blocks: the bare <tool> key stays tool-wide even when the
        # session has a quota group; a group-scoped binding constraint names the group.
        scope = f" group {group}" if group and end != limit_until(tool) else ""
        raise LaunchError(f"{tool}{scope} is limited until {end.strftime('%Y-%m-%dT%H:%M:%SZ')} "
                          "(observed quota/access limit); move the task to another tool or wait.")
    check["limits"] = "clear"

    override = os.environ.get(f"AGENTFLOW_{tool.upper()}_PROBE")
    if override is not None and override.strip().lower() in ("", "off", "none", "unsupported"):
        raise LaunchError(f"no supported model-access check for {tool} (AGENTFLOW_{tool.upper()}_PROBE={override!r}). "
                          f"An unattended launch needs a free check that exits 0 on access: set "
                          f"AGENTFLOW_{tool.upper()}_PROBE to its arguments, or start this task with --manual.")
    probe = split_args(override) if override is not None else PROBE_ARGS.get(tool)
    if not probe:
        raise LaunchError(f"model access for {tool} cannot be checked on this machine (no known free probe). "
                          f"Set AGENTFLOW_{tool.upper()}_PROBE to a check that exits 0 on access "
                          f"(for example an auth/status subcommand), or start this task with --manual.")
    # An operator-supplied probe may carry a secret anywhere in its argv: record only its source and a hash,
    # and keep the argv itself out of diagnostics.
    check["probeSource"] = "env" if override is not None else "builtin"
    check["probe"] = probe if override is None else None
    check["probeHash"] = argv_hash(probe) if override is not None else None
    probe_desc = f"{exe} {' '.join(probe)}" if override is None \
        else f"{exe} <custom probe sha256:{check['probeHash']}>"
    probe_timeout = env_seconds("AGENTFLOW_PROBE_TIMEOUT", PROBE_TIMEOUT)
    try:
        code, _ = run_capture([exe] + probe, timeout=probe_timeout)
    except subprocess.TimeoutExpired:
        raise LaunchError(f"{tool} access check timed out after {probe_timeout}s: {probe_desc}. "
                          f"Fix the CLI or set AGENTFLOW_{tool.upper()}_PROBE.")
    if code:
        raise LaunchError(f"{tool} access check failed (exit {code}): {probe_desc}. "
                          "Sign in or fix the account, or set AGENTFLOW_" + tool.upper() +
                          "_PROBE to a working free check. The attempt was not created.")

    # Selected-model inference check: explicit opt-in only (it may cost tokens), a separate strict bound, an
    # empty temp cwd and no repository tools. Only the audited built-in counts: custom argv cannot be told
    # apart from an auth/catalog check, so it fails closed. Account access above proves no model entitlement.
    chosen = check["model"] = selected_model(tool, model)
    menv = f"AGENTFLOW_{tool.upper()}_MODEL_PROBE"
    mo = os.environ.get(menv)
    if mo is None or mo.strip().lower() in ("", "off", "none", "unsupported"):
        raise LaunchError(f"no inference check for the selected model of {tool} ({menv} "
                          f"{'unset' if mo is None else '=' + repr(mo)}). An unattended launch must prove access "
                          f"to the selected concrete model: set {menv}=on for the built-in bounded check (may "
                          "cost tokens), or start this task with --manual. Account access alone is not "
                          "inference entitlement.")
    if mo.strip().lower() not in ("on", "builtin", "1", "true", "yes"):
        raise LaunchError(f"{menv} accepts only `on` (the built-in audited inference check); custom probe "
                          "arguments are not selected-model evidence - a catalog or auth check exiting 0 "
                          "proves nothing about inference. Account-level checks belong in "
                          f"AGENTFLOW_{tool.upper()}_PROBE; to skip the model check use --manual.")
    margv = list(MODEL_PROBE_ARGS.get(tool) or [])
    if not margv:
        raise LaunchError(f"no built-in model inference check for {tool}: {menv}=on cannot run here. "
                          "Start this task with --manual.")
    if chosen:
        margv += model_args(tool, chosen, None)
    model_probe_timeout = env_seconds("AGENTFLOW_MODEL_PROBE_TIMEOUT", MODEL_PROBE_TIMEOUT)
    check["modelProbe"] = {"at": now(), "model": chosen, "source": "builtin",
                           "argv": margv, "timeout": model_probe_timeout}
    try:
        with tempfile.TemporaryDirectory(prefix="af-model-probe-") as probe_dir:
            code, _ = run_capture([exe] + margv, timeout=model_probe_timeout, cwd=probe_dir)
    except subprocess.TimeoutExpired:
        raise LaunchError(f"{tool} model inference check timed out after {model_probe_timeout}s "
                          f"(model: {chosen or 'tool default'}): {exe} {' '.join(margv)}. "
                          "Fix the CLI, or use --manual.")
    if code:
        raise LaunchError(f"{tool} account access probe passed but inference with the selected model "
                          f"({chosen or 'tool default'}) was denied (exit {code}): "
                          f"{exe} {' '.join(margv)}. Check the model name and the account's "
                          "entitlement, or use --manual. The attempt was not created.")
    check["modelProbe"]["result"] = "ok"
    return check


# --- attempt completion: stop classification and recovery capture --------------------------------------------------
RECOVERY_MAX_FILES = 200


def git_out(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else None


def classify_stop(a, endcheck_bad, hint=None):
    """The attempt's stopReason (protocol: Recovery): launcher facts first (an explicit stop, a dead
    process, the wall clock), then the shared detector's flag, then evidence-based classes
    (launch/environment error, end-check violation, nonzero exit, clean completion). Free text
    alone never classifies an attempt."""
    if hint in ("stopped", "dead", "timeout"):
        return hint
    if a.get("limitHit"):
        return "limit"
    if (a.get("note") or "").startswith("launch error:"):
        return "environment"
    if endcheck_bad:
        return "verification"
    if a.get("exitCode") not in (None, 0):
        return "implementation"
    return "completed"


def capture_recovery(a, t, reason):
    """Bounded recovery state for an attempt that did not complete, stored on its record: per checkout the
    branch, HEAD, tracked modifications and untracked paths (paths/status only - file contents and other
    secrets never enter runtime state), whether the Task File already holds a Result, and the classified
    stop reason. A successor continues from this record instead of a lost narrative."""
    rec = {"capturedAt": now(), "stopReason": reason,
           "hasResult": bool(((t or {}).get("result") or "").strip())}
    repos = []
    for c in (t or {}).get("checkouts") or []:
        path = c.get("path")
        if not path or not Path(path).is_dir():
            continue
        r = subprocess.run(["git", "-C", str(path), "status", "--porcelain"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        status = (r.stdout or "").splitlines() if r.returncode == 0 else []
        tracked = sorted({line[3:] for line in status if len(line) > 3 and line[:2] != "??"})
        new = sorted({line[3:] for line in status if len(line) > 3 and line[:2] == "??"})
        repos.append({"path": path,
                      "branch": git_out(path, "rev-parse", "--abbrev-ref", "HEAD"),
                      "head": git_out(path, "rev-parse", "HEAD"),
                      "modified": tracked[:RECOVERY_MAX_FILES],
                      "untracked": new[:RECOVERY_MAX_FILES],
                      "truncated": len(tracked) + len(new) > RECOVERY_MAX_FILES})
    rec["repos"] = repos
    a["recovery"] = rec
    return rec


def handover_note(prev, fresh=False):
    """The recovery line appended to a successor's prompt: what ended the previous attempt and what draft
    state the worktree still holds (paths/counts only, never file contents). One line: the prompt travels
    as a single command-line argument and cmd.exe ends a command at a newline."""
    if not prev:
        return None
    rec = prev.get("recovery") or {}
    reason = rec.get("stopReason") or prev.get("stopReason") or "error"
    parts = [f"Recovery handover: attempt {prev.get('n')} of this task ended as '{reason}'."]
    if fresh:
        parts.append("The draft state was deliberately discarded (`Resume: start fresh`): the worktree "
                     "was reset to the branch HEAD before your start.")
    else:
        repos = rec.get("repos") or []
        if repos:
            seen = "; ".join(
                f"{r.get('path')} (branch {r.get('branch')}, HEAD {str(r.get('head') or '')[:12]}, "
                f"{len(r.get('modified') or [])} modified + {len(r.get('untracked') or [])} untracked"
                f"{', list truncated' if r.get('truncated') else ''})" for r in repos)
            parts.append(f"The task's draft state was preserved ({seen}): inspect `git status` and "
                         "continue from it instead of starting over.")
        else:
            parts.append("No draft worktree state could be captured; check the attempt log.")
        if not rec.get("hasResult"):
            parts.append("The Task File has no Result yet; write yours there when done.")
    return " ".join(parts)


def apply_resume(t, c):
    """`Resume:` continuation for one developer worktree (protocol: Recovery): '<sha>' keeps the worktree
    and its drafts and requires the commit to be an ancestor of its HEAD; 'start fresh' discards only this
    worktree's draft state; 'none' (or absent) leaves the worktree as found."""
    rv = (t.get("resume") or "").strip()
    if not rv or rv.lower() == "none":
        return
    path = c["path"]
    if rv.lower() == "start fresh":
        for args in (("reset", "--hard", "HEAD"), ("clean", "-fd")):
            if subprocess.run(["git", "-C", path, *args], capture_output=True).returncode:
                raise LaunchError(f"Resume 'start fresh': git {' '.join(args)} failed in {path}")
        print(f"Resume start fresh: {path} was reset to HEAD and cleaned")
        return
    if subprocess.run(["git", "-C", path, "merge-base", "--is-ancestor", rv, "HEAD"],
                      capture_output=True).returncode:
        raise LaunchError(f"Resume {rv}: that commit is not an ancestor of the HEAD of {path} - the "
                          "preserved work is elsewhere; fix the branch or the Resume line, drafts are "
                          "not silently discarded.")


# --- attempt completion ---------------------------------------------------------------------------------------------
def complete_attempt(tid, rt, state, hint=None):
    """End-of-attempt check, the classified stop reason, recovery capture on failure, then the final state."""
    a = last_attempt(rt)
    t = None
    try:
        t = invoke_gate("task", tid)
        bad = invoke_gate("endcheck", tid).get("violations") or []
        remove_checkout(t)
    except Exception as e:
        bad = [f"end check failed: {e}"]
    if bad:
        state = "error"
        a["note"] = "; ".join(x for x in [a.get("note"), *bad] if x)
    if a.get("log"):  # what the tool itself reported about its runtime, else the record stays 'unknown'
        model, effort = effective_identity(a["log"])
        a["effectiveModel"], a["effectiveEffort"] = model or "unknown", effort or "unknown"
    a["status"], a["finishedAt"] = state, now()
    a["stopReason"] = classify_stop(a, bad, hint)
    if a["stopReason"] != "completed":
        capture_recovery(a, t, a["stopReason"])
    write_rt(tid, rt)
    if bad:
        print(f"warning: {tid} attempt {a['n']} failed the end check: {'; '.join(bad)}", file=sys.stderr)


# --- subcommands ----------------------------------------------------------------------------------------------------
def cmd_status():
    if RT_DIR.is_dir():
        for p in sorted(RT_DIR.glob("T-*.json")):
            if not re.match(r"^T-\d+\.json$", p.name):
                continue
            try:
                rt = ledger.check_runtime(json.loads(p.read_text(encoding="utf-8-sig")), p.stem)
            except (OSError, ValueError) as e:
                print(f"{p.stem}  state-error: cannot read runtime state ({e})")
                continue
            a = last_attempt(rt)
            if not a:
                continue
            state = a.get("status")
            if state == "running" and not a.get("manual") and not attempt_alive(a):
                state = "blocked" if attempt_uncertain(a) else "dead"
            print(f"{rt.get('taskId') or p.stem}  {state:<8} attempt={a.get('n')}  tool={a.get('tool') or ''}  "
                  f"exit={a.get('exitCode') if a.get('exitCode') is not None else ''}  "
                  f"stop={a.get('stopReason') or ''}  limitHit={a.get('limitHit')}  "
                  f"group={a.get('quotaGroup') or ''}  finished={a.get('finishedAt') or ''}")
    return 0


def _launch_lock(wait=0.0):
    """The project launch lock (.runtime/launch.lock, O_EXCL): serializes a new attempt with an external
    stop, so a stop decided on attempt n can never land its kill or its record write on attempt n+1
    created meanwhile. `wait` seconds of bounded retry let a short launch finish first; a lock older
    than 300s is a crashed launcher's leftover and is removed. Returns (fd, path); release with
    os.close(fd) and path.unlink(missing_ok=True)."""
    lock = RT_DIR / "launch.lock"
    deadline = time.time() + wait
    while True:
        try:
            if time.time() - lock.stat().st_mtime > 300:
                lock.unlink()  # left by a crashed launcher
        except OSError:
            pass
        try:
            return os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY), lock
        except FileExistsError:
            if time.time() >= deadline:
                raise LaunchError(f"another launcher run is in progress ({lock}). Wait and check --status.")
            time.sleep(0.2)


def stop_attempt(tid, initiator, reason, hint, expect=None):
    """Close a running attempt from outside (shared by --stop and the watchdog), serialized with launches
    by the same launch.lock: a bounded wait lets an in-flight launch finish, then the record is re-read
    inside the lock and must still name the expected attempt - a stale caller never stops a newer one.
    Then kill under the recorded-identity rules and close with the classified end, or refuse while
    managed processes still run (the task stays locked). `initiator`/`reason` land in `stoppedBy` as
    safe metadata - never raw argv or environment. Returns True when the attempt was closed."""
    fd, lock = _launch_lock(wait=STOP_LOCK_WAIT)
    try:
        rt = read_rt(tid)
        a = last_attempt(rt)
        if expect is not None and (not a or a.get("n") != expect):
            raise LaunchError(f"{tid}: expected attempt {expect} but the last recorded attempt is "
                              f"{a.get('n') if a else 'none'} - a stale stop was refused, nothing was killed")
        if not a or a.get("status") != "running":
            if a and a.get("machineLease"):
                machine_capacity.release(a["machineLease"])
            return False
        if attempt_alive(a):
            kill_tree(a["pid"])
            a["stoppedBy"] = {"initiator": initiator, "reason": reason, "at": now()}
            write_rt(tid, rt)   # who stopped it survives a blocked cleanup retry
            strays, members = leftover_processes(tid, a, grace=3.0)
            if strays or members:
                raise _leftover_error(tid, strays, members, what="releasing the lock")
        elif attempt_uncertain(a):
            # A process sits on the recorded pid but its identity cannot be confirmed: it may be a reused
            # pid, so no kill is sent to it - and closing the attempt would free the lock while the worker
            # may still run. The lock releases only on a verified stop or a verified process identity.
            raise LaunchError(f"{tid}: pid {a['pid']} is alive but its start identity cannot be confirmed "
                              "(none recorded, or not measurable now) - a possibly reused pid is never "
                              "killed and the task stays locked. If the process really is this worker, "
                              f"end it and run run_task.py {tid} --stop again.")
        elif a.get("pid"):
            # The recorded worker is gone but never wrote a final state; its managed children may still write.
            strays, members = leftover_processes(tid, a)
            if strays or members:
                raise _leftover_error(tid, strays, members, what="releasing the lock")
        # 'timeout' means the wall clock enforced a kill - the watchdog's kill just now, or the recorded one
        # a blocked cleanup is retrying. A worker the watchdog found overdue but already gone is 'dead';
        # a --stop command line stays 'stopped'.
        if (a.get("stoppedBy") or {}).get("initiator") == "watchdog":
            hint = "timeout"
        elif initiator == "watchdog":
            hint = "dead"
        a["stoppedBy"] = {"initiator": initiator, "reason": reason, "at": now()}
        a["exitCode"], a["note"] = -1, "; ".join(x for x in [a.get("note"), reason] if x)
        complete_attempt(tid, rt, "error", hint=hint)
        if a.get("machineLease"):
            machine_capacity.release(a["machineLease"])
        return True
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def cmd_stop(tid, expect=None):
    stopped = stop_attempt(tid, "cli", "stopped with --stop", "stopped", expect=expect)
    print(f"{tid} stopped, lock released" if stopped else f"{tid}: no running attempt")
    return 0


def cmd_watchdog(tid=None, expect=None):
    """Enforce persisted launch deadlines from outside the worker: every running non-manual attempt whose
    deadline passed is stopped through the same guarded path as --stop - classified 'timeout', initiator
    'watchdog' - under the expected-attempt guard. Manual attempts and attempts inside their bound are
    left untouched, an attempt whose bound cannot be read stays locked and diagnosed, and the watchdog
    only stops: it never relaunches. Quiet when nothing is overdue."""
    paths = [RT_DIR / f"{tid}.json"] if tid else sorted(RT_DIR.glob("T-*.json"))
    rc = 0
    for p in paths:
        if not re.match(r"^T-\d+\.json$", p.name) or not p.exists():
            continue
        try:
            rt = ledger.check_runtime(json.loads(p.read_text(encoding="utf-8-sig")), p.stem)
        except (OSError, ValueError) as e:
            print(f"{p.stem}  watchdog: cannot read runtime state ({e})", file=sys.stderr)
            rc = 1
            continue
        a = last_attempt(rt)
        if not a or a.get("status") != "running" or a.get("manual") or not a.get("pid"):
            continue   # manual sessions and unstarted or finished attempts are never the watchdog's
        due = attempt_deadline(a)
        if due is None:
            print(f"{p.stem}  watchdog: attempt {a.get('n')} is running but has no readable deadline "
                  "or start - left locked for diagnosis", file=sys.stderr)
            rc = 1
            continue
        if due > datetime.now(timezone.utc):
            continue   # unexpired
        try:
            if stop_attempt(p.stem, "watchdog", f"worker deadline {due.strftime('%Y-%m-%dT%H:%M:%SZ')} "
                            "passed (watchdog)", "timeout",
                            expect=expect if expect is not None else a.get("n")):
                print(f"{p.stem}  watchdog: attempt {a['n']} stopped at its deadline "
                      f"{due.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        except Exception as e:   # one task's failure never stops the sweep of the others
            print(f"{p.stem}  watchdog: {type(e).__name__}: {e}", file=sys.stderr)
            rc = 1
    return rc


def cmd_mark_finished(tid):
    rt = read_rt(tid)
    a = last_attempt(rt)
    if not a or not a.get("manual") or a.get("status") != "running":
        raise LaunchError(f"{tid} has no running manual attempt (start one with --manual)")
    complete_attempt(tid, rt, "exited")
    print(f"{tid} manual attempt {a['n']}: {a['status']}")
    return 0


def cmd_recheck(tid):
    """The end check failed an attempt whose tool exited 0; after the cause is fixed, run it again."""
    rt = read_rt(tid)
    a = last_attempt(rt)
    if not a or a.get("status") != "error" or a.get("exitCode") != 0 or a.get("limitHit") or a.get("manual"):
        raise LaunchError(f"{tid}: --recheck needs a last attempt in 'error' whose tool exited 0 "
                          "without a usage limit")
    bad = invoke_gate("endcheck", tid).get("violations") or []
    if bad:
        print(f"{tid} attempt {a['n']} still fails the end check: {'; '.join(bad)}")
        return 1
    a["status"] = "exited"
    a["note"] = "; ".join(x for x in [a.get("note"), f"recheck passed {now()}"] if x)
    write_rt(tid, rt)
    print(f"{tid} attempt {a['n']}: exited (end check passed on recheck)")
    return 0


def run_logged(argv, log, cwd, env, timeout=None, on_spawn=None):
    """Tee: the tool's output goes to the console and the attempt log as it is produced. With `timeout`
    (seconds) the launcher enforces the wall clock itself: on expiry the managed process tree is killed and
    (exit code, True) is returned - a tool that ignores its own CLI timeout is still bounded. `on_spawn`
    runs right after the tool process exists: the worker uses it to record the tool's session identity
    for takeover checks."""
    with open(log, "a", encoding="utf-8", errors="replace") as fh:
        # On POSIX the tool leads its own session/group: a wall-clock kill of its tree cannot SIGTERM
        # the worker itself (it would die before recording the error attempt).
        kw = {} if os.name == "nt" else {"start_new_session": True}
        p = subprocess.Popen(cmd_argv(argv), cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace", bufsize=1, **kw)
        if on_spawn:
            on_spawn(p.pid)

        def pump():
            for line in p.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                fh.write(line)
                fh.flush()

        reader = threading.Thread(target=pump, daemon=True)
        reader.start()
        try:
            code, timed_out = p.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            kill_tree(p.pid)
            try:
                code = p.wait(timeout=POST_KILL_WAIT)
            except subprocess.TimeoutExpired:
                code = -1   # the direct child outlived its own kill; the timeout verdict stands
            timed_out = True
        reader.join(timeout=10)
        return code, timed_out


def _attempt_log(log, line):
    """A durable launcher note inside the attempt log: the worker's own stdout is discarded, so the log
    file is the only place a launcher-side fact (the power-guard outcome) survives."""
    if not log:
        return
    try:
        with open(log, "a", encoding="utf-8", errors="replace") as fh:
            fh.write(f"[run_task {now()}] {line}\n")
    except OSError:
        pass


def cmd_worker(tid, tool):
    """Runs inside the worker process: set up by the launch, writes the final attempt state."""
    rt = read_rt(tid)
    att = last_attempt(rt)
    log, code, timed_out, note = att.get("log"), 1, False, None
    guard_held, guard_detail = False, "not requested"
    try:
        if att.get("machineLease"):
            if not machine_capacity.activate(att["machineLease"], os.getpid(), pid_start(os.getpid())):
                raise LaunchError("machine capacity activation failed")
        # A bounded worker asks Windows to keep the system out of automatic idle sleep while it runs
        # (power_guard: system execution only - never display-on or away mode, and an explicit user
        # sleep/lid still wins; POSIX is a no-op). A failed request is recorded, not hidden.
        guard_held, guard_detail = power_guard.acquire()
        _attempt_log(log, f"power guard: {guard_detail}")
        t = invoke_gate("task", tid)
        env = {**os.environ, **worker_env(t)}
        # the resolved bound is always positive: an invalid/zero AGENTFLOW_WORKER_TIMEOUT keeps the
        # default, and the task's own duration budget (from attempt 1's start) clamps it when tighter
        timeout, bound = worker_bound(rt, att)
        prompt = t["prompt"] + (f" {att['handover']}" if att.get("handover") else "")
        argv = [tool_exe(tool)] + tool_argv(tool, t["role"], prompt, t["model"], t["effort"])
        code, timed_out = run_logged(argv, log, cwd=t["workdir"], env=env, timeout=timeout,
                                     on_spawn=lambda pid: write_tool_session(tid, pid))
        if timed_out:
            note = (f"wall-clock timeout after {int(timeout)}s: the managed process tree was killed "
                    f"({bound})")
    except Exception as e:
        note = f"launch error: {e}"
        print(note)
    finally:
        if guard_held:
            _rel, rel_detail = power_guard.release()
            _attempt_log(log, f"power guard release: {rel_detail}")
    rt = read_rt(tid)  # re-read: the launcher wrote the pid after start
    a = last_attempt(rt)
    a["powerGuard"] = {"held": guard_held, "detail": guard_detail}
    a["exitCode"] = 124 if timed_out and code == 0 else code
    # The shared detector judges the session log's tail the same way tick.py and the conductor do: strong
    # provider-directed phrases count even on a clean exit, weak quota words need failure evidence, and a
    # report that merely quotes quota wording stays subject matter. A timed-out attempt is a wall-clock
    # error either way, so its log is not judged.
    detail = limit_detection.detect_detail_file(log, code) if not timed_out and log else None
    a["limitHit"] = bool(detail)
    if detail:
        a["limitPhrase"], a["limitKind"] = detail
    if note:
        a["note"] = note
    complete_attempt(tid, rt, "error" if timed_out or code else "exited",
                     hint="timeout" if timed_out else None)
    if att.get("machineLease"):
        machine_capacity.release(att["machineLease"])
    print(f"\n{tid} attempt {a['n']}: {a['status']} (exit {code}).")
    return 0


def cmd_launch(tid, tool, manual, grant):
    if not tool and not manual:
        raise LaunchError("tool required: codex | claude | agy | devin (or --manual)")
    nested_check()
    fd, lock = _launch_lock()
    lease, worker_started, a, rt = None, False, None, None
    try:
        rt = read_rt(tid)  # corrupted state fails closed in read_rt
        prev = last_attempt(rt)
        if attempt_uncertain(prev):
            raise LaunchError(f"{tid}: a process is alive on the recorded pid {prev.get('pid')} but its start "
                              "identity is unconfirmed (a possibly reused pid) - the task stays locked until "
                              "the process ends or its identity is verified")
        if attempt_held(prev):
            raise LaunchError(f"{tid} already has a running attempt ({prev.get('tool')}, pid {prev.get('pid')}). "
                              f"One task = one worker. Stop it first: run_task.py {tid} --stop")
        if prev and prev.get("status") == "running":
            print(f"warning: previous attempt of {tid} died without a final state (process gone?). "
                  "Recovery applies.", file=sys.stderr)
            prev["status"], prev["note"] = "error", "dead: process gone without a final state"
            prev["finishedAt"], prev["stopReason"] = now(), "dead"
            try:
                capture_recovery(prev, invoke_gate("task", tid), "dead")
            except LaunchError as e:
                prev.setdefault("recovery", {"capturedAt": now(), "stopReason": "dead",
                                             "error": f"task state unreadable: {e}"})
            write_rt(tid, rt)
        if prev and prev.get("pid"):
            strays, members = leftover_processes(tid, prev, grace=2.0)
            if strays or members:
                raise _leftover_error(tid, strays, members)
        live = live_tasks()
        more = (["--live", ",".join(live)] if live else []) + (["--manual"] if manual else ["--tool", tool])
        pf = invoke_gate("preflight", tid, more)
        if not pf.get("ok"):
            raise LaunchError(f"{tid} preflight failed, nothing was created:\n  - "
                              + "\n  - ".join(pf["problems"])
                              + "\nFix the Task File (or the project Preflight rules) and launch again.")
        t = pf["task"]
        if not manual and t["role"] not in ("developer", "tester"):
            raise LaunchError(f"Role '{t['role']}': the launcher starts developer and tester only. Use --manual.")
        if reason := budget_stop(rt or {}, tool if not manual else None):
            raise LaunchError(f"{tid}: {reason}. Nothing was started; the attempt records and their "
                              "recovery checkpoints are preserved - the Orchestrator decides the "
                              "successor task.")
        check = None
        if not manual:
            if t["role"] not in PERMISSIONS.get(tool, ()):
                raise LaunchError(f"{tool} as {t['role']} is not a supported permission mode on this platform; "
                                  "the launcher refuses it rather than silently downgrading isolation. "
                                  "See the permission matrix in run_task.py.")
            check = resource_check(tool, t["model"])
            port = (t.get("env") or {}).get("PORT")
            try:
                lease, reason = machine_capacity.claim(tool, ROOT, tid, port=port,
                                                       pid=os.getpid(), pid_start=pid_start(os.getpid()),
                                                       grant=grant, group=check.get("quotaGroup"))
            except (OSError, ValueError, TimeoutError) as e:
                raise LaunchError(f"machine capacity failed: {e}")
            if not lease:
                raise LaunchError(f"machine capacity wait: {reason}")
        init_workdir(t)
        if tool == "agy":
            print(f"Antigravity: make sure '{t['workdir']}' is in its trusted folders before the first run.")

        if not rt:
            rt = {"taskId": tid, "attempts": []}
        n = len(rt["attempts"]) + 1
        a = {"n": n, "taskId": tid, "tool": tool or "manual",
             "toolArgsHash": argv_hash(split_args(os.environ.get(f"AGENTFLOW_{tool.upper()}_ARGS")))
             if tool else None,
             "requestedModel": t["model"], "requestedEffort": t["effort"],
             "toolVersion": tool_version(check["exe"]) if check else "unknown",
             "effectiveModel": "unknown", "effectiveEffort": "unknown",
             "role": t["role"], "manual": manual, "status": "running", "pid": None, "pidStart": None,
             "exitCode": None, "startedAt": now(), "finishedAt": None, "limitHit": False,
             "stopReason": None,
             "quotaGroup": (check or {}).get("quotaGroup") if check else t.get("quotaGroup"),
             "target": t["target"], "workdir": t["workdir"],
             "log": None if manual else str(RT_DIR / f"{tid}.{n}.log"),
             "baseline": invoke_gate("task", tid).get("baseline"),
             "machineLease": lease, "note": None}
        if not manual:
            a["launch"] = {"exe": check["exe"],
                           "argv": tool_argv(tool, t["role"], None, t["model"], t["effort"], masked=True)}
            # the bound the worker will enforce, and the absolute clock the watchdog enforces
            a["workerTimeout"], _ = worker_bound(rt, a)
            a["deadline"] = (parse_ts(a["startedAt"])
                             + timedelta(seconds=a["workerTimeout"])).strftime("%Y-%m-%dT%H:%M:%SZ")
        if check:
            a["resourceCheck"] = check
        if prev and (prev.get("recovery") or prev.get("stopReason")):
            fresh = (t.get("resume") or "").strip().lower() == "start fresh"
            a["handover"] = handover_note(prev, fresh)
        rt["attempts"].append(a)
        write_rt(tid, rt)  # a running attempt = the task's lock for the worker's lifetime

        # Record issuance before handing control to a worker, including direct and --manual launches.
        r = subprocess.run(python_cmd() + [str(LEDGER), "set", tid, "--status", "in progress"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise LaunchError(f"ledger refused launch of {tid}: {(r.stdout + r.stderr).strip()}")

        if manual:
            e = worker_env(t)
            e["AGENTFLOW_ATTEMPT"], e["AGENTFLOW_ATTEMPT_ROOT"] = f"{tid}#{n}", str(Path(t["workdir"]).resolve())
            handover = f" {a['handover']}" if a.get("handover") else ""
            print(f"{tid} attempt {n} ready for a manual start.\n  folder: {t['workdir']}\n"
                  f"  env:    {', '.join(f'{k}={v}' for k, v in e.items())}\n"
                  f"  prompt: {t['prompt']}{handover}\nWhen it ends: run_task.py {tid} --mark-finished")
            return 0

        # The worker gets the environment through the spawn call alone: no plaintext handover file, so
        # operator AGENTFLOW_* values (which may carry secrets) are never serialized to disk.
        env = dict(os.environ)
        env.pop("AGENTFLOW_TARGET", None)
        env.pop("AGENTFLOW_EVIDENCE", None)
        # the attempt markers: a launch inside this session's checkout is a nested helper (nested_check)
        env["AGENTFLOW_ATTEMPT"] = f"{tid}#{n}"
        env["AGENTFLOW_ATTEMPT_ROOT"] = str(Path(t["workdir"]).resolve())
        cmd = worker_python_cmd() + [str(Path(__file__).resolve()), tid, tool, "--worker"]
        kw = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
              "env": env, "close_fds": True}
        if os.name == "nt":
            kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        p = subprocess.Popen(cmd, **kw)
        worker_started = True
        _job_assign(p.pid)  # leftover tracking survives broken parent chains (no-op off Windows)
        rt = read_rt(tid)
        cur = last_attempt(rt)
        if cur.get("status") == "running" and alive(p.pid):  # the worker may already have finished
            cur["pid"], cur["pidStart"] = p.pid, pid_start(p.pid)
            write_rt(tid, rt)
    except Exception as e:
        if not worker_started and a and a.get("status") == "running":
            a["status"], a["finishedAt"] = "error", now()
            a["note"] = f"launch failed: {e}"
            a["stopReason"] = "environment"
            write_rt(tid, rt)
        raise
    finally:
        if lease and not worker_started:
            machine_capacity.release(lease)
        os.close(fd)
        lock.unlink(missing_ok=True)
    print(f"{tid} attempt {n} started in {tool} (pid {p.pid}). log: {a['log']}")
    return 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONUTF8"] = "1"
    RT_DIR.mkdir(parents=True, exist_ok=True)
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("task", nargs="?", help="task id T-NNN")
    ap.add_argument("tool", nargs="?", choices=TOOLS, help="worker CLI tool")
    ap.add_argument("--status", action="store_true", help="process state of the last attempt of every task")
    ap.add_argument("--stop", action="store_true", help="kill a hung worker (whole process tree), release the lock")
    ap.add_argument("--mark-finished", action="store_true", help="a manual attempt has finished")
    ap.add_argument("--recheck", action="store_true", help="rerun the end check after its cause was fixed")
    ap.add_argument("--manual", action="store_true", help="prepare the launch; a human starts the tool")
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)  # internal: inside the worker process
    ap.add_argument("--dispatch-grant", help="shared-dispatch grant token to exchange for the machine lease")
    ap.add_argument("--watchdog", action="store_true",
                    help="stop non-manual attempts past their recorded deadline (all tasks, or the named one)")
    ap.add_argument("--expect-attempt", type=int, metavar="N",
                    help="refuse the stop when the last attempt is not N (stale-stop guard)")
    a = ap.parse_args()
    try:
        if a.status:
            return cmd_status()
        if a.watchdog:
            if a.task and not re.match(r"^T-\d+$", a.task):
                raise LaunchError("task id T-NNN required")
            return cmd_watchdog(a.task, a.expect_attempt)
        if not a.task or not re.match(r"^T-\d+$", a.task):
            raise LaunchError("task id T-NNN required")
        if a.stop:
            return cmd_stop(a.task, a.expect_attempt)
        if a.mark_finished:
            return cmd_mark_finished(a.task)
        if a.recheck:
            return cmd_recheck(a.task)
        if a.worker:
            if not a.tool:
                raise LaunchError("--worker needs the tool")
            return cmd_worker(a.task, a.tool)
        return cmd_launch(a.task, a.tool, a.manual, a.dispatch_grant)
    except LaunchError as e:
        print(f"run_task: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"run_task: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
