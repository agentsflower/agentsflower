"""Routing quality counts distinguish recommendation, fallback, and observed outcome."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import route_report  # noqa: E402


def recommendation():
    return {"jevChoice": "codex-sol", "choice": "codex-sol", "applied": True,
            "tool": "codex", "model": "gpt-6.1-sol", "backupTool": "devin", "backupModel": "swe-2-high",
            "complexity": 1.2, "confidence": 0.94, "eligibleOptions": ["codex-sol", "devin-swe2"],
            "requestId": "req-1"}


class RouteReportTests(unittest.TestCase):
    def test_first_attempt_primary_pass(self):
        item = route_report.summarize("T-1", {"Role": "developer", "Status": "done"}, [recommendation()],
                                      [{"tool": "codex", "status": "exited", "exitCode": 0,
                                        "startedAt": "2026-10-12T10:00:00Z", "finishedAt": "2026-10-12T10:01:00Z"}])
        self.assertEqual((item["actualSource"], item["actualModel"]), ("primary", "gpt-6.1-sol"))
        self.assertTrue(item["firstAttemptPass"])
        self.assertEqual(item["attemptWallSeconds"], 60.0)

    def test_backup_and_partial_tester_are_not_counted_as_first_pass(self):
        attempts = [{"tool": "codex", "status": "error", "exitCode": 1},
                    {"tool": "devin", "status": "exited", "exitCode": 0}]
        item = route_report.summarize("T-2", {"Role": "tester", "Status": "done"}, [recommendation()],
                                      attempts, verdict="partial")
        self.assertEqual((item["actualSource"], item["actualModel"]), ("backup", "swe-2-high"))
        self.assertFalse(item["acceptedPass"])
        self.assertFalse(item["firstAttemptPass"])
        self.assertIsNone(item["attemptWallSeconds"])

    def test_report_groups_comparable_tasks_and_ignores_missing_route(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for tid, tool in (("T-1", "codex"), ("T-2", "devin")):
                (root / f"{tid}.route.json").write_text(json.dumps([recommendation()]), encoding="utf-8")
                (root / f"{tid}.json").write_text(json.dumps({"attempts": [
                    {"tool": tool, "status": "exited", "exitCode": 0}]}), encoding="utf-8")
            rows = {tid: {"Role": "developer", "Status": "done"} for tid in ("T-1", "T-2", "T-3")}
            with patch.object(route_report.gate, "parse", side_effect=route_report.gate.TaskError("fixture")):
                result = route_report.report(rows, root)
        self.assertEqual(len(result["tasks"]), 2)
        self.assertEqual(result["groups"][0]["tasks"], 2)
        self.assertEqual(result["groups"][0]["backupUsed"], 1)

    def test_all_projects_combines_installed_reports_and_names_missing_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            installed = Path(temp) / "installed"
            missing = Path(temp) / "missing"
            script = installed / ".agentflow" / "tools" / "route_report.py"
            script.parent.mkdir(parents=True)
            script.write_text("# fixture\n", encoding="utf-8")
            missing.mkdir()
            item = route_report.summarize("T-1", {"Role": "developer", "Status": "done"},
                                          [recommendation()], [{"tool": "codex", "status": "exited", "exitCode": 0}])
            fake = lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=json.dumps({"tasks": [item]}))
            result = route_report.report_all([installed, missing], fake)
        self.assertEqual(result["groups"][0]["tasks"], 1)
        self.assertEqual(result["tasks"][0]["project"], str(installed.resolve()))
        self.assertIn(str(missing.resolve()), result["errors"])
