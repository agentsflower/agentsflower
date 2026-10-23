"""The launcher's model flags and wrapper compatibility.
Regression: a machine default `--model` plus a task `Model:` made Devin exit ("--model cannot be used multiple times").
The flag logic lives in run_task.py (Python); run-task.ps1 only translates parameters and delegates."""
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import run_task  # noqa: E402


def clean_args(**update):
    cleared = {f"AGENTFLOW_{t.upper()}_ARGS": "" for t in ("codex", "claude", "agy", "devin")}
    cleared.update(update)
    return patch.dict(os.environ, cleared)


class LauncherArgsTests(unittest.TestCase):
    def worker_argv(self, tool, model, effort, env_args):
        with clean_args(**{f"AGENTFLOW_{tool.upper()}_ARGS": env_args} if env_args else {}):
            return run_task.tool_argv(tool, "developer", "<prompt>", model, effort)

    def test_task_model_replaces_machine_default(self):
        args = self.worker_argv("devin", "swe-2-max", None, "--model swe-2-high --foo bar")
        self.assertEqual(args.count("--model"), 1)
        self.assertEqual(args[args.index("--foo"):], ["--foo", "bar", "--model", "swe-2-max"])

    def test_machine_default_stays_without_task_model(self):
        args = self.worker_argv("devin", None, None, "--model swe-2-high")
        self.assertEqual(args[-2:], ["--model", "swe-2-high"])

    def test_codex_effort_from_task_wins(self):
        with clean_args(AGENTFLOW_CODEX_ARGS="-c model_reasoning_effort=xhigh -c x=1"):
            args = run_task.tool_argv("codex", "developer", "<prompt>", "gpt-6.1-sol", "medium")
        self.assertNotIn("model_reasoning_effort=xhigh", args)
        self.assertEqual(args, ["exec", "-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=medium",
                                "-c", "x=1", "--sandbox", "danger-full-access", "<prompt>"])

    def test_codex_default_effort_kept_without_task_effort(self):
        with clean_args(AGENTFLOW_CODEX_ARGS="-c model_reasoning_effort=xhigh"):
            args = run_task.tool_argv("codex", "developer", "<prompt>", None, None)
        self.assertIn("model_reasoning_effort=xhigh", args)

    def test_agy_model_and_effort(self):
        args = self.worker_argv("agy", "m1", "high", "--effort low")
        self.assertEqual(args[-4:], ["--model", "m1", "--effort", "high"])

    def test_claude_model_and_effort(self):
        args = self.worker_argv("claude", "opus", "xhigh", "--effort medium")
        self.assertEqual(args[-4:], ["--model", "opus", "--effort", "xhigh"])

    def test_wrapper_delegates_and_preserves_the_exit_code(self):
        """run-task.ps1 translates old parameters and delegates to run_task.py (skipped where pwsh is missing)."""
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell unavailable")
        env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        env["AGENTFLOW_PYTHON"] = sys.executable
        r = subprocess.run([shell, "-NoProfile", "-File", str(FLOW / "tools" / "run-task.ps1"), "T-999"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertNotEqual(r.returncode, 0)  # the task does not exist: the delegated call fails, not the wrapper
        self.assertNotIn("parameter", (r.stdout + r.stderr).lower())


if __name__ == "__main__":
    unittest.main()
