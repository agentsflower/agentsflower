#!/usr/bin/env python3
"""Opt-in adapters from a tool's own lifecycle hooks to AgentFlow's bounded completion check.

  python .agentflow/tools/hooks.py enable codex            # validate the runtime, print the manual steps
  python .agentflow/tools/hooks.py enable codex --write    # ...and write project-local .codex/hooks.json
  python .agentflow/tools/hooks.py codex-stop              # the Stop hook: runs `gate.py done`, advisory only

Codex CLI exposes lifecycle hooks since 0.114.0 ([features] codex_hooks; renamed [features] hooks
around 0.129.0). `enable` never trusts a docs page: it asks the installed binary for its version and
its feature surface, and refuses - writing nothing - when the runtime is missing, too old or cannot
prove the hooks feature. Enabling is opt-in twice: the command does nothing but print without
--write, and it adds one project-local .codex/hooks.json entry without touching global configuration
or any existing hook. The feature flag itself (config.toml) stays the operator's line to write.

The Stop hook is advisory: it maps the session's cwd back to the AgentFlow attempt that owned it,
runs the same completion check acceptance runs (gate.py done, which writes the bounded verify
record), prints a short actionable summary and exits 0 either way. It never spawns a worker, never
accepts a result, never reports a limit/blocker as a reason to continue, and is inert inside a
managed worker session (AGENTFLOW_ATTEMPT set): recursion and double bookkeeping stay impossible.
"""
import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from paths import FLOW_ROOT, REPO_ROOT  # noqa: E402

MIN_HOOKS = (0, 114, 0)     # first codex-cli with lifecycle hooks ([features] codex_hooks)
RENAMED_AT = (0, 129, 0)    # the flag was renamed to [features] hooks; the rename release must
                            # prove the surface - docs say 'renamed around this version', so the
                            # adapter trusts only what `codex features list` actually answers
PROBE_TIMEOUT = 15


def _run(exe, *args):
    try:
        r = subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=PROBE_TIMEOUT, stdin=subprocess.DEVNULL)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return None, ""


def _version(text):
    m = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", text)
    return tuple(int(g) for g in m.groups()) if m else None


def _features(text):
    """`codex features list` rows like 'hooks stable true' -> {name: (stage, enabled)}."""
    out = {}
    for ln in text.splitlines():
        if m := re.match(r"^\s*(codex_hooks|hooks)\s+(\S+)\s+(true|false)\s*$", ln):
            out[m.group(1)] = (m.group(2), m.group(3) == "true")
    return out


def codex_support(exe):
    """{supported, version, feature, stage, reason} for one codex executable. Only what the binary
    itself reports counts: below 0.114.0 there are no hooks; from the rename release on the runtime
    must answer `features list` and advertise an enabled hooks feature; between them the documented
    `codex_hooks` flag stands on its own but an explicit 'false' still vetoes it."""
    s = {"supported": False, "version": None, "feature": None, "stage": None, "reason": ""}
    code, out = _run(exe, "--version")
    if code != 0 or not (v := _version(out)):
        s["reason"] = (f"cannot determine the codex version from '{Path(exe).name} --version' "
                       f"(exit {code})" if code is not None else f"'{exe}' does not run")
        return s
    s["version"] = ".".join(map(str, v))
    if v < MIN_HOOKS:
        s["reason"] = (f"codex-cli {s['version']} has no lifecycle hooks; they need >= "
                       f"{'.'.join(map(str, MIN_HOOKS))}")
        return s
    want = "hooks" if v >= RENAMED_AT else "codex_hooks"
    code, out = _run(exe, "features", "list")
    found = _features(out) if code == 0 else {}
    if found:
        for name in ("hooks", "codex_hooks"):
            if name in found:
                stage, on = found[name]
                if not on:
                    s["reason"] = f"codex-cli {s['version']} lists the '{name}' feature disabled"
                    return s
                s.update(supported=True, feature=name, stage=stage)
                return s
    if v >= RENAMED_AT:
        s["reason"] = (f"codex-cli {s['version']} could not prove the hooks feature surface "
                       f"('features list' {'did not answer' if code != 0 else 'lists no hooks feature'}); "
                       f"the flag was renamed to 'hooks' near {'.'.join(map(str, RENAMED_AT))} and a mute "
                       "runtime is never enabled on trust")
        return s
    s.update(supported=True, feature="codex_hooks")  # the documented flag for this version range
    return s


# --- codex-stop -----------------------------------------------------------------------------------------------------
def _norm(path):
    try:
        return os.path.normcase(str(Path(path).resolve()))
    except OSError:
        return os.path.normcase(str(path))


def _task_for_cwd(cwd):
    """(task id, its last attempt) whose recorded workdir is the session's cwd, else (None, None)."""
    rt = FLOW_ROOT / "tasks" / ".runtime"
    if not rt.is_dir():
        return None, None
    for p in sorted(rt.glob("T-*.json")):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            att = (doc.get("attempts") or [None])[-1]
        except (OSError, ValueError):
            continue
        if att and att.get("workdir") and _norm(att["workdir"]) == _norm(cwd):
            return p.stem, att
    return None, None


def cmd_stop():
    if os.environ.get("AGENTFLOW_ATTEMPT"):
        print(f"managed AgentFlow session ({os.environ['AGENTFLOW_ATTEMPT']}): the launcher owns this "
              "lifecycle - the hook stays inert")
        return 0
    try:
        ctx = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        ctx = {}
    tid, att = _task_for_cwd(ctx.get("cwd") or os.getcwd())
    if not tid:
        print("codex stop: no AgentFlow attempt recorded for this folder - the normal path stands: "
              "run_task.py <task> --manual, then ledger.py accept")
        return 0
    if att.get("limitHit"):
        print(f"{tid}: the worker reported a usage limit ({att.get('limitPhrase') or 'provider limit'}); "
              "the observed-limits machinery owns the hold - nothing to accept")
        return 0
    if att.get("status") == "running":
        if not att.get("manual"):
            print(f"{tid}: attempt {att['n']} is still running - the launcher owns it; "
                  "nothing to accept")
            return 0
        import run_task  # a manual session's Stop is the session end: the mark-finished transition
        try:
            run_task.cmd_mark_finished(tid)
        except run_task.LaunchError as e:
            print(f"{tid}: {e}")
            return 0
    try:
        outcome = gate.result_field(gate.parse(tid), "Outcome")
    except (gate.TaskError, OSError) as e:
        print(f"{tid}: cannot read the Task File ({e}); check .agentflow/tools/gate.py done {tid}")
        return 0
    if outcome == "blocked":
        print(f"{tid}: Result Outcome is 'blocked' - the Orchestrator decides the successor; "
              "nothing to accept")
        return 0
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            ok = gate.done(tid)
    except Exception as e:  # an advisory hook degrades to bounded text, never to a crash or a claim
        print(f"{tid}: the completion check errored ({e}); run: python .agentflow/tools/gate.py "
              f"done {tid}")
        return 0
    for ln in buf.getvalue().splitlines()[:20]:
        print(ln)
    print(f"{tid}: gate done -> {'PASS' if ok else 'FAIL'}")
    if ok:
        print(f"next step: python .agentflow/tools/accept.py {tid}")
    else:
        print(f"investigate, then re-run: python .agentflow/tools/gate.py done {tid}")
    return 0


# --- enable ---------------------------------------------------------------------------------------------------------
def _codex_exe():
    raw = os.environ.get("AGENTFLOW_CODEX") or "codex"
    if any(c in raw for c in "*?"):  # same wildcard rule the launcher documents
        import run_task
        return run_task.resolve_exe("codex", raw)
    return shutil.which(raw) or raw


def _hook_entry(command):
    return {"matcher": "", "hooks": [{"type": "command", "command": command}]}


def cmd_enable(write):
    exe = _codex_exe()
    s = codex_support(exe)
    if not s["supported"]:
        print(f"unsupported: {s['reason']} - nothing was enabled or written", file=sys.stderr)
        return 1
    script = Path(__file__).resolve()
    command = f'"{sys.executable}" "{script}" codex-stop'
    flag = s["feature"]
    stage = f" ({s['stage']})" if s.get("stage") else ""
    print(f"codex-cli {s['version']}{stage} supports Stop hooks via the '{flag}' feature.")
    print("To finish enabling it, add to your codex config.toml (~/.codex/config.toml, or this "
          "project's .codex/config.toml if it is a trusted project):")
    print(f"\n  [features]\n  {flag} = true\n")
    hpath = REPO_ROOT / ".codex" / "hooks.json"
    if not write:
        print(f"Then run this command again with --write to install the project-local Stop hook "
              f"({hpath}), or write it yourself:")
        print(f'\n  {{"hooks": {{"Stop": [{json.dumps(_hook_entry(command))}]}}}}\n')
        return 0
    try:
        cfg = json.loads(hpath.read_text(encoding="utf-8")) if hpath.exists() else {}
    except ValueError as e:
        print(f"unsupported: {hpath} is not valid JSON ({e}) - fix or remove it, then re-run --write",
              file=sys.stderr)
        return 1
    if not isinstance(cfg, dict):
        print(f"unsupported: {hpath} must hold a JSON object - fix or remove it, then re-run --write",
              file=sys.stderr)
        return 1
    hooks = cfg.setdefault("hooks", {})
    stop = hooks.setdefault("Stop", [])
    if not isinstance(hooks, dict) or not isinstance(stop, list):
        print(f"unsupported: {hpath} 'hooks.Stop' is not a list - fix it, then re-run --write",
              file=sys.stderr)
        return 1
    if not any("codex-stop" in h.get("command", "")
               for entry in stop for h in (entry.get("hooks") or [])):
        stop.append(_hook_entry(command))
    hpath.parent.mkdir(parents=True, exist_ok=True)
    hpath.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {hpath} (existing hooks kept; nothing outside this project changed).")
    print("The hook is advisory: it runs 'gate.py done' and reports; it never accepts, spawns or "
          "continues on its own.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    en = sub.add_parser("enable", help="validate a runtime and opt in to its hook adapter")
    en.add_argument("tool", choices=("codex",))
    en.add_argument("--write", action="store_true",
                    help="write the project-local hooks.json (without it only the steps are printed)")
    sub.add_parser("codex-stop", help="the codex Stop hook: run the bounded completion check, advisory")
    a = ap.parse_args()
    if a.cmd == "enable":
        return cmd_enable(a.write)
    if a.cmd == "codex-stop":
        return cmd_stop()


if __name__ == "__main__":
    sys.exit(main())
