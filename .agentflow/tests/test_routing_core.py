"""Routing core (T-074): the persisted assessment schema and the admission APIs run_task.py/tick.py
will call (launch wiring is T-076). In-process tests pin FLOW_ROOT, the options file and the
environment; the end-to-end tests run route.py in a disposable project against the local TypeSafe
stand-in - no network, no real key, no real machine registry."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import gate  # noqa: E402
import quota_groups  # noqa: E402
import route  # noqa: E402

TASK = """# T-099: Probe

Role: developer
Tool: devin
Model: swe-2-high
Stage: 1
Depends on: none
Branch: t-099-probe
Worktree: W:/nowhere/t-099
Independent check: none - probe
Resume: none

## Goal

Add a settings switch.

## Allowed files

- `src/`

## Acceptance criteria

- [ ] The switch persists.

## Checks

- `git --version` - git runs

## Result
"""

OPTS = {"options": {
    "devin-swe-2": {"tool": "devin",
                    "model_by_effort": {"medium": "swe-2-medium", "high": "swe-2-high",
                                        "max": "swe-2-max"},
                    "default_effort": "high", "quota_group": "devin"},
    "codex-ultra": {"tool": "codex", "model": "gpt-x",
                    "efforts": ["low", "medium", "high", "xhigh", "max", "ultra"],
                    "quota_group": "codex"},
    "agy-flash": {"tool": "agy",
                  "model_by_effort": {"medium": "gem-flash-medium", "high": "gem-flash-high"},
                  "quota_group": "agy-gemini"},
    "claude-plain": {"tool": "claude", "model": "sonnet", "tier": "medium",
                     "quota_group": "claude"},
}}


class Fake(BaseHTTPRequestHandler):
    answers = {}
    status = 200
    seen = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Fake.seen.append(body)
        if Fake.status != 200:
            data = json.dumps({"error": "rejected"}).encode()
        else:
            data = json.dumps({"model": "jev-1.13.0", "answers": Fake.answers,
                               "usage": {"input_tokens": 300, "output_tokens": 30}}).encode()
        self.send_response(Fake.status)
        self.send_header("x-typesafe-request-id", "req_core")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def answers(choice="devin-swe-2", confidence=0.95, effort="high",
            probabilities=None, complexity=0.4):
    return {"option": {"type": "choice", "choice": choice, "confidence": confidence,
                       "probabilities": probabilities or {choice: 0.9}},
            "effort": {"type": "choice", "choice": effort, "confidence": 0.95,
                       "probabilities": {effort: 0.9}},
            "complexity": {"type": "score", "score": complexity, "confidence": 0.9,
                           "probabilities": {"0": 0.6, "1": 0.3, "2": 0.1}}}


class RoutingCoreTests(unittest.TestCase):
    """In-process: pure functions and the admission APIs on a disposable task file + record dir."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.task_path = self.dir / "T-099-probe.md"
        self.task_path.write_text(TASK, encoding="utf-8")
        self.rt = self.dir / ".runtime"
        self.rt.mkdir()
        opts_path = self.dir / "model-options.json"
        opts_path.write_text(json.dumps(OPTS), encoding="utf-8")
        patcher = patch.object(quota_groups, "OPTIONS", opts_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.t = {"id": "T-099", "file": str(self.task_path), "model": "swe-2-high", "effort": None}

    def record(self, **kw):
        rec = {"event": "assessment", "schemaVersion": 1, "task": "T-099", "source": "jev",
               "at": "2026-10-18T00:00:00Z", "band": "high", "status": "ok",
               "requirementsHash": gate.requirements_hash(TASK),
               "required": {"effort": "high", "complexity": 0.4},
               "selected": {"option": "devin-swe-2", "tool": "devin",
                            "model": "swe-2-high", "effort": None}}
        rec.update(kw)
        route._log("T-099", rec, self.rt)
        return rec

    # --- requirements binding -------------------------------------------------
    def test_requirements_hash_ignores_routing_fields_and_binds_the_contract(self):
        h = gate.requirements_hash(TASK)
        routed = TASK.replace("Tool: devin", "Tool: codex") \
                     .replace("Model: swe-2-high", "Model: gpt-x, effort=max") \
                     .replace("Resume: none", "Resume: attempt-2\nBackup Tool: agy\n"
                                            "Backup Model: gem\nRouting exception: human approved")
        self.assertEqual(h, gate.requirements_hash(routed),
                         "Tool/Model/Backup/Routing exception/Resume lines never invalidate an assessment")
        changed = TASK.replace("Add a settings switch.", "Add two switches.")
        self.assertNotEqual(h, gate.requirements_hash(changed),
                            "a changed contract is a different requirement")

    # --- persisted record ------------------------------------------------------
    def test_log_and_history_follow_the_configured_flow_root(self):
        other = self.dir / "relocated" / ".agentflow"
        with patch.object(route, "FLOW_ROOT", other):
            route._log("T-007", {"event": "assessment", "schemaVersion": 1, "task": "T-007",
                                 "status": "ok"})
            self.assertEqual([e["task"] for e in route.history("T-007")], ["T-007"])
            self.assertEqual(route.latest_assessment("T-007")["status"], "ok")
        self.assertTrue((other / "tasks" / ".runtime" / "T-007.route.json").exists())
        self.assertFalse((self.rt / "T-007.route.json").exists())

    def test_history_rejects_malformed_and_foreign_records(self):
        (self.rt / "T-099.route.json").write_text('{"not": "a list"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            route.history("T-099", self.rt)
        (self.rt / "T-099.route.json").write_text(
            json.dumps([{"event": "assessment", "task": "T-123"}]), encoding="utf-8")
        with self.assertRaises(ValueError):
            route.history("T-099", self.rt)
        (self.rt / "T-099.route.json").write_text(
            json.dumps([{"event": "admission", "task": "T-099"}]), encoding="utf-8")
        self.assertIsNone(route.latest_assessment("T-099", self.rt),
                          "a non-assessment event admits nothing")

    # --- adequacy and ordering ---------------------------------------------------
    def test_adequacy_is_capability_and_effort_based(self):
        o = OPTS["options"]["devin-swe-2"]
        self.assertIsNone(route.adequate_reason(o, {"effort": "max", "complexity": 0.4}))
        self.assertIn("effort", route.adequate_reason(o, {"effort": "ultra", "complexity": 0.4}))
        capped = dict(o, max_complexity=1)
        self.assertIn("cap", route.adequate_reason(capped, {"effort": "high", "complexity": 1.8}))
        tiered = OPTS["options"]["claude-plain"]
        self.assertIsNone(route.adequate_reason(tiered, {"effort": "medium"}))
        self.assertIn("effort", route.adequate_reason(tiered, {"effort": "high"}),
                      "an effort-less option reaches only its declared tier")

    def test_resolve_requirement_never_resolves_below(self):
        o = OPTS["options"]["devin-swe-2"]
        self.assertEqual(route.resolve_requirement(o, "high"), ("swe-2-high", None, "high"))
        self.assertEqual(route.resolve_requirement(o, "ultra"), (None, None, None))
        codex = OPTS["options"]["codex-ultra"]
        self.assertEqual(route.resolve_requirement(codex, "low"), ("gpt-x", "low", "low"))

    def test_admission_order_floor_then_preferred_then_rest(self):
        cfg = {"floor": {"option": "devin-swe-2", "effort": "high"}, "prefer": ["devin"]}
        cands = OPTS["options"]
        probs = {"codex-ultra": 0.9, "agy-flash": 0.7, "devin-swe-2": 0.05}
        order = route.admission_order(cands, cfg, probs)
        self.assertEqual(order[0], "devin-swe-2", "the floor option leads when it can meet it")
        self.assertEqual(order[1], "codex-ultra", "Jev ranking orders the non-preferred remainder")
        nofloor = route.admission_order({"codex-ultra": cands["codex-ultra"],
                                         "agy-flash": cands["agy-flash"]},
                                        cfg, probs)
        self.assertEqual(nofloor[0], "codex-ultra")

    # --- record-level admission ---------------------------------------------------
    def test_missing_stale_failed_and_low_confidence_are_diagnosable_blocks(self):
        problems, ev = route.assessment_problems(self.t, self.rt)
        self.assertIsNone(ev)
        self.assertIn("no recorded routing assessment", problems[0])
        for status, want in (("blocked", "'blocked'"), ("failed", "'failed'"),
                             ("low-confidence", "'low-confidence'")):
            self.record(status=status, blocked="nothing adequate" if status == "blocked" else None,
                        error="no key" if status == "failed" else None)
            problems, ev = route.assessment_problems(self.t, self.rt)
            self.assertIsNone(ev)
            self.assertIn(want, problems[0])
        self.record(status="ok", requirementsHash="0" * 64)
        problems, ev = route.assessment_problems(self.t, self.rt)
        self.assertIsNone(ev)
        self.assertIn("stale", problems[0])

    def test_ok_assessment_gives_jev_evidence(self):
        self.record()
        problems, ev = route.assessment_problems(self.t, self.rt)
        self.assertEqual(problems, [])
        self.assertEqual(ev["source"], "jev")
        self.assertEqual(ev["required"], {"effort": "high", "complexity": 0.4})
        self.assertEqual(ev["selected"]["model"], "swe-2-high")

    def test_human_exception_is_distinguishable_not_jev_evidence(self):
        exc = TASK.replace("Resume: none", "Resume: none\nRouting exception: approved by the human")
        self.task_path.write_text(exc, encoding="utf-8")
        self.record(status="failed", error="no key")
        problems, ev = route.assessment_problems(self.t, self.rt)
        self.assertEqual(problems, [])
        self.assertEqual(ev["source"], "human-exception")
        self.assertEqual(ev["reason"], "approved by the human")
        self.assertTrue(ev["overrode"], "the exception names what it overrode")
        route.log_admission("T-099", ev, self.rt)
        event = route.history("T-099", self.rt)[-1]
        self.assertEqual(event["event"], "human-exception",
                         "the override is recorded as a human decision, never as Jev evidence")
        self.assertEqual(event["reason"], "approved by the human")

    # --- resolved-identity admission ---------------------------------------------------
    def test_admission_checks_the_resolved_identity_after_env(self):
        self.record()
        with patch.dict(os.environ, {}, clear=True):
            problems, ev = route.admission(self.t, "devin", self.rt)
        self.assertEqual(problems, [])
        self.assertEqual(ev["admitted"]["tier"], "high")
        self.assertFalse(ev["deviation"], "the launch matches the recorded selection")
        # a stronger model is admitted and the deviation stays visible
        strong = dict(self.t, model="swe-2-max")
        with patch.dict(os.environ, {}, clear=True):
            problems, ev = route.admission(strong, "devin", self.rt)
        self.assertEqual(problems, [])
        self.assertTrue(ev["deviation"])

    def test_header_or_env_downgrade_is_refused(self):
        self.record()
        low = dict(self.t, model="swe-2-medium")
        with patch.dict(os.environ, {}, clear=True):
            problems, ev = route.admission(low, "devin", self.rt)
        self.assertIsNone(ev)
        self.assertIn("below the recorded requirement", problems[0])
        no_model = dict(self.t, model=None)
        with patch.dict(os.environ, {"AGENTFLOW_DEVIN_ARGS": "--model swe-2-medium"}, clear=True):
            problems, ev = route.admission(no_model, "devin", self.rt)
        self.assertIn("below the recorded requirement", problems[0],
                      "an env-injected weaker model cannot slip past the assessment")
        with patch.dict(os.environ, {"AGENTFLOW_DEVIN_ARGS": "--model invented-x"}, clear=True):
            problems, ev = route.admission(no_model, "devin", self.rt)
        self.assertIn("not in model-options.json", problems[0],
                      "an unconfigured model is unverifiable, so it refuses")

    def test_backup_must_meet_the_same_requirement(self):
        self.record()
        ok, _ = route.backup_ok("T-099", "devin", "swe-2-high", None, self.rt)
        self.assertTrue(ok)
        ok, reason = route.backup_ok("T-099", "devin", "swe-2-medium", None, self.rt)
        self.assertFalse(ok)
        self.assertIn("below the recorded requirement", reason)
        ok, _ = route.backup_ok("T-099", "agy", "gem-flash-medium", None, self.rt)
        self.assertFalse(ok, "another tool's weaker backup stays ineligible")
        (self.rt / "T-099.route.json").unlink()
        ok, reason = route.backup_ok("T-099", "devin", "swe-2-high", None, self.rt)
        self.assertFalse(ok)
        self.assertIn("no ok assessment", reason)

    def test_env_selected_parses_documented_flag_forms(self):
        cases = {"AGENTFLOW_CODEX_ARGS": [("-m gpt-x --effort high", ("gpt-x", "high")),
                                        ("--model=gpt-x --effort=low", ("gpt-x", "low")),
                                        ("-c model_reasoning_effort=xhigh", (None, "xhigh"))],
                 "AGENTFLOW_DEVIN_ARGS": [("--model swe-2-max", ("swe-2-max", None))]}
        for var, pairs in cases.items():
            tool = var.split("_")[1].lower()
            for args, want in pairs:
                with patch.dict(os.environ, {var: args}, clear=True):
                    self.assertEqual(route.env_selected(tool), want, f"{var}={args}")


class RoutingRecordTests(unittest.TestCase):
    """End-to-end: route.py in a disposable project persists the schemaVersioned record."""

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Fake)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        Fake.seen.clear()
        Fake.status = 200
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "p"
        flow = self.root / ".agentflow"
        shutil.copytree(FLOW / "tools", flow / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        (flow / "tasks").mkdir(parents=True)
        (flow / "docs").mkdir()
        (flow / "tasks" / "T-099-probe.md").write_text(TASK, encoding="utf-8")
        self.write_options({})

    def tearDown(self):
        self.tmp.cleanup()

    def write_options(self, extra):
        cfg = {"policy": "floor first", "jev_model": "jev-1.13.0",
               "floor": {"option": "devin-swe-2", "effort": "high"},
               "prefer": ["devin"], "options": dict(OPTS["options"])}
        cfg.update(extra)
        (self.root / ".agentflow" / "docs" / "model-options.json").write_text(
            json.dumps(cfg), encoding="utf-8")

    def route(self, *args, key=True):
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("TYPESAFE_", "AGENTFLOW_"))}
        env["TYPESAFE_BASE_URL"] = f"http://127.0.0.1:{self.server.server_port}"
        env["AGENTFLOW_MACHINE_STATE_DIR"] = self.tmp.name
        env["AGENTFLOW_ROUTE_ASSUME_CLI_AVAILABLE"] = "1"
        if key:
            env["TYPESAFE_API_KEY"] = "test-key-never-printed"
        return subprocess.run([sys.executable, "-X", "utf8",
                               self.root / ".agentflow" / "tools" / "route.py", *args],
                              capture_output=True, text=True, encoding="utf-8", env=env)

    def rec(self):
        p = self.root / ".agentflow" / "tasks" / ".runtime" / "T-099.route.json"
        return json.loads(p.read_text(encoding="utf-8"))[-1]

    def test_ok_assessment_persists_the_binding_schema(self):
        Fake.answers = answers(effort="low", probabilities={"devin-swe-2": 0.9, "codex-ultra": 0.1})
        r = self.route("T-099")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = self.rec()
        self.assertEqual((rec["event"], rec["schemaVersion"], rec["status"]),
                         ("assessment", 1, "ok"))
        self.assertEqual(rec["requirementsHash"], gate.requirements_hash(TASK))
        self.assertEqual(rec["required"]["effort"], "high",
                         "the project floor lifts Jev's 'low', never lowers it")
        self.assertEqual(rec["floor"]["option"], "devin-swe-2")
        self.assertEqual(rec["selected"]["model"], "swe-2-high")
        self.assertEqual(rec["jev"]["requestId"], "req_core")
        self.assertEqual(rec["requestId"], "req_core")
        self.assertIn("availability", rec)
        self.assertIn("claude-plain", rec["inadequate"])

    def test_floor_beats_a_higher_ranked_other_cli(self):
        Fake.answers = answers(choice="codex-ultra",
                               probabilities={"codex-ultra": 0.9, "devin-swe-2": 0.1})
        r = self.route("T-099")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = self.rec()
        self.assertEqual(rec["choice"], "devin-swe-2")
        self.assertEqual(rec["jevChoice"], "codex-ultra")
        self.assertIn("policy order", rec["selectionReason"])

    def test_nothing_adequate_is_a_blocked_record_not_a_pick(self):
        self.write_options({"options": {"devin-swe-2": OPTS["options"]["devin-swe-2"],
                                        "claude-plain": OPTS["options"]["claude-plain"]},
                            "floor": {"option": "devin-swe-2", "effort": "high"},
                            "prefer": []})
        Fake.answers = answers(choice="devin-swe-2", effort="ultra")
        r = self.route("T-099")
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        rec = self.rec()
        self.assertEqual(rec["status"], "blocked")
        self.assertIn("no option meets the requirement", rec["blocked"])
        self.assertIn("devin-swe-2", rec["inadequate"], "the record names why each option failed")

    def test_low_confidence_and_failed_are_persisted_not_silent(self):
        Fake.answers = answers(confidence=0.4)
        r = self.route("T-099")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(self.rec()["status"], "low-confidence")
        r = self.route("T-099", key=False)
        self.assertEqual(r.returncode, 3)
        rec = self.rec()
        self.assertEqual(rec["status"], "failed")
        self.assertIn("no TypeSafe key", rec["error"])
        self.assertIn("requirementsHash", rec, "even a failed assessment binds the contract")

    def test_a_held_adequate_option_is_diagnosed_not_used(self):
        registry = Path(self.tmp.name) / "registry.json"
        registry.write_text(json.dumps({"limits": {"codex": time.time() + 3600}}), encoding="utf-8")
        Fake.answers = answers(choice="codex-ultra",
                               probabilities={"codex-ultra": 0.9, "devin-swe-2": 0.1})
        r = self.route("T-099")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = self.rec()
        self.assertEqual(rec["choice"], "devin-swe-2")
        self.assertIn("codex-ultra", rec["excluded"])
        self.assertIn("codex-ultra", rec["adequateHeld"],
                      "the adequate-but-held option is named so a blocked launch knows what it waits on")
        self.assertIn("limited until", rec["adequateHeld"]["codex-ultra"])

    def test_stale_contract_makes_the_record_refuse_admission(self):
        Fake.answers = answers()
        r = self.route("T-099")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.task_path = self.root / ".agentflow" / "tasks" / "T-099-probe.md"
        self.task_path.write_text(TASK.replace("Add a settings switch.", "Add two switches."),
                                  encoding="utf-8")
        t = {"id": "T-099", "file": str(self.task_path), "model": "swe-2-high", "effort": None}
        problems, ev = route.assessment_problems(t, self.root / ".agentflow" / "tasks" / ".runtime")
        self.assertIsNone(ev)
        self.assertIn("stale", problems[0])


if __name__ == "__main__":
    unittest.main()
