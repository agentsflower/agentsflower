"""Unified AgentFlow command line: one entry point for the template's tools.

Source checkout (this file sits in <repo>/.agentflow/tools/):

  python .agentflow/tools/cli.py --help

Installed package (`pip install agentflow-sdlc` provides the `agentflow` command
and bundles the whole template under agentflow/template/):

  agentflow --version
  agentflow install <project> [--update] [--dry-run] [--inside-repo]
                            [--workspace] [--repos a,b] [--git-init]
  agentflow run T-NNN --role <developer|tester|deployer> [--project <dir>]
  agentflow gate <task|preflight|endcheck|verify|done|stage> ... [--project <dir>]
  agentflow done T-NNN [--project <dir>]     the single completion check (gate.py done)
  agentflow accept T-NNN [--dry-run] [--project <dir>]
  agentflow ledger <add|set|approve|show> ... [--project <dir>]
  agentflow mcp [--enable-orchestrator-tools] [--project <dir>]
  agentflow dashboard [--open] [--project <dir>]

Project commands find the project root by walking up from --project (or the
current directory) to a folder whose `.agentflow/` is an installed one: the
protocol file plus `template-source.json` or `state/`. Bundled template data has
no state/, tasks or template-source.json, so project commands never operate on
the package's own copy inside site-packages.

`run` reads the Role and Tool fields from the Task File: --role must match the
Task File's Role or nothing is started, and the deployer always launches in
--manual mode (the launcher itself refuses an unattended deployer).

Every operation is a subprocess without a shell; the child's exit code is this
command's exit code, and arguments are passed through as a list, never re-parsed.
"""
import argparse
import re
import subprocess
import sys
import webbrowser
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
# <template>/.agentflow in a checkout, agentflow/template/ in an installed package
TEMPLATE_FLOW = TOOLS_DIR.parent
INSTALLER = TOOLS_DIR / "install.py"

TASK_TOOLS = ("codex", "claude", "agy", "devin")  # run_task.py positional choices


def version():
    v = TEMPLATE_FLOW / "VERSION"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "?"


def flow_dir(root: Path) -> Path:
    if (root / ".agentsflower").is_dir():
        return root / ".agentsflower"
    return root / ".agentflow"


def is_project_root(d: Path) -> bool:
    for name in (".agentsflower", ".agentflow"):
        flow = d / name
        if (flow / "docs" / "ai-handoff-protocol.md").is_file():
            if (flow / "state").is_dir() or (flow / "template-source.json").is_file():
                return True
    return False


def find_root(start: Path) -> Path | None:
    d = start.resolve()
    if d.is_file():
        d = d.parent
    for cand in (d, *d.parents):
        if is_project_root(cand):
            return cand
    return None


def task_file(root: Path, tid: str) -> Path | None:
    tasks = flow_dir(root) / "tasks"
    for f in sorted(tasks.glob(f"{tid}*.md")):
        if f.stem == tid or f.stem.startswith(tid + "-"):
            return f
    return None


def task_field(text: str, name: str) -> str:
    m = re.search(rf"^{re.escape(name)}:[ \t]*([^<\s]+)", text, re.M)
    return m.group(1).strip() if m else ""


def run_tool(root: Path, script: str, args, cwd=None) -> int:
    path = flow_dir(root) / "tools" / script if root else TOOLS_DIR / script
    if not path.is_file():
        print(f"agentflow: missing tool script {path}", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(path), *args], cwd=cwd or root)


def cmd_install(args) -> int:
    if not INSTALLER.is_file():
        print(f"agentflow: no installer at {INSTALLER}", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(INSTALLER), *args])


def cmd_run(a) -> int:
    root = find_root(a.project)
    if not root:
        print(f"agentflow: no installed AgentFlow project found at or above {a.project}", file=sys.stderr)
        return 2
    tf = task_file(root, a.task)
    if not tf:
        print(f"agentflow: no Task File {a.task}*.md under {root / '.agentflow' / 'tasks'}", file=sys.stderr)
        return 1
    text = tf.read_text(encoding="utf-8")
    role = task_field(text, "Role")
    if not role:
        print(f"agentflow: {tf.name} has no Role: field", file=sys.stderr)
        return 1
    if role != a.role:
        print(f"agentflow: {tf.name} is a {role} task; --role {a.role} refused. Nothing was started.",
              file=sys.stderr)
        return 1
    tool = task_field(text, "Tool").split(",")[0].strip()
    if role == "deployer":
        argv = [a.task, "--manual"]  # the launcher starts no deployer unattended
    else:
        if tool not in TASK_TOOLS:
            print(f"agentflow: {tf.name} names tool '{tool or '?'}', expected one of "
                  f"{', '.join(TASK_TOOLS)}", file=sys.stderr)
            return 1
        argv = [a.task, tool]
    return run_tool(root, "run_task.py", argv)


def cmd_passthrough(a, script) -> int:
    root = find_root(a.project)
    if not root:
        print(f"agentflow: no installed AgentFlow project found at or above {a.project}", file=sys.stderr)
        return 2
    return run_tool(root, script, a.args)


def cmd_done(a) -> int:
    root = find_root(a.project)
    if not root:
        print(f"agentflow: no installed AgentFlow project found at or above {a.project}", file=sys.stderr)
        return 2
    return run_tool(root, "gate.py", ["done", a.task, *a.args])


def cmd_dashboard(a) -> int:
    root = find_root(a.project)
    if not root:
        print(f"agentflow: no installed AgentFlow project found at or above {a.project}", file=sys.stderr)
        return 2
    code = subprocess.call([sys.executable, str(flow_dir(root) / "dashboard" / "build.py")], cwd=root)
    if code == 0 and a.open:
        page = flow_dir(root) / "dashboard" / "out" / "index.html"
        if page.is_file():
            webbrowser.open(page.as_uri())
    return code


def cmd_studio(a) -> int:
    root = find_root(a.project)
    if not root:
        print(f"agentsflower: no installed AgentsFlower project found at or above {a.project}", file=sys.stderr)
        return 2
    args = []
    if getattr(a, "port", None):
        args.extend(["--port", str(a.port)])
    if getattr(a, "open", False):
        args.append("--open")
    return run_tool(root, "studio.py", args)



def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="agentflow", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"agentflow {version()}")
    ap.add_argument("--project", type=Path, default=None,
                    help="project dir or any dir inside it (default: current directory); "
                         "place before the subcommand")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("install", help="install or update AgentFlow in a project (bundled template)")
    p.add_argument("args", nargs=argparse.REMAINDER,
                   help="installer arguments: <target> [--update] [--dry-run] [--inside-repo] "
                        "[--workspace] [--repos a,b] [--git-init] [--mcp [--mcp-client claude|cursor]]")

    p = sub.add_parser("run", help="start the worker of a Task File (role must match it)")
    p.add_argument("task", help="task id T-NNN")
    p.add_argument("--role", required=True, choices=("developer", "tester", "deployer"),
                   help="must equal the Task File's Role: field; a mismatch starts nothing")
    p.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="project dir or any dir inside it (default: current directory)")

    for name, script in (("gate", "gate.py"), ("accept", "accept.py"), ("ledger", "ledger.py"),
                         ("mcp", "mcp_server.py"), ("hooks", "hooks.py"), ("graft", "graft.py")):
        p = sub.add_parser(name, help=f"pass arguments to .agentflow/tools/{script}")
        p.add_argument("args", nargs=argparse.REMAINDER, help=f"arguments of {script} (see its --help)")
        p.set_defaults(script=script)

    p = sub.add_parser("done", help="the single completion check for a Task File (gate.py done)")
    p.add_argument("task", help="task id T-NNN")
    p.add_argument("args", nargs=argparse.REMAINDER, help="further gate.py done arguments, e.g. --out f.json")
    p.add_argument("--project", type=Path, default=argparse.SUPPRESS,
                   help="project dir or any dir inside it (default: current directory)")

    p = sub.add_parser("dashboard", help="rebuild the task dashboard; --open shows it in a browser")
    p.add_argument("--open", action="store_true", help="open out/index.html after a successful build")
    p.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="project dir or any dir inside it (default: current directory)")

    p = sub.add_parser("studio", help="launch AgentsFlower Studio modern Local Web UI")
    p.add_argument("--port", type=int, default=8888, help="port to bind (default: 8888)")
    p.add_argument("--open", action="store_true", help="open Studio in a browser")
    p.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="project dir or any dir inside it (default: current directory)")

    a = ap.parse_args(argv)
    a.project = a.project or Path.cwd()
    if a.cmd == "install":
        return cmd_install(a.args)
    if a.cmd == "run":
        return cmd_run(a)
    if a.cmd == "done":
        return cmd_done(a)
    if a.cmd == "dashboard":
        return cmd_dashboard(a)
    if a.cmd == "studio":
        return cmd_studio(a)
    return cmd_passthrough(a, a.script)


if __name__ == "__main__":
    sys.exit(main())
