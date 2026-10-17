#!/usr/bin/env python3
"""Launch one worker attempt for one task and track its process state.

  python .agentflow/tools/run_task.py T-007 codex          # launch a developer or tester task
  python .agentflow/tools/run_task.py T-007 --manual       # same gate and preparation, no process: a human starts the tool
  python .agentflow/tools/run_task.py --status             # process state of the last attempt of every task
  python .agentflow/tools/run_task.py T-007 --stop         # kill a hung worker (whole process tree), release the lock
  python .agentflow/tools/run_task.py T-007 --mark-finished# a manual attempt has finished
  python .agentflow/tools/run_task.py T-007 --recheck      # rerun the end check for an attempt that exited 0 but failed it

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
itself - AGENTFLOW_WORKER_TIMEOUT seconds (default 1200 = 20 minutes, 0 or a non-number disables it). On expiry
the launcher kills the managed process tree, records a timeout error and releases the machine lease. All tools
above run non-interactively, so every worker obeys this bound; an interactive session is a --manual attempt.
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
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger  # noqa: E402
import machine_capacity  # noqa: E402
from paths import FLOW_ROOT, REPO_ROOT  # noqa: E402

ROOT = REPO_ROOT
RT_DIR = FLOW_ROOT / "tasks" / ".runtime"
GATE = FLOW_ROOT / "tools" / "gate.py"
LEDGER = FLOW_ROOT / "tools" / "ledger.py"
MACHINE = FLOW_ROOT / "tools" / "machine_capacity.py"
LIMITS_FILE = RT_DIR / "tool-limits.json"
TOOLS = ("codex", "claude", "agy", "devin")

LIMIT_RE = re.compile(
    r"usage limit|rate limit|quota|session limit|hit your limit|out of credits|"
    r"disabled[^\r\n]*subscription access|subscription access[^\r\n]*disabled|"
    r"ask your admin to enable access", re.I)

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
# in seconds; 0 or a non-number disables the bound.
WORKER_TIMEOUT = 1200

# tool -> roles the launcher will start (see the permission matrix in the docstring). Anything else refuses.
PERMISSIONS = {t: ("developer", "tester") for t in TOOLS}


class LaunchError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def tool_argv(tool, role, prompt, model, effort):
    """Full argv after the executable, in the same order the PowerShell launcher built it."""
    if tool == "codex":
        base = ["exec"] + env_args("codex", model, effort)
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
    return base + env_args(tool, model, effort) + model_args(tool, model, effort)


def tool_exe(tool):
    return resolve_exe(tool, os.environ.get(f"AGENTFLOW_{tool.upper()}"))


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


def tree_pgroups(pid):
    """Process-group ids of the tree rooted at pid: the root's group plus the group of every live
    descendant, so a managed child that leads its own session is reached too."""
    groups = set()
    try:
        groups.add(os.getpgid(int(pid)))
    except OSError:
        pass
    kids = {}  # ppid -> [(pid, pgrp)]
    proc = Path("/proc")
    if proc.is_dir():
        for d in proc.iterdir():  # Linux: /proc/<pid>/stat holds ppid and pgrp after the comm field
            if not d.name.isdigit():
                continue
            try:
                stat = (d / "stat").read_text().rsplit(")", 1)[1].split()
                kids.setdefault(int(stat[1]), []).append((int(d.name), int(stat[2])))
            except (OSError, IndexError, ValueError):
                continue
    else:
        try:
            out = subprocess.run(["ps", "-eo", "pid=,ppid=,pgid="], capture_output=True, text=True,
                                 timeout=10).stdout
        except (OSError, subprocess.SubprocessError):
            return groups
        for line in out.splitlines():
            f = line.split()
            if len(f) == 3:
                kids.setdefault(int(f[1]), []).append((int(f[0]), int(f[2])))
    stack, seen = [int(pid)], {int(pid)}
    while stack:
        for child, grp in kids.pop(stack.pop(), []):
            if child not in seen:
                seen.add(child)
                stack.append(child)
                groups.add(grp)
    return groups


def kill_tree(pid):
    """Kill the worker and its managed descendants (the tool process and what it spawned)."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
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
        p.wait()
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


# --- resource and permission checks before a worker start -----------------------------------------------------------
def limit_until(tool):
    """Observed quota/access limits, project file and shared machine registry; earliest expiry wins.
    A malformed project record fails closed: 'no limits known' is never inferred from a bad file."""
    ends = []
    if LIMITS_FILE.exists():
        try:
            lim = ledger.check_limits(json.loads(LIMITS_FILE.read_text(encoding="utf-8-sig")))
        except (OSError, ValueError) as e:
            raise LaunchError(f"cannot read observed limits {LIMITS_FILE.name}: {e}")
        rec = lim.get(tool)
        if rec:
            try:
                ends.append(datetime.strptime(rec["until"], "%Y-%m-%dT%H:%M:%SZ")
                            .replace(tzinfo=timezone.utc))
            except ValueError as e:
                raise LaunchError(f"cannot read observed limits {LIMITS_FILE.name}: "
                                  f"bad 'until' for {tool}: {e}")
    machine = machine_capacity.limit_until(tool)
    if machine:
        ends.append(machine)
    return max(ends) if ends else None


def resource_check(tool, model=None):
    """Executable, authenticated access, selected-model inference, observed limits. Raises LaunchError with an
    actionable diagnostic; returns what was observed (freshness + source, no secrets, no quota figures)."""
    check = {"at": now(), "exe": None, "probe": None, "probeSource": None}
    exe = tool_exe(tool)
    found = shutil.which(exe) or (str(Path(exe).resolve()) if Path(exe).exists() else None)
    if not found:
        raise LaunchError(f"{tool} executable not found: '{exe}'. Set AGENTFLOW_{tool.upper()} to its path "
                          "(wildcards allowed, the newest match wins).")
    check["exe"] = found

    end = limit_until(tool)
    if end and end > datetime.now(timezone.utc):
        raise LaunchError(f"{tool} is limited until {end.strftime('%Y-%m-%dT%H:%M:%SZ')} "
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
    chosen = selected_model(tool, model)
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


# --- attempt completion ---------------------------------------------------------------------------------------------
def complete_attempt(tid, rt, state):
    """End-of-attempt check, then the final state."""
    a = last_attempt(rt)
    try:
        bad = invoke_gate("endcheck", tid).get("violations") or []
        remove_checkout(invoke_gate("task", tid))
    except Exception as e:
        bad = [f"end check failed: {e}"]
    if bad:
        state = "error"
        a["note"] = "; ".join(x for x in [a.get("note"), *bad] if x)
    a["status"], a["finishedAt"] = state, now()
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
                  f"limitHit={a.get('limitHit')}  finished={a.get('finishedAt') or ''}")
    return 0


def cmd_stop(tid):
    rt = read_rt(tid)
    a = last_attempt(rt)
    if attempt_alive(a):
        kill_tree(a["pid"])
    elif attempt_uncertain(a):
        # A process sits on the recorded pid but its identity cannot be confirmed: it may be a reused pid,
        # so no kill is sent to it - and closing the attempt would free the lock while the worker may
        # still run. The lock releases only on a verified stop or a verified process identity.
        raise LaunchError(f"{tid}: pid {a['pid']} is alive but its start identity cannot be confirmed "
                          "(none recorded, or not measurable now) - a possibly reused pid is never killed "
                          "and the task stays locked. If the process really is this worker, end it and run "
                          f"run_task.py {tid} --stop again.")
    if a and a.get("status") == "running":
        a["exitCode"], a["note"] = -1, "; ".join(x for x in [a.get("note"), "stopped with --stop"] if x)
        complete_attempt(tid, rt, "error")
    if a and a.get("machineLease"):
        machine_capacity.release(a["machineLease"])
    print(f"{tid} stopped, lock released")
    return 0


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


def run_logged(argv, log, cwd, env, timeout=None):
    """Tee: the tool's output goes to the console and the attempt log as it is produced. With `timeout`
    (seconds) the launcher enforces the wall clock itself: on expiry the managed process tree is killed and
    (exit code, True) is returned - a tool that ignores its own CLI timeout is still bounded."""
    with open(log, "a", encoding="utf-8", errors="replace") as fh:
        # On POSIX the tool leads its own session/group: a wall-clock kill of its tree cannot SIGTERM
        # the worker itself (it would die before recording the error attempt).
        kw = {} if os.name == "nt" else {"start_new_session": True}
        p = subprocess.Popen(cmd_argv(argv), cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace", bufsize=1, **kw)

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
            code, timed_out = p.wait(), True
        reader.join(timeout=10)
        return code, timed_out


def cmd_worker(tid, tool):
    """Runs inside the worker process: set up by the launch, writes the final attempt state."""
    rt = read_rt(tid)
    att = last_attempt(rt)
    log, code, timed_out, note = att.get("log"), 1, False, None
    try:
        if att.get("machineLease"):
            if not machine_capacity.activate(att["machineLease"], os.getpid(), pid_start(os.getpid())):
                raise LaunchError("machine capacity activation failed")
        t = invoke_gate("task", tid)
        env = {**os.environ, **worker_env(t)}
        raw = os.environ.get("AGENTFLOW_WORKER_TIMEOUT")
        try:
            timeout = int(raw) if raw else WORKER_TIMEOUT
        except ValueError:
            timeout = 0
        timeout = timeout if timeout > 0 else None
        argv = [tool_exe(tool)] + tool_argv(tool, t["role"], t["prompt"], t["model"], t["effort"])
        code, timed_out = run_logged(argv, log, cwd=t["workdir"], env=env, timeout=timeout)
        if timed_out:
            note = (f"wall-clock timeout after {timeout}s: the managed process tree was killed "
                    f"(AGENTFLOW_WORKER_TIMEOUT)")
    except Exception as e:
        note = f"launch error: {e}"
        print(note)
    rt = read_rt(tid)  # re-read: the launcher wrote the pid after start
    a = last_attempt(rt)
    a["exitCode"] = 124 if timed_out and code == 0 else code
    try:
        tail = Path(log).read_text(encoding="utf-8", errors="replace")[-8000:] if log and Path(log).is_file() else ""
    except OSError:
        tail = ""
    # A successful report that merely mentions quota words (a test case, a summary) is not a limit; a timed-out
    # attempt is a wall-clock error either way. Real provider failures still set the flag (nonzero + wording).
    a["limitHit"] = bool(code) and not timed_out and bool(LIMIT_RE.search(tail))
    if note:
        a["note"] = note
    complete_attempt(tid, rt, "error" if timed_out or code else "exited")
    if att.get("machineLease"):
        machine_capacity.release(att["machineLease"])
    print(f"\n{tid} attempt {a['n']}: {a['status']} (exit {code}).")
    return 0


def cmd_launch(tid, tool, manual, grant):
    if not tool and not manual:
        raise LaunchError("tool required: codex | claude | agy | devin (or --manual)")
    lock = RT_DIR / "launch.lock"
    if lock.exists() and time.time() - lock.stat().st_mtime > 300:
        lock.unlink()  # left by a crashed launcher
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise LaunchError(f"another launcher run is in progress ({lock}). Wait and check --status.")
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
                                                       grant=grant)
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
             "role": t["role"], "manual": manual, "status": "running", "pid": None, "pidStart": None,
             "exitCode": None, "startedAt": now(), "finishedAt": None, "limitHit": False,
             "target": t["target"], "workdir": t["workdir"],
             "log": None if manual else str(RT_DIR / f"{tid}.{n}.log"),
             "baseline": invoke_gate("task", tid).get("baseline"),
             "machineLease": lease, "note": None}
        if check:
            a["resourceCheck"] = check
        rt["attempts"].append(a)
        write_rt(tid, rt)  # a running attempt = the task's lock for the worker's lifetime

        # Record issuance before handing control to a worker, including direct and --manual launches.
        r = subprocess.run(python_cmd() + [str(LEDGER), "set", tid, "--status", "in progress"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode:
            raise LaunchError(f"ledger refused launch of {tid}: {(r.stdout + r.stderr).strip()}")

        if manual:
            e = worker_env(t)
            print(f"{tid} attempt {n} ready for a manual start.\n  folder: {t['workdir']}\n"
                  f"  env:    {', '.join(f'{k}={v}' for k, v in e.items())}\n"
                  f"  prompt: {t['prompt']}\nWhen it ends: run_task.py {tid} --mark-finished")
            return 0

        # The worker gets the environment through the spawn call alone: no plaintext handover file, so
        # operator AGENTFLOW_* values (which may carry secrets) are never serialized to disk.
        env = dict(os.environ)
        env.pop("AGENTFLOW_TARGET", None)
        env.pop("AGENTFLOW_EVIDENCE", None)
        cmd = worker_python_cmd() + [str(Path(__file__).resolve()), tid, tool, "--worker"]
        kw = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
              "env": env, "close_fds": True}
        if os.name == "nt":
            kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kw["start_new_session"] = True
        p = subprocess.Popen(cmd, **kw)
        worker_started = True
        rt = read_rt(tid)
        cur = last_attempt(rt)
        if cur.get("status") == "running" and alive(p.pid):  # the worker may already have finished
            cur["pid"], cur["pidStart"] = p.pid, pid_start(p.pid)
            write_rt(tid, rt)
    except Exception as e:
        if not worker_started and a and a.get("status") == "running":
            a["status"], a["finishedAt"] = "error", now()
            a["note"] = f"launch failed: {e}"
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
    a = ap.parse_args()
    try:
        if a.status:
            return cmd_status()
        if not a.task or not re.match(r"^T-\d+$", a.task):
            raise LaunchError("task id T-NNN required")
        if a.stop:
            return cmd_stop(a.task)
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
