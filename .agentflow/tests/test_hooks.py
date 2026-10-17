"""hooks.py: the opt-in Codex Stop-hook adapter - a runtime surface check before enabling, bounded
actionable failure text, and a fallback to the runner/acceptance path. It never spawns workers,
never accepts a result and never treats a stop/limit/blocker as a reason to continue."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_done_gate as dg  # noqa: E402  # new_repo, task_text, sh, Base fixture helpers

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import hooks  # noqa: E402


def fake_codex(tmp, version="0.118.0", features=None):
    """A fake codex CLI answering --version and 'features list' (None: no such subcommand)."""
    feat_cmd = "exit /b 2" if features is None else f'echo {features} & exit /b 0'
    feat_sh = "exit 2" if features is None else f'echo "{features}"; exit 0'
    if os.name == "nt":
        p = Path(tmp) / "codex.cmd"
        p.write_text(f'@echo off\r\nif "%~1"=="--version" echo codex-cli {version} & exit /b 0\r\n'
                     f'if "%~1"=="features" ({feat_cmd})\r\nexit /b 2\r\n', encoding="ascii")
        return p
    p = Path(tmp) / "codex.sh"
    p.write_text(f'#!/bin/sh\nif [ "$1" = "--version" ]; then echo "codex-cli {version}"; exit 0; fi\n'
                 f'if [ "$1" = "features" ]; then {feat_sh}; fi\nexit 2\n', encoding="ascii")
    p.chmod(0o755)
    return p


class CodexSurfaceTests(unittest.TestCase):
    """check codex: the installed version and the hook feature surface decide - never the docs."""

    def setUp(self):
        self.tmp = dg.tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_supported_when_the_feature_surface_checks_out(self):
        exe = fake_codex(self.tmp.name, "0.118.0", features="codex_hooks experimental true")
        s = hooks.codex_support(str(exe))
        self.assertTrue(s["supported"], s)
        self.assertEqual(s["version"], "0.118.0")
        self.assertEqual(s["feature"], "codex_hooks")

    def test_new_feature_name_and_stable_stage(self):
        exe = fake_codex(self.tmp.name, "0.134.0", features="hooks stable true")
        s = hooks.codex_support(str(exe))
        self.assertTrue(s["supported"], s)
        self.assertEqual(s["feature"], "hooks")
        self.assertEqual(s["stage"], "stable")

    def test_too_old_or_unverifiable_is_unsupported(self):
        exe = fake_codex(self.tmp.name, "0.100.0")
        s = hooks.codex_support(str(exe))
        self.assertFalse(s["supported"])
        self.assertIn("0.114.0", s["reason"])
        # >= the flag-rename release must prove the renamed surface; an unanswerable probe fails closed
        exe = fake_codex(self.tmp.name, "0.134.0", features=None)
        s = hooks.codex_support(str(exe))
        self.assertFalse(s["supported"])
        # a version-floor release needs no subcommand: codex_hooks is the documented flag
        exe = fake_codex(self.tmp.name, "0.118.0", features=None)
        s = hooks.codex_support(str(exe))
        self.assertTrue(s["supported"], s)
        self.assertEqual(s["feature"], "codex_hooks")

    def test_missing_or_mute_cli_is_unsupported(self):
        s = hooks.codex_support(str(Path(self.tmp.name) / "nope"))
        self.assertFalse(s["supported"])
        exe = fake_codex(self.tmp.name, "garbage")
        s = hooks.codex_support(str(exe))
        self.assertFalse(s["supported"])


class CodexStopTests(dg.Base):
    """codex-stop runs the common completion command and reports; all exits stay 0 - it never
    continues a session, spawns a worker or accepts a result."""

    def hook(self, root, *args, env=None, stdin=""):
        e = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        e.update(env or {})
        return subprocess.run([sys.executable, str(root / ".agentflow" / "tools" / "hooks.py"),
                               "codex-stop", *args], cwd=root, env=e, input=stdin,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def manual_attempt(self, root, tid="T-001", workdir="", **kw):
        rt = root / ".agentflow" / "tasks" / ".runtime" / f"{tid}.json"
        state = json.loads(rt.read_text(encoding="utf-8"))
        state["attempts"][-1].update({"status": "running", "manual": True, "tool": "manual",
                                      "workdir": workdir, **kw})
        rt.write_text(json.dumps(state), encoding="utf-8")

    def test_done_pass_reports_the_next_step(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        self.manual_attempt(root, workdir=str(wt))
        r = self.hook(root, stdin=json.dumps({"cwd": str(wt)}))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("PASS", r.stdout)
        self.assertIn("accept.py T-001", r.stdout)

    def test_done_failure_returns_bounded_actionable_text(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root)  # no Result at all: evaluate() lists what is missing
        self.manual_attempt(root, workdir=str(wt))
        r = self.hook(root, stdin=json.dumps({"cwd": str(wt)}))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("FAIL", r.stdout)
        self.assertIn("Outcome", r.stdout)
        self.assertLess(len(r.stdout.splitlines()), 30, "hook output stays bounded")
        self.assertIn("gate.py done T-001", r.stdout)

    def test_a_managed_worker_session_is_inert(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        self.manual_attempt(root, workdir=str(wt))
        r = self.hook(root, env={"AGENTFLOW_ATTEMPT": "T-001#1"})
        self.assertEqual(r.returncode, 0)
        self.assertIn("managed", r.stdout)
        self.assertNotIn("done", r.stdout.lower())

    def test_a_usage_limit_is_never_a_reason_to_continue(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        self.manual_attempt(root, workdir=str(wt), limitHit=True,
                            limitPhrase="you've hit your usage limit", limitKind="quota")
        r = self.hook(root, stdin=json.dumps({"cwd": str(wt)}))
        self.assertEqual(r.returncode, 0)
        self.assertIn("limit", r.stdout.lower())
        self.assertNotIn("PASS", r.stdout)

    def test_a_blocked_task_is_never_a_reason_to_continue(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result="Outcome: blocked\n")
        self.manual_attempt(root, workdir=str(wt))
        r = self.hook(root, stdin=json.dumps({"cwd": str(wt)}))
        self.assertEqual(r.returncode, 0)
        self.assertIn("blocked", r.stdout.lower())
        self.assertNotIn("PASS", r.stdout)

    def test_no_matching_task_falls_back_to_the_runner_path(self):
        root, wt = self.dev_project()
        r = self.hook(root, stdin=json.dumps({"cwd": str(self.base / "elsewhere")}))
        self.assertEqual(r.returncode, 0)
        self.assertIn("run_task.py", r.stdout)  # the normal path is named, not replaced


class CodexEnableTests(unittest.TestCase):
    """enable codex: opt-in only; validates the runtime before printing the manual step, and can
    write the project-local hooks.json itself."""

    def setUp(self):
        self.tmp = dg.tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "project"
        dg.new_repo(self.root)
        flow = self.root / ".agentflow"
        dg.shutil.copytree(FLOW / "tools", flow / "tools", ignore=dg.shutil.ignore_patterns("__pycache__"))
        (flow / "tasks").mkdir(parents=True, exist_ok=True)
        self.exe = fake_codex(self.tmp.name, "0.134.0", features="hooks stable true")

    def tearDown(self):
        self.tmp.cleanup()

    def enable(self, *args, env=None):
        e = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        e.update(env or {})
        return subprocess.run([sys.executable, str(self.root / ".agentflow" / "tools" / "hooks.py"),
                               "enable", "codex", *args], cwd=self.root, env=e,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def test_enable_prints_the_manual_step_without_writing(self):
        r = self.enable(env={"AGENTFLOW_CODEX": str(self.exe)})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Stop", r.stdout)
        self.assertIn("codex-stop", r.stdout)
        self.assertIn("features", r.stdout)   # the feature flag the version needs
        self.assertFalse((self.root / ".codex").exists())  # nothing written without --write

    def test_enable_write_installs_a_project_hook(self):
        r = self.enable("--write", env={"AGENTFLOW_CODEX": str(self.exe)})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cfg = json.loads((self.root / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        entry = cfg["hooks"]["Stop"][0]["hooks"][0]
        self.assertEqual(entry["type"], "command")
        self.assertIn("codex-stop", entry["command"])
        self.assertIn("hooks.py", entry["command"])

    def test_enable_refuses_an_unsupported_runtime(self):
        old = fake_codex(self.tmp.name, "0.100.0")
        r = self.enable(env={"AGENTFLOW_CODEX": str(old)})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unsupported", r.stdout.lower() + r.stderr.lower())
        self.assertFalse((self.root / ".codex").exists())


if __name__ == "__main__":
    unittest.main()
