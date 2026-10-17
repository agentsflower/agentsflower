"""Optional-SDK MCP integration, run explicitly:

  python .agentflow/tests/check_mcp.py

Not part of `python -m unittest discover` (name has no test_ prefix): it needs
network access to provision the official `mcp` SDK and the `build` package into
disposable virtual environments. Core runtime stays stdlib-only.

What it proves (task criteria M-01..M-05):
- the packaged agentflow-sdlc wheel installs alongside `mcp>=2.3,<3`;
- `python .agentflow/tools/mcp_server.py` without the SDK fails with the
  install-extra diagnostic and exit code 2 (no homegrown fallback);
- a real MCP stdio handshake against the installed project's mcp_server.py:
  initialize, list_tools (read-only set only), agentflow_status,
  agentflow_query_ledger and an invalid-input call that returns a structured
  error instead of crashing;
- the privileged agentflow_accept_task is absent by default and present only
  with --enable-orchestrator-tools;
- the packaged `agentflow --project <dir> mcp` entry reaches the same server
  through the CLI (packaged resources exercised end to end).
No LLM/API calls: the only third-party traffic is pip installing released
packages.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAIL = []

# Runs inside the provisioned venv (the outer interpreter stays stdlib-only):
# one stdio session per invocation; prints `RESULT <json>` on stdout.
DRIVER = '''import asyncio, json, sys
from mcp import Client
from mcp.client.stdio import StdioServerParameters

async def main():
    cmd, args, calls = sys.argv[1], json.loads(sys.argv[2]), json.loads(sys.argv[3])
    async with Client(StdioServerParameters(command=cmd, args=args)) as client:
        tools = await client.list_tools()
        out = {"tools": {t.name: bool(t.annotations and t.annotations.read_only_hint)
                         for t in tools.tools}, "calls": []}
        for name, cargs in calls:
            r = await client.call_tool(name, cargs)
            text = "".join(getattr(b, "text", "") for b in r.content)
            payload = getattr(r, "structured_content", None)
            if not isinstance(payload, dict):
                try:
                    payload = json.loads(text)
                except (ValueError, TypeError):
                    payload = {"_text": text}
            out["calls"].append({"payload": payload, "is_error": r.is_error})
    print("RESULT " + json.dumps(out))

asyncio.run(main())
'''


def step(msg):
    print(f"== {msg}", flush=True)


def check(cond, what):
    print(f"  {'ok ' if cond else 'FAIL'} {what}", flush=True)
    if not cond:
        FAIL.append(what)


def run(cmd, cwd=None, ok=True, **kw):
    p = subprocess.run([str(c) for c in cmd], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if ok and p.returncode:
        raise RuntimeError(f"{cmd} -> {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


def venv_py(d: Path) -> Path:
    return d / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def venv_exe(d: Path, name: str) -> Path:
    return d / ("Scripts" if os.name == "nt" else "bin") / (name + (".exe" if os.name == "nt" else ""))


def make_venv(path: Path) -> Path:
    step(f"venv {path}")
    venv.create(path, with_pip=True)
    return venv_py(path)


def make_project(tmp: Path) -> Path:
    proj = tmp / "mcp proj"  # a path with a space
    proj.mkdir()
    for args in (("init", "-q", "-b", "main"), ("config", "user.email", "t@example.invalid"),
                 ("config", "user.name", "t")):
        run(["git", "-C", proj, *args])
    (proj / "AGENTS.md").write_text("# Own rules\n", encoding="utf-8")
    run(["git", "-C", proj, "add", "-A"])
    run(["git", "-C", proj, "commit", "-qm", "init"])
    return proj


def exercise(session, cmd, args, label):
    """One stdio session: handshake, list-tools, read-only calls, rejected inputs."""
    out = session(cmd, args, [("agentflow_status", {}),
                              ("agentflow_query_ledger", {"limit": 10, "filter_role": "developer"}),
                              ("agentflow_query_ledger", {"limit": 0}),
                              ("agentflow_get_task", {"task_id": "x; rm -rf /"})])
    names = sorted(out["tools"])
    check(names == ["agentflow_get_task", "agentflow_query_ledger",
                    "agentflow_run_gate", "agentflow_status"],
          f"{label}: default surface is exactly the four task tools ({names})")
    check(not out["tools"]["agentflow_run_gate"],
          f"{label}: run_gate is not labelled read-only")
    ok, ledger_ok, ledger_bad, task_bad = [c["payload"] for c in out["calls"]]
    check(ok.get("ok") is True and "agentflow_version" in ok,
          f"{label}: agentflow_status -> {ok}")
    check(ledger_ok.get("ok") is True and "tasks" in ledger_ok,
          f"{label}: agentflow_query_ledger -> ok")
    check(ledger_bad.get("ok") is False and "limit" in ledger_bad.get("error", ""),
          f"{label}: out-of-bounds limit is rejected ({ledger_bad})")
    check(task_bad.get("ok") is False, f"{label}: bad task id is rejected ({task_bad})")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="af mcp check "))
    try:
        step("build wheel of the checkout")
        bld = make_venv(tmp / "venv build")
        run([bld, "-m", "pip", "install", "-q", "build"])
        run([bld, "-m", "build", "--outdir", tmp / "dist"], cwd=ROOT)
        wheel = next((tmp / "dist").glob("*.whl"), None)
        check(wheel is not None, "wheel built")
        if wheel is None:
            return report()

        step("missing-SDK diagnostic (build venv has no mcp)")
        p = run([bld, str(ROOT / ".agentflow" / "tools" / "mcp_server.py")], ok=False, timeout=30)
        check(p.returncode == 2 and "pip install" in p.stderr and "agentflow-sdlc[mcp]" in p.stderr,
              f"no SDK -> exit 2 with install-extra diagnostic on stderr ({p.returncode}; {p.stderr.strip()[:120]})")

        step("mcp venv: install released SDK + the packaged wheel")
        py = make_venv(tmp / "venv mcp")
        run([py, "-m", "pip", "install", "-q", "mcp>=2.3,<3"])
        run([py, "-m", "pip", "install", "-q", wheel])
        meta = run([py, "-c", "import mcp, mcp_types; from mcp.server import MCPServer; "
                            "import importlib.metadata as m; print(m.version('mcp'))"]).stdout.strip()
        check(meta.startswith("2."), f"installed mcp SDK is the released 2.x line ({meta})")

        step("install AgentFlow into a disposable project")
        proj = make_project(tmp)
        af = venv_exe(tmp / "venv mcp", "agentflow")
        run([af, "install", str(proj)])
        server_py = proj / ".agentflow" / "tools" / "mcp_server.py"
        check(server_py.is_file(), "installed project carries tools/mcp_server.py")

        driver = tmp / "mcp_driver.py"
        driver.write_text(DRIVER, encoding="utf-8")

        def session(cmd, args, calls):
            p = run([py, driver, str(cmd), json.dumps([str(a) for a in args]),
                     json.dumps(calls)], timeout=120)
            line = [l for l in p.stdout.splitlines() if l.startswith("RESULT ")]
            if not line:
                raise RuntimeError(f"driver produced no RESULT\n{p.stdout}\n{p.stderr}")
            return json.loads(line[-1][len("RESULT "):])

        step("stdio handshake + tool calls against the installed server")
        exercise(session, py, [server_py], "installed project")

        step("opt-in surface")
        names = sorted(session(py, [server_py, "--enable-orchestrator-tools"], [])["tools"])
        check("agentflow_accept_task" in names,
              f"--enable-orchestrator-tools exposes accept ({names})")

        step("packaged entry: agentflow --project <dir> mcp")
        out = session(af, ["--project", proj, "mcp"], [("agentflow_status", {})])
        r = out["calls"][0]["payload"]
        check(r.get("ok") is True, f"agentflow mcp through the packaged CLI -> {r}")
    finally:
        if os.environ.get("AGENTFLOW_MCP_KEEP") != "1":
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"kept {tmp}")
    return report()


def report() -> int:
    if FAIL:
        print(f"\nFAILED ({len(FAIL)}):", flush=True)
        for f in FAIL:
            print("  - " + f)
        return 1
    print("\ncheck_mcp: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
