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

    def test_assessment_and_admission_metadata_is_exposed_safely(self):
        """T-078/S-02: the report surfaces assessment status, exclusions and the human-exception
        record; absent fields stay None (unknown), never fabricated."""
        rec = {"event": "assessment", "schemaVersion": 1, "status": "blocked",
               "blocked": "no option is eligible", "jevChoice": "devin-swe-2",
               "tool": "devin", "model": "swe-2-high",
               "required": {"effort": "high", "complexity": 1.9},
               "excluded": {"agy": "limited until ..."}, "inadequate": {"codex-sol": "cap"},
               "adequateHeld": {"agy": "limited"}}
        adm = {"event": "human-exception", "source": "human-exception",
               "reason": "human assigned", "overrode": ["no recorded assessment"]}
        item = route_report.summarize("T-9", {"Role": "developer", "Status": "in progress"},
                                      [rec, adm], [])
        self.assertEqual(item["assessmentStatus"], "blocked")
        self.assertEqual(item["blocked"], "no option is eligible")
        self.assertEqual(item["excluded"], {"agy": "limited until ..."})
        self.assertEqual(item["inadequate"], {"codex-sol": "cap"})
        self.assertEqual(item["adequateHeld"], {"agy": "limited"})
        self.assertEqual(item["humanExceptions"], 1)
        self.assertEqual(item["admissionSource"], "human-exception")
        self.assertEqual(item["humanExceptionReason"], "human assigned")
        self.assertIsNone(item["admissionDeviation"])
        bare = route_report.summarize("T-8", {"Role": "developer", "Status": "done"},
                                    [recommendation()], [])
        self.assertIsNone(bare["assessmentStatus"])   # a legacy record has no status
        self.assertIsNone(bare["excluded"])
        self.assertEqual(bare["humanExceptions"], 0)
        self.assertIsNone(bare["admissionSource"])

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


def write(runtime, name, value):
    (runtime / name).write_text(json.dumps(value), encoding="utf-8")


class MetricsTests(unittest.TestCase):
    def test_first_pass_uses_first_verify_record_not_a_later_pass(self):
        """A fail followed by a pass is not a first-pass: only record #1 counts."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root, "T-1.verify.json", [{"n": 1, "ok": False}, {"n": 2, "ok": True}])
            write(root, "T-1.json", {"attempts": [{"tool": "codex", "status": "exited"}]})
            rows = {"T-1": {"Role": "developer", "Status": "done", "Tool": "codex"}}
            result = route_report.metrics(rows, root)
        self.assertEqual(result["firstPassGateRate"],
                         [{"role": "developer", "tool": "codex", "tasks": 1, "firstVerifyPass": 0}])

    def test_tasks_without_evidence_are_not_failures(self):
        """No verify file: excluded from the denominator, counted as missing evidence."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rows = {"T-1": {"Role": "developer", "Status": "done", "Tool": "codex"},
                    "T-2": {"Role": "developer", "Status": "in progress", "Tool": "devin"}}
            result = route_report.metrics(rows, root)
        self.assertEqual(result["firstPassGateRate"], [])
        self.assertEqual(result["tasksWithoutEvidence"], 2)

    def test_denominator_groups_by_recorded_role_and_tool(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for tid, ok in (("T-1", True), ("T-2", False), ("T-3", True)):
                write(root, f"{tid}.verify.json", [{"n": 1, "ok": ok}])
                write(root, f"{tid}.json", {"attempts": [{"tool": "devin"}]})
            rows = {"T-1": {"Role": "developer", "Status": "done"},
                    "T-2": {"Role": "developer", "Status": "done"},
                    "T-3": {"Role": "tester", "Status": "done"}}
            with patch.object(route_report, "_tester_verdict", return_value="pass"):
                result = route_report.metrics(rows, root)
        groups = {(g["role"], g["tool"]): g for g in result["firstPassGateRate"]}
        self.assertEqual(groups[("developer", "devin")]["tasks"], 2)
        self.assertEqual(groups[("developer", "devin")]["firstVerifyPass"], 1)
        self.assertEqual(groups[("tester", "devin")]["firstVerifyPass"], 1)

    def test_fail_verdict_is_a_valid_negative_report_not_a_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rows = {"T-1": {"Role": "tester", "Status": "done"},
                    "T-2": {"Role": "tester", "Status": "done"}}
            verdicts = iter(["fail", "pass"])
            with patch.object(route_report, "_tester_verdict", side_effect=lambda tid: next(verdicts)):
                result = route_report.metrics(rows, root)
        self.assertEqual(result["testerVerdicts"], {"fail": 1, "pass": 1})

    def test_lead_time_is_none_without_attempt_history(self):
        self.assertIsNone(route_report.lead_seconds([]))
        self.assertIsNone(route_report.lead_seconds([{"tool": "codex"}]))
        self.assertIsNone(route_report.lead_seconds(
            [{"startedAt": "2026-10-12T10:00:00Z"}]))
        self.assertEqual(route_report.lead_seconds(
            [{"startedAt": "2026-10-12T10:00:00Z", "finishedAt": "2026-10-12T10:30:00Z"}]), 1800.0)

    def test_fresh_clone_reports_absence_honestly(self):
        """Empty runtime: no zero or invented metrics; cost is N/A, not a number."""
        with tempfile.TemporaryDirectory() as temp:
            result = route_report.metrics({"T-1": {"Role": "developer", "Status": "done"}}, Path(temp))
        self.assertEqual(result["firstPassGateRate"], [])
        self.assertEqual(result["leadSeconds"], [])
        self.assertIsNone(result["cost"])
        self.assertIn("N/A", result["definitions"]["cost"])
