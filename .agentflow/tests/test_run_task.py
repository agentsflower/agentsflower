"""run_task.py lifecycle in disposable repositories: Python fake workers, isolated machine state, no real model calls."""
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_endcheck  # noqa: E402

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import run_task  # noqa: E402


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


class ModelProbeArgvTests(unittest.TestCase):
    def test_bootstrap_probe_argv_and_denial(self):
        expected = {
            "devin": ["-p", "reply with the single word ok", "--respect-workspace-trust", "false",
                      "--permission-mode", "auto", "--model", "test-model"],
            "codex": ["exec", "--sandbox", "read-only", "--skip-git-repo-check",
                      "reply with the single word ok", "-m", "test-model"],
            "claude": ["-p", "reply with the single word ok", "--allowedTools", "", "--model", "test-model"],
            "agy": ["-p", "reply with the single word ok", "--output-format", "stream-json",
                    "--model", "test-model"],
        }
        for tool, argv in expected.items():
            for denied in (False, True):
                with self.subTest(tool=tool, denied=denied):
                    calls = []

                    def fake_capture(args, timeout, cwd=None):
                        calls.append(args)
                        if cwd is None:
                            self.assertEqual(args[1:], run_task.PROBE_ARGS[tool])
                            return 0, "authenticated"
                        self.assertEqual(list(Path(cwd).iterdir()), [])
                        self.assertEqual(args, ["fake-cli"] + argv)
                        self.assertEqual(timeout, 17)
                        return (4 if denied else 0), "never serialize probe output"

                    with patch.dict(os.environ, {f"AGENTFLOW_{tool.upper()}_MODEL_PROBE": "on",
                                                 "AGENTFLOW_MODEL_PROBE_TIMEOUT": "17"}, clear=True), \
                            patch.object(run_task, "tool_exe", return_value="fake-cli"), \
                            patch.object(run_task.shutil, "which", return_value="fake-cli"), \
                            patch.object(run_task, "limit_until", return_value=None), \
                            patch.object(run_task, "run_capture", side_effect=fake_capture):
                        if denied:
                            with self.assertRaisesRegex(run_task.LaunchError, "was denied.*exit 4"):
                                run_task.resource_check(tool, "test-model")
                        else:
                            evidence = run_task.resource_check(tool, "test-model")["modelProbe"]
                            self.assertEqual(evidence["argv"], argv)
                            self.assertEqual(evidence["model"], "test-model")
                            self.assertEqual(evidence["source"], "builtin")
                            self.assertEqual(evidence["result"], "ok")
                            self.assertTrue(evidence["at"])
                            self.assertNotIn("never serialize", str(evidence))
                    self.assertEqual(len(calls), 2)

    def test_builtin_probes_match_installed_cli_help_without_escalation(self):
        """Reviewed against installed --help (T-022): every built-in names the flag its CLI needs for
        noninteractive inference in an empty untrusted temporary directory, and none escalates permissions."""
        codex = run_task.MODEL_PROBE_ARGS["codex"]
        self.assertIn("--skip-git-repo-check", codex)   # codex exec refuses outside a repository
        self.assertEqual(codex[codex.index("--sandbox") + 1], "read-only")
        devin = run_task.MODEL_PROBE_ARGS["devin"]
        self.assertEqual(devin[devin.index("--respect-workspace-trust") + 1], "false")  # print mode fails untrusted
        self.assertEqual(devin[devin.index("--permission-mode") + 1], "auto")           # read-only approval only
        claude = run_task.MODEL_PROBE_ARGS["claude"]
        self.assertIn("-p", claude)                     # print mode: the workspace trust dialog is skipped
        self.assertEqual(claude[claude.index("--allowedTools") + 1], "")                # no tools at all
        self.assertEqual(run_task.MODEL_PROBE_ARGS["agy"], ["-p", "reply with the single word ok",
                                                          "--output-format", "stream-json"])
        for argv in run_task.MODEL_PROBE_ARGS.values():
            for forbidden in ("--dangerously-skip-permissions", "danger-full-access", "dangerous"):
                self.assertNotIn(forbidden, argv)  # devin's "--permission-mode auto" is asserted above


class RunTaskTests(unittest.TestCase):
    def setUp(self):
        test_endcheck.WorktreeCopyTests.setUp(self)  # temp repo root "p" + worktree self.wt on t-001-probe
        self.flow = self.root / ".agentflow"
        shutil.copy(FLOW / "tasks/_template.md", self.flow / "tasks")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        self.env.update(AGENTFLOW_PYTHON=sys.executable, PYTHONUTF8="1",
                        AGENTFLOW_MACHINE_STATE_DIR=str(Path(self.tmp.name) / "machine"),
                        AGENTFLOW_DEVIN_MODEL_PROBE="on")  # opt into the built-in audited inference probe
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env["PATH"]
        self.env.update(GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.invalid")
        self.tool("ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1",
                  "--role", "developer", "--tool", "devin", "--status", "ready")
        self.rt_file = self.flow / "tasks" / ".runtime" / "T-001.json"

    def tearDown(self):
        for _ in range(10):  # a just-finished worker may still hold the temp tree for a moment
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

    # --- manual cycle, duplicate and terminal refusals ---------------------------------------------------------
    def test_manual_cycle_duplicate_and_relaunch(self):
        r = self.launch("T-001", "--manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("in progress", self.tool("ledger.py", "show", "T-001").stdout)
        self.assertEqual(self.attempt()["status"], "running")
        r = self.launch("T-001", "--manual")  # one task = one worker
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("already has a running attempt", r.stdout + r.stderr)
        self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 1)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        self.assertEqual(self.attempt()["status"], "exited")
        self.assertEqual(self.launch("T-001", "--manual").returncode, 0)
        self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 2)

    def test_awaiting_approval_and_terminal_states_refuse(self):
        self.tool("ledger.py", "add", "T-002", "--title", "Plan", "--stage", "1",
                  "--role", "developer", "--tool", "devin")  # blocked, awaiting approval
        src = self.flow / "tasks" / "T-001-probe.md"
        (self.flow / "tasks" / "T-002-probe.md").write_text(
            src.read_text().replace("T-001", "T-002").replace("t-001-probe", "t-002-probe"), encoding="utf-8")
        r = self.launch("T-002", "--manual")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("awaits the human's approval", r.stdout + r.stderr)
        self.tool("ledger.py", "set", "T-001", "--status", "cancelled", "--notes", "probe")
        r = self.launch("T-001", "--manual")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("final ledger status", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())

    def test_launch_lock_blocks_and_stale_lock_is_removed(self):
        lock = self.flow / "tasks" / ".runtime" / "launch.lock"
        lock.parent.mkdir(exist_ok=True)
        lock.write_text("x")
        r = self.launch("T-001", "--manual")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("another launcher run is in progress", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        old = time.time() - 400  # left by a crashed launcher: older than five minutes
        os.utime(lock, (old, old))
        r = self.launch("T-001", "--manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_corrupted_runtime_state_fails_closed(self):
        self.rt_file.parent.mkdir(exist_ok=True)
        self.rt_file.write_text("{ not json", encoding="utf-8")
        r = self.launch("T-001", "--manual")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("runtime state", r.stdout + r.stderr)

    # --- real launches with a fake worker ----------------------------------------------------------------------
    def test_launch_status_and_stop_kills_the_tree(self):
        child = Path(self.tmp.name) / "child.pid"
        body = (f'"{sys.executable}" -c "import subprocess,sys,time;'
                f"c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(120)']);"
                f"open({str(child)!r},'w').write(str(c.pid));time.sleep(120)\"")
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\n' + body + " %*",
                        'if [ "$1" = "auth" ]; then exit 0; fi\n' + body + ' "$@"')
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not child.exists():
            time.sleep(0.2)
        self.assertTrue(child.exists(), "fake worker did not start its descendant")
        child_pid = int(child.read_text())
        a = self.attempt()
        self.assertEqual(a["status"], "running")
        self.assertTrue(run_task.alive(a["pid"], a["pidStart"]))
        self.assertIn("T-001", self.launch("--status").stdout)
        r = self.launch("T-001", "--stop")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.attempt()["status"], "error")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and (run_task.alive(a["pid"]) or run_task.alive(child_pid)):
            time.sleep(0.2)
        self.assertFalse(run_task.alive(a["pid"]), "worker survived --stop")
        self.assertFalse(run_task.alive(child_pid), "managed descendant survived --stop")

    def test_wall_clock_timeout_kills_the_tree_and_records_an_error(self):
        """A tool that ignores any CLI timeout is still bounded: the launcher kills the managed tree,
        records a timeout error and releases the lease. Output streams into the log while running."""
        child = Path(self.tmp.name) / "timeout-child.pid"
        body = ('echo EARLY-STREAMED\r\n'
                f'"{sys.executable}" -c "import subprocess,sys,time;'
                f"c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(300)']);"
                f"open({str(child)!r},'w').write(str(c.pid));time.sleep(300)\"")
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\n' + body + " %*",
                        'if [ "$1" = "auth" ]; then exit 0; fi\necho EARLY-STREAMED\n' + body + ' "$@"')
        r = self.launch("T-001", "devin", env={"AGENTFLOW_WORKER_TIMEOUT": "5"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        log = Path(a["log"])
        streamed = False
        deadline = time.monotonic() + 20  # captured while the attempt still runs, not only at exit
        while time.monotonic() < deadline:
            if self.attempt()["status"] == "running" and log.is_file() and "EARLY-STREAMED" in log.read_text():
                streamed = True
                break
            if self.attempt()["status"] != "running":
                break
            time.sleep(0.2)
        self.assertTrue(streamed, "tool output did not reach the log while the attempt was running")
        a = self.wait_state("error", timeout=45)
        self.assertIn("wall-clock timeout", a["note"] or "")
        self.assertTrue(child.exists(), "fake worker did not start its descendant")
        child_pid = int(child.read_text())
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and run_task.alive(child_pid):
            time.sleep(0.2)
        self.assertFalse(run_task.alive(child_pid), "managed descendant survived the wall-clock timeout")
        reg = Path(self.env["AGENTFLOW_MACHINE_STATE_DIR"]) / "registry.json"
        self.assertEqual(json.loads(reg.read_text())["leases"], [])  # the lease was released

    def test_recorded_pid_identity_is_verified_before_any_kill(self):
        """A pid whose recorded start cannot be confirmed is not ours: no signal is sent to a possibly
        reused pid (macOS/Linux now measure start via `ps -o lstart=` as a /proc fallback)."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            self.assertTrue(run_task.alive(p.pid))
            real = run_task.pid_start(p.pid)
            if real is None:
                self.skipTest("process start identity is not measurable on this platform")
            self.assertTrue(run_task.alive(p.pid, real))
            self.assertFalse(run_task.alive(p.pid, real + 10_000_000))  # same pid, wrong start: not ours
            if os.name == "nt":  # unmeasurable identity: GetProcessTimes fails
                with patch.object(run_task.ctypes.windll.kernel32, "GetProcessTimes", return_value=0):
                    self.assertFalse(run_task.alive(p.pid, real))
            else:
                with patch.object(run_task, "pid_start", return_value=None):
                    self.assertFalse(run_task.alive(p.pid, real))  # unmeasurable: refuse the pid
        finally:
            p.kill()
            p.wait()

    def test_launch_exit_code_and_limit_detection(self):
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\necho hit your usage limit. Try again at 3:30 PM.\r\nexit /b 1',
                        'if [ "$1" = "auth" ]; then exit 0; fi\necho "hit your usage limit"\nexit 1')
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("error")
        self.assertEqual(a["exitCode"], 1)
        self.assertTrue(a["limitHit"])
        self.assertTrue(Path(a["log"]).is_file())

    def test_successful_report_mentioning_quota_is_not_a_limit(self):
        """A worker that exits 0 while its report merely discusses quota/rate-limit test cases must not set
        limitHit - the tool stays usable."""
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\n'
                        'echo covered rate limit and quota exhaustion cases, all green\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\n'
                        'echo "covered rate limit and quota exhaustion cases, all green"\nexit 0')
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("exited")
        self.assertEqual(a["exitCode"], 0)
        self.assertFalse(a["limitHit"])

    def test_probe_timeouts_kill_the_probe_tree(self):
        """Both access and model probes are bounded by the launcher and their managed children die with them."""
        child = Path(self.tmp.name) / "probe-child.pid"
        hang_cmd = ('if "%~1"=="auth" exit /b 0\r\n'
                    f'"{sys.executable}" -c "import subprocess,sys,time;'
                    "c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(300)']);"
                    f"open({str(child)!r},'w').write(str(c.pid));time.sleep(300)\"")
        hang_sh = ('if [ "$1" = "auth" ]; then exit 0; fi\n'
                   f'"{sys.executable}" -c \'import subprocess,sys,time;'
                   'c=subprocess.Popen([sys.executable,"-c","import time;time.sleep(300)"]);'
                   f'open("{child}","w").write(str(c.pid));time.sleep(300)\'')
        # the account probe hangs with a live descendant
        self.fake_devin('if "%~1"=="--hang" goto :hang\r\nif "%~1"=="auth" exit /b 0\r\nexit /b 0\r\n'
                        ':hang\r\n' + hang_cmd.split("\r\n", 1)[1],
                        'if [ "$1" = "--hang" ]; then ' + hang_sh.split("\n", 1)[1] + '; fi\n'
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_PROBE": "--hang",
                                             "AGENTFLOW_PROBE_TIMEOUT": "3"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("access check timed out after 3s", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        self.assertTrue(child.exists(), "hung probe did not start its descendant")
        child_pid = int(child.read_text())
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and run_task.alive(child_pid):
            time.sleep(0.2)
        self.assertFalse(run_task.alive(child_pid), "probe descendant survived the probe timeout")
        # the model probe hangs the same way under its own bound
        child.unlink()
        self.fake_devin(hang_cmd, hang_sh, probe="none")
        r = self.launch("T-001", "devin", env={"AGENTFLOW_MODEL_PROBE_TIMEOUT": "3"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("model inference check timed out after 3s", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())

    def test_failed_handoff_keeps_a_recoverable_attempt(self):
        self.fake_devin("exit /b 0", "exit 0")
        r = self.launch("T-001", "devin",
                        env={"AGENTFLOW_WORKER_PYTHON": str(Path(self.tmp.name) / "no-such-python")})
        self.assertNotEqual(r.returncode, 0)
        a = self.attempt()
        self.assertEqual(a["status"], "error")
        self.assertIn("launch failed", a["note"] or "")
        self.assertIsNone(a["pid"])
        self.assertIn("in progress", self.tool("ledger.py", "show", "T-001").stdout)
        reg = Path(self.env["AGENTFLOW_MACHINE_STATE_DIR"]) / "registry.json"
        self.assertEqual(json.loads(reg.read_text())["leases"], [])  # the lease went back

    def test_endcheck_violation_then_recheck(self):
        copy = self.wt / ".agentflow" / "tasks" / "T-001-probe.md"
        self.fake_devin(f'if "%~1"=="auth" exit /b 0\r\necho Outcome: completed>> "{copy}"\r\nexit /b 0',
                        f'if [ "$1" = "auth" ]; then exit 0; fi\necho "Outcome: completed" >> "{copy}"\nexit 0')
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("error")
        self.assertEqual(a["exitCode"], 0)
        self.assertIn("worktree copy", a["note"])
        r = self.launch("T-001", "--recheck")  # cause not fixed yet
        self.assertEqual(r.returncode, 1)
        main_task = self.flow / "tasks" / "T-001-probe.md"
        main_task.write_text(main_task.read_text(encoding="utf-8") + "Outcome: completed\n", encoding="utf-8")
        r = self.launch("T-001", "--recheck")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.attempt()["status"], "exited")

    # --- resource and permission preflight ----------------------------------------------------------------------
    def test_missing_executable_refuses_before_anything_is_created(self):
        r = self.launch("T-001", "devin",
                        env={"AGENTFLOW_DEVIN": str(Path(self.tmp.name) / "no-devin-here")})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("executable not found", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        self.assertIn("ready", self.tool("ledger.py", "show", "T-001").stdout)

    def test_unsupported_or_failing_access_probe_blocks_unattended_launch(self):
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\nif "%~1"=="--probe-fail" exit /b 3\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\nif [ "$1" = "--probe-fail" ]; then exit 3; fi\nexit 0')
        r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_PROBE": "off"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no supported model-access check", r.stdout + r.stderr)
        r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_PROBE": "--probe-fail"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("access check failed (exit 3)", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        # a working override records its source; nothing about the account is stored
        r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_PROBE": "--probe-ok"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertEqual(a["resourceCheck"]["probeSource"], "env")
        self.assertIsNone(a["resourceCheck"]["probe"])  # operator argv is never serialized
        self.assertTrue(a["resourceCheck"]["probeHash"])
        self.assertEqual(a["resourceCheck"]["limits"], "clear")
        self.wait_state("exited")

    def test_selected_model_inference_probe_required_denied_and_recorded(self):
        """An unattended launch proves the selected model can run inference (an explicit opt-in, bounded check):
        account access alone is not entitlement, custom probe modes fail closed, auth success with the model
        denied fails closed."""
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        env = dict(self.env)
        env.pop("AGENTFLOW_DEVIN_MODEL_PROBE", None)  # no opt-in: fail closed, never a surprise paid call
        r = subprocess.run([sys.executable, str(self.flow / "tools" / "run_task.py"), "T-001", "devin"],
                           cwd=self.root, env=env, capture_output=True, text=True, errors="replace", timeout=45)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("inference check", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_MODEL_PROBE": "off"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("inference check", r.stdout + r.stderr)
        # custom argv - including a catalog/auth call that would exit 0 - is not model evidence: fail closed
        for bad in ("catalog", "auth status", "--infer {model}", "on extra"):
            r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_MODEL_PROBE": bad})
            self.assertNotEqual(r.returncode, 0, bad)
            self.assertIn("accepts only `on`", r.stdout + r.stderr, bad)
            self.assertFalse(self.rt_file.exists(), bad)
        # account access succeeds but inference with the selected model is denied
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0', probe="deny")
        r = self.launch("T-001", "devin")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("inference with the selected model", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        # `on` opts into the built-in bounded check; the task's concrete model is appended with the tool's flag
        # and recorded with source, time and outcome
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        task = self.flow / "tasks" / "T-001-probe.md"
        task.write_text(task.read_text(encoding="utf-8").replace("Tool: devin", "Tool: devin\nModel: test-model-9"),
                        encoding="utf-8")
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        mp = self.attempt()["resourceCheck"]["modelProbe"]
        self.assertEqual((mp["model"], mp["source"], mp["result"]), ("test-model-9", "builtin", "ok"))
        self.assertEqual(mp["argv"][:2], ["-p", "reply with the single word ok"])
        self.assertEqual(mp["argv"][-2:], ["--model", "test-model-9"])
        self.assertTrue(mp["at"] and mp["timeout"])
        self.wait_state("exited")

    def test_probe_secrets_are_never_serialized(self):
        """Operator probe argv is recorded only as a hash and never shown in diagnostics, whatever shape the
        secret takes; probe output is never recorded; no env handover file is written (dummy secrets only)."""
        secrets = ["DUMMY-TOKEN-VALUE-0123456789abcdef", "hunter2", "--config hunter2"]
        self.fake_devin('if "%~1"=="--token" exit /b 2\r\nif "%~1"=="hunter2" exit /b 2\r\n'
                        'if "%~1"=="--config" exit /b 2\r\nif "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'for a in "$@"; do case "$a" in --token|hunter2|--config) exit 2;; esac; done\n'
                        'if [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        for probe in (f"--token {secrets[0]}", secrets[1], secrets[2]):
            r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_PROBE": probe})
            self.assertNotEqual(r.returncode, 0, probe)
            out = r.stdout + r.stderr
            for s in ("DUMMY-TOKEN-VALUE-0123456789abcdef", "hunter2"):
                self.assertNotIn(s, out, probe)
            self.assertNotIn("--config", out, probe)
            self.assertFalse(self.rt_file.exists(), probe)
        # a secret inside the model-probe variable fails closed without leaking anywhere
        r = self.launch("T-001", "devin", env={"AGENTFLOW_DEVIN_MODEL_PROBE": f"--api-key {secrets[0]}"})
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn(secrets[0], r.stdout + r.stderr)
        # a succeeding secret-bearing account probe leaves only a hash in the recorded evidence
        self.fake_devin('if "%~1"=="--token" exit /b 0\r\nif "%~1"=="auth" exit /b 0\r\nexit /b 0',
                        'if [ "$1" = "--token" ]; then exit 0; fi\nif [ "$1" = "auth" ]; then exit 0; fi\nexit 0')
        r = self.launch("T-001", "devin",
                        env={"AGENTFLOW_DEVIN_PROBE": f"--token {secrets[0]}",
                             "AGENTFLOW_DEVIN_ARGS": f"--flag {secrets[1]}"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        check = self.attempt()["resourceCheck"]
        self.assertEqual(check["probeSource"], "env")
        self.assertIsNone(check["probe"])
        self.assertTrue(check["probeHash"])
        self.wait_state("exited")
        raw = self.rt_file.read_text(encoding="utf-8-sig")
        for s in secrets[:2]:
            self.assertNotIn(s, raw)
            self.assertNotIn(s, r.stdout + r.stderr)
        a = self.attempt()
        self.assertNotIn("toolArgs", a)
        self.assertTrue(a["toolArgsHash"])
        # no plaintext env handover file was ever written for the attempt
        self.assertFalse((self.rt_file.parent / "T-001.env.json").exists())

    def test_observed_limit_and_full_machine_slot_wait(self):
        lim = self.flow / "tasks" / ".runtime" / "tool-limits.json"
        lim.parent.mkdir(exist_ok=True)
        until = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 3600))
        lim.write_text(json.dumps({"devin": {"until": until, "reason": "test", "at": until}}), encoding="utf-8")
        self.fake_devin("exit /b 0", "exit 0")
        r = self.launch("T-001", "devin")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("limited until", r.stdout + r.stderr)
        lim.unlink()
        helper = self.flow / "tools" / "machine_capacity.py"
        env = dict(self.env, AGENTFLOW_MACHINE_DEVIN_MAX="1")
        claim = subprocess.run([sys.executable, str(helper), "claim", "devin", str(self.root), "other",
                                "--pid", str(os.getpid())], env=env, capture_output=True, text=True)
        token = claim.stdout.strip()
        self.assertTrue(token, claim.stdout + claim.stderr)
        try:
            r = self.launch("T-001", "devin", env={"AGENTFLOW_MACHINE_DEVIN_MAX": "1"})
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("machine capacity wait", r.stdout + r.stderr)
        finally:
            subprocess.run([sys.executable, str(helper), "release", token], env=env, check=True)

    def test_dispatch_grant_becomes_the_worker_lease(self):
        self.fake_devin(f'if "%~1"=="auth" exit /b 0\r\n"{sys.executable}" -c "import time;time.sleep(1)"\r\nexit /b 0',
                        f'if [ "$1" = "auth" ]; then exit 0; fi\n"{sys.executable}" -c "import time;time.sleep(1)"\nexit 0')
        env = {**self.env, "AGENTFLOW_SHARED_DISPATCHER": "active", "PYTHONPATH": str(self.flow / "tools")}
        setup = ("import dispatch; from pathlib import Path; "
                 f"p=Path({json.dumps(str(self.root))}); dispatch.register(p, [('T-001','devin')]); "
                 "token,reason=dispatch.request(p,'T-001','devin'); "
                 "print(token or reason); raise SystemExit(0 if token else 1)")
        claim = subprocess.run([sys.executable, "-c", setup], cwd=self.root, env=env,
                               capture_output=True, text=True, timeout=15)
        self.assertEqual(claim.returncode, 0, claim.stdout + claim.stderr)
        r = self.launch("T-001", "devin", "--dispatch-grant", claim.stdout.strip(), env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.wait_state("exited")
        state = json.loads((Path(self.env["AGENTFLOW_MACHINE_STATE_DIR"]) / "registry.json").read_text())
        self.assertEqual(state["dispatch"]["grants"], [])
        self.assertEqual(state["leases"], [])

    def test_wrong_grant_is_refused(self):
        r = self.launch("T-001", "devin", "--dispatch-grant", "not-a-real-grant",
                        env={"AGENTFLOW_DEVIN": "unused"})
        self.assertNotEqual(r.returncode, 0)
        # the executable check fires before the grant exchange: give a real fake to reach the grant
        self.fake_devin("exit /b 0", "exit 0")
        r = self.launch("T-001", "devin", "--dispatch-grant", "not-a-real-grant")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("grant", r.stdout + r.stderr)

    # --- tester checkout isolation and Setup link safety ---------------------------------------------------------
    def test_tester_checkout_removed_and_link_target_untouched(self):
        (self.root / "assets").mkdir()
        (self.root / "assets" / "keep.txt").write_text("keep\n", encoding="utf-8")
        test_endcheck.git(self.root, "add", "assets/keep.txt")
        test_endcheck.git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "assets")
        (self.wt / "src").mkdir()
        (self.wt / "src" / "a.txt").write_text("product\n", encoding="utf-8")
        test_endcheck.git(self.wt, "add", "src/a.txt")
        test_endcheck.git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "product")
        sha = subprocess.check_output(["git", "-C", str(self.wt), "rev-parse", "HEAD"], text=True).strip()
        main_task = self.flow / "tasks" / "T-001-probe.md"
        main_task.write_text(main_task.read_text(encoding="utf-8") + f"Outcome: completed\nChange: {sha}\n",
                             encoding="utf-8")
        self.assertEqual(self.launch("T-001", "--manual").returncode, 0)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        self.tool("ledger.py", "set", "T-001", "--status", "review")
        tester = f"""# T-002: Check T-001

Role: tester
Tool: devin
Stage: 1
Depends on: T-001
Verifies: T-001 @ {sha}
Resume: none

## Allowed files

- `evidence/` - tester notes

## Acceptance criteria

- [ ] checked

## Checks

- `python -c "print(1)"` - probe

## Setup

- link: assets

## Result
"""
        (self.flow / "tasks" / "T-002-check.md").write_text(tester, encoding="utf-8")
        self.tool("ledger.py", "add", "T-002", "--title", "Check", "--stage", "1",
                  "--role", "tester", "--tool", "devin", "--status", "ready")
        checkout = Path(f"{self.wt}.t-002")
        r = self.launch("T-002", "--manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((checkout / "src" / "a.txt").is_file(), "detached checkout missing the change")
        link = checkout / "assets"
        self.assertTrue(link.exists(), "Setup link was not created in the checkout")
        self.assertEqual(self.launch("T-002", "--mark-finished").returncode, 0)
        self.assertFalse(checkout.exists(), "disposable checkout was not removed")
        self.assertEqual((self.root / "assets" / "keep.txt").read_text(), "keep\n",
                         "cleanup followed the junction and emptied its target")


def clean_tool_args(**update):
    """Deterministic AGENTFLOW_<TOOL>_ARGS: clear the machine's real values, then apply the test's."""
    cleared = {f"AGENTFLOW_{t.upper()}_ARGS": "" for t in ("codex", "claude", "agy", "devin")}
    cleared.update(update)
    return patch.dict(os.environ, cleared)


class ArgvParityTests(unittest.TestCase):
    """Model/effort flag building: the task's Model line wins over machine defaults (regression: a duplicate
    --model made Devin exit). Pure functions, no repo needed."""

    def args(self, tool, model=None, effort=None, env_args=None):
        with clean_tool_args(**({f"AGENTFLOW_{tool.upper()}_ARGS": env_args} if env_args else {})):
            return run_task.tool_argv(tool, "developer", "<prompt>", model, effort)

    def test_task_model_replaces_machine_default(self):
        a = self.args("devin", "swe-2-max", env_args="--model swe-2-high --foo bar")
        self.assertEqual(a.count("--model"), 1)
        tail = a[a.index("--foo"):]
        self.assertEqual(tail, ["--foo", "bar", "--model", "swe-2-max"])

    def test_machine_default_stays_without_task_model(self):
        a = self.args("devin", env_args="--model swe-2-high")
        self.assertEqual(a[-2:], ["--model", "swe-2-high"])

    def test_codex_effort_from_task_wins(self):
        with clean_tool_args(AGENTFLOW_CODEX_ARGS="-c model_reasoning_effort=xhigh -c x=1"):
            a = run_task.tool_argv("codex", "developer", "<p>", "gpt-6.1-sol", "medium")
        self.assertNotIn("model_reasoning_effort=xhigh", a)
        self.assertEqual(a, ["exec", "-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=medium",
                             "-c", "x=1", "--sandbox", "danger-full-access", "<p>"])

    def test_codex_default_effort_kept_without_task_effort(self):
        with clean_tool_args(AGENTFLOW_CODEX_ARGS="-c model_reasoning_effort=xhigh"):
            a = run_task.tool_argv("codex", "developer", "<p>", None, None)
        self.assertIn("model_reasoning_effort=xhigh", a)

    def test_claude_and_agy_model_effort(self):
        with clean_tool_args(AGENTFLOW_CLAUDE_ARGS="--effort medium"):
            a = run_task.tool_argv("claude", "developer", "<p>", "opus", "xhigh")
        self.assertEqual(a[-4:], ["--model", "opus", "--effort", "xhigh"])
        with clean_tool_args(AGENTFLOW_AGY_ARGS="--effort low"):
            a = run_task.tool_argv("agy", "developer", "<p>", "m1", "high")
        self.assertEqual(a[-4:], ["--model", "m1", "--effort", "high"])

    def test_tester_argv_matches_the_matrix(self):
        with clean_tool_args():
            self.assertEqual(run_task.tool_argv("claude", "tester", "<p>", None, None)[:3],
                             ["-p", "<p>", "--allowedTools"])
            agy = run_task.tool_argv("agy", "tester", "<p>", None, None)
            self.assertEqual(agy, ["-p", "<p>", "--output-format", "stream-json"])
            self.assertNotIn("-i", agy)  # regression: interactive agy hung a Tester attempt
            self.assertFalse(any("dangerous" in a for a in agy))
            self.assertEqual(run_task.tool_argv("codex", "tester", "<p>", None, None)[1:4],
                             ["--sandbox", "workspace-write", "--add-dir"])


if __name__ == "__main__":
    unittest.main()
