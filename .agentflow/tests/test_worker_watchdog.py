"""The external worker-deadline watchdog (T-072; repairs the missed deadlines T-040 exposed):
an invalid/zero AGENTFLOW_WORKER_TIMEOUT keeps a positive default, the launch persists the
resolved bound and its absolute deadline, and `run_task.py --watchdog` stops overdue non-manual
attempts under the same identity guards as --stop - classified 'timeout' with the watchdog
recorded as initiator. Manual and unexpired attempts stay untouched; it never relaunches.
Disposable repositories, fake workers, no real model calls."""
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_endcheck  # noqa: E402

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import run_task  # noqa: E402

TS = "%Y-%m-%dT%H:%M:%SZ"


def fake_tool(tmp, name, body_cmd, body_sh):
    """A fake worker CLI: .cmd on Windows, executable .sh elsewhere."""
    if os.name == "nt":
        p = Path(tmp) / f"{name}.cmd"
        p.write_text("@echo off\r\n" + body_cmd + "\r\n", encoding="ascii")
        return p
    p = Path(tmp) / f"{name}.sh"
    p.write_text("#!/bin/sh\n" + body_sh + "\n", encoding="ascii")
    p.chmod(0o755)
    return p


def past(seconds=0):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).strftime(TS)


class WorkerWatchdogTests(unittest.TestCase):
    def setUp(self):
        test_endcheck.WorktreeCopyTests.setUp(self)  # temp repo root "p" + worktree self.wt on t-001-probe
        self.flow = self.root / ".agentflow"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        self.env.update(AGENTFLOW_PYTHON=sys.executable, PYTHONUTF8="1",
                        AGENTFLOW_MACHINE_STATE_DIR=str(Path(self.tmp.name) / "machine"),
                        AGENTFLOW_DEVIN_MODEL_PROBE="on")  # opt into the built-in audited inference probe
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env["PATH"]
        self.env.update(GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid")
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1",
                  "--role", "developer", "--tool", "devin", "--status", "ready")
        self.rt_dir = self.flow / "tasks" / ".runtime"
        self.rt_dir.mkdir(exist_ok=True)
        self.rt_file = self.rt_dir / "T-001.json"

    def tearDown(self):
        for _ in range(10):  # a just-killed worker may still hold the temp tree for a moment
            try:
                test_endcheck.WorktreeCopyTests.tearDown(self)
                return
            except OSError:
                time.sleep(0.5)

    def tool(self, name, *args):
        r = subprocess.run([sys.executable, str(self.flow / "tools" / name), *args],
                           cwd=self.root, env=self.env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def launch(self, *args, env=None, timeout=45):
        return subprocess.run([sys.executable, str(self.flow / "tools" / "run_task.py"), *args],
                              cwd=self.root, env={**self.env, **(env or {})},
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout)

    def attempt(self):
        return json.loads(self.rt_file.read_text(encoding="utf-8-sig"))["attempts"][-1]

    def wait_state(self, want, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            a = self.attempt()
            if a["status"] == want:
                return a
            time.sleep(0.2)
        self.fail(f"attempt did not reach '{want}': {self.attempt()}")

    def fake_devin(self, cmd, sh, probe="ok"):
        """A fake devin CLI; `probe` answers the built-in model check (argv[1] is its fixed prompt)."""
        pc = {"ok": 'if "%~2"=="reply with the single word ok" exit /b 0\r\n',
              "deny": 'if "%~2"=="reply with the single word ok" exit /b 4\r\n'}.get(probe, "")
        ps = {"ok": 'if [ "$2" = "reply with the single word ok" ]; then exit 0; fi\n',
              "deny": 'if [ "$2" = "reply with the single word ok" ]; then exit 4; fi\n'}.get(probe, "")
        self.env["AGENTFLOW_DEVIN"] = str(fake_tool(self.tmp.name, "fake-devin", pc + cmd, ps + sh))

    def seed(self, tid, attempt):
        (self.rt_dir / f"{tid}.json").write_text(
            json.dumps({"taskId": tid, "attempts": [attempt]}), encoding="utf-8")

    def sleeper(self):
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])

        def kill():
            p.kill()
            p.wait()
        self.addCleanup(kill)
        return p

    def wait_dead(self, pid, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and run_task.alive(pid):
            time.sleep(0.2)
        self.assertFalse(run_task.alive(pid), f"pid {pid} is still alive")

    # --- W-01: a positive bound survives bad input; resolved timeout and deadline are persisted ----------
    def test_invalid_or_zero_worker_timeout_keeps_the_positive_default(self):
        """W-01: a missing, non-numeric, zero or negative AGENTFLOW_WORKER_TIMEOUT falls back to the
        positive default - a managed worker is never unbounded."""
        att = {"startedAt": past(0)}
        for raw in (None, "0", "-60", "abc", "10x"):
            with self.subTest(raw=raw), \
                    patch.dict(os.environ, {} if raw is None else {"AGENTFLOW_WORKER_TIMEOUT": raw},
                               clear=True):
                self.assertEqual(run_task.worker_bound({}, att),
                                 (run_task.WORKER_TIMEOUT, "AGENTFLOW_WORKER_TIMEOUT"), raw)
        with patch.dict(os.environ, {"AGENTFLOW_WORKER_TIMEOUT": "45"}, clear=True):
            self.assertEqual(run_task.worker_bound({}, att), (45, "AGENTFLOW_WORKER_TIMEOUT"))

    def test_launch_persists_the_resolved_timeout_and_deadline(self):
        """W-01: the attempt record carries the resolved bound and the absolute deadline the
        watchdog later enforces - measured from the attempt's own start."""
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        r = self.launch("T-001", "devin", env={"AGENTFLOW_WORKER_TIMEOUT": "not-a-number"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("exited")
        self.assertEqual(a["workerTimeout"], run_task.WORKER_TIMEOUT)
        deadline = datetime.strptime(a["deadline"], TS).replace(tzinfo=timezone.utc)
        started = datetime.strptime(a["startedAt"], TS).replace(tzinfo=timezone.utc)
        self.assertEqual((deadline - started).total_seconds(), run_task.WORKER_TIMEOUT)

    # --- W-02: the watchdog stops overdue workers; manual and unexpired attempts stay untouched ---------
    def test_watchdog_stops_an_overdue_worker_and_records_who(self):
        """W-02/W-05: an overdue non-manual attempt is killed under identity guards, classified
        'timeout' with the watchdog as recorded initiator - distinguishable from a human stop."""
        p = self.sleeper()
        start = run_task.pid_start(p.pid)
        if start is None:
            self.skipTest("process start identity is not measurable on this platform")
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": p.pid, "pidStart": start, "taskId": "T-001",
                            "startedAt": past(30), "deadline": past(1)})
        r = self.launch("T-001", "--watchdog")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertEqual(a["status"], "error")
        self.assertEqual(a["stopReason"], "timeout")
        self.assertEqual(a["stoppedBy"]["initiator"], "watchdog")
        self.assertIn("deadline", a["stoppedBy"]["reason"])
        self.assertTrue(a["recovery"]["capturedAt"])   # a failed attempt keeps its recovery record
        self.wait_dead(p.pid)

    def test_watchdog_enforces_the_persisted_deadline_and_releases_the_lease(self):
        """A real launch's own deadline is the watchdog's clock: a worker that outlives it is
        stopped, its managed tree dies and the machine lease is released - externally, even
        though the in-process bound was far away."""
        child = Path(self.tmp.name) / "wd-child.pid"
        body = (f'"{sys.executable}" -c "import subprocess,sys,time;'
                f"c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(120)']);"
                f"open({str(child)!r},'w').write(str(c.pid));time.sleep(120)\"")
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\n' + body + " %*",
                        'if [ "$1" = "auth" ]; then exit 0; fi\n' + body + ' "$@"')
        r = self.launch("T-001", "devin")   # the default bound: the worker itself is far from timing out
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        wait = time.monotonic() + 30
        while time.monotonic() < wait and not child.exists():
            time.sleep(0.2)
        self.assertTrue(child.exists(), "fake worker did not start its descendant")
        rt = json.loads(self.rt_file.read_text(encoding="utf-8-sig"))
        rt["attempts"][-1]["deadline"] = past(1)   # the persisted clock ran out
        self.rt_file.write_text(json.dumps(rt), encoding="utf-8")
        r = self.launch("T-001", "--watchdog")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertEqual((a["status"], a["stopReason"]), ("error", "timeout"))
        self.assertEqual(a["stoppedBy"]["initiator"], "watchdog")
        child_pid = int(child.read_text())
        wait = time.monotonic() + 10
        while time.monotonic() < wait and (run_task.alive(a["pid"]) or run_task.alive(child_pid)):
            time.sleep(0.2)
        self.assertFalse(run_task.alive(a["pid"]), "the worker survived the watchdog")
        self.assertFalse(run_task.alive(child_pid), "managed descendant survived the watchdog")
        reg = Path(self.env["AGENTFLOW_MACHINE_STATE_DIR"]) / "registry.json"
        self.assertEqual(json.loads(reg.read_text())["leases"], [])  # the lease was released

    def test_watchdog_leaves_manual_and_unexpired_attempts_alone(self):
        """W-02: a -Manual attempt stays untouched even past a deadline (the human's own session
        is not the watchdog's worker), and a non-manual attempt inside its bound is not killed;
        the watchdog also never starts anything (no blind relaunch)."""
        live = self.sleeper()
        start = run_task.pid_start(live.pid)
        if start is None:
            self.skipTest("process start identity is not measurable on this platform")
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": live.pid, "pidStart": start, "taskId": "T-001",
                            "startedAt": past(30)})   # legacy record: fallback deadline is far ahead
        self.seed("T-002", {"n": 1, "tool": "manual", "manual": True, "status": "running",
                            "pid": None, "taskId": "T-002",
                            "startedAt": past(7200), "deadline": past(1)})
        r = self.launch("--watchdog")   # a whole-project scan
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.attempt()["status"], "running")
        t2 = json.loads((self.rt_dir / "T-002.json").read_text(encoding="utf-8-sig"))["attempts"][-1]
        self.assertEqual(t2["status"], "running")
        self.assertTrue(run_task.alive(live.pid), "an unexpired worker was killed")
        self.assertFalse((self.rt_dir / "T-002.json").read_text().count('"n": 2'),
                         "the watchdog must never create an attempt")

    def test_watchdog_legacy_attempt_gets_a_bounded_fallback_deadline(self):
        """W-02: attempts recorded before `deadline` existed are still bounded - their clock is
        startedAt + the resolved worker timeout, never 'no deadline'."""
        p = self.sleeper()
        start = run_task.pid_start(p.pid)
        if start is None:
            self.skipTest("process start identity is not measurable on this platform")
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": p.pid, "pidStart": start, "taskId": "T-001",
                            "startedAt": past(run_task.WORKER_TIMEOUT + 60)})   # no deadline field
        r = self.launch("T-001", "--watchdog")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertEqual((a["status"], a["stopReason"]), ("error", "timeout"))
        self.assertEqual(a["stoppedBy"]["initiator"], "watchdog")
        self.wait_dead(p.pid)

    def test_watchdog_never_kills_a_pid_whose_identity_is_unconfirmed(self):
        """W-02 identity guard: a live process on the recorded pid that may be a reused pid is not
        a kill target even when the deadline passed - the task stays locked and diagnosed."""
        p = self.sleeper()
        start = run_task.pid_start(p.pid)
        if start is None:
            self.skipTest("process start identity is not measurable on this platform")
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": p.pid, "pidStart": start + 10_000_000, "taskId": "T-001",
                            "startedAt": past(30), "deadline": past(1)})
        r = self.launch("T-001", "--watchdog")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("identity", r.stdout + r.stderr)
        self.assertEqual(self.attempt()["status"], "running", "the attempt must stay locked")
        self.assertTrue(run_task.alive(p.pid), "a possibly reused pid was killed")

    def test_watchdog_gone_worker_is_closed_dead_once_cleanup_is_verified(self):
        """Recovery: an overdue attempt whose worker already vanished is closed as 'dead'
        (it was not killed by the watchdog) once no managed strays keep writing."""
        p = self.sleeper()
        start = run_task.pid_start(p.pid)
        p.kill()
        p.wait()
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": p.pid, "pidStart": start, "taskId": "T-001",
                            "startedAt": past(30), "deadline": past(1)})
        r = self.launch("T-001", "--watchdog")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertEqual((a["status"], a["stopReason"]), ("error", "dead"))

    # --- W-03: the expected-attempt guard ----------------------------------------------------------------
    def test_expected_attempt_guard_blocks_a_stale_stop(self):
        """W-03: a watchdog that decided on attempt n cannot stop attempt n+1 - the stop re-reads
        the record and refuses a moved-on attempt (an old watchdog never kills a new worker)."""
        self.seed("T-001", {"n": 2, "tool": "devin", "manual": False, "status": "running",
                            "pid": None, "taskId": "T-001",
                            "startedAt": past(30), "deadline": past(1)})
        with patch.object(run_task, "RT_DIR", self.rt_dir):
            with self.assertRaisesRegex(run_task.LaunchError, "expected attempt 1"):
                run_task.stop_attempt("T-001", "watchdog", "probe", "timeout", expect=1)
        a = self.attempt()
        self.assertEqual((a["status"], a["n"]), ("running", 2))
        r = self.launch("T-001", "--stop", "--expect-attempt", "1")   # same guard on the public stop
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("expected attempt 1", r.stdout + r.stderr)
        self.assertEqual(self.attempt()["status"], "running")

    def test_stop_serialized_with_launch_never_overwrites_a_newer_attempt(self):
        """P-06: the external stop shares launch.lock with launches. While a launch holds it the stop
        waits its bounded wait, then re-reads inside the lock - an attempt recorded in that window is
        seen, so the stale decision refuses and its writes can never erase the newer attempt (not only
        when the new attempt existed before the stop's first read)."""
        p = self.sleeper()
        start = run_task.pid_start(p.pid)
        if start is None:
            self.skipTest("process start identity is not measurable on this platform")
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": p.pid, "pidStart": start, "taskId": "T-001",
                            "startedAt": past(30), "deadline": past(1)})
        lock = self.rt_dir / "launch.lock"
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)   # an in-flight launch holds it
        outcome = {}

        def stop():
            try:
                outcome["rc"] = run_task.stop_attempt("T-001", "watchdog", "probe", "timeout", expect=1)
            except Exception as e:
                outcome["err"] = e

        with patch.object(run_task, "RT_DIR", self.rt_dir):
            th = threading.Thread(target=stop)
            th.start()
            time.sleep(1.0)   # the external stop is waiting on the launch lock now
            rt = json.loads(self.rt_file.read_text(encoding="utf-8-sig"))
            rt["attempts"][0].update(status="exited", finishedAt=past(0))
            rt["attempts"].append({"n": 2, "taskId": "T-001", "tool": "devin", "manual": False,
                                   "status": "running", "pid": None, "startedAt": past(0)})
            self.rt_file.write_text(json.dumps(rt), encoding="utf-8")   # the launch lands mid-wait
            os.close(fd)
            lock.unlink()
            th.join(20)
        self.assertFalse(th.is_alive(), "the stop did not finish after the lock was released")
        self.assertIsNone(outcome.get("rc"))
        self.assertIn("expected attempt 1", str(outcome.get("err")))   # the re-read saw attempt 2
        attempts = json.loads(self.rt_file.read_text(encoding="utf-8-sig"))["attempts"]
        self.assertEqual([a["n"] for a in attempts], [1, 2])
        self.assertEqual(attempts[1]["status"], "running")   # the newer record survived untouched
        self.assertTrue(run_task.alive(p.pid), "a refused stop still killed")

    def test_a_held_launch_lock_bounds_the_stops_wait(self):
        """P-06: the external stop's wait on launch.lock is bounded - a launch that outlasts it defers
        the stop to the next watchdog round instead of hanging it."""
        with patch.object(run_task, "RT_DIR", self.rt_dir), \
                patch.object(run_task, "STOP_LOCK_WAIT", 0.3):
            lock = self.rt_dir / "launch.lock"
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            try:
                t0 = time.monotonic()
                with self.assertRaisesRegex(run_task.LaunchError, "another launcher run"):
                    run_task.stop_attempt("T-001", "watchdog", "probe", "timeout", expect=1)
                self.assertLess(time.monotonic() - t0, 5)
            finally:
                os.close(fd)
                lock.unlink(missing_ok=True)

    def test_taskkill_is_bounded(self):
        """P-06: the Windows tree kill itself carries a timeout - a hung taskkill can no longer wedge
        an external stop."""
        with patch.object(run_task.os, "name", "nt"), \
                patch.object(run_task.subprocess, "run") as r, \
                patch.object(run_task, "_job_terminate"):
            run_task.kill_tree(4321)
        self.assertEqual(r.call_args[0][0][:2], ["taskkill", "/PID"])
        self.assertIsNotNone(r.call_args[1].get("timeout"))

    def test_conductor_runs_the_watchdog_every_round(self):
        """W-03: the conductor invokes the launcher watchdog inside its round loop, placed before
        the background-Orchestrator liveness check so it also runs while one is alive."""
        src = (FLOW / "tools" / "conductor.ps1").read_text(encoding="utf-8")
        loop = src[src.index("while ($true)"):]
        wd = loop.index("--watchdog")
        self.assertLess(wd, loop.index("Test-Alive $s"),
                        "the watchdog call must precede the Orchestrator-alive branch")
        self.assertIn("-not $DryRun", loop[:wd], "a dry run must change nothing")

    # --- W-05: who stopped it ----------------------------------------------------------------------------
    def test_cli_stop_records_a_different_initiator(self):
        """W-05: --stop on the same overdue attempt stays a command-line 'stopped' with its own
        recorded initiator - a watchdog stop is distinguishable from a CLI one, and the record
        does not claim an actual human issued every CLI stop."""
        p = self.sleeper()
        start = run_task.pid_start(p.pid)
        if start is None:
            self.skipTest("process start identity is not measurable on this platform")
        self.seed("T-001", {"n": 1, "tool": "devin", "manual": False, "status": "running",
                            "pid": p.pid, "pidStart": start, "taskId": "T-001",
                            "startedAt": past(30), "deadline": past(1)})
        r = self.launch("T-001", "--stop")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertEqual(a["stopReason"], "stopped")
        self.assertEqual(a["stoppedBy"]["initiator"], "cli")
        self.wait_dead(p.pid)


if __name__ == "__main__":
    unittest.main()
