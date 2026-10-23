#!/usr/bin/env python3
"""AgentFlow MCP server (optional).

Exposes deterministic project operations over the Model Context Protocol
using the official `mcp` SDK (PyPI `mcp` 2.x). The core template stays
stdlib-only: without the SDK this script exits with a clear diagnostic
instead of falling back to a homegrown protocol. Install it with
`pip install "agentflow-sdlc[mcp]"` or `pip install "mcp>=2.3,<3"`.

  python .agentflow/tools/mcp_server.py
  python .agentflow/tools/mcp_server.py --enable-orchestrator-tools

The script's own location inside <project>/.agentflow/tools/ defines the
project root it serves; it reads task contracts, the ledger and VERSION in
place and runs gate.py / accept.py as argument-list subprocesses (no shell).

`--enable-orchestrator-tools` additionally exposes `agentflow_accept_task`,
which invokes accept.py verbatim. The flag is an operator control of this
server's surface, not proof of the caller's role or identity: any MCP client
that can reach the server can call whatever it exposes.

stdout carries protocol traffic only; diagnostics go to stderr.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
from paths import FLOW_ROOT, REPO_ROOT  # noqa: E402
import ledger  # noqa: E402

TASK_ID = re.compile(r"T-\d{1,4}")
GATE_CHECKS = ("verify", "preflight", "endcheck", "task")  # gate.py subcommands that take a task id
ROLES = ("developer", "tester", "deployer", "orchestrator")
LIMIT_MIN, LIMIT_MAX = 1, 200
LOG_LIMIT = 20000  # bounded tool output: a gate/accept log tail, not a stream

SDK_MISSING = (
    "the optional MCP SDK is not installed. Install it with "
    "`pip install \"agentflow-sdlc[mcp]\"` or `pip install \"mcp>=2.3,<3\"` "
    "(the core AgentFlow tools do not need it; there is no fallback server)."
)


class SdkMissing(Exception):
    pass


def version() -> str:
    v = FLOW_ROOT / "VERSION"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "?"


def _err(msg):
    return {"ok": False, "error": msg}


def _clip(s: str) -> str:
    return s if len(s) <= LOG_LIMIT else s[:LOG_LIMIT] + f"\n... [{len(s) - LOG_LIMIT} chars truncated]"


def _valid_task_id(value) -> bool:
    return isinstance(value, str) and TASK_ID.fullmatch(value) is not None


def _task_file(tid: str) -> Path | None:
    tasks = FLOW_ROOT / "tasks"
    hits = sorted(tasks.glob(f"{tid}-*.md")) + ([tasks / f"{tid}.md"] if (tasks / f"{tid}.md").is_file() else [])
    return hits[0] if hits else None


def _ledger_rows() -> list[dict]:
    path = ledger.ledger_path()
    if not path.exists():
        return []
    _, cols, rows, _, _ = ledger.load(path)
    return [dict(zip(cols, r)) for r in rows]


def _run(script: str, args: list[str], timeout=600):
    p = subprocess.run([sys.executable, str(TOOLS_DIR / script), *args],
                       cwd=REPO_ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, _clip((p.stdout + p.stderr).strip())


def status() -> dict:
    """Read-only project snapshot: AgentFlow version and open ledger tasks."""
    rows = _ledger_rows()
    open_tasks = [{"id": r["ID"], "role": r["Role"], "status": r["Status"], "title": r["Title"]}
                  for r in rows if r["Status"] in ("in progress", "review", "blocked")]
    return {"ok": True, "agentflow_version": version(), "project": REPO_ROOT.name,
            "tasks": {"total": len(rows), "open": open_tasks}}


def get_task(task_id) -> dict:
    """Read one Task File (.agentflow/tasks/T-NNN-*.md) verbatim."""
    if not _valid_task_id(task_id):
        return _err(f"bad task id {task_id!r}: expected T-NNN")
    f = _task_file(task_id)
    if not f:
        return _err(f"no Task File for {task_id}")
    return {"ok": True, "task_id": task_id, "file": f.relative_to(REPO_ROOT).as_posix(),
            "content": f.read_text(encoding="utf-8-sig")}


def run_gate(task_id, check_type) -> dict:
    """Run an existing gate.py check for a task (mutates project state as the gate does;
    NOT read-only). Returns the structured outcome, exit status and bounded log."""
    if not _valid_task_id(task_id):
        return _err(f"bad task id {task_id!r}: expected T-NNN")
    if check_type not in GATE_CHECKS:
        return _err(f"bad check_type {check_type!r}: expected one of {', '.join(GATE_CHECKS)}")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.json"
        code, log = _run("gate.py", [check_type, task_id, "--out", str(out)])
        evidence = None
        if out.is_file():
            try:
                evidence = json.loads(out.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                evidence = None
    return {"ok": code == 0, "exit_code": code, "check": check_type, "task_id": task_id,
            "evidence": evidence, "log": log}


def query_ledger(limit=50, filter_role="") -> dict:
    """Read the Task Ledger: the last `limit` rows, optionally filtered by role."""
    if not isinstance(limit, int) or isinstance(limit, bool) or not (LIMIT_MIN <= limit <= LIMIT_MAX):
        return _err(f"bad limit {limit!r}: expected an integer {LIMIT_MIN}..{LIMIT_MAX}")
    if filter_role and filter_role not in ROLES:
        return _err(f"bad filter_role {filter_role!r}: expected one of {', '.join(ROLES)}")
    rows = _ledger_rows()
    if filter_role:
        rows = [r for r in rows if r["Role"] == filter_role]
    return {"ok": True, "count": min(limit, len(rows)), "tasks": rows[-limit:]}


def accept_task(task_id) -> dict:
    """Orchestrator tool (only exposed with --enable-orchestrator-tools): invoke
    accept.py verbatim - verify, merge, ledger, cleanup."""
    if not _valid_task_id(task_id):
        return _err(f"bad task id {task_id!r}: expected T-NNN")
    code, log = _run("accept.py", [task_id])
    return {"ok": code == 0, "exit_code": code, "task_id": task_id, "log": log}


def build_server(enable_orchestrator: bool = False):
    """Create the MCPServer and register the tools. Raises SdkMissing when the
    optional `mcp` package is not installed."""
    try:
        from mcp.server import MCPServer
        from mcp_types import ToolAnnotations
    except ImportError as e:
        raise SdkMissing(SDK_MISSING) from e

    server = MCPServer(
        "agentflow",
        version=version(),
        instructions=("AgentFlow task-contract workflow. Read-only tools inspect the project; "
                      "agentflow_run_gate mutates state like gate.py and is not read-only."),
    )
    ro = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)
    mut = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False)

    @server.tool(name="agentflow_status", annotations=ro)
    def _status() -> dict:
        """AgentFlow version and open tasks of the project this server was started in."""
        return status()

    @server.tool(name="agentflow_get_task", annotations=ro)
    def _get_task(task_id: str) -> dict:
        """Read one Task File by id (T-NNN)."""
        return get_task(task_id)

    @server.tool(name="agentflow_run_gate", annotations=mut)
    def _run_gate(task_id: str, check_type: str) -> dict:
        """Run gate.py for a task: check_type is verify, preflight, endcheck or task.
        Executes the real gate (writes runtime evidence); not read-only."""
        return run_gate(task_id, check_type)

    @server.tool(name="agentflow_query_ledger", annotations=ro)
    def _query_ledger(limit: int = 50, filter_role: str = "") -> dict:
        """Last `limit` Task Ledger rows (1..200), optionally filtered by role."""
        return query_ledger(limit, filter_role)

    if enable_orchestrator:
        @server.tool(name="agentflow_accept_task", annotations=mut)
        def _accept_task(task_id: str) -> dict:
            """Accept a completed task: runs accept.py (verify, merge, ledger, cleanup).
            Available only because this server was started with
            --enable-orchestrator-tools (an operator control, not a role check)."""
            return accept_task(task_id)

    return server


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--enable-orchestrator-tools", action="store_true",
                    help="also expose agentflow_accept_task (accept.py). This is an operator "
                         "control of the server surface, not proof of the caller's role.")
    a = ap.parse_args(argv)
    try:
        server = build_server(a.enable_orchestrator_tools)
    except SdkMissing as e:
        print(f"agentflow mcp: {e}", file=sys.stderr)
        return 2
    server.run("stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
