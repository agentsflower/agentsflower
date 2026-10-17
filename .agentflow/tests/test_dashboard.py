"""Dashboard pages: English labels, Verifies-based tester links, demo fixture safety."""
import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("workflow_dashboard", FLOW / "dashboard" / "build.py")
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)

DEV = """# T-001: Change something
Role: developer
Tool: codex
Independent check: tester
## Goal
Demo goal.
## Result
Outcome: completed
Change: 9f00dc1
"""

TESTER = """# T-002: Verify the delivery of T-001 by hand
Role: tester
Tool: devin
Verifies: T-003 @ deadbee
## Goal
Demo goal.
## Result
Outcome: completed
Verdict: fail
"""

OTHER = """# T-003: Another change
Role: developer
Tool: codex
Independent check: none - local
## Goal
Demo goal.
## Result
Outcome: completed
Change: abc1234
"""

ROW = {"ID": "", "Title": "", "Stage": "1", "Role": "", "Tool": "", "Status": "done",
       "Depends on": "", "Commit / artifact": "", "Notes": "", "Updated": "2026-10-16"}


def row(tid, title, role, status="done", commit=""):
    r = dict(ROW)
    r.update({"ID": tid, "Title": title, "Role": role, "Status": status, "Commit / artifact": commit})
    return r


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        (self.base / "T-001-dev.md").write_text(DEV, encoding="utf-8")
        (self.base / "T-002-check.md").write_text(TESTER, encoding="utf-8")
        (self.base / "T-003-other.md").write_text(OTHER, encoding="utf-8")
        self.files = {"T-001": self.base / "T-001-dev.md",
                      "T-002": self.base / "T-002-check.md",
                      "T-003": self.base / "T-003-other.md"}
        self.rows = [row("T-001", "Change something", "developer", commit="9f00dc1"),
                     row("T-002", "Verify the delivery of T-001 by hand", "tester"),
                     row("T-003", "Another change", "developer", commit="abc1234")]

    def tearDown(self):
        self.temp.cleanup()

    def tasks(self):
        with patch.object(dashboard, "ROOT", self.base), patch.object(dashboard, "OUT", self.base / "out"):
            tasks, goal_text = dashboard.build_tasks(self.rows, self.files, {}, {})
            dashboard.link_checks(tasks)
        return tasks

    def test_check_edge_uses_verifies_not_title(self):
        """The tester title names T-001 but Verifies names T-003: only T-003 is checked."""
        tasks = self.tasks()
        self.assertEqual(tasks["T-001"]["checkedBy"], [])
        self.assertEqual(tasks["T-001"]["check"], "Tester required, no report")
        checked = tasks["T-003"]["checkedBy"]
        self.assertEqual([c["id"] for c in checked], ["T-002"])
        edges = dashboard.check_edges(tasks)
        self.assertEqual(edges, [{"from": "T-002", "to": "T-003", "kind": "check",
                                  "sha": "deadbee", "stale": True}])

    def test_stale_checker_link_is_flagged(self):
        tasks = self.tasks()
        c = tasks["T-003"]["checkedBy"][0]
        self.assertEqual(c["sha"], "deadbee")
        self.assertTrue(c["stale"])  # verifies deadbee, current commit abc1234
        self.assertIn("stale link", tasks["T-003"]["check"])

    def test_fresh_sha_is_not_stale(self):
        with patch.object(dashboard, "ROOT", self.base), patch.object(dashboard, "OUT", self.base / "out"):
            tasks, _ = dashboard.build_tasks(self.rows, self.files, {}, {})
        tasks["T-003"]["verifies"] = None
        tasks["T-002"]["verifies"] = {"task": "T-003", "sha": "abc1234"}
        dashboard.link_checks(tasks)
        self.assertFalse(tasks["T-003"]["checkedBy"][0]["stale"])

    def test_verdict_stays_separate_from_status_and_outcome(self):
        """A fail verdict is a valid negative report: status/outcome/check are three fields."""
        tasks = self.tasks()
        tester = tasks["T-002"]
        self.assertEqual(tester["status"], "Done")
        self.assertEqual(tester["result"], "Completed by worker")
        self.assertEqual(tester["verdict"], "fail")
        self.assertEqual(tasks["T-003"]["check"], "Tester: fail (stale link)")

    def test_machine_key_kept_next_to_display_status(self):
        tasks = self.tasks()
        self.assertEqual(tasks["T-001"]["status"], "Done")
        self.assertEqual(tasks["T-001"]["statusKey"], "done")

    def test_demo_graph_is_deterministic_marked_and_isolated(self):
        g1, _, _ = dashboard.demo_graph()
        g2, _, _ = dashboard.demo_graph()
        self.assertEqual(json.dumps(g1, sort_keys=True), json.dumps(g2, sort_keys=True))
        self.assertTrue(g1["demo"])
        self.assertEqual(g1["project"], "demo-project")
        self.assertTrue(all(t["notes"] == "DEMO DATA row" for t in g1["tasks"]))
        page = dashboard.render("template.html").replace("__PROJECT__", g1["project"]).replace(
            "__DATA__", json.dumps(g1, ensure_ascii=False))
        self.assertIn("DEMO DATA", page)

    def test_english_labels_in_both_pages(self):
        g, _, _ = dashboard.demo_graph()
        for tpl in ("template.html", "graph_template.html", "filterbar.js"):
            src = (dashboard.HERE / tpl).read_text(encoding="utf-8")
            self.assertNotRegex(src, r"[А-Яа-я]", tpl)
        common = (dashboard.HERE / "common.js").read_text(encoding="utf-8")
        cyr_lines = [l for l in common.split("\n") if re.search(r"[А-Яа-я]", l)]
        self.assertEqual(len(cyr_lines), 1)  # only the char class of the rich() field-name regex
        self.assertIn("rich", cyr_lines[0])
        for t in g["tasks"]:
            self.assertIn(t["status"], dashboard.STATUS_EN.values())

    def test_metrics_present_in_payload(self):
        g, _, _ = dashboard.demo_graph()
        self.assertIn("firstPassGateRate", g["metrics"])
        self.assertIn("definitions", g["metrics"])
        self.assertIsNone(g["metrics"]["cost"])

    def test_main_demo_writes_only_out(self):
        out = self.base / "out"
        with patch.object(dashboard, "OUT", out), contextlib.redirect_stdout(io.StringIO()):
            dashboard.main(["--demo"])
        self.assertTrue((out / "index.html").exists())
        self.assertTrue((out / "graph.html").exists())
        index = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("DEMO DATA", index)


if __name__ == "__main__":
    unittest.main()
