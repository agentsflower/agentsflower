"""A planned task waits for the human's approval: ledger.py add makes it blocked "awaiting approval", nothing launches
it (tick.py, gate.py preflight) until ledger.py approve. Regression: the conductor would have launched a freshly
planned task within minutes, before the human said yes."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]

TASK = """# T-001: Probe

Role: developer
Tool: codex
Stage: 1
Depends on: none
Branch: t-001-probe
Worktree: {wt}
Independent check: none - probe
Resume: none

## Goal

Probe.

## Allowed files

- `src/a.txt` - probe

## Do not touch

- `docs/`

## Acceptance criteria

- [ ] probe passes

## Checks

- `python -c "print(1)"` - probe
"""


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.machine_env = patch.dict(os.environ, {"AGENTFLOW_MACHINE_STATE_DIR": self.tmp.name})
        self.machine_env.start()
        self.root = Path(self.tmp.name) / "p"
        flow = self.root / ".agentflow"
        shutil.copytree(FLOW / "tools", flow / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(FLOW / "tasks" / "_template.md", (flow / "tasks").mkdir(parents=True) or flow / "tasks")
        (flow / "state").mkdir()
        (flow / "tasks" / "T-001-probe.md").write_text(TASK.format(wt=Path(self.tmp.name) / "wt" / "p-t-001-probe"), encoding="utf-8")
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.root)], check=True)
        self.flow = flow

    def tearDown(self):
        self.machine_env.stop()
        self.tmp.cleanup()

    def tool(self, name, *args, check=True):
        p = subprocess.run([sys.executable, str(self.flow / "tools" / name), *args], capture_output=True, text=True,
                           encoding="utf-8", cwd=self.root)
        if check:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def row(self):
        return self.tool("ledger.py", "show", "T-001").stdout.split(" | ")

    def preflight(self):
        out = Path(self.tmp.name) / "pf.json"
        self.tool("gate.py", "preflight", "T-001", "--out", str(out), check=False)
        return json.loads(out.read_text(encoding="utf-8"))

    def test_planned_task_waits_until_approved(self):
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1", "--role", "developer", "--tool", "codex",
                  "--notes", "why")
        row = self.row()
        self.assertEqual(row[5], "blocked")
        self.assertEqual(row[8], "awaiting approval; why")
        pf = self.preflight()
        self.assertFalse(pf["ok"])
        self.assertTrue(any("approval" in p for p in pf["problems"]), pf["problems"])
        tick = json.loads(self.tool("tick.py", "run", "--dry-run", "--json").stdout)
        self.assertEqual(tick["would"], [])
        self.assertIn("approval", tick["waits"][0]["detail"])

        self.tool("ledger.py", "approve", "T-001")
        row = self.row()
        self.assertEqual((row[5], row[8]), ("ready", "why"))
        self.assertTrue(self.preflight()["ok"], self.preflight()["problems"])
        tick = json.loads(self.tool("tick.py", "run", "--dry-run", "--json").stdout)
        self.assertEqual([w["task"] for w in tick["would"]], ["T-001"])

    def test_explicit_ready_needs_no_approval_and_approve_refuses_it(self):
        self.tool("ledger.py", "add", "T-001", "--title", "Successor", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--status", "ready")
        self.assertEqual(self.row()[5], "ready")
        p = self.tool("ledger.py", "approve", "T-001", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not awaiting approval", p.stdout + p.stderr)

    def test_approval_gate_cannot_be_bypassed_by_a_direct_set(self):
        """The flag is a gate, not a status: `set` cannot clear it, move the task, or claim it -
        only `approve`, a terminal status, or a note that keeps the prefix is allowed."""
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--notes", "why")
        for args in (("set", "T-001", "--status", "in progress"),
                     ("set", "T-001", "--status", "ready"),
                     ("set", "T-001", "--status", "review"),
                     ("set", "T-001", "--notes", "no longer waiting")):
            p = self.tool("ledger.py", *args, check=False)
            self.assertNotEqual(p.returncode, 0, args)
            self.assertIn("approval of the plan", p.stdout + p.stderr, args)
        self.tool("ledger.py", "set", "T-001", "--notes", "awaiting approval; revised")
        self.assertEqual(self.row()[8], "awaiting approval; revised")
        self.tool("ledger.py", "approve", "T-001")
        self.assertEqual(self.row()[5], "ready")
        # a terminal status while awaiting stays allowed: the task can never launch anyway
        self.tool("ledger.py", "add", "T-002", "--title", "Plan", "--stage", "1", "--role", "developer",
                  "--tool", "codex")
        self.tool("ledger.py", "set", "T-002", "--status", "cancelled", "--notes", "dropped")
        self.assertIn("cancelled", self.tool("ledger.py", "show", "T-002").stdout)

    def test_in_progress_claim_needs_a_running_attempt(self):
        """Claims bind to the launcher's record: `set --status in progress` needs a running attempt in
        tasks/.runtime/T-NNN.json. A corrupt file refuses the claim - never a silent yes."""
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--status", "ready")
        p = self.tool("ledger.py", "set", "T-001", "--status", "in progress", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("running attempt", p.stdout + p.stderr)
        rt = self.flow / "tasks" / ".runtime"
        rt.mkdir(parents=True, exist_ok=True)
        (rt / "T-001.json").write_text(json.dumps({"taskId": "T-001", "attempts": [
            {"n": 1, "status": "running", "manual": True}]}), encoding="utf-8")
        self.tool("ledger.py", "set", "T-001", "--status", "in progress")
        self.assertEqual(self.row()[5], "in progress")
        # an attempt that is not running (exited, error) grants no claim either
        self.tool("ledger.py", "add", "T-002", "--title", "Plan", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--status", "ready")
        (rt / "T-002.json").write_text(json.dumps({"taskId": "T-002", "attempts": [
            {"n": 1, "status": "exited", "exitCode": 0}]}), encoding="utf-8")
        p = self.tool("ledger.py", "set", "T-002", "--status", "in progress", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("running attempt", p.stdout + p.stderr)
        (rt / "T-002.json").write_text("{ broken", encoding="utf-8")
        p = self.tool("ledger.py", "set", "T-002", "--status", "in progress", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("cannot read runtime state", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
