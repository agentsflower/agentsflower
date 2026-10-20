"""Quota groups (T-030): one CLI identity, several provider budgets. A hold under
'<tool>:<group>' blocks only that group; bare '<tool>' stays tool-wide; account/access
failures are always tool-wide; legacy tool-wide holds migrate without losing their
reset time. No provider calls, no real machine registry."""
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
import limit_detection  # noqa: E402
import machine_capacity as machine  # noqa: E402
import quota_groups  # noqa: E402
import tick  # noqa: E402

# Holds recorded at AT must still be active when the assertion reads them: parse_reset anchors them a few
# hours after `at`, and active_limits compares against the real wall clock - so AT stays close to now.
AT = datetime.now(timezone.utc)

OPTS = {"policy": "test", "options": {
    "agy": {"tool": "agy", "quota_group": "agy-gemini",
            "model_by_effort": {"medium": "gemini-3.8-flash-medium", "high": "gemini-3.8-flash-high"}},
    "agy_sonnet": {"tool": "agy", "model": "claude-sonnet-4-6", "quota_group": "agy-claude-gpt"},
    "agy_opus": {"tool": "agy", "model": "claude-opus-4-6-thinking", "quota_group": "agy-claude-gpt"},
    "agy_gpt": {"tool": "agy", "model": "gpt-oss-120b-medium", "quota_group": "agy-claude-gpt"},
    "devin": {"tool": "devin", "model_by_effort": {"medium": "swe-2-medium", "high": "swe-2-high"}},
}}

QUOTA_LOG = "Error: RESOURCE_EXHAUSTED: Individual quota reached. Quota resets in 167h.\n"
ACCOUNT_LOG = "Your organization has disabled subscription access for this tool. Ask your admin to enable access\n"


def task(tid, model):
    return {"id": tid, "role": "developer", "depends": [], "independent": "none - probe",
            "model": model, "result": ""}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        opts = Path(self.tmp.name) / "model-options.json"
        opts.write_text(json.dumps(OPTS), encoding="utf-8")
        self.patches = [patch.object(quota_groups, "OPTIONS", opts),
                        patch.dict(os.environ, {"AGENTFLOW_MACHINE_STATE_DIR": str(Path(self.tmp.name) / "machine")})]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)


class ResolutionTests(Base):
    def test_configured_models_resolve_their_groups(self):
        self.assertEqual(quota_groups.group_for("agy", "claude-sonnet-4-6"), "agy-claude-gpt")
        self.assertEqual(quota_groups.group_for("agy", "claude-opus-4-6-thinking"), "agy-claude-gpt")
        self.assertEqual(quota_groups.group_for("agy", "gpt-oss-120b-medium"), "agy-claude-gpt")
        self.assertEqual(quota_groups.group_for("agy", "gemini-3.8-flash-high"), "agy-gemini")

    def test_unknown_model_has_no_group(self):
        self.assertIsNone(quota_groups.group_for("agy", "some-invented-model"))
        self.assertIsNone(quota_groups.group_for("agy", "argon-1"))
        self.assertIsNone(quota_groups.group_for("codex", "gpt-6.1-sol"))

    def test_no_model_is_the_tools_default_group(self):
        self.assertEqual(quota_groups.group_for("agy"), "agy-gemini")
        self.assertIsNone(quota_groups.group_for("devin"))  # the bare option has no group
        self.assertIsNone(quota_groups.group_for("claude"))  # unconfigured tool

    def test_missing_options_file_means_no_groups(self):
        self.assertIsNone(quota_groups.group_for("agy", "claude-sonnet-4-6", opts={}))
        self.assertIsNone(quota_groups.default_group("agy", opts={}))
        self.assertEqual(quota_groups.options(Path(self.tmp.name) / "absent.json"), {})

    def test_project_file_names_an_agy_default_and_its_groups(self):
        real = quota_groups.options(FLOW / "docs" / "model-options.json")
        self.assertEqual(real["agy"]["quota_group"], "agy-gemini",
                         "the option named after the tool defines the CLI default group")
        self.assertEqual({o["quota_group"] for o in real.values() if o.get("quota_group")},
                         {"devin", "codex", "agy-gemini", "agy-claude-gpt", "claude"})
        self.assertEqual(quota_groups.group_for("devin", "gemini-4-argon-high", real), "devin",
                         "Devin's argon variants resolve inside the devin quota group")


class MachineGroupHoldTests(Base):
    def claim(self, group=None):
        return machine.claim("agy", Path(self.tmp.name) / "p", "T-1", pid=os.getpid(), group=group)

    def test_group_hold_blocks_only_that_group(self):
        until = datetime.now(timezone.utc) + timedelta(hours=100)
        machine.record_limit("agy", until, group="agy-gemini")
        token, reason = self.claim("agy-gemini")
        self.assertIsNone(token)
        self.assertIn("group 'agy-gemini'", reason)
        token, reason = self.claim("agy-claude-gpt")
        self.assertTrue(token, reason)
        machine.release(token)
        self.assertIsNotNone(machine.limit_until("agy", "agy-gemini"))
        self.assertIsNone(machine.limit_until("agy", "agy-claude-gpt"))
        self.assertIsNone(machine.limit_until("agy"))

    def test_tool_wide_hold_blocks_every_group(self):
        machine.record_limit("agy", datetime.now(timezone.utc) + timedelta(hours=1))
        for group in (None, "agy-gemini", "agy-claude-gpt"):
            token, reason = self.claim(group)
            self.assertIsNone(token, group)
            self.assertIn("globally limited", reason)

    def test_move_limit_preserves_reset_time_and_leaves_the_rest(self):
        until = datetime.now(timezone.utc) + timedelta(hours=167)
        machine.record_limit("agy", until)
        machine.record_limit("devin", datetime.now(timezone.utc) + timedelta(minutes=5))
        other = machine.claim("codex", Path(self.tmp.name) / "p", "T-9", pid=os.getpid())[0]
        end = machine.move_limit("agy", "agy-gemini")
        try:
            self.assertEqual(end, until.timestamp())
            self.assertIsNone(machine.limit_until("agy"))
            self.assertEqual(machine.limit_until("agy", "agy-gemini").timestamp(), until.timestamp())
            token, reason = self.claim("agy-claude-gpt")   # moved hold frees the other group
            self.assertTrue(token, reason)
            machine.release(token)
            self.assertIsNotNone(machine.limit_until("devin"))  # unrelated limits stay
        finally:
            machine.release(other)
        self.assertIsNone(machine.move_limit("agy", "agy-gemini"))  # nothing left to move

    def test_port_reservation_is_unaffected_by_groups(self):
        first, _ = machine.claim("agy", Path(self.tmp.name) / "p", "T-1", port="4350",
                                 pid=os.getpid(), group="agy-claude-gpt")
        second, reason = machine.claim("devin", Path(self.tmp.name) / "q", "T-2",
                                       port="4350", pid=os.getpid())
        self.assertIsNone(second)
        self.assertIn("PORT=4350", reason)
        machine.release(first)


class TickGroupTests(Base):
    def setUp(self):
        super().setUp()
        rt = Path(self.tmp.name) / "rt"
        new = [patch.object(tick, "RT", rt), patch.object(tick, "HEARTBEAT", rt / "hb.json"),
               patch.object(tick, "LIMITS", rt / "tool-limits.json"),
               patch.object(tick, "TICK", rt / "tick.json"), patch.object(tick, "LOCK", rt / "tick.lock")]
        self.patches += new
        for p in new:
            p.start()
            self.addCleanup(p.stop)

    def decide(self, tasks, rows):
        with patch.object(tick.gate, "parse", side_effect=lambda t: tasks[t]), \
                patch.object(tick.gate, "last_attempt", return_value=None):
            return {t: (a, d) for t, a, d in tick.decide(rows, AT)}

    def test_gemini_exhaustion_leaves_claude_gpt_launchable(self):
        tick.record_limit("agy", QUOTA_LOG, group="agy-gemini", at=AT)
        tasks = {"T-1": task("T-1", "claude-sonnet-4-6"), "T-2": task("T-2", "gpt-oss-120b-medium"),
                 "T-3": task("T-3", "gemini-3.8-flash-high"), "T-4": task("T-4", None)}
        rows = {t: {"Status": "ready", "Tool": "agy"} for t in tasks}
        out = self.decide(tasks, rows)
        self.assertEqual(out["T-1"], ("launch", "agy"))
        self.assertEqual(out["T-2"], ("launch", "agy"))
        self.assertEqual(out["T-3"][0], "need")
        self.assertIn("agy-gemini", out["T-3"][1])
        self.assertEqual(out["T-4"][0], "need")  # unmodelled agy is the default: Gemini, exhausted

    def test_claude_gpt_exhaustion_leaves_gemini_launchable(self):
        tick.record_limit("agy", QUOTA_LOG, group="agy-claude-gpt", at=AT)
        tasks = {"T-1": task("T-1", "gemini-3.8-flash-medium"), "T-2": task("T-2", "claude-sonnet-4-6")}
        rows = {t: {"Status": "ready", "Tool": "agy"} for t in tasks}
        out = self.decide(tasks, rows)
        self.assertEqual(out["T-1"], ("launch", "agy"))
        self.assertEqual(out["T-2"][0], "need")
        self.assertIn("agy-claude-gpt", out["T-2"][1])

    def test_tool_wide_failure_still_holds_every_group(self):
        tick.record_limit("agy", ACCOUNT_LOG, at=AT)  # account signal: tool-wide
        tasks = {"T-1": task("T-1", "claude-sonnet-4-6"), "T-2": task("T-2", "invented-model")}
        rows = {t: {"Status": "ready", "Tool": "agy"} for t in tasks}
        out = self.decide(tasks, rows)
        self.assertEqual(out["T-1"][0], "need")
        self.assertEqual(out["T-2"][0], "need")  # unknown model: the global hold still applies

    def test_learn_limits_scopes_quota_to_the_attempt_group(self):
        log = Path(self.tmp.name) / "T-1.1.log"
        log.write_text(QUOTA_LOG, encoding="utf-8")
        att = {"n": 1, "tool": "agy", "status": "error", "exitCode": 1, "log": str(log),
               "quotaGroup": "agy-claude-gpt", "limitKind": "quota", "finishedAt": tick.iso(AT)}
        with patch.object(tick.gate, "last_attempt", return_value=att):
            tick.learn_limits({"T-1": {"Status": "in progress"}})
        self.assertEqual(sorted(tick.active_limits()), ["agy:agy-claude-gpt"])
        with machine._locked() as state:
            self.assertEqual(sorted(state["limits"]), ["agy:agy-claude-gpt"])

    def test_learn_limits_account_signal_stays_tool_wide(self):
        log = Path(self.tmp.name) / "T-1.1.log"
        log.write_text(ACCOUNT_LOG, encoding="utf-8")
        att = {"n": 1, "tool": "agy", "status": "error", "exitCode": 1, "log": str(log),
               "quotaGroup": "agy-claude-gpt", "limitKind": "account", "finishedAt": tick.iso(AT)}
        with patch.object(tick.gate, "last_attempt", return_value=att):
            tick.learn_limits({"T-1": {"Status": "in progress"}})
        self.assertEqual(sorted(tick.active_limits()), ["agy"])

    def test_learn_limits_attempt_without_group_stays_tool_wide(self):
        log = Path(self.tmp.name) / "T-1.1.log"
        log.write_text(QUOTA_LOG, encoding="utf-8")
        att = {"n": 1, "tool": "agy", "status": "error", "exitCode": 1, "log": str(log),
               "finishedAt": tick.iso(AT)}  # launched before quota groups: no quotaGroup field
        with patch.object(tick.gate, "last_attempt", return_value=att):
            tick.learn_limits({"T-1": {"Status": "in progress"}})
        self.assertEqual(sorted(tick.active_limits()), ["agy"])

    def test_migrate_moves_local_and_machine_holds_preserving_time(self):
        entry = tick.record_limit("agy", QUOTA_LOG, at=AT)  # a legacy tool-wide hold
        lines = tick.migrate_limit("agy", "agy-gemini")
        self.assertEqual(sorted(tick.active_limits()), ["agy:agy-gemini"])
        self.assertTrue(any("agy:agy-gemini" in line and entry["until"] in line for line in lines), lines)
        self.assertAlmostEqual(tick.limit_end("agy", "agy-gemini").timestamp(),
                               tick.parse_iso(entry["until"]).timestamp(), delta=1.0)  # registry keeps float time
        self.assertIsNone(tick.limit_end("agy"))
        self.assertEqual(tick.migrate_limit("agy", "agy-gemini"), [])

    def test_next_orchestrator_checks_the_tools_default_group(self):
        with patch.dict(os.environ, {"AGENTFLOW_ORCHESTRATORS": "agy,devin"}):
            tick.record_limit("agy", QUOTA_LOG, group="agy-gemini", at=AT)
            self.assertEqual(tick.next_orchestrator(), "devin")  # background agy would consume Gemini

    def test_next_orchestrator_ignores_another_groups_hold(self):
        with patch.dict(os.environ, {"AGENTFLOW_ORCHESTRATORS": "agy,devin"}):
            tick.record_limit("agy", QUOTA_LOG, group="agy-claude-gpt", at=AT)
            self.assertEqual(tick.next_orchestrator(), "agy")  # the Claude/GPT hold does not stop Gemini

    def test_existing_tool_wide_record_blocks_exhausted_families_but_allows_a_group_probe(self):
        """The pre-quota-groups agy record is tool-wide: a task on an observed-exhausted family
        still waits, while a new option can be scoped to a fresh group and probed."""
        tick.record_limit("agy", ACCOUNT_LOG, at=AT)
        tasks = {"T-1": task("T-1", "claude-sonnet-4-6")}
        rows = {"T-1": {"Status": "ready", "Tool": "agy"}}
        self.assertEqual(self.decide(tasks, rows)["T-1"][0], "need")
        # scoping the legacy hold to its real group frees the remaining families
        tick.migrate_limit("agy", "agy-claude-gpt")
        tasks["T-2"] = task("T-2", "gemini-3.8-flash-high")
        rows["T-2"] = {"Status": "ready", "Tool": "agy"}
        out = self.decide(tasks, rows)
        self.assertEqual(out["T-1"][0], "need")
        self.assertEqual(out["T-2"], ("launch", "agy"))


class DispatchGroupTests(Base):
    """dispatch.py keeps its tool-wide grant contract (not part of this change): a grant for a
    group-held tool may still be issued, and the launcher's scoped claim refuses it - the grant
    is released by tick.run and the task waits. These tests pin the unchanged behavior."""

    def setUp(self):
        super().setUp()
        self.a = Path(self.tmp.name) / "a"
        (self.a / ".agentflow" / "docs").mkdir(parents=True)

    def test_request_sees_only_tool_wide_holds(self):
        machine.record_limit("agy", datetime.now(timezone.utc) + timedelta(hours=1), group="agy-gemini")
        import dispatch
        dispatch.register(self.a, [("T-1", "agy")])
        grant, reason = dispatch.request(self.a, "T-1", "agy")
        self.assertTrue(grant, reason)  # tool-wide view: the scoped hold is invisible here
        dispatch.release(grant)
        lease, reason = machine.claim("agy", self.a, "T-1", pid=os.getpid(), group="agy-gemini")
        self.assertIsNone(lease)  # the scoped claim is where the hold bites
        self.assertIn("agy-gemini", reason)


class DetectionKindTests(unittest.TestCase):
    def test_quota_and_account_phrases_classify(self):
        self.assertEqual(limit_detection.detect_detail(QUOTA_LOG, 1)[1], "quota")
        self.assertEqual(limit_detection.detect_detail(ACCOUNT_LOG, 0)[1], "account")
        self.assertEqual(limit_detection.detect_detail("out of credits\n", 0)[1], "account")
        self.assertEqual(limit_detection.detect_detail("You've hit your usage limit. Resets in 2h\n", 0)[1],
                         "quota")
        self.assertIsNone(limit_detection.detect_detail("all good\n", 0))


if __name__ == "__main__":
    unittest.main()
