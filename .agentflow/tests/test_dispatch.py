"""Shared dispatcher shadow plan: fairness, capacity, and no worker launches."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import dispatch  # noqa: E402
import machine_capacity  # noqa: E402


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = patch.dict(os.environ, {"AGENTFLOW_MACHINE_STATE_DIR": self.tmp.name,
                                        "AGENTFLOW_MACHINE_CODEX_MAX": "2"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.a = Path(self.tmp.name) / "a"
        self.b = Path(self.tmp.name) / "b"
        for root in (self.a, self.b):
            rules = root / ".agentflow" / "docs" / "project-rules.md"
            rules.parent.mkdir(parents=True)
            rules.write_text("## Preflight\n\n- parallel: codex=2\n", encoding="utf-8")

    def test_shadow_plan_shares_two_slots_between_projects(self):
        ready = {self.a: [("T-1", "codex"), ("T-2", "codex")],
                 self.b: [("T-3", "codex"), ("T-4", "codex")]}
        report = dispatch.plan([self.a, self.b], lambda root: (ready[root], None))
        self.assertEqual([item["task"] for item in report["selected"]], ["T-1", "T-3"])
        self.assertEqual([item["task"] for item in report["waits"]], ["T-2", "T-4"])
        self.assertEqual(report["launches"], 0)
        with machine_capacity._locked() as state:
            self.assertEqual(state["leases"], [])

    def test_existing_lease_and_project_rule_are_respected(self):
        token, reason = machine_capacity.claim("codex", self.a, "existing", pid=os.getpid())
        self.assertTrue(token, reason)
        try:
            report = dispatch.plan([self.a, self.b],
                                   lambda root: ([("T-1" if root == self.a else "T-2", "codex")], None))
            self.assertEqual(len(report["selected"]), 1)
            self.assertEqual(len(report["waits"]), 1)
        finally:
            machine_capacity.release(token)

    def test_last_served_rotates_first_project(self):
        tasks = [{"project": str(root), "task": name, "tool": "codex"}
                 for root, name in ((self.a, "T-1"), (self.b, "T-2"))]
        self.assertEqual(dispatch.fair_order(tasks, {"codex": str(self.a)})[0]["project"], str(self.b))

    def test_grants_round_robin_and_convert_to_worker_leases(self):
        for root in (self.a, self.b):
            (root / ".agentflow" / "docs" / "project-rules.md").write_text(
                "## Preflight\n\n- parallel: codex=1\n", encoding="utf-8")
        dispatch.register(self.a, [("T-1", "codex"), ("T-2", "codex")])
        dispatch.register(self.b, [("T-3", "codex")])
        first, reason = dispatch.request(self.a, "T-1", "codex")
        self.assertTrue(first, reason)
        waiting, reason = dispatch.request(self.a, "T-2", "codex")
        self.assertIsNone(waiting)
        self.assertIn(str(self.b), reason)
        second, reason = dispatch.request(self.b, "T-3", "codex")
        self.assertTrue(second, reason)
        leases = []
        try:
            for root, task, grant in ((self.a, "T-1", first), (self.b, "T-3", second)):
                lease, reason = machine_capacity.claim("codex", root, task, pid=os.getpid(), grant=grant)
                self.assertTrue(lease, reason)
                leases.append(lease)
            self.assertEqual(len(leases), 2)
            with machine_capacity._locked() as state:
                self.assertEqual(state["dispatch"]["grants"], [])
        finally:
            for lease in leases:
                machine_capacity.release(lease)

    def test_grant_is_bound_to_task_and_expires(self):
        dispatch.register(self.a, [("T-1", "codex")])
        grant, reason = dispatch.request(self.a, "T-1", "codex")
        self.assertTrue(grant, reason)
        lease, reason = machine_capacity.claim("codex", self.a, "T-wrong", pid=os.getpid(), grant=grant)
        self.assertIsNone(lease)
        self.assertIn("another task", reason)
        with machine_capacity._locked() as state:
            state["dispatch"]["grants"][0]["until"] = 0
        lease, reason = machine_capacity.claim("codex", self.a, "T-1", pid=os.getpid(), grant=grant)
        self.assertIsNone(lease)
        self.assertIn("expired", reason)


if __name__ == "__main__":
    unittest.main()
