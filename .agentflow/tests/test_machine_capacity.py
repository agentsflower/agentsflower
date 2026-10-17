"""Two AgentFlow projects share tool slots, ports and observed tool limits."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import machine_capacity as machine  # noqa: E402


class MachineCapacityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        # a machine's own AGENTFLOW_* variables must not leak into the fixture
        clean = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        clean["AGENTFLOW_MACHINE_STATE_DIR"] = self.tmp.name
        env = patch.dict(os.environ, clean, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.projects = [Path(self.tmp.name) / "project-a", Path(self.tmp.name) / "project-b"]
        for root in self.projects:
            (root / ".agentflow" / "docs").mkdir(parents=True)
            (root / ".agentflow" / "docs" / "project-rules.md").write_text(
                "# Rules\n\n## Preflight\n\n- parallel: codex=1\n", encoding="utf-8")

    def test_codex_slot_is_shared_and_released(self):
        first, reason = machine.claim("codex", self.projects[0], "T-001", pid=os.getpid())
        self.assertTrue(first, reason)
        second, reason = machine.claim("codex", self.projects[1], "T-001", pid=os.getpid())
        self.assertIsNone(second)
        self.assertIn("no free machine slot", reason)
        machine.release(first)
        second, reason = machine.claim("codex", self.projects[1], "T-001", pid=os.getpid())
        self.assertTrue(second, reason)

    def test_capacity_hint_reflects_other_project(self):
        first, _ = machine.claim("codex", self.projects[0], "T-001", pid=os.getpid())
        self.assertFalse(machine.has_capacity("codex", self.projects[1]))
        machine.release(first)
        self.assertTrue(machine.has_capacity("codex", self.projects[1]))

    def test_active_dispatcher_separates_machine_and_project_caps(self):
        with patch.dict(os.environ, {"AGENTFLOW_MACHINE_CODEX_MAX": "2", "AGENTFLOW_SHARED_DISPATCHER": "active"}):
            first, reason = machine.claim("codex", self.projects[0], "T-001", pid=os.getpid())
            self.assertTrue(first, reason)
            try:
                self.assertFalse(machine.has_capacity("codex", self.projects[0]))
                self.assertTrue(machine.has_capacity("codex", self.projects[1]))
            finally:
                machine.release(first)

    def test_port_is_shared_even_when_tools_differ(self):
        first, _ = machine.claim("devin", self.projects[0], "T-002", port="4348", pid=os.getpid())
        second, reason = machine.claim("claude", self.projects[1], "T-002", port="4348", pid=os.getpid())
        self.assertIsNone(second)
        self.assertIn("PORT=4348", reason)
        machine.release(first)
        second, reason = machine.claim("claude", self.projects[1], "T-002", port="4348", pid=os.getpid())
        self.assertTrue(second, reason)

    @unittest.skipUnless(os.name == "nt", "Windows PID start-time guard")
    def test_dead_worker_is_cleaned_and_pid_start_guards_reuse(self):
        token, _ = machine.claim("codex", self.projects[0], "T-003", pid=os.getpid())
        self.assertTrue(machine.activate(token, os.getpid(), 1))
        next_token, reason = machine.claim("codex", self.projects[1], "T-003", pid=os.getpid())
        self.assertTrue(next_token, reason)

    def test_pending_handoff_survives_launcher_exit_until_worker_activates(self):
        token, _ = machine.claim("codex", self.projects[0], "T-003", pid=999999999)
        blocked, reason = machine.claim("codex", self.projects[1], "T-003", pid=os.getpid())
        self.assertIsNone(blocked, reason)
        self.assertTrue(machine.activate(token, os.getpid()))
        machine.release(token)
        available, reason = machine.claim("codex", self.projects[1], "T-003", pid=os.getpid())
        self.assertTrue(available, reason)

    def test_limit_is_shared(self):
        until = datetime.now(timezone.utc) + timedelta(minutes=10)
        machine.record_limit("claude", until)
        token, reason = machine.claim("claude", self.projects[1], "orchestrator", pid=os.getpid())
        self.assertIsNone(token)
        self.assertIn("globally limited", reason)
        self.assertIsNotNone(machine.limit_until("claude"))

    @unittest.skipUnless(os.name == "nt", "Windows os.replace failures carry winerror")
    def test_transient_replace_failures_retry_until_success(self):
        real_replace = os.replace
        calls = []

        def flaky(src, dst):
            calls.append(1)
            if len(calls) < 3:
                raise OSError(13, "denied", None, 5)  # ERROR_ACCESS_DENIED: scanner/indexer holds the file
            return real_replace(src, dst)

        with patch.object(os, "replace", side_effect=flaky):
            token, reason = machine.claim("codex", self.projects[0], "T-010", pid=os.getpid())
        self.assertTrue(token, reason)
        self.assertEqual(len(calls), 3)
        state = json.loads((Path(self.tmp.name) / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(len(state["leases"]), 1)
        self.assertEqual(list(Path(self.tmp.name).glob("*.tmp")), [])

    @unittest.skipUnless(os.name == "nt", "Windows os.replace failures carry winerror")
    def test_permanent_replace_failure_fails_closed_and_cleans_up(self):
        first, _ = machine.claim("codex", self.projects[0], "T-010", pid=os.getpid())
        registry = Path(self.tmp.name) / "registry.json"
        before = registry.read_bytes()
        calls = []

        def denied(src, dst):
            calls.append(1)
            raise OSError(13, "denied", None, 32)  # ERROR_SHARING_VIOLATION that never clears

        with patch.object(machine, "REPLACE_DELAY", 0), \
                patch.object(os, "replace", side_effect=denied):
            with self.assertRaises(PermissionError):
                machine.release(first)
        self.assertEqual(len(calls), machine.REPLACE_ATTEMPTS, "bounded backoff: no infinite loop")
        self.assertEqual(registry.read_bytes(), before, "the previous registry is preserved")
        self.assertEqual(list(Path(self.tmp.name).glob("*.tmp")), [], "temp file leaked")
        token, reason = machine.claim("codex", self.projects[1], "T-010", pid=os.getpid())
        self.assertIsNone(token, "failed replace left no lease behind")
        self.assertIn("no free machine slot", reason)

    def test_non_retryable_replace_error_is_not_retried(self):
        calls = []

        def gone(src, dst):
            calls.append(1)
            raise FileNotFoundError("registry directory vanished")

        with patch.object(os, "replace", side_effect=gone):
            with self.assertRaises(FileNotFoundError):
                machine.claim("codex", self.projects[0], "T-010", pid=os.getpid())
        self.assertEqual(len(calls), 1)
        self.assertEqual(list(Path(self.tmp.name).glob("*.tmp")), [])

    def test_concurrent_launchers_cannot_both_claim_the_last_slot(self):
        script = FLOW / "tools" / "machine_capacity.py"
        env = dict(os.environ)
        launchers = [subprocess.Popen([sys.executable, str(script), "claim", "codex", str(root), "T-004",
                                       "--pid", str(os.getpid())], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True, env=env) for root in self.projects]
        results = [p.communicate(timeout=10) for p in launchers]
        self.assertEqual(sorted(p.returncode for p in launchers), [0, 4], results)
        state = json.loads((Path(self.tmp.name) / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(len(state["leases"]), 1)


if __name__ == "__main__":
    unittest.main()
