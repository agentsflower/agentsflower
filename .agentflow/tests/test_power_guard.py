"""power_guard.py (T-080): the bounded worker's process-scoped execution request against automatic
idle system sleep. The Windows API is mocked here so the suite stays portable; the live probe is one
of the task's Checks. Worker integration is proven through a real fake-worker launch: the attempt
record and its log carry the guard outcome durably, and nothing is pretended when it fails."""
import json
import os
import subprocess
import sys
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_endcheck  # noqa: E402

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import power_guard  # noqa: E402
import run_task  # noqa: E402


def fake_tool(tmp, name, body_cmd, body_sh):
    """A fake worker CLI: .cmd on Windows, executable .sh elsewhere."""
    if os.name == "nt":
        p = Path(tmp) / f"{name}.cmd"
        p.write_text("@echo off\r\n" + body_cmd + "\r\n", encoding="ascii")
        return p
    p = Path(tmp) / f"{name}.sh"
    p.write_text("#!/bin/sh\n" + body_sh + "\n", encoding="ascii")
    p.chmod(0o755)
    return p


def past(seconds=0):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


class PowerGuardApiTests(unittest.TestCase):
    """The Windows API, mocked: flags, return handling and the POSIX no-op."""

    def _windows(self, *returns):
        """Patch the platform to Windows and kernel32 to a mock answering `returns` in order."""
        k = MagicMock()
        k.SetThreadExecutionState.side_effect = list(returns)
        return (patch.object(power_guard, "_windows", return_value=True),
                patch.object(power_guard, "_kernel32", return_value=k), k)

    def test_acquire_holds_system_execution_never_display_or_away(self):
        """P-01/P-03: the request is ES_CONTINUOUS|ES_SYSTEM_REQUIRED only - the display is never
        held on and away mode is never requested."""
        w, kpatch, k = self._windows(power_guard.ES_CONTINUOUS)
        with w, kpatch:
            held, detail = power_guard.acquire()
        self.assertTrue(held, detail)
        flags = k.SetThreadExecutionState.call_args[0][0]
        self.assertEqual(flags, power_guard.ES_CONTINUOUS | power_guard.ES_SYSTEM_REQUIRED)
        self.assertFalse(flags & power_guard.ES_DISPLAY_REQUIRED, "the display is never held on")
        self.assertFalse(flags & power_guard.ES_AWAYMODE_REQUIRED, "away mode is never requested")
        self.assertIn("0x80000000", detail)

    def test_acquire_failure_is_reported_not_pretended(self):
        """P-02: a 0 from the API means failure - held=False with the reason, never a fake success."""
        w, kpatch, _k = self._windows(0)
        with w, kpatch:
            held, detail = power_guard.acquire()
        self.assertFalse(held)
        self.assertIn("failed", detail)

    def test_release_clears_to_continuous(self):
        """P-01: release restores ES_CONTINUOUS alone - the request ends with the worker."""
        w, kpatch, k = self._windows(power_guard.ES_CONTINUOUS | power_guard.ES_SYSTEM_REQUIRED)
        with w, kpatch:
            ok, detail = power_guard.release()
        self.assertTrue(ok, detail)
        k.SetThreadExecutionState.assert_called_once_with(power_guard.ES_CONTINUOUS)

    def test_release_failure_is_reported(self):
        """P-02: a failed release is reported the same honest way."""
        w, kpatch, _k = self._windows(0)
        with w, kpatch:
            ok, detail = power_guard.release()
        self.assertFalse(ok)
        self.assertIn("failed", detail)

    def test_posix_is_a_noop(self):
        """P-02: off Windows nothing is requested or released and kernel32 is never touched."""
        with patch.object(power_guard, "_windows", return_value=False), \
                patch.object(power_guard, "_kernel32") as km:
            held, detail = power_guard.acquire()
            self.assertFalse(held)
            self.assertIn("not Windows", detail)
            self.assertFalse(power_guard.release()[0])
            km.assert_not_called()


class PowerGuardWorkerTests(unittest.TestCase):
    """The guard inside a real managed worker attempt (fake tool, no real model calls)."""

    def setUp(self):
        test_endcheck.WorktreeCopyTests.setUp(self)  # temp repo root "p" + worktree self.wt on t-001-probe
        self.flow = self.root / ".agentflow"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        self.env.update(AGENTFLOW_PYTHON=sys.executable, PYTHONUTF8="1",
                        AGENTFLOW_MACHINE_STATE_DIR=str(Path(self.tmp.name) / "machine"),
                        AGENTFLOW_DEVIN_MODEL_PROBE="on")  # opt into the built-in audited inference probe
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env["PATH"]
        self.env.update(GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid")
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1",
                  "--role", "developer", "--tool", "devin", "--status", "ready")
        self.rt_dir = self.flow / "tasks" / ".runtime"
        self.rt_dir.mkdir(exist_ok=True)
        self.rt_file = self.rt_dir / "T-001.json"

    def tearDown(self):
        for _ in range(10):
            try:
                test_endcheck.WorktreeCopyTests.tearDown(self)
                return
            except OSError:
                time.sleep(0.5)

    def tool(self, name, *args):
        r = subprocess.run([sys.executable, str(self.flow / "tools" / name), *args],
                           cwd=self.root, env=self.env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def launch(self, *args, env=None, timeout=45):
        return subprocess.run([sys.executable, str(self.flow / "tools" / "run_task.py"), *args],
                              cwd=self.root, env={**self.env, **(env or {})},
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout)

    def attempt(self):
        return json.loads(self.rt_file.read_text(encoding="utf-8-sig"))["attempts"][-1]

    def wait_state(self, want, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            a = self.attempt()
            if a["status"] == want:
                return a
            time.sleep(0.2)
        self.fail(f"attempt did not reach '{want}': {self.attempt()}")

    def fake_devin(self, cmd, sh, probe="ok"):
        """A fake devin CLI; `probe` answers the built-in model check (argv[1] is its fixed prompt)."""
        pc = {"ok": 'if "%~2"=="reply with the single word ok" exit /b 0\r\n',
              "deny": 'if "%~2"=="reply with the single word ok" exit /b 4\r\n'}.get(probe, "")
        ps = {"ok": 'if [ "$2" = "reply with the single word ok" ]; then exit 0; fi\n',
              "deny": 'if [ "$2" = "reply with the single word ok" ]; then exit 4; fi\n'}.get(probe, "")
        self.env["AGENTFLOW_DEVIN"] = str(fake_tool(self.tmp.name, "fake-devin", pc + cmd, ps + sh))

    def seed(self, tid, attempt):
        (self.rt_dir / f"{tid}.json").write_text(
            json.dumps({"taskId": tid, "attempts": [attempt]}), encoding="utf-8")

    def test_worker_holds_and_releases_the_guard_for_its_lifetime(self):
        """P-01/P-03: a real managed attempt acquires the OS request before the tool runs and
        releases it after exit - recorded durably in the attempt log and on the attempt record."""
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("exited")
        self.assertEqual(a["powerGuard"]["held"], os.name == "nt")
        self.assertTrue(a["powerGuard"]["detail"])
        log = Path(a["log"]).read_text(encoding="utf-8", errors="replace")
        self.assertIn("power guard:", log)
        self.assertIn("power guard release", log)

    def test_guard_releases_when_the_worker_run_raises(self):
        """P-01: an exception inside the worker still releases a held request (the finally path) -
        acquire then release, in that order, and the record carries the outcome."""
        log = Path(self.tmp.name) / "attempt.log"
        log.write_text("", encoding="utf-8")
        self.seed("T-001", {"n": 1, "taskId": "T-001", "tool": "devin", "manual": False,
                            "status": "running", "startedAt": past(0), "log": str(log),
                            "workdir": str(self.wt)})
        calls = []

        def fake_gate(cmd, tid, more=()):
            return {"violations": []} if cmd == "endcheck" else {
                "id": "T-001", "role": "developer", "workdir": str(self.wt), "checkouts": [],
                "setup": [], "env": {}, "target": "local", "prompt": "p", "model": None,
                "effort": None, "resume": None}

        with patch.object(run_task, "RT_DIR", self.rt_dir), \
                patch.object(run_task, "invoke_gate", side_effect=fake_gate), \
                patch.object(run_task.power_guard, "acquire",
                             side_effect=lambda: calls.append("acquire") or (True, "mock held")), \
                patch.object(run_task.power_guard, "release",
                             side_effect=lambda: calls.append("release") or (True, "mock released")), \
                patch.object(run_task, "run_logged", side_effect=RuntimeError("boom")):
            self.assertEqual(run_task.cmd_worker("T-001", "devin"), 0)
        self.assertEqual(calls, ["acquire", "release"])
        a = self.attempt()
        self.assertTrue(a["powerGuard"]["held"])
        self.assertEqual(a["stopReason"], "environment")

    def test_a_failed_acquire_is_on_the_record_not_hidden(self):
        """P-02: the API failing inside the worker leaves held=False with the reason on the
        attempt record - the launcher never pretends the sleep protection exists."""
        log = Path(self.tmp.name) / "attempt.log"
        log.write_text("", encoding="utf-8")
        self.seed("T-001", {"n": 1, "taskId": "T-001", "tool": "devin", "manual": False,
                            "status": "running", "startedAt": past(0), "log": str(log),
                            "workdir": str(self.wt)})

        def fake_gate(cmd, tid, more=()):
            return {"violations": []} if cmd == "endcheck" else {
                "id": "T-001", "role": "developer", "workdir": str(self.wt), "checkouts": [],
                "setup": [], "env": {}, "target": "local", "prompt": "p", "model": None,
                "effort": None, "resume": None}

        with patch.object(run_task, "RT_DIR", self.rt_dir), \
                patch.object(run_task, "invoke_gate", side_effect=fake_gate), \
                patch.object(run_task.power_guard, "acquire",
                             return_value=(False, "SetThreadExecutionState failed (returned 0)")), \
                patch.object(run_task.power_guard, "release") as rel, \
                patch.object(run_task, "run_logged", return_value=(0, False)):
            self.assertEqual(run_task.cmd_worker("T-001", "devin"), 0)
        rel.assert_not_called()   # nothing was held, so nothing is released
        a = self.attempt()
        self.assertFalse(a["powerGuard"]["held"])
        self.assertIn("failed", a["powerGuard"]["detail"])
        self.assertIn("power guard: SetThreadExecutionState failed",
                      log.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
