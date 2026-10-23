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
        for tpl in ("template.html", "graph_template.html", "roadmap_template.html",
                    "roadmap.js", "roadmap.css", "filterbar.js"):
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
        self.assertTrue((out / "roadmap.html").exists())
        index = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("DEMO DATA", index)


PLAN_FIXTURE = """# Project Plan

## Roadmap

### Stage 6. Public release

Status: current.

Exit criteria: packaged CLI and CI on three OSes;
publication is done by the human.

### Stage 1. Team layer

Status: closed (1.2.0).

Exit criteria: roles, Task Files, ledger on a live project.

### Stage 5. Structured stage

Status: planned.

Exit criteria:
- S5-E1: scenarios pass
  evidence: state=pass; label="recorded pass"; provenance="gate verify record"; recorded=2026-10-20; artifact=abc1234; ref=README.md
- S5-E2: external CI green
  evidence: state=fail; external=true; ref=https://ci.invalid/run/7; recorded=2026-10-20
- S5-E3: pending item
- loose prose bullet stays text

Recurring: periodic audit
an ongoing declaration; a completed cycle never closes the stage
- cycle-2026-10-01: completed; recorded=2026-10-01; ref=README.md; note="first cycle"

References:
- old audit file; note="outside this repo"

### Stage 2. Fenced away

Status: closed.

```text
### Stage 9. Not a stage
Status: current.
```

#### deeper heading inside the stage body
Exit criteria: still read after a level-4 heading.

### Stage 3 (odd heading)

Status: closed.

### Stage 8

Status: closed.

### Stage 7. Duplicated

Status: closed.

### Stage 7. Duplicated again

Status: current.
"""


def fake_task(tid, stage, status="done"):
    return {"id": tid, "stage": stage, "status": dashboard.STATUS_EN[status],
            "statusKey": status, "checkedBy": [], "reportCommit": None, "commit": ""}


class PlanParserTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def join(self, stages, problems):
        with patch.object(dashboard, "ROOT", self.base), patch.object(dashboard, "OUT", self.base / "out"):
            return dashboard.join_stages(stages, problems, {})

    def test_source_order_and_raw_text_preserved(self):
        stages, problems = dashboard.parse_plan(PLAN_FIXTURE)
        self.assertEqual([s["id"] for s in stages], ["6", "1", "5", "2", "8", "7", "7"])
        s6 = stages[0]
        self.join(stages, problems)
        self.assertEqual(s6["ordinal"], 0)
        self.assertEqual(s6["title"], "Public release")
        self.assertEqual(s6["declaredRaw"], "current.")
        self.assertEqual(s6["declared"], "Current")
        self.assertTrue(s6["exitCriteria"].startswith("Exit criteria: packaged CLI"))
        self.assertIn("publication is done by the human.", s6["exitCriteria"])  # multiline verbatim
        self.assertGreater(s6["line"], 0)
        self.assertEqual(s6["source"], dashboard.PLAN_REL)

    def test_fenced_code_and_heading_boundaries(self):
        stages, _ = dashboard.parse_plan(PLAN_FIXTURE)
        self.assertNotIn("9", [s["id"] for s in stages])  # heading inside ``` fence is opaque
        s2 = next(s for s in stages if s["id"] == "2")
        self.join(stages, [])
        self.assertEqual(s2["exitCriteria"], "Exit criteria: still read after a level-4 heading.")
        self.assertEqual(s2["declared"], "Closed")

    def test_malformed_and_duplicate_headings_are_diagnosed(self):
        stages, problems = dashboard.parse_plan(PLAN_FIXTURE)
        self.assertNotIn("3", [s["id"] for s in stages])  # '### Stage 3 (odd heading)' has no separator
        s8 = next(s for s in stages if s["id"] == "8")    # '### Stage 8' - id only, no title
        self.assertIsNone(s8["title"])
        self.assertTrue(any("unrecognized stage heading" in p for p in problems))
        self.assertTrue(any("has no title" in p for p in problems))
        self.join(stages, problems)
        dups = [s for s in stages if s["id"] == "7"]
        self.assertTrue(all(s["duplicate"] for s in dups))
        self.assertTrue(any("duplicate stage id '7'" in p for p in problems))

    def test_undecodable_plan_is_a_diagnostic_not_a_crash(self):
        """T-106 V-02 repro: non-UTF-8 plan bytes degrade like a missing plan."""
        plan = self.base / "project-plan.md"
        plan.write_bytes(b"\xff\xfe")
        problems = []
        with patch.object(dashboard, "PLAN", plan):
            self.assertIsNone(dashboard.read_plan(problems))
            with patch.object(Path, "read_text", side_effect=ValueError("weird plan bytes")):
                self.assertIsNone(dashboard.read_plan(problems))
        self.assertEqual(len(problems), 2)
        self.assertTrue(all("unreadable" in p for p in problems))


class StageJoinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        (self.base / "README.md").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def join(self, tasks):
        stages, self.problems = dashboard.parse_plan(PLAN_FIXTURE)
        with patch.object(dashboard, "ROOT", self.base), patch.object(dashboard, "OUT", self.base / "out"):
            stages, unmapped = dashboard.join_stages(stages, self.problems, tasks)
        return stages, unmapped

    def test_counts_denominator_and_no_percentage(self):
        tasks = {"T-1": fake_task("T-1", "5", "done"), "T-2": fake_task("T-2", "5", "in progress"),
                 "T-3": fake_task("T-3", "5", "rejected"), "T-4": fake_task("T-4", "6", "done")}
        stages, unmapped = self.join(tasks)
        s5 = next(s for s in stages if s["id"] == "5")
        self.assertEqual(s5["taskIds"], ["T-1", "T-2", "T-3"])
        self.assertEqual(s5["counts"]["total"], 3)
        self.assertEqual(s5["counts"]["accepted"], 1)
        self.assertEqual(s5["counts"]["active"], 1)
        self.assertEqual(s5["counts"]["rejected"], 1)
        self.assertNotIn("percent", s5)  # no stage-completion percentage is computed
        s1 = next(s for s in stages if s["id"] == "1")
        self.assertEqual(s1["counts"]["total"], 0)  # zero-task stage: no 0%/100% verdict exists
        self.assertEqual(unmapped, [])

    def test_duplicate_ids_never_resolve_silently(self):
        tasks = {"T-1": fake_task("T-1", "7", "done"), "T-2": fake_task("T-2", "5", "ready")}
        stages, unmapped = self.join(tasks)
        dups = [s for s in stages if s["id"] == "7"]
        self.assertEqual(len(dups), 2)
        self.assertTrue(all(s["duplicate"] for s in dups))
        self.assertEqual(dups[0]["taskIds"], [])  # ambiguous stage id: tasks are not attached
        self.assertEqual(unmapped, ["T-1"])
        self.assertTrue(any("duplicate stage id '7'" in p for p in self.problems))

    def test_unmapped_and_missing_stage_tasks_stay_visible(self):
        tasks = {"T-1": fake_task("T-1", "9", "ready"), "T-2": fake_task("T-2", "—", "ready"),
                 "T-3": fake_task("T-3", "6", "done")}
        stages, unmapped = self.join(tasks)
        self.assertEqual(sorted(unmapped), ["T-1", "T-2"])
        s6 = next(s for s in stages if s["id"] == "6")
        self.assertEqual(s6["taskIds"], ["T-3"])  # bad stage data never hides readable tasks

    def test_declared_ledger_mismatch_is_a_warning_not_a_rewrite(self):
        tasks = {"T-1": fake_task("T-1", "5", "in progress")}
        stages, _ = self.join(tasks)
        s5 = next(s for s in stages if s["id"] == "5")
        self.assertEqual(s5["declared"], "Planned")  # declared status is not rewritten
        self.assertEqual(s5["counts"]["active"], 1)  # execution counts stay independent

    def test_authored_criteria_evidence_and_coverage(self):
        stages, unmapped = self.join({})
        s5 = next(s for s in stages if s["id"] == "5")
        self.assertEqual([c["id"] for c in s5["criteria"]], ["S5-E1", "S5-E2", "S5-E3"])
        e1, e2, e3 = (c["evidence"] for c in s5["criteria"])
        self.assertEqual(e1["state"], "pass")
        self.assertEqual(e1["refKind"], "file")
        self.assertTrue(e1["refExists"])  # README.md exists in the fixture root
        self.assertEqual(e2["state"], "fail")
        self.assertTrue(e2["external"])  # external URL: a reference, never fetched
        self.assertEqual(e2["refKind"], "url")
        self.assertEqual(e3["state"], "unknown")  # declared criterion without evidence
        self.assertEqual(s5["coverage"], {"kind": "authored", "total": 3,
                                        "states": {"pass": 1, "fail": 1, "unknown": 1}})
        s1 = next(s for s in stages if s["id"] == "1")
        self.assertIsNone(s1["criteria"])
        self.assertEqual(s1["coverage"]["kind"], "unstructured")

    def test_recurring_cycle_and_historical_refs(self):
        stages, _ = self.join({})
        s5 = next(s for s in stages if s["id"] == "5")
        self.assertEqual(s5["recurring"]["kind"], "periodic audit")
        self.assertIn("never closes", s5["recurring"]["note"])
        self.assertEqual(len(s5["recurring"]["cycles"]), 1)
        cyc = s5["recurring"]["cycles"][0]
        self.assertEqual(cyc["id"], "cycle-2026-10-01")
        self.assertEqual(cyc["result"], "completed")
        self.assertEqual(cyc["refKind"], "file")
        self.assertEqual(s5["historicalRefs"], [{"label": "old audit file", "note": "outside this repo"}])

    def test_bad_refs_rejected_and_missing_marked(self):
        plan = """## Roadmap

### Stage 1. R

Status: current.

Exit criteria:
- E-1: escape
  evidence: state=pass; ref=../outside/secret.txt
- E-2: js scheme
  evidence: state=pass; ref=javascript:alert(1)
- E-3: missing file
  evidence: state=pass; ref=no/such/file.md
"""
        stages, problems = dashboard.parse_plan(plan)
        with patch.object(dashboard, "ROOT", self.base), patch.object(dashboard, "OUT", self.base / "out"):
            dashboard.join_stages(stages, problems, {})
        ev = [c["evidence"] for c in stages[0]["criteria"]]
        self.assertEqual(ev[0]["refKind"], "invalid")   # traversal rejected
        self.assertEqual(ev[1]["refKind"], "invalid")   # javascript: rejected
        self.assertEqual(ev[2]["refKind"], "file")
        self.assertFalse(ev[2]["refExists"])            # missing: shown as text, not a link
        self.assertTrue(any("escapes the project root" in p for p in problems))
        self.assertTrue(any("not allowed" in p for p in problems))
        self.assertTrue(any("not found under the project root" in p for p in problems))

    def test_unknown_declared_status_warns_and_stays_raw(self):
        plan = "### Stage 1. X\n\nStatus: under review by committee.\n"
        stages, problems = dashboard.parse_plan(plan)
        dashboard.join_stages(stages, problems, {})
        self.assertIsNone(stages[0]["declared"])
        self.assertEqual(stages[0]["declaredRaw"], "under review by committee.")
        self.assertTrue(any("not a known stage state" in p for p in problems))

    def test_missing_and_malformed_plan_never_hides_tasks(self):
        tasks = {"T-1": fake_task("T-1", "1", "ready")}
        stages, unmapped = dashboard.join_stages([], [], tasks)  # no parsed stages at all
        self.assertEqual(stages, [])
        self.assertEqual(unmapped, ["T-1"])  # task data survives a bad/missing plan


class RuntimeAllowlistTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.rt = self.base / ".runtime"
        self.rt.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def attach(self, tasks):
        problems = []
        with patch.object(dashboard, "RUNTIME", self.rt):
            missing = dashboard.attach_runtime(tasks, problems)
        return missing, problems

    def test_attempt_allowlist_drops_process_internals(self):
        (self.rt / "T-1.json").write_text(json.dumps({"taskId": "T-1", "attempts": [{
            "n": 1, "tool": "devin", "status": "exited", "exitCode": 0,
            "startedAt": "2026-10-20T00:00:00Z", "finishedAt": "2026-10-20T00:10:00Z",
            "requestedModel": "swe-2-high", "effectiveModel": "unknown",
            "limitHit": False, "stopReason": "completed", "workerTimeout": 1200,
            "pid": 1234, "machineLease": "abc", "workdir": "C:/secret/dir",
            "log": str(self.base / "x" / "T-1.1.log"),
            "launch": {"argv": ["-p", "prompt text"]}, "resourceCheck": {"argv": ["a"]},
            "quotaGroup": "devin"}]}), encoding="utf-8")
        tasks = {"T-1": fake_task("T-1", "1")}
        self.attach(tasks)
        att = tasks["T-1"]["attempts"][0]
        self.assertEqual(att["requestedModel"], "swe-2-high")
        self.assertEqual(att["effectiveModel"], "unknown")
        for banned in ("pid", "machineLease", "workdir", "launch", "resourceCheck",
                       "quotaGroup", "argv", "env", "baseline"):
            self.assertNotIn(banned, att)
        self.assertEqual(att["logRef"], "T-1.1.log")  # outside root -> basename only

    def test_routing_allowlist_and_degradation(self):
        (self.rt / "T-1.route.json").write_text(json.dumps([
            {"event": "assessment", "task": "T-1", "at": "t", "source": "jev", "status": "ok",
             "tool": "devin", "model": "swe-2-high", "recommended": ["devin-swe-2"],
             "selected": {"option": "devin-swe-2", "model": "swe-2-high", "secret": "x"},
             "availability": {"at": "t0", "source": "probe", "rawReport": "x"},
             "usage": {"input_tokens": 5}, "jev": {"model": "x", "usage": {}},
             "probabilities": {"a": 1}, "requestId": "req_1"},
            {"event": "admission", "task": "T-1", "at": "t2",
             "admitted": {"tool": "devin", "model": "swe-2-high", "tier": "high",
                          "option": "devin-swe-2", "secretField": "x"},
             "deviation": False},
            {"event": "mystery", "payload": "not exported"}]), encoding="utf-8")
        tasks = {"T-1": fake_task("T-1", "1"), "T-2": fake_task("T-2", "1")}
        self.attach(tasks)
        r = tasks["T-1"]["routing"]
        self.assertEqual(len(r["assessments"]), 1)
        self.assertNotIn("usage", r["assessments"][0])
        self.assertNotIn("probabilities", r["assessments"][0])
        self.assertNotIn("requestId", r["assessments"][0])
        self.assertEqual(r["assessments"][0]["selected"],
                         {"option": "devin-swe-2", "model": "swe-2-high"})
        self.assertEqual(r["assessments"][0]["availability"], {"at": "t0", "source": "probe"})
        self.assertEqual(len(r["events"]), 1)  # mystery event is not exported
        self.assertEqual(r["events"][0]["admitted"]["model"], "swe-2-high")
        self.assertNotIn("secretField", r["events"][0]["admitted"])
        self.assertIsNone(tasks["T-2"]["routing"])  # absent record -> unknown, not invented

    def test_verify_records_allowlist_and_stale_binding(self):
        (self.rt / "T-1.verify.json").write_text(json.dumps([
            {"n": 1, "at": "t", "ok": True, "sha": "oldsha1", "criteria": {"V-1": "pass"},
             "problems": [], "checks": [{"cmd": "c", "exit": 0, "out": "lots of output"}],
             "log": "x.log"}]), encoding="utf-8")
        t1 = fake_task("T-1", "1")
        t1["commit"] = "newsha9"  # record bound to a different artifact
        tasks = {"T-1": t1}
        self.attach(tasks)
        v = tasks["T-1"]["verifications"][0]
        self.assertEqual(v["criteria"], {"V-1": "pass"})
        self.assertTrue(v["stale"])  # artifact-mismatched evidence is labeled stale
        self.assertEqual(v["checks"], [{"cmd": "c", "exit": 0}])  # check output text is not exported

    def test_malformed_and_absent_runtime_records(self):
        (self.rt / "T-1.json").write_text("{ not json", encoding="utf-8")
        tasks = {"T-1": fake_task("T-1", "1"), "T-2": fake_task("T-2", "1")}
        missing, problems = self.attach(tasks)
        self.assertFalse(missing)
        self.assertIsNone(tasks["T-1"]["attempts"])
        self.assertIsNone(tasks["T-2"]["attempts"])
        self.assertTrue(any("T-1.json" in p for p in problems))
        with patch.object(dashboard, "RUNTIME", self.base / "nope"):
            problems2 = []
            self.assertTrue(dashboard.attach_runtime(tasks, problems2))
            self.assertIsNone(tasks["T-1"]["attempts"])  # absent dir: not recorded, not a crash


class RoadmapPayloadTests(unittest.TestCase):
    def test_demo_roadmap_fixture_covers_plan_cases(self):
        g, _, _ = dashboard.demo_graph()
        self.assertEqual(g["schemaVersion"], 1)
        self.assertTrue(g["provenance"]["synthetic"])
        by_id = {}
        for s in g["stages"]:
            by_id.setdefault(s["id"], []).append(s)
        self.assertEqual(len(by_id), 6)  # six unique stages; the duplicate adds a 7th record
        self.assertEqual(len(g["stages"]), 7)
        self.assertTrue(all(s["duplicate"] for s in by_id["3"]))
        zero = [s["id"] for s in g["stages"] if s["counts"]["total"] == 0]
        self.assertTrue({"1", "2", "3", "4"} <= set(zero))  # zero-task stages stay visible
        s4 = by_id["4"][0]
        self.assertEqual(len(s4["recurring"]["cycles"]), 1)  # recurring stage, one cycle
        s6 = by_id["6"][0]
        states = s6["coverage"]["states"]
        self.assertEqual(states.get("fail"), 1)      # failed external evidence
        self.assertEqual(states.get("pending"), 1)   # pending external evidence
        self.assertGreater(s6["counts"]["accepted"], 0)  # accepted tasks alongside
        s5 = by_id["5"][0]
        self.assertEqual(s5["declared"], "Planned")  # active planned stage
        self.assertGreater(s5["counts"]["active"], 0)
        self.assertIn("T-108", g["diagnostics"]["unmappedTaskIds"])
        self.assertTrue(any("duplicate stage id" in w for w in g["diagnostics"]["warnings"]))
        t103 = next(t for t in g["tasks"] if t["id"] == "T-103")
        self.assertEqual(len(t103["attempts"]), 2)   # recorded attempt history
        self.assertIsNotNone(t103["routing"])

    def test_demo_determinism_includes_roadmap(self):
        g1, _, _ = dashboard.demo_graph()
        g2, _, _ = dashboard.demo_graph()
        self.assertEqual(json.dumps(g1, sort_keys=True), json.dumps(g2, sort_keys=True))

    def test_negative_verdict_and_stale_link_stay_distinct(self):
        g, _, _ = dashboard.demo_graph()
        t103 = next(t for t in g["tasks"] if t["id"] == "T-103")
        self.assertTrue(t103["checkedBy"][0]["stale"])  # stale Verifies SHA labeled stale
        warnings = g["diagnostics"]["warnings"]
        self.assertTrue(any("stale link" in w for w in warnings))


class RoadmapPageTests(unittest.TestCase):
    """T-046: the roadmap page consumes the shared payload; existing pages stay wired."""

    def page(self, demo=True):
        out = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(out, ignore_errors=True))
        with patch.object(dashboard, "OUT", out), contextlib.redirect_stdout(io.StringIO()):
            dashboard.main(["--demo"] if demo else [])
        return (out / "roadmap.html").read_text(encoding="utf-8")

    def test_roadmap_page_is_self_contained(self):
        page = self.page()
        for marker in ("/*COMMON_CSS*/", "/*COMMON_JS*/", "/*FILTERBAR_CSS*/",
                       "/*FILTERBAR_JS*/", "/*ROADMAP_CSS*/", "/*ROADMAP_JS*/", "__DATA__"):
            self.assertNotIn(marker, page)
        self.assertIn("const DATA = {", page)  # payload embedded, no external fetch
        self.assertNotIn("http://", page.split("const DATA =")[0].split("</script>")[0])

    def test_all_pages_carry_roadmap_navigation(self):
        for tpl in ("template.html", "graph_template.html", "roadmap_template.html"):
            page = dashboard.render(tpl)
            self.assertIn('href="roadmap.html"', page, tpl)
            self.assertIn('href="index.html"', page, tpl)
            self.assertIn('href="graph.html"', page, tpl)

    def test_roadmap_vocabulary_keeps_the_three_facts_separate(self):
        js = (dashboard.HERE / "roadmap.js").read_text(encoding="utf-8")
        for label in ("Declared status", "Local tasks", "Exit-criteria evidence",
                      "No local tasks", "not tracked per criterion", "Unmapped",
                      "Active blockers", "Recurring:", "stale", "not recorded", "unknown"):
            self.assertIn(label, js)
        tpl = (dashboard.HERE / "roadmap_template.html").read_text(encoding="utf-8")
        self.assertIn("stage list unaffected", tpl)      # filters slice tasks only
        self.assertIn("C.taskCard", tpl)                 # drill-down reuses the shared card
        self.assertIn('C.initHeader("roadmap"', tpl)     # shared header/theme/built chrome
        for view in ("cards", "journey", "matrix"):      # all three approved layouts
            self.assertIn(f'data-v="{view}"', tpl)

    def test_roadmap_page_marks_demo_and_shows_diagnostics(self):
        page = self.page()
        self.assertIn("DEMO DATA", page)
        self.assertIn("Diagnostics — build snapshot", page)
        self.assertIn("Payload provenance", page)
        self.assertIn("unmappedTaskIds", page)           # the payload field travels to the page

    def test_roadmap_runtime_sections_allowlist_only(self):
        js = (dashboard.HERE / "roadmap.js").read_text(encoding="utf-8")
        for banned in ("argv", "env", "pid", "quota", "machineLease", "workdir"):
            self.assertNotIn(banned, js)


GOLDEN_DEMO = json.loads(r"""{"commits": [["2026-10-10T12:00:00+03:00", "demo ledger update 0"], ["2026-10-11T12:00:00+03:00", "demo ledger update 1"], ["2026-10-12T12:00:00+03:00", "demo ledger update 2"], ["2026-10-13T12:00:00+03:00", "demo ledger update 3"], ["2026-10-14T12:00:00+03:00", "demo ledger update 4"], ["2026-10-15T12:00:00+03:00", "demo ledger update 5"], ["2026-10-16T12:00:00+03:00", "demo ledger update 6"], ["2026-10-17T12:00:00+03:00", "demo ledger update 7"], ["2026-10-18T12:00:00+03:00", "demo ledger update 8"]], "edges": [{"from": "T-105", "kind": "dep", "t0": "2026-10-15T12:00:00+03:00", "t1": null, "to": "T-106"}, {"from": "T-103", "kind": "dep", "t0": "2026-10-14T12:00:00+03:00", "t1": null, "to": "T-107"}, {"from": "T-105", "kind": "succ", "to": "T-106"}, {"from": "T-102", "kind": "check", "sha": "abc1234", "stale": false, "to": "T-101"}, {"from": "T-104", "kind": "check", "sha": "deadbeef", "stale": true, "to": "T-103"}], "metrics": {"cost": null, "definitions": {"attempts": "Launcher attempts recorded in .agentflow/tasks/.runtime/T-NNN.json.", "cost": "Token, context and cost telemetry is not recorded by AgentFlow tools; reported as N/A.", "firstPassGateRate": "First recorded `gate.py verify` result per task (.agentflow/tasks/.runtime/T-NNN.verify.json record #1, field `ok`). A later PASS never rewrites the first attempt. Denominator: only tasks with at least one verify record; tasks without records are counted in tasksWithoutEvidence, never as failures.", "leadSeconds": "Last attempt finishedAt minus first attempt startedAt. null (N/A) when attempt history or timestamps are missing; zero is never substituted for missing evidence.", "routingOutcomes": "Jev route recommendations (T-NNN.route.json) vs the tool of the last recorded attempt and the final ledger Status. Descriptive only; no causal model-quality or efficiency claim.", "testerVerdicts": "Verdict line of tester Task Files. pass / partial / unverified / fail are all valid reports: a fail verdict is a completed negative review, not a worker failure."}, "firstPassGateRate": [{"firstVerifyPass": 1, "role": "developer", "tasks": 2, "tool": "codex"}, {"firstVerifyPass": 1, "role": "tester", "tasks": 1, "tool": "devin"}], "leadSeconds": [{"max": 7200.0, "median": 5400.0, "min": 3600.0, "role": "developer", "tasks": 2, "tool": "codex"}], "note": "DEMO fixture; not real project evidence.", "tasksWithoutEvidence": 5, "testerVerdicts": {"none-recorded": 1, "pass": 1}}, "pings": ["2026-10-10T12:00:00+03:00", "2026-10-10T19:12:00+03:00", "2026-10-11T02:24:00+03:00", "2026-10-11T09:36:00+03:00", "2026-10-11T16:48:00+03:00", "2026-10-12T00:00:00+03:00", "2026-10-12T07:12:00+03:00", "2026-10-12T14:24:00+03:00", "2026-10-12T21:36:00+03:00", "2026-10-13T04:48:00+03:00", "2026-10-13T12:00:00+03:00", "2026-10-13T19:12:00+03:00", "2026-10-14T02:24:00+03:00", "2026-10-14T09:36:00+03:00", "2026-10-14T16:48:00+03:00", "2026-10-15T00:00:00+03:00", "2026-10-15T07:12:00+03:00", "2026-10-15T14:24:00+03:00", "2026-10-15T21:36:00+03:00", "2026-10-16T04:48:00+03:00", "2026-10-16T12:00:00+03:00", "2026-10-16T19:12:00+03:00", "2026-10-17T02:24:00+03:00", "2026-10-17T09:36:00+03:00"], "tasks": [{"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "Outcome: done\nVerdict: completed", "c0": 1791622800.0, "chain": "T-101", "check": "Tester assigned", "checkedBy": [{"id": "T-102", "sha": "abc1234", "stale": false, "status": "Done", "verdict": "completed"}], "commit": "abc1234", "created": "2026-10-10", "createdAt": "2026-10-10T12:00:00+03:00", "deps": [], "endAt": "2026-10-12T12:00:00+03:00", "file": ".agentflow/tasks/T-101-demo.md", "fileHref": "#", "final": true, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-101", "ind": "none", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "done", "outcomeSrc": "Outcome", "reportCommit": {"label": "Change:", "line": "Change: abc1234", "sha": "abc1234"}, "result": "Completed by worker", "resultFull": "Outcome: done\nVerdict: completed", "resultText": "Outcome: done\nVerdict: completed", "role": "Developer", "roleKey": "developer", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "1", "status": "Done", "statusKey": "done", "timeline": [["2026-10-10T12:00:00+03:00", "Ready"], ["2026-10-11T00:00:00+03:00", "In progress"], ["2026-10-12T12:00:00+03:00", "Done"]], "title": "Launcher parity fix", "tool": "Codex", "toolRaw": "codex", "updated": "2026-10-12", "verdict": "completed", "verifies": null, "waitsOwner": false, "work": ["2026-10-10T21:36:00+03:00", "2026-10-11T09:36:00+03:00"]}, {"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "Outcome: done\nVerdict: completed", "c0": 1791709200.0, "chain": "T-102", "check": "—", "checkedBy": [], "commit": "def5678", "created": "2026-10-11", "createdAt": "2026-10-11T12:00:00+03:00", "deps": [], "endAt": "2026-10-13T12:00:00+03:00", "file": ".agentflow/tasks/T-102-demo.md", "fileHref": "#", "final": true, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-102", "ind": "tester", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "done", "outcomeSrc": "Outcome", "reportCommit": {"label": "Change:", "line": "Change: def5678", "sha": "def5678"}, "result": "Completed by worker", "resultFull": "Outcome: done\nVerdict: completed", "resultText": "Outcome: done\nVerdict: completed", "role": "Tester", "roleKey": "tester", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "1", "status": "Done", "statusKey": "done", "timeline": [["2026-10-11T12:00:00+03:00", "Ready"], ["2026-10-12T00:00:00+03:00", "In progress"], ["2026-10-13T12:00:00+03:00", "Done"]], "title": "Verify launcher parity", "tool": "devin", "toolRaw": "devin", "updated": "2026-10-13", "verdict": "completed", "verifies": {"sha": "abc1234", "stale": false, "task": "T-101"}, "waitsOwner": false, "work": []}, {"attemptsHint": 0, "blockedBy": [], "blocks": ["T-107"], "body": "Outcome: done\nVerdict: completed", "c0": 1791795600.0, "chain": "T-103", "check": "Tester assigned (stale link)", "checkedBy": [{"id": "T-104", "sha": "deadbeef", "stale": true, "status": "In progress", "verdict": ""}], "commit": "9f00dc1", "created": "2026-10-12", "createdAt": "2026-10-12T12:00:00+03:00", "deps": [], "endAt": null, "file": ".agentflow/tasks/T-103-demo.md", "fileHref": "#", "final": false, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-103", "ind": "tester", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "done", "outcomeSrc": "Outcome", "reportCommit": {"label": "Change:", "line": "Change: 9f00dc1", "sha": "9f00dc1"}, "result": "Completed by worker", "resultFull": "Outcome: done\nVerdict: completed", "resultText": "Outcome: done\nVerdict: completed", "role": "Developer", "roleKey": "developer", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "2", "status": "In review", "statusKey": "review", "timeline": [["2026-10-12T12:00:00+03:00", "Ready"], ["2026-10-13T00:00:00+03:00", "In progress"], ["2026-10-14T12:00:00+03:00", "In review"]], "title": "Honest metrics dashboard", "tool": "devin", "toolRaw": "devin", "updated": "2026-10-14", "verdict": "completed", "verifies": null, "waitsOwner": false, "work": ["2026-10-12T21:36:00+03:00", "2026-10-13T09:36:00+03:00"]}, {"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "Outcome: in progress\nVerdict: ", "c0": 1791882000.0, "chain": "T-104", "check": "—", "checkedBy": [], "commit": "", "created": "2026-10-13", "createdAt": "2026-10-13T12:00:00+03:00", "deps": [], "endAt": null, "file": ".agentflow/tasks/T-104-demo.md", "fileHref": "#", "final": false, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-104", "ind": "tester", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "in progress", "outcomeSrc": "Outcome", "reportCommit": null, "result": "No report", "resultFull": "Outcome: in progress\nVerdict: ", "resultText": "Outcome: in progress\nVerdict: ", "role": "Tester", "roleKey": "tester", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "2", "status": "In progress", "statusKey": "in progress", "timeline": [["2026-10-13T12:00:00+03:00", "Ready"], ["2026-10-13T12:00:00+03:00", "In progress"]], "title": "Verify metrics dashboard", "tool": "Codex", "toolRaw": "codex", "updated": "2026-10-15", "verdict": "", "verifies": {"sha": "deadbeef", "stale": true, "task": "T-103"}, "waitsOwner": false, "work": []}, {"attemptsHint": 0, "blockedBy": [], "blocks": ["T-106"], "body": "Outcome: blocked\nVerdict: ", "c0": 1791968400.0, "chain": "T-106", "check": "No independent check", "checkedBy": [], "commit": "", "created": "2026-10-14", "createdAt": "2026-10-14T12:00:00+03:00", "deps": [], "endAt": "2026-10-16T12:00:00+03:00", "file": ".agentflow/tasks/T-105-demo.md", "fileHref": "#", "final": true, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-105", "ind": "none", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "blocked", "outcomeSrc": "Outcome", "reportCommit": null, "result": "Worker blocked", "resultFull": "Outcome: blocked\nVerdict: ", "resultText": "Outcome: blocked\nVerdict: ", "role": "Developer", "roleKey": "developer", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "2", "status": "Rejected", "statusKey": "rejected", "timeline": [["2026-10-14T12:00:00+03:00", "Ready"], ["2026-10-15T00:00:00+03:00", "In progress"], ["2026-10-16T12:00:00+03:00", "Rejected"]], "title": "Old probe cleanup", "tool": "Antigravity", "toolRaw": "agy", "updated": "2026-10-16", "verdict": "", "verifies": null, "waitsOwner": false, "work": ["2026-10-14T21:36:00+03:00", "2026-10-15T09:36:00+03:00"]}, {"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "Outcome: in progress\nVerdict: ", "c0": 1792054800.0, "chain": "T-106", "check": "No independent check", "checkedBy": [], "commit": "", "created": "2026-10-15", "createdAt": "2026-10-15T12:00:00+03:00", "deps": ["T-105"], "endAt": null, "file": ".agentflow/tasks/T-106-demo.md", "fileHref": "#", "final": false, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-106", "ind": "none", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "in progress", "outcomeSrc": "Outcome", "reportCommit": null, "result": "No report", "resultFull": "Outcome: in progress\nVerdict: ", "resultText": "Outcome: in progress\nVerdict: ", "role": "Developer", "roleKey": "developer", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "2", "status": "In progress", "statusKey": "in progress", "timeline": [["2026-10-15T12:00:00+03:00", "Ready"], ["2026-10-15T12:00:00+03:00", "In progress"]], "title": "Successor probe cleanup", "tool": "Codex", "toolRaw": "codex", "updated": "2026-10-17", "verdict": "", "verifies": null, "waitsOwner": false, "work": ["2026-10-15T21:36:00+03:00", "2026-10-16T09:36:00+03:00"]}, {"attemptsHint": 0, "blockedBy": ["T-103"], "blocks": [], "body": "", "c0": 1792141200.0, "chain": "T-107", "check": "—", "checkedBy": [], "commit": "", "created": "2026-10-16", "createdAt": "2026-10-16T12:00:00+03:00", "deps": ["T-103"], "endAt": null, "file": ".agentflow/tasks/T-107-demo.md", "fileHref": "#", "final": false, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-107", "ind": "none", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "", "outcomeSrc": "", "reportCommit": null, "result": "No report", "resultFull": "", "resultText": "", "role": "Deployer", "roleKey": "deployer", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "2", "status": "Blocked", "statusKey": "blocked", "timeline": [["2026-10-16T12:00:00+03:00", "Ready"], ["2026-10-17T00:00:00+03:00", "In progress"]], "title": "Deploy staging update", "tool": "Claude Code", "toolRaw": "claude", "updated": "2026-10-18", "verdict": "", "verifies": null, "waitsOwner": false, "work": []}, {"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "", "c0": 1792227600.0, "chain": "T-108", "check": "No independent check", "checkedBy": [], "commit": "", "created": "2026-10-17", "createdAt": "2026-10-17T12:00:00+03:00", "deps": [], "endAt": "2026-10-19T12:00:00+03:00", "file": ".agentflow/tasks/T-108-demo.md", "fileHref": "#", "final": true, "goal": "Demo goal text.", "goalFull": "Demo goal text.", "id": "T-108", "ind": "none", "notes": "DEMO DATA row", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "", "outcomeSrc": "", "reportCommit": null, "result": "No report", "resultFull": "", "resultText": "", "role": "Developer", "roleKey": "developer", "size": {"add": 80, "codeAdd": 60, "codeDel": 15, "codeFiles": 3, "commits": 2, "del": 20, "files": 5}, "sizeCls": "S", "sizeN": 75, "stage": "1", "status": "Cancelled", "statusKey": "cancelled", "timeline": [["2026-10-17T12:00:00+03:00", "Ready"], ["2026-10-18T00:00:00+03:00", "In progress"], ["2026-10-19T12:00:00+03:00", "Cancelled"]], "title": "Cancelled experiment", "tool": "Codex", "toolRaw": "codex", "updated": "2026-10-19", "verdict": "", "verifies": null, "waitsOwner": false, "work": ["2026-10-17T21:36:00+03:00", "2026-10-18T09:36:00+03:00"]}]}""")  # demo payload produced by the pre-roadmap build on the same fixture


GOLDEN_TASKS = json.loads(r"""[{"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "# T-001: Change something\nRole: developer\nTool: codex\nIndependent check: tester\n## Goal\nDemo goal.\n## Result\nOutcome: completed\nChange: 9f00dc1\n", "c0": 0, "chain": "T-001", "check": "Tester required, no report", "checkedBy": [], "commit": "9f00dc1", "created": "2026-10-16", "deps": [], "file": "T-001-dev.md", "fileHref": "../T-001-dev.md", "final": true, "goal": "Demo goal.", "goalFull": "Demo goal.", "id": "T-001", "ind": "tester", "notes": "", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "completed", "outcomeSrc": "Outcome", "reportCommit": {"label": "Change:", "line": "9f00dc1", "sha": "9f00dc1"}, "result": "Completed by worker", "resultFull": "Outcome: completed\nChange: 9f00dc1", "resultText": "Outcome: completed Change: 9f00dc1", "role": "Developer", "roleKey": "developer", "stage": "1", "status": "Done", "statusKey": "done", "title": "Change something", "tool": "not set", "toolRaw": "", "updated": "2026-10-16", "verdict": "", "verifies": null, "waitsOwner": false}, {"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "# T-002: Verify the delivery of T-001 by hand\nRole: tester\nTool: devin\nVerifies: T-003 @ deadbee\n## Goal\nDemo goal.\n## Result\nOutcome: completed\nVerdict: fail\n", "c0": 0, "chain": "T-002", "check": "—", "checkedBy": [], "commit": "", "created": "2026-10-16", "deps": [], "file": "T-002-check.md", "fileHref": "../T-002-check.md", "final": true, "goal": "Demo goal.", "goalFull": "Demo goal.", "id": "T-002", "ind": "", "notes": "", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "completed", "outcomeSrc": "Outcome", "reportCommit": null, "result": "Completed by worker", "resultFull": "Outcome: completed\nVerdict: fail", "resultText": "Outcome: completed Verdict: fail", "role": "Tester", "roleKey": "tester", "stage": "1", "status": "Done", "statusKey": "done", "title": "Verify the delivery of T-001 by hand", "tool": "not set", "toolRaw": "", "updated": "2026-10-16", "verdict": "fail", "verifies": {"sha": "deadbee", "stale": true, "task": "T-003"}, "waitsOwner": false}, {"attemptsHint": 0, "blockedBy": [], "blocks": [], "body": "# T-003: Another change\nRole: developer\nTool: codex\nIndependent check: none - local\n## Goal\nDemo goal.\n## Result\nOutcome: completed\nChange: abc1234\n", "c0": 0, "chain": "T-003", "check": "Tester: fail (stale link)", "checkedBy": [{"id": "T-002", "sha": "deadbee", "stale": true, "status": "Done", "verdict": "fail"}], "commit": "abc1234", "created": "2026-10-16", "deps": [], "file": "T-003-other.md", "fileHref": "../T-003-other.md", "final": true, "goal": "Demo goal.", "goalFull": "Demo goal.", "id": "T-003", "ind": "none", "notes": "", "origin": "Orchestrator", "originWhy": "default: the Task File is written by the Orchestrator", "outcomeRaw": "completed", "outcomeSrc": "Outcome", "reportCommit": {"label": "Change:", "line": "abc1234", "sha": "abc1234"}, "result": "Completed by worker", "resultFull": "Outcome: completed\nChange: abc1234", "resultText": "Outcome: completed Change: abc1234", "role": "Developer", "roleKey": "developer", "stage": "1", "status": "Done", "statusKey": "done", "title": "Another change", "tool": "not set", "toolRaw": "", "updated": "2026-10-16", "verdict": "", "verifies": null, "waitsOwner": false}]""")  # task payload of the pre-roadmap build on the fixed 3-task fixture above


class TaskFieldRegressionTests(unittest.TestCase):
    """P-08: existing task fields are unchanged vs the pre-change build on the same inputs."""
    def test_fixed_fixture_task_fields_match_pre_roadmap_build(self):
        """Every field the pre-change build emitted for the DEV/TESTER/OTHER fixture is identical."""
        rows = [row("T-001", "Change something", "developer", commit="9f00dc1"),
                row("T-002", "Verify the delivery of T-001 by hand", "tester"),
                row("T-003", "Another change", "developer", commit="abc1234")]
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        (base / "T-001-dev.md").write_text(DEV, encoding="utf-8")
        (base / "T-002-check.md").write_text(TESTER, encoding="utf-8")
        (base / "T-003-other.md").write_text(OTHER, encoding="utf-8")
        files = {"T-001": base / "T-001-dev.md", "T-002": base / "T-002-check.md",
                 "T-003": base / "T-003-other.md"}
        with patch.object(dashboard, "ROOT", base), patch.object(dashboard, "OUT", base / "out"):
            tasks, goal_text = dashboard.build_tasks(rows, files, {}, {})
            dashboard.link_checks(tasks)
            graph = dashboard.finish_graph(tasks, goal_text, [], [], [], [])
        self.assertEqual([t["id"] for t in graph["tasks"]], [t["id"] for t in GOLDEN_TASKS])
        for old, new in zip(GOLDEN_TASKS, graph["tasks"]):
            for k, v in old.items():
                self.assertEqual(new.get(k), v, f"task {old['id']} field {k!r} changed")

    def test_demo_task_fields_match_pre_roadmap_build(self):
        """Demo payload: all pre-existing fields identical; `stage` differs only because the
        fixture input was reassigned across roadmap stages for P-07 coverage."""
        g, _, _ = dashboard.demo_graph()
        self.assertEqual([t["id"] for t in g["tasks"]], [t["id"] for t in GOLDEN_DEMO["tasks"]])
        for old, new in zip(GOLDEN_DEMO["tasks"], g["tasks"]):
            for k, v in old.items():
                if k == "stage":
                    continue  # fixture input changed, not a computed field regression
                self.assertEqual(new.get(k), v, f"task {old['id']} field {k!r} changed")
        for name in ("edges", "commits", "pings", "metrics"):
            self.assertEqual(g[name], GOLDEN_DEMO[name], name)


if __name__ == "__main__":
    unittest.main()
