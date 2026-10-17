"""cli.py routing: project discovery, role validation, passthrough argv and exit codes."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import cli  # noqa: E402

TASK_DEV = """# T-001: sample

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 1
Depends on: none
Branch: t-001-sample
Worktree: /tmp/x

## Goal
x
"""
TASK_DEP = TASK_DEV.replace("Role: developer", "Role: deployer").replace("Tool: devin", "Tool: none")


def make_project(base: Path) -> Path:
    flow = base / ".agentflow"
    (flow / "docs").mkdir(parents=True)
    (flow / "docs" / "ai-handoff-protocol.md").write_text("# p\n", encoding="utf-8")
    (flow / "template-source.json").write_text("{}\n", encoding="utf-8")
    (flow / "tools").mkdir()
    for s in ("run_task.py", "gate.py", "accept.py", "ledger.py"):
        (flow / "tools" / s).write_text("# tool\n", encoding="utf-8")
    (flow / "tasks").mkdir()
    return base


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = make_project(Path(self.tmp.name) / "proj")

    def test_find_root_walks_up(self):
        nested = self.root / "a" / "b c"
        nested.mkdir(parents=True)
        self.assertEqual(cli.find_root(nested), self.root.resolve())

    def test_state_dir_also_marks_project(self):
        (self.root / ".agentflow" / "template-source.json").unlink()
        (self.root / ".agentflow" / "state").mkdir()
        self.assertEqual(cli.find_root(self.root), self.root.resolve())

    def test_no_protocol_no_state_is_not_a_project(self):
        bare = Path(self.tmp.name) / "bundle"
        (bare / ".agentflow" / "docs").mkdir(parents=True)
        (bare / ".agentflow" / "docs" / "ai-handoff-protocol.md").write_text("# p\n", encoding="utf-8")
        self.assertIsNone(cli.find_root(bare))

    def test_passthrough_without_project_fails_closed(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = cli.main(["--project", str(Path(self.tmp.name) / "nowhere"), "ledger", "show"])
        self.assertEqual(code, 2)
        self.assertIn("no installed AgentFlow project", err.getvalue())


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = make_project(Path(self.tmp.name) / "proj")
        self.calls = []
        self.fake_call = patch.object(cli.subprocess, "call",
                                      side_effect=lambda argv, cwd=None: self.calls.append((argv, cwd)) or 0)
        self.fake_call.start()
        self.addCleanup(self.fake_call.stop)

    def write_task(self, text=TASK_DEV, name="T-001-sample.md"):
        (self.root / ".agentflow" / "tasks" / name).write_text(text, encoding="utf-8")

    def run_cli(self, *argv):
        return cli.main(["--project", str(self.root), *argv])

    def test_role_mismatch_starts_nothing(self):
        self.write_task()
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = self.run_cli("run", "T-001", "--role", "tester")
        self.assertEqual(code, 1)
        self.assertIn("refused", err.getvalue())
        self.assertFalse(self.calls)

    def test_run_launches_task_tool(self):
        self.write_task()
        self.assertEqual(self.run_cli("run", "T-001", "--role", "developer"), 0)
        argv, cwd = self.calls[0]
        self.assertEqual(argv[1:], [str(self.root / ".agentflow" / "tools" / "run_task.py"), "T-001", "devin"])
        self.assertEqual(cwd, self.root)

    def test_deployer_is_manual_only(self):
        self.write_task(TASK_DEP)
        self.assertEqual(self.run_cli("run", "T-001", "--role", "deployer"), 0)
        argv, _ = self.calls[0]
        self.assertEqual(argv[2:], ["T-001", "--manual"])

    def test_missing_task_file(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_cli("run", "T-009", "--role", "developer"), 1)
        self.assertFalse(self.calls)

    def test_missing_role_field(self):
        self.write_task(TASK_DEV.replace("Role: developer\n", ""))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.run_cli("run", "T-001", "--role", "developer"), 1)
        self.assertFalse(self.calls)


class PassthroughTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = make_project(Path(self.tmp.name) / "proj")
        self.calls = []
        self.fake_call = patch.object(cli.subprocess, "call",
                                      side_effect=lambda argv, cwd=None: self.calls.append((argv, cwd)) or 7)
        self.fake_call.start()
        self.addCleanup(self.fake_call.stop)

    def run_cli(self, *argv):
        return cli.main(["--project", str(self.root), *argv])

    def test_gate_passthrough_argv_and_exit_code(self):
        self.assertEqual(self.run_cli("gate", "verify", "T-001"), 7)
        argv, _ = self.calls[0]
        self.assertEqual(argv[1:], [str(self.root / ".agentflow" / "tools" / "gate.py"), "verify", "T-001"])

    def test_done_routes_to_gate_done(self):
        self.assertEqual(self.run_cli("done", "T-001"), 7)
        argv, _ = self.calls[0]
        self.assertEqual(argv[1:], [str(self.root / ".agentflow" / "tools" / "gate.py"), "done", "T-001"])

    def test_ledger_and_accept_passthrough(self):
        self.assertEqual(self.run_cli("ledger", "set", "T-001", "--status", "ready"), 7)
        self.assertEqual(self.run_cli("accept", "T-001", "--dry-run"), 7)
        self.assertEqual(self.calls[0][0][1:], [str(self.root / ".agentflow" / "tools" / "ledger.py"),
                                                "set", "T-001", "--status", "ready"])
        self.assertEqual(self.calls[1][0][1:], [str(self.root / ".agentflow" / "tools" / "accept.py"),
                                                "T-001", "--dry-run"])

    def test_dashboard_open_after_success(self):
        out = self.root / ".agentflow" / "dashboard" / "out" / "index.html"
        out.parent.mkdir(parents=True)
        out.write_text("<html>", encoding="utf-8")
        with patch.object(cli.webbrowser, "open") as op, \
                patch.object(cli.subprocess, "call", return_value=0) as call:
            self.assertEqual(cli.main(["--project", str(self.root), "dashboard", "--open"]), 0)
        self.assertEqual(call.call_args[0][0][1],
                         str(self.root / ".agentflow" / "dashboard" / "build.py"))
        op.assert_called_once_with(out.as_uri())

    def test_install_uses_sibling_or_bundled_installer(self):
        with patch.object(cli.subprocess, "call", return_value=0) as call:
            self.assertEqual(cli.main(["install", "some proj", "--update", "--dry-run"]), 0)
        argv = call.call_args[0][0]
        self.assertEqual(argv[1], str(cli.INSTALLER))
        self.assertEqual(argv[2:], ["some proj", "--update", "--dry-run"])  # argument boundary kept
        self.assertTrue(cli.INSTALLER.is_file())  # checkout: .agentflow/tools/install.py


class FrontMatterTests(unittest.TestCase):
    def test_help_and_version(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as e:
                cli.main(["--help"])
        self.assertEqual(e.exception.code, 0)
        self.assertIn("agentflow", out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as e:
                cli.main(["--version"])
        self.assertEqual(e.exception.code, 0)
        self.assertIn(cli.version(), out.getvalue())


if __name__ == "__main__":
    unittest.main()
