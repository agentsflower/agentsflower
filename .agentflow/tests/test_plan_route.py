"""Planning advice uses Jev's existing typed questions and never selects a worker task."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import plan_route  # noqa: E402


class PlanningRouteTests(unittest.TestCase):
    def test_recommends_primary_backup_and_compares_current_chat(self):
        config = {"policy": "best fit", "options": {
            "codex": {"tool": "codex", "model": "gpt-6.1-sol", "efforts": ["medium", "high"]},
            "devin": {"tool": "devin", "model_by_effort": {"medium": "swe-2-medium", "high": "swe-2-high"}}}}
        calls = []

        def fake(state, questions, key, model):
            calls.append((state, questions, key, model))
            return {"option": {"choice": "codex", "confidence": 0.95,
                               "probabilities": {"codex": 0.8, "devin": 0.2}},
                    "effort": {"choice": "high", "confidence": 0.96},
                    "complexity": {"score": 1.2, "confidence": 0.9}}, \
                   {"model": "jev-1.13.0", "requestId": "req-plan", "usage": {"input_tokens": 100}}

        with patch.object(plan_route.route, "cli_usable", return_value=True):
            result = plan_route.recommend("Plan the migration", config, "codex", "gpt-6.1-sol", fake, "test-key")
        self.assertEqual(result["tool"], "codex")
        self.assertEqual((result["backupTool"], result["backupModel"]), ("devin", "swe-2-high"))
        self.assertTrue(result["matchesCurrent"])
        self.assertNotIn("Plan the migration", str(result), "only a goal hash is logged")
        self.assertEqual(calls[0][0]["planning"]["goal"], "Plan the migration")
        self.assertEqual(sorted(calls[0][1]), ["complexity", "effort", "option"])

    def test_kind_reaches_the_jev_state_and_result(self):
        """B-07: decision difficulty is expressible: --kind tags the Jev state, the effort question's
        note, and the recorded recommendation. 'plan' stays the default; nothing forces low effort."""
        config = {"policy": "best fit", "options": {
            "codex": {"tool": "codex", "model": "gpt-6.1-sol", "efforts": ["low", "medium", "high"]}}}
        calls = []

        def fake(state, questions, key, model):
            calls.append((state, questions))
            return {"option": {"choice": "codex", "confidence": 0.95,
                               "probabilities": {"codex": 1.0}},
                    "effort": {"choice": "low", "confidence": 0.9},
                    "complexity": {"score": 0.4, "confidence": 0.9}}, {"model": "jev-1.13.0"}

        with patch.object(plan_route.route, "cli_usable", return_value=True):
            result = plan_route.recommend("Plan the migration", config, asker=fake, kind="dispatch")
        self.assertEqual(result["kind"], "dispatch")
        self.assertEqual(calls[0][0]["planning"]["kind"], "dispatch")
        self.assertIn("dispatch", str(calls[0][1]["effort"]["instructions"]))
        self.assertEqual(result["effort"], "low")  # Jev chose it; the kind never forces a tier
        with patch.object(plan_route.route, "cli_usable", return_value=True):
            result = plan_route.recommend("Plan the migration", config, asker=fake)
        self.assertEqual(result["kind"], "plan")
        self.assertNotIn("dispatch", str(calls[1][1]["effort"]["instructions"]))


if __name__ == "__main__":
    unittest.main()
