"""Real direct/manual launches in disposable repositories; no model is invoked."""
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path
import test_endcheck
import gate  # noqa: E402  (tools dir is already on sys.path via test_endcheck)


class LauncherLifecycleTests(unittest.TestCase):
    def setUp(self):
        test_endcheck.WorktreeCopyTests.setUp(self)
        self.flow = self.root / ".agentflow"
        source = Path(__file__).resolve().parents[1]
        shutil.copy(source / "tasks/_template.md", self.flow / "tasks")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        self.env.update(AGENTFLOW_PYTHON=sys.executable,
                        AGENTFLOW_MACHINE_STATE_DIR=str(Path(self.tmp.name) / "machine"), PYTHONUTF8="1",
                        AGENTFLOW_DEVIN_MODEL_PROBE="on")  # opt into the built-in probe; fakes exit 0 anyway
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env["PATH"]
        self.env.update(GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid")
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1",
                  "--role", "developer", "--tool", "devin", "--status", "ready")

    def tearDown(self):
        test_endcheck.WorktreeCopyTests.tearDown(self)

    def tool(self, name, *args):
        r = subprocess.run([sys.executable, str(self.flow / "tools" / name), *args],
                           cwd=self.root, env=self.env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def launch(self, shell, *args):
        return subprocess.run([shell, "-NoProfile", "-File", str(self.flow / "tools/run-task.ps1"),
                               "T-001", *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45)

    def check_manual(self, shell):
        if not shutil.which(shell):
            self.skipTest(shell + " unavailable")
        r = self.launch(shell, "-Manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("in progress", self.tool("ledger.py", "show", "T-001").stdout)
        rt = self.flow / "tasks/.runtime/T-001.json"
        att = json.loads(rt.read_text())["attempts"][-1]
        self.assertEqual((att["status"], att["taskId"]), ("running", "T-001"))
        # Duplicate launch must not create a second attempt.
        self.assertNotEqual(self.launch(shell, "-Manual").returncode, 0)
        self.assertEqual(len(json.loads(rt.read_text())["attempts"]), 1)
        r = self.launch(shell, "-MarkFinished")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self.launch(shell, "-Manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(json.loads(rt.read_text())["attempts"]), 2)

    def test_manual_powershell_5(self):
        self.check_manual("powershell")

    def test_manual_powershell_7(self):
        self.check_manual("pwsh")

    def test_complete_manual_cycle_and_accept(self):
        if not shutil.which("pwsh"):
            self.skipTest("pwsh unavailable")
        r = self.launch("pwsh", "-Manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        (self.wt / "src").mkdir()
        (self.wt / "src/a.txt").write_text("product\n")
        test_endcheck.git(self.wt, "add", "src/a.txt")
        test_endcheck.git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "product")
        sha = subprocess.check_output(["git", "-C", str(self.wt), "rev-parse", "HEAD"], text=True).strip()
        task = self.flow / "tasks/T-001-probe.md"
        task.write_text(task.read_text() + f"Outcome: completed\nChange: {sha}\n")
        r = self.launch("pwsh", "-MarkFinished")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.tool("accept.py", "T-001")
        self.assertIn("done", self.tool("ledger.py", "show", "T-001").stdout)
        self.assertTrue((self.root / "src/a.txt").exists())
        self.assertFalse(self.wt.exists())
        # the verification record binds task, attempt, requirements hash and the full artifact SHA
        rec = json.loads((self.flow / "tasks/.runtime/T-001.verify.json").read_text())[-1]
        self.assertEqual((rec["taskId"], rec["attempt"]), ("T-001", 1))
        self.assertRegex(rec["sha"], r"^[0-9a-f]{40}$")
        self.assertEqual(rec["headerHash"], gate.sha256(gate.header(task.read_text(encoding="utf-8"))))
        self.assertEqual(list((self.flow / "tasks/.runtime").glob("*.tmp")), [])  # atomic writes leave nothing

    def test_nonempty_live_list_in_both_shells(self):
        rt = self.flow / "tasks/.runtime"
        rt.mkdir(exist_ok=True)
        (rt / "T-002.json").write_text(json.dumps({"taskId": "T-002", "attempts": [
            {"n": 1, "manual": True, "status": "running"}]}))
        for shell in ("powershell", "pwsh"):
            if not shutil.which(shell):
                continue
            # Unknown live task is a deliberate preflight refusal, not an argv parser failure.
            r = self.launch(shell, "-Manual")
            self.assertNotIn("expected one argument", r.stdout + r.stderr)
            self.assertIn("T-002", r.stdout + r.stderr)

    def test_process_start_failure_keeps_recoverable_attempt(self):
        if os.name == "nt":
            fake = Path(self.tmp.name) / "fake-worker.cmd"
            fake.write_text("@echo off\nexit /b 0\n")  # the spawn itself fails, not the tool
        else:
            fake = Path(self.tmp.name) / "fake-worker.sh"
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
        env = dict(self.env, AGENTFLOW_DEVIN=str(fake),
                   AGENTFLOW_WORKER_PYTHON=str(Path(self.tmp.name) / "no-such-python"))
        r = subprocess.run([sys.executable, str(self.flow / "tools" / "run_task.py"), "T-001", "devin"],
                           env=env, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        rt = json.loads((self.flow / "tasks/.runtime/T-001.json").read_text())
        self.assertEqual(rt["attempts"][-1]["status"], "error")
        self.assertIn("in progress", self.tool("ledger.py", "show", "T-001").stdout)

    @unittest.skipUnless(os.name == "nt" and shutil.which("pwsh"), "Windows PowerShell required")
    def test_tick_launch_uses_launcher_transition_without_model(self):
        fake = Path(self.tmp.name) / "fake-worker.cmd"
        fake.write_text(f'@echo off\n"{sys.executable}" -c "import time; time.sleep(1)"\nexit /b 0\n')
        self.env["AGENTFLOW_DEVIN"] = str(fake)
        script = "import tick; ok, detail = tick.do_launch('T-001', 'devin'); print(detail); raise SystemExit(0 if ok else 1)"
        self.env["PYTHONPATH"] = str(self.flow / "tools")
        r = subprocess.run([sys.executable, "-c", script], cwd=self.root, env=self.env,
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("in progress", self.tool("ledger.py", "show", "T-001").stdout)
        runtime = self.flow / "tasks/.runtime/T-001.json"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            attempt = json.loads(runtime.read_text())["attempts"][-1]
            if attempt["status"] != "running":
                break
            time.sleep(0.1)
        self.assertEqual(attempt["status"], "exited", attempt)
        # Runtime is written just before the worker exits; wait for its OS process
        # too, otherwise Windows can still hold the temporary repository open.
        if attempt.get("pid"):
            subprocess.run(["pwsh", "-NoProfile", "-Command",
                            f"$p = Get-Process -Id {int(attempt['pid'])} -ErrorAction SilentlyContinue; "
                            "if ($p) { $p.WaitForExit() }"], capture_output=True, timeout=30)

    @unittest.skipUnless(os.name == "nt" and shutil.which("pwsh"), "Windows PowerShell required")
    def test_dispatch_grant_becomes_worker_lease(self):
        fake = Path(self.tmp.name) / "fake-worker.cmd"
        fake.write_text(f'@echo off\n"{sys.executable}" -c "import time; time.sleep(1)"\nexit /b 0\n')
        self.env["AGENTFLOW_DEVIN"] = str(fake)
        self.env["AGENTFLOW_SHARED_DISPATCHER"] = "active"
        self.env["PYTHONPATH"] = str(self.flow / "tools")
        setup = ("import dispatch; from pathlib import Path; "
                 f"p=Path({json.dumps(str(self.root))}); "
                 "dispatch.register(p, [('T-001','devin')]); "
                 "token,reason=dispatch.request(p,'T-001','devin'); "
                 "print(token or reason); raise SystemExit(0 if token else 1)")
        claim = subprocess.run([sys.executable, "-c", setup], cwd=self.root, env=self.env,
                               capture_output=True, text=True, timeout=10)
        self.assertEqual(claim.returncode, 0, claim.stdout + claim.stderr)
        grant = claim.stdout.strip()
        launch = ("import tick; "
                  f"ok,detail=tick.do_launch('T-001','devin',{json.dumps(grant)}); "
                  "print(detail); raise SystemExit(0 if ok else 1)")
        result = subprocess.run([sys.executable, "-c", launch], cwd=self.root, env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        runtime = self.flow / "tasks/.runtime/T-001.json"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            attempt = json.loads(runtime.read_text())["attempts"][-1]
            if attempt["status"] != "running":
                break
            time.sleep(0.1)
        self.assertEqual(attempt["status"], "exited", attempt)
        if attempt.get("pid"):
            subprocess.run(["pwsh", "-NoProfile", "-Command",
                            f"$p = Get-Process -Id {int(attempt['pid'])} -ErrorAction SilentlyContinue; "
                            "if ($p) { $p.WaitForExit() }"], capture_output=True, timeout=30)
        state = json.loads((Path(self.env["AGENTFLOW_MACHINE_STATE_DIR"]) / "registry.json").read_text())
        self.assertEqual(state["dispatch"]["grants"], [])
        self.assertEqual(state["leases"], [])

    def test_ledger_failure_records_error_without_launch(self):
        if not shutil.which("pwsh"):
            self.skipTest("pwsh unavailable")
        ledger = self.flow / "tools/ledger.py"
        ledger.write_text("if __name__ == '__main__': raise SystemExit('simulated ledger failure')\n"
                          + ledger.read_text(encoding="utf-8"), encoding="utf-8")
        r = self.launch("pwsh", "-Manual")
        self.assertNotEqual(r.returncode, 0)
        rt = json.loads((self.flow / "tasks/.runtime/T-001.json").read_text())
        self.assertEqual(rt["attempts"][-1]["status"], "error")
        self.assertIsNone(rt["attempts"][-1]["pid"])
