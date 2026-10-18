"""T-078: the scheduler (tick.py) consults the persisted routing assessment before an automatic
launch and the recorded requirement before a backup switch. A missing/stale/blocked assessment is
an actionable need, never a doomed launch; an inadequate or group-held backup never replaces the
primary; a tester admitted on Devin launches on Devin (independence = fresh isolated session); a
reported availability window never overrides an observed hold or the recorded adequacy floor.
run_task.admission stays the final authority: these tests pin the scheduler-side pre-check."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import gate  # noqa: E402
import route  # noqa: E402
import tick  # noqa: E402

AT = datetime(2026, 10, 18, 12, 0, tzinfo=timezone.utc)

DEV_TASK = """# {tid}: Probe

Role: developer
Tool: {tool}
{model}Stage: 5
Depends on: none
Branch: {branch}
Worktree: W:/none/{branch}
Independent check: none - probe
Resume: none
{extra}
## Goal

Do a thing.

## Acceptance criteria

- [ ] The thing is done.

## Checks

- `git --version` - git runs

## Result
"""

TESTER_TASK = """# {tid}: Check

Role: tester
Tool: {tool}
{model}Stage: 5
Depends on: T-900
Verifies: T-900 @ {sha}
Resume: none
{extra}
## Goal

Check it.

## Acceptance criteria

- [ ] It checks out.

## Checks

- `git --version` - git runs

## Result
"""


def task_file(folder, tid, tool="devin", model="swe-2-high", extra="", role="developer"):
    if role == "tester":
        text = TESTER_TASK.format(tid=tid, tool=tool, model=f"Model: {model}\n" if model else "",
                                  sha="b" * 40, extra=extra)
    else:
        text = DEV_TASK.format(tid=tid, tool=tool, model=f"Model: {model}\n" if model else "",
                               branch=f"{tid.lower()}-probe", extra=extra)
    path = Path(folder) / f"{tid}-probe.md"
    path.write_text(text, encoding="utf-8")
    return path, text


def assessment(path_text, tid, status="ok", tool="devin", model="swe-2-high",
               required=None, **kw):
    rec = {"event": "assessment", "schemaVersion": 1, "task": tid, "source": "jev",
           "at": "2026-10-18T00:00:00Z", "status": status,
           "requirementsHash": gate.requirements_hash(path_text),
           "required": required or {"effort": "high", "complexity": 0.4},
           "selected": {"option": "devin-swe-2", "tool": tool, "model": model, "effort": None}}
    rec.update(kw)
    return rec


class SchedulerAdmissionTests(unittest.TestCase):
    """decide() consults route.assessment_problems for every ready task: the record-level gate the
    launcher then re-validates fully (route.admission stays the final authority)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rt = Path(self.tmp.name)
        clean = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        clean["AGENTFLOW_MACHINE_STATE_DIR"] = str(rt / "machine")
        self.patches = [patch.object(tick, "RT", rt), patch.object(tick, "TICK", rt / "tick.json"),
                        patch.object(tick, "LOCK", rt / "tick.lock"),
                        patch.object(tick, "LIMITS", rt / "tool-limits.json"),
                        patch.object(tick, "HEARTBEAT", rt / "orchestrator.json"),
                        patch.dict(os.environ, clean, clear=True)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def task(self, tid, tool="devin", model="swe-2-high", extra="", role="developer"):
        path, text = task_file(self.tmp.name, tid, tool, model, extra, role)
        return {"id": tid, "file": str(path), "role": role, "depends": [],
                "independent": "none - probe", "result": "", "model": model, "effort": None}

    def write_route(self, tid, *records):
        p = Path(self.tmp.name) / f"{tid}.route.json"
        p.write_text(json.dumps(list(records)), encoding="utf-8")

    def decide(self, tasks, rows):
        with patch.object(tick.gate, "parse", side_effect=lambda t: tasks[t]), \
                patch.object(tick.gate, "last_attempt", return_value=None), \
                patch.object(tick, "alive", return_value=False):
            return {t: (a, d) for t, a, d in tick.decide(rows, AT)}

    def test_missing_assessment_is_an_actionable_need_not_a_launch(self):
        tasks = {"T-1": self.task("T-1")}
        out = self.decide(tasks, {"T-1": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-1"][0], "need")
        self.assertIn("routing admission", out["T-1"][1])
        self.assertIn("route.py", out["T-1"][1])

    def test_ok_assessment_launches(self):
        t = self.task("T-1")
        self.write_route("T-1", assessment(Path(t["file"]).read_text(encoding="utf-8"), "T-1"))
        out = self.decide({"T-1": t}, {"T-1": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-1"], ("launch", "devin"))

    def test_blocked_and_stale_assessments_are_actionable_blocks(self):
        t = self.task("T-1")
        text = Path(t["file"]).read_text(encoding="utf-8")
        self.write_route("T-1", assessment(text, "T-1", status="blocked",
                                           blocked="no option is eligible or usable today"))
        out = self.decide({"T-1": t}, {"T-1": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-1"][0], "need")
        self.assertIn("'blocked'", out["T-1"][1])
        self.write_route("T-1", assessment(text, "T-1", requirementsHash="0" * 64))
        out = self.decide({"T-1": t}, {"T-1": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-1"][0], "need")
        self.assertIn("stale", out["T-1"][1])

    def test_human_exception_line_admits_the_automatic_launch(self):
        t = self.task("T-1", extra="Routing exception: human assigned this worker\n")
        out = self.decide({"T-1": t}, {"T-1": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-1"], ("launch", "devin"))  # logged as human-exception by the launcher

    def test_tester_on_devin_is_not_removed_because_the_developer_used_devin(self):
        """S-05: independence for a tester is the fresh session on an isolated checkout, not a
        different CLI. A tester whose ok assessment selected Devin launches on Devin even though
        the checked task ran on Devin; the scheduler applies no same-CLI removal."""
        task_file(self.tmp.name, "T-900", "devin")                      # the checked task ran devin
        t = self.task("T-2", role="tester")
        self.write_route("T-2", assessment(Path(t["file"]).read_text(encoding="utf-8"), "T-2"))
        out = self.decide({"T-2": t}, {"T-2": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-2"], ("launch", "devin"))

    def test_an_actual_devin_hold_still_blocks_despite_the_reported_window(self):
        """The human's 'no Devin limits until 2026-11-01' report is qualitative; an observed hold
        on the devin quota group still turns the launch into a need."""
        t = self.task("T-1")
        self.write_route("T-1", assessment(Path(t["file"]).read_text(encoding="utf-8"), "T-1"))
        tick.record_limit("devin", "usage limit", group="devin", at=AT)
        out = self.decide({"T-1": t}, {"T-1": {"Status": "ready", "Tool": "devin"}})
        self.assertEqual(out["T-1"][0], "need")
        self.assertIn("limited", out["T-1"][1])


class SchedulerBackupTests(unittest.TestCase):
    """use_backup() consults route.backup_ok before rewriting the header: only a backup meeting the
    recorded requirement, without a live hold on its quota group, may replace the primary."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rt = Path(self.tmp.name)
        clean = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        clean["AGENTFLOW_MACHINE_STATE_DIR"] = str(rt / "machine")
        self.patches = [patch.object(tick, "RT", rt), patch.dict(os.environ, clean, clear=True)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def backup_task(self, tid, backup="devin", backup_model="swe-2-high", role="developer"):
        extra = f"Backup Tool: {backup}\nBackup Model: {backup_model}\n"
        return task_file(self.tmp.name, tid, "codex", "gpt-6-astra", extra, role)

    def run_backup(self, tid, path, rec=None):
        if rec is not None:
            (Path(self.tmp.name) / f"{tid}.route.json").write_text(
                json.dumps([rec]), encoding="utf-8")
        with patch.object(tick.gate, "last_attempt", return_value=None), \
                patch.object(tick.gate, "parse", return_value={"id": tid, "file": str(path)}), \
                patch.object(tick.machine_capacity, "has_capacity", return_value=True), \
                patch.object(tick, "limited", return_value=False), \
                patch.object(tick, "py", return_value=(0, "")), \
                patch.object(tick.route, "_log"):
            return tick.use_backup(tid, "codex")

    def test_adequate_backup_switches_and_rewrites_the_header(self):
        path, text = self.backup_task("T-1")
        rec = assessment(text, "T-1", required={"effort": "high", "complexity": 0.4})
        switched, tool = self.run_backup("T-1", path, rec)
        self.assertTrue(switched)
        self.assertEqual(tool, "devin")
        self.assertIn("Tool: devin\nModel: swe-2-high\n", path.read_text(encoding="utf-8"))

    def test_inadequate_backup_never_replaces_the_primary(self):
        """Recorded requirement xhigh, backup swe-2-high (tier high): refused, header untouched."""
        path, text = self.backup_task("T-1")
        rec = assessment(text, "T-1", required={"effort": "xhigh", "complexity": 0.4})
        switched, why = self.run_backup("T-1", path, rec)
        self.assertFalse(switched)
        self.assertIn("not admissible", why)
        self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_a_held_backup_group_stays_scoped_and_refused(self):
        """A live hold on the backup's quota group refuses it; a hold on another group does not."""
        path, text = self.backup_task("T-1")
        rec = assessment(text, "T-1")
        tick.machine_capacity.record_limit("devin", AT + timedelta(hours=1), "devin")
        switched, why = self.run_backup("T-1", path, rec)
        self.assertFalse(switched)
        self.assertIn("limited", why)
        self.assertEqual(path.read_text(encoding="utf-8"), text)
        tick.machine_capacity.record_limit("agy", AT + timedelta(hours=1), "agy-claude-gpt")
        # the unrelated group hold does not change the devin refusal - scoping is preserved
        switched, why = self.run_backup("T-1", path, rec)
        self.assertFalse(switched)

    def test_no_ok_assessment_means_no_backup_switch(self):
        path, text = self.backup_task("T-1")
        switched, why = self.run_backup("T-1", path)
        self.assertFalse(switched)
        self.assertIn("no ok assessment", why)
        self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_devin_backup_serves_a_tester_of_a_devin_task(self):
        """S-05 backup path: a tester checking a Devin-built task may switch to an adequate
        Devin backup - the scheduler removes no Devin option for the developer's tool."""
        task_file(self.tmp.name, "T-900", "devin")
        path, text = self.backup_task("T-2", role="tester")
        rec = assessment(text, "T-2")
        switched, tool = self.run_backup("T-2", path, rec)
        self.assertTrue(switched)
        self.assertEqual(tool, "devin")


if __name__ == "__main__":
    unittest.main()
