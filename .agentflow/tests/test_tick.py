"""tick.py: which steps it takes without judgment, which it leaves to an Orchestrator, limits and the heartbeat."""
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import run_task  # noqa: E402
import tick  # noqa: E402

AT = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)


def dev(tid, outcome="completed", independent="tester", depends=()):
    return {"id": tid, "role": "developer", "depends": list(depends), "independent": independent,
            "result": f"Outcome: {outcome}\nChange: {'a' * 40}\n" if outcome else ""}


def tester(tid, checks, outcome="completed", verdict="pass"):
    return {"id": tid, "role": "tester", "depends": [], "independent": "", "checked": {"id": checks},
            "result": f"Outcome: {outcome}\nVerdict: {verdict}\n"}


def done_attempt(tool="codex", **kw):
    return {"n": 1, "tool": tool, "status": "exited", "exitCode": 0, "limitHit": False, "log": None, **kw}


class TickTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        rt = Path(self.tmp.name)
        # a machine's own AGENTFLOW_* variables must not leak into the fixture
        clean = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        clean.update({"AGENTFLOW_MACHINE_STATE_DIR": self.tmp.name, "AGENTFLOW_MACHINE_CODEX_MAX": "1"})
        self.patches = [patch.object(tick, "RT", rt), patch.object(tick, "HEARTBEAT", rt / "orchestrator.json"),
                        patch.object(tick, "LIMITS", rt / "tool-limits.json"), patch.object(tick, "TICK", rt / "tick.json"),
                        patch.object(tick, "LOCK", rt / "tick.lock"),
                        patch.dict(os.environ, clean, clear=True)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def decide(self, tasks, attempts, rows):
        with patch.object(tick.gate, "parse", side_effect=lambda t: tasks[t]), \
                patch.object(tick.gate, "last_attempt", side_effect=lambda t: attempts.get(t)), \
                patch.object(tick, "alive", return_value=False):
            return {t: (a, d) for t, a, d in tick.decide(rows, AT)}

    def test_tester_pass_is_accepted_and_unlocks_its_developer_only_then(self):
        tasks = {"T-1": dev("T-1"), "T-2": tester("T-2", "T-1")}
        att = {"T-1": done_attempt(), "T-2": done_attempt()}
        out = self.decide(tasks, att, {"T-1": {"Role": "developer", "Status": "review"},
                                       "T-2": {"Role": "tester", "Status": "in progress"}})
        self.assertEqual(out["T-2"][0], "accept")
        self.assertEqual(out["T-1"][0], "wait")
        out = self.decide(tasks, att, {"T-1": {"Role": "developer", "Status": "review"},
                                       "T-2": {"Role": "tester", "Status": "done"}})
        self.assertEqual(out["T-1"][0], "accept")

    def test_judgment_is_left_to_the_orchestrator(self):
        tasks = {"T-1": dev("T-1"), "T-2": tester("T-2", "T-1", verdict="fail"), "T-3": dev("T-3", outcome="blocked"),
                 "T-4": dev("T-4")}
        att = {t: done_attempt() for t in tasks}
        rows = {"T-1": {"Role": "developer", "Status": "review"}, "T-2": {"Role": "tester", "Status": "in progress"},
                "T-3": {"Role": "developer", "Status": "in progress"}, "T-4": {"Role": "developer", "Status": "in progress"}}
        out = self.decide(tasks, att, rows)
        self.assertEqual(out["T-2"][0], "need")  # a failed test: reject and successor
        self.assertEqual(out["T-1"][0], "wait")  # its tester exists but is not done
        self.assertEqual(out["T-3"][0], "need")  # blocked
        self.assertEqual(out["T-4"], ("need", "developer completed: write its tester task"))

    def test_developer_without_independent_check_is_accepted(self):
        out = self.decide({"T-1": dev("T-1", independent="none (docs only)")}, {"T-1": done_attempt()},
                          {"T-1": {"Role": "developer", "Status": "in progress"}})
        self.assertEqual(out["T-1"][0], "accept")

    def test_launch_only_when_dependencies_done_and_tool_free(self):
        tasks = {"T-1": dev("T-1", outcome=""), "T-2": dev("T-2", outcome="", depends=["T-9"]),
                 "T-3": dev("T-3", outcome=""), "T-9": dev("T-9")}
        rows = {"T-1": {"Status": "ready", "Tool": "codex"}, "T-2": {"Status": "ready", "Tool": "codex"},
                "T-3": {"Status": "ready", "Tool": "devin"}, "T-9": {"Status": "review", "Tool": "codex"}}
        tick.record_limit("devin", "You hit your limit. Resets in 2h", at=AT)
        out = self.decide(tasks, {"T-9": {"n": 1, "status": "running", "pid": 1}}, rows)
        self.assertEqual(out["T-1"], ("launch", "codex"))
        self.assertEqual(out["T-2"][0], "wait")
        self.assertEqual(out["T-3"][0], "need")
        self.assertIn("limited", out["T-3"][1])
        self.assertEqual(out["T-9"][0], "need")  # running, but its process is gone

    def test_usage_limit_is_a_need_not_an_acceptance(self):
        out = self.decide({"T-1": dev("T-1", outcome="")}, {"T-1": done_attempt(status="error", limitHit=True)},
                          {"T-1": {"Role": "developer", "Status": "in progress"}})
        self.assertEqual(out["T-1"][0], "need")
        self.assertIn("usage limit", out["T-1"][1])

    def test_reset_times(self):
        self.assertEqual(tick.parse_reset("Resets in 158h43m", AT), AT + timedelta(hours=158, minutes=43))
        self.assertEqual(tick.parse_reset("limit reached, resets in 2d 3h", AT), AT + timedelta(days=2, hours=3))
        self.assertEqual(tick.parse_reset("rate limit, please wait", AT), AT + timedelta(hours=1))
        t = tick.parse_reset("Claude usage limit reached. Your limit resets 3:30pm", AT).astimezone()
        self.assertEqual((t.hour, t.minute), (15, 30))
        self.assertTrue(AT < t <= AT + timedelta(days=1))

    def test_next_orchestrator_skips_limited_tools(self):
        with patch.dict(tick.os.environ, {"AGENTFLOW_ORCHESTRATORS": "claude,codex,devin,agy"}):
            tick.record_limit("claude", "session limit, resets in 3h")
            self.assertEqual(tick.next_orchestrator(), "codex")
            tick.record_limit("codex", "usage limit")
            self.assertEqual(tick.next_orchestrator(), "devin")
            self.assertEqual(tick.next_orchestrator(datetime.now(timezone.utc) + timedelta(hours=4)), "claude")

    def test_next_orchestrator_skips_a_busy_machine_slot(self):
        with patch.dict(tick.os.environ, {"AGENTFLOW_ORCHESTRATORS": "codex,devin"}):
            token, reason = tick.machine_capacity.claim("codex", FLOW.parent, "other-project", pid=os.getpid())
            self.assertTrue(token, reason)
            try:
                self.assertEqual(tick.next_orchestrator(), "devin")
            finally:
                tick.machine_capacity.release(token)

    def test_disabled_subscription_access_temporarily_skips_the_tool(self):
        message = ("Your organization has disabled Claude subscription access for Claude Code · "
                   "Use an Anthropic API key instead, or ask your admin to enable access")
        self.assertIsNotNone(tick.LIMIT_RE.search(message))
        with patch.dict(tick.os.environ, {"AGENTFLOW_ORCHESTRATORS": "claude,codex,devin,agy"}):
            entry = tick.record_limit("claude", message, at=AT)
            self.assertEqual(tick.next_orchestrator(AT), "codex")
            self.assertEqual(entry["until"], tick.iso(AT + timedelta(hours=1)))
            self.assertEqual(tick.next_orchestrator(AT + timedelta(hours=1, seconds=1)), "claude")

    def test_heartbeat_is_one_holder_at_a_time(self):
        self.assertIsNone(tick.heartbeat("claude"))
        self.assertEqual(tick.heartbeat("codex-background")["holder"], "claude")
        self.assertIsNone(tick.heartbeat("claude"))  # refresh by the holder
        self.assertIsNone(tick.heartbeat("codex-background", force=True))
        tick.release("claude")  # not the holder: nothing happens
        self.assertEqual(tick.live_orchestrator()["holder"], "codex-background")
        tick.release("codex-background")
        self.assertIsNone(tick.live_orchestrator())

    def test_stale_heartbeat_is_not_live(self):
        tick.heartbeat("claude")
        later = datetime.now(timezone.utc) + timedelta(minutes=tick.stale_minutes() + 1)
        self.assertIsNone(tick.live_orchestrator(later))

    def test_run_reports_only_while_an_orchestrator_is_live(self):
        tick.heartbeat("claude")
        acts = []
        with patch.object(tick.gate, "ledger_rows", return_value={"T-1": {"Status": "ready", "Tool": "codex"}}), \
                patch.object(tick.gate, "parse", return_value=dev("T-1", outcome="")), \
                patch.object(tick.gate, "last_attempt", return_value=None):
            rep = tick.run(launch=lambda t, tool: acts.append(t) or (True, tool))
            self.assertTrue(rep["reportOnly"])
            self.assertEqual(acts, [])
            self.assertEqual(rep["would"][0]["task"], "T-1")
            tick.release()
            rep = tick.run(launch=lambda t, tool: acts.append(t) or (True, tool))
            self.assertFalse(rep["reportOnly"])
            self.assertEqual(acts, ["T-1"])

    def test_shadow_dispatcher_reports_without_changing_existing_launch(self):
        proposal = {"mode": "shadow", "selected": [], "waits": [], "launches": 0}
        with patch.dict(os.environ, {"AGENTFLOW_SHARED_DISPATCHER": "shadow"}), \
                patch("dispatch.plan", return_value=proposal), \
                patch.object(tick.gate, "ledger_rows", return_value={"T-1": {"Status": "ready", "Tool": "codex"}}), \
                patch.object(tick.gate, "parse", return_value=dev("T-1", outcome="")), \
                patch.object(tick.gate, "last_attempt", return_value=None):
            calls = []
            report = tick.run(launch=lambda task, tool: calls.append((task, tool)) or (True, tool))
        self.assertEqual(calls, [("T-1", "codex")])
        self.assertEqual(report["dispatchShadow"], proposal)

    def test_backup_switches_only_an_unstarted_task(self):
        path = Path(self.tmp.name) / "T-1.md"
        path.write_text("# T-1\n\nRole: developer\nTool: codex\nModel: gpt-6.1-sol, effort=high\n"
                        "Backup Tool: devin\nBackup Model: swe-2-high\nStage: 1\n\n## Result\n", encoding="utf-8")
        with patch.object(tick.gate, "last_attempt", return_value=None), \
                patch.object(tick.gate, "parse", return_value={"file": str(path)}), \
                patch.object(tick.machine_capacity, "has_capacity", return_value=True), \
                patch.object(tick, "limited", return_value=False), \
                patch.object(tick, "py", return_value=(0, "")), \
                patch.object(tick.route, "_log"):
            switched, tool = tick.use_backup("T-1", "codex")
        self.assertTrue(switched)
        self.assertEqual(tool, "devin")
        text = path.read_text(encoding="utf-8")
        self.assertIn("Tool: devin\nModel: swe-2-high\n", text)
        self.assertNotIn("Backup Tool:", text)
        with patch.object(tick.gate, "last_attempt", return_value={"n": 1}):
            self.assertFalse(tick.use_backup("T-1", "devin")[0])

    def test_run_uses_backup_when_primary_slot_is_full(self):
        rows = {"T-1": {"Status": "ready", "Tool": "codex"}}
        launches = []

        def switch(tid, tool):
            rows[tid]["Tool"] = "devin"
            return True, "devin"

        with patch.dict(os.environ, {"AGENTFLOW_BACKUP_ROUTING": "on"}), \
                patch.object(tick.gate, "ledger_rows", side_effect=lambda: {k: dict(v) for k, v in rows.items()}), \
                patch.object(tick.gate, "parse", return_value=dev("T-1", outcome="")), \
                patch.object(tick.gate, "last_attempt", return_value=None), \
                patch.object(tick.machine_capacity, "has_capacity", side_effect=lambda tool, *_: tool != "codex"), \
                patch.object(tick, "use_backup", side_effect=switch):
            report = tick.run(launch=lambda tid, tool: launches.append((tid, tool)) or (True, tool))
        self.assertEqual(launches, [("T-1", "devin")])
        self.assertIn({"task": "T-1", "action": "backup", "detail": "codex -> devin"}, report["acted"])

    def test_active_dispatcher_passes_grant_to_launcher(self):
        rows = {"T-1": {"Status": "ready", "Tool": "codex"}}
        launched = []
        with patch.dict(os.environ, {"AGENTFLOW_SHARED_DISPATCHER": "active"}), \
                patch.object(tick.gate, "ledger_rows", return_value=rows), \
                patch.object(tick.gate, "parse", return_value=dev("T-1", outcome="")), \
                patch.object(tick.gate, "last_attempt", return_value=None), \
                patch.object(tick.dispatch, "register") as register, \
                patch.object(tick.dispatch, "request", return_value=("grant-1", "")), \
                patch.object(tick.dispatch, "release") as release:
            report = tick.run(launch=lambda tid, tool, grant: launched.append((tid, tool, grant)) or (True, tool))
        register.assert_called_once_with(FLOW.parent, [("T-1", "codex")])
        release.assert_called_once_with("grant-1")
        self.assertEqual(launched, [("T-1", "codex", "grant-1")])
        self.assertEqual(report["dispatchMode"], "active")

    def test_run_accepts_a_chain_in_one_tick(self):
        rows = {"T-1": {"Role": "developer", "Status": "review"}, "T-2": {"Role": "tester", "Status": "in progress"}}
        tasks = {"T-1": dev("T-1"), "T-2": tester("T-2", "T-1")}

        def accept(tid):
            rows[tid]["Status"] = "done"
            return True, f"{tid} accepted"

        with patch.object(tick.gate, "ledger_rows", side_effect=lambda: {k: dict(v) for k, v in rows.items()}), \
                patch.object(tick.gate, "parse", side_effect=lambda t: tasks[t]), \
                patch.object(tick.gate, "last_attempt", return_value=done_attempt()):
            rep = tick.run(accept=accept)
        self.assertEqual([a["task"] for a in rep["acted"]], ["T-2", "T-1"])
        self.assertEqual(rep["needs"], [])

    def test_a_refused_acceptance_becomes_a_need_and_is_not_retried(self):
        calls = []
        with patch.object(tick.gate, "ledger_rows", return_value={"T-1": {"Role": "developer", "Status": "in progress"}}), \
                patch.object(tick.gate, "parse", return_value=dev("T-1", independent="none")), \
                patch.object(tick.gate, "last_attempt", return_value=done_attempt()):
            rep = tick.run(accept=lambda t: calls.append(t) or (False, "STOPPED: verify failed"))
        self.assertEqual(calls, ["T-1"])
        self.assertEqual(len(rep["needs"]), 1)
        self.assertIn("accept stopped", rep["needs"][0]["detail"])

    def test_malformed_runtime_files_fail_closed(self):
        """tool-limits.json / orchestrator.json: a bad file is a diagnosable error, never 'no limits'
        or 'no live orchestrator' - and a corrupt T-NNN.json surfaces as a need, not a crash."""
        rt = Path(self.tmp.name)
        (rt / "tool-limits.json").write_text("{ broken", encoding="utf-8")
        with self.assertRaises(tick.StateError):
            tick.limit_end("codex")
        (rt / "tool-limits.json").write_text('{"codex": "not-an-object"}', encoding="utf-8")
        self.assertIsNone(tick.limit_end("codex"))  # a non-record entry is skipped, not a crash
        (rt / "orchestrator.json").write_text('["not", "an", "object"]', encoding="utf-8")
        with self.assertRaises(tick.StateError):
            tick.live_orchestrator()

    def test_an_unreadable_attempt_becomes_a_need_not_a_crash(self):
        with patch.object(tick.gate, "parse", return_value=dev("T-1", outcome="")), \
                patch.object(tick.gate, "last_attempt",
                             side_effect=tick.gate.TaskError("cannot read runtime state T-1.json: bogus")), \
                patch.object(tick, "alive", return_value=False):
            out = {t: (a, d) for t, a, d in tick.decide({"T-1": {"Status": "in progress", "Role": "developer"}})}
        self.assertEqual(out["T-1"][0], "need")
        self.assertIn("runtime state", out["T-1"][1])

    def test_alive_requires_the_recorded_process_identity(self):
        """tick judges a worker by the same pid + pidStart rule as the launcher: a live pid with a
        wrong start is not the recorded worker (a reused pid cannot impersonate it)."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            self.assertTrue(tick.alive(p.pid))
            start = run_task.pid_start(p.pid)
            if start is None:
                self.skipTest("process start identity is not measurable on this platform")
            self.assertTrue(tick.alive(p.pid, start))
            self.assertFalse(tick.alive(p.pid, start + 10_000_000))
        finally:
            p.kill()
            p.wait()


if __name__ == "__main__":
    unittest.main()
