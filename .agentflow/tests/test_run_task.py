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
import gate  # noqa: E402
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

    def test_structurally_invalid_runtime_state_fails_closed(self):
        """A file that parses but is not an attempt history also refuses the launch and shows up in
        --status: schema is checked at read time, never guessed as 'no active work'."""
        self.rt_file.parent.mkdir(exist_ok=True)
        cases = [
            {"taskId": "T-999", "attempts": []},                                 # another task's state
            {"attempts": []},                                                    # names no task at all
            {"taskId": "T-001"},                                                 # no attempts list
            {"taskId": "T-001", "attempts": {"n": 1}},                           # attempts not a list
            {"taskId": "T-001", "attempts": [{"n": "1", "status": "running"}]},  # n not an int
            {"taskId": "T-001", "attempts": [{"n": 1, "status": "bogus"}]},      # unknown status
            {"taskId": "T-001", "attempts": [{"n": 1, "status": "exited", "taskId": "T-999"}]},  # other task's attempt
            ["T-001"],                                                           # not an object
            {},                                                                  # empty container is not 'no attempts'
        ]
        for bad in cases:
            with self.subTest(bad=bad):
                self.rt_file.write_text(json.dumps(bad), encoding="utf-8")
                r = self.launch("T-001", "--manual")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("runtime state", r.stdout + r.stderr)
                self.assertIn("state-error", self.launch("--status").stdout)

    def test_terminal_states_acquire_no_attempt(self):
        """done/rejected/cancelled cannot launch a new attempt; the legacy verify record that proves
        'done' (no taskId/headerHash fields) still counts - the migration path for old evidence."""
        src = (self.flow / "tasks" / "T-001-probe.md").read_text(encoding="utf-8")
        for tid in ("T-002", "T-003"):
            (self.flow / "tasks" / f"{tid}-probe.md").write_text(
                src.replace("T-001", tid).replace("t-001-probe", f"{tid.lower()}-probe"), encoding="utf-8")
            self.tool("ledger.py", "add", tid, "--title", "Probe", "--stage", "1",
                      "--role", "developer", "--tool", "devin", "--status", "ready")
        # the claim path: a recorded running attempt, then the terminal ledger transitions
        rt = self.flow / "tasks" / ".runtime"
        rt.mkdir(exist_ok=True)
        for tid in ("T-002", "T-003"):
            (rt / f"{tid}.json").write_text(json.dumps({"taskId": tid, "attempts": [{"n": 1, "status": "running"}]}),
                                           encoding="utf-8")
            self.tool("ledger.py", "set", tid, "--status", "in progress")
            state = json.loads((rt / f"{tid}.json").read_text(encoding="utf-8"))
            state["attempts"][-1]["status"] = "exited"  # the worker ended; the ledger decides next
            (rt / f"{tid}.json").write_text(json.dumps(state), encoding="utf-8")
        self.tool("ledger.py", "set", "T-002", "--status", "rejected", "--notes", "-> T-003: probe")
        # 'done' needs a passing verify: a pre-2.12.1 record without the binding fields stays valid
        self.tool("ledger.py", "set", "T-003", "--status", "review")
        (rt / "T-003.verify.json").write_text(json.dumps([{
            "n": 1, "at": "2026-10-17T00:00:00Z", "attempt": 1, "role": "developer",
            "sha": "abc1234", "target": "local", "ok": True, "problems": [], "checks": [], "log": None}]),
            encoding="utf-8")
        self.tool("ledger.py", "set", "T-003", "--status", "done", "--commit", "abc1234")
        for tid in ("T-002", "T-003"):
            r = self.launch(tid, "--manual")
            self.assertNotEqual(r.returncode, 0, tid)
            self.assertIn("final ledger status", r.stdout + r.stderr, tid)
            attempts = json.loads((rt / f"{tid}.json").read_text(encoding="utf-8"))["attempts"]
            self.assertEqual(len(attempts), 1)  # no new attempt was acquired

    def test_acceptance_is_bound_to_the_current_attempt_and_task_file(self):
        """`set --status done` takes only a PASS bound to this task, its last attempt, the current
        requirements hash and the artifact SHA. A stale PASS (earlier attempt, changed header) or a
        different artifact never accepts; a truthy non-boolean `ok` is a diagnosable error, not evidence."""
        rt_dir = self.rt_file.parent
        rt_dir.mkdir(exist_ok=True)
        sha = "a" * 40

        def task_file(tid):
            return (self.flow / "tasks" / f"{tid}-probe.md").read_text(encoding="utf-8")

        def rec(tid, hh, **kw):
            return {"n": 1, "at": "2026-10-17T00:00:00Z", "taskId": tid, "attempt": 1,
                    "role": "developer", "headerHash": hh, "sha": sha, "target": "local",
                    "ok": True, "problems": [], "checks": [], "log": None, **kw}

        def done(tid, commit=sha):
            return subprocess.run([sys.executable, str(self.flow / "tools" / "ledger.py"), "set",
                                   tid, "--status", "done", "--commit", commit],
                                  cwd=self.root, env=self.env, capture_output=True, text=True)

        # T-001: a fully bound PASS accepts
        self.rt_file.write_text(json.dumps({"taskId": "T-001", "attempts": [
            {"n": 1, "status": "running", "taskId": "T-001"}]}), encoding="utf-8")
        self.tool("ledger.py", "set", "T-001", "--status", "in progress")
        self.rt_file.write_text(json.dumps({"taskId": "T-001", "attempts": [
            {"n": 1, "status": "exited", "taskId": "T-001"}]}), encoding="utf-8")
        self.tool("ledger.py", "set", "T-001", "--status", "review")
        hh = gate.sha256(gate.header(task_file("T-001")))
        (rt_dir / "T-001.verify.json").write_text(json.dumps([rec("T-001", hh)]), encoding="utf-8")
        r = done("T-001")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        # T-002 carries the refusal cases; a refused acceptance leaves it at review
        (self.flow / "tasks" / "T-002-probe.md").write_text(
            task_file("T-001").replace("T-001", "T-002").replace("t-001-probe", "t-002-probe"), encoding="utf-8")
        self.tool("ledger.py", "add", "T-002", "--title", "Probe", "--stage", "1",
                  "--role", "developer", "--tool", "devin", "--status", "ready")
        rt2, v2 = rt_dir / "T-002.json", rt_dir / "T-002.verify.json"
        rt2.write_text(json.dumps({"taskId": "T-002", "attempts": [
            {"n": 1, "status": "running", "taskId": "T-002"}]}), encoding="utf-8")
        self.tool("ledger.py", "set", "T-002", "--status", "in progress")
        rt2.write_text(json.dumps({"taskId": "T-002", "attempts": [
            {"n": 1, "status": "exited", "taskId": "T-002"},
            {"n": 2, "status": "exited", "taskId": "T-002"}]}), encoding="utf-8")
        self.tool("ledger.py", "set", "T-002", "--status", "review")
        hh2 = gate.sha256(gate.header(task_file("T-002")))

        def rec2(**kw):
            r = rec("T-002", hh2, attempt=2)
            r.update(kw)
            return r

        v2.write_text(json.dumps([rec2(attempt=1)]), encoding="utf-8")  # PASS from the earlier attempt
        r = done("T-002")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("stale", r.stdout + r.stderr)
        v2.write_text(json.dumps([rec2(sha="b" * 40)]), encoding="utf-8")  # a different artifact
        r = done("T-002")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("artifact", r.stdout + r.stderr)
        v2.write_text(json.dumps([rec2(headerHash="0" * 64)]), encoding="utf-8")  # changed requirements
        r = done("T-002")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("stale", r.stdout + r.stderr)
        v2.write_text(json.dumps([rec2(taskId="T-999")]), encoding="utf-8")  # another task's record
        r = done("T-002")
        self.assertNotEqual(r.returncode, 0)
        v2.write_text(json.dumps([rec2(ok="yes")]), encoding="utf-8")  # truthy ok is not a PASS
        r = done("T-002")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("verify records", r.stdout + r.stderr)
        # a live last attempt cannot be accepted even with a fully bound record
        rt2.write_text(json.dumps({"taskId": "T-002", "attempts": [
            {"n": 1, "status": "exited", "taskId": "T-002"},
            {"n": 2, "status": "running", "taskId": "T-002"}]}), encoding="utf-8")
        v2.write_text(json.dumps([rec2()]), encoding="utf-8")
        r = done("T-002")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("exited", r.stdout + r.stderr)
        # the bound record passes once the attempt is exited
        rt2.write_text(json.dumps({"taskId": "T-002", "attempts": [
            {"n": 1, "status": "exited", "taskId": "T-002"},
            {"n": 2, "status": "exited", "taskId": "T-002"}]}), encoding="utf-8")
        r = done("T-002")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_malformed_verify_records_fail_closed(self):
        """A truncated or wrong-shaped verify file stops the gate with a diagnosable error -
        it is never read as 'no evidence'."""
        v = self.flow / "tasks" / ".runtime" / "T-001.verify.json"
        v.parent.mkdir(exist_ok=True)
        for bad in ("{ truncated", '{"n": 1}', '["x", 1]'):
            with self.subTest(bad=bad):
                v.write_text(bad, encoding="utf-8")
                r = subprocess.run([sys.executable, str(self.flow / "tools" / "gate.py"), "verify", "T-001"],
                                   cwd=self.root, env=self.env, capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, bad)
                self.assertIn("verify records", r.stdout + r.stderr, bad)

    def test_malformed_tool_limits_fail_closed(self):
        """A corrupt or wrong-shaped tool-limits.json refuses the launch instead of reading as 'no limits'."""
        lim = self.flow / "tasks" / ".runtime" / "tool-limits.json"
        lim.parent.mkdir(exist_ok=True)
        self.fake_devin("exit /b 0", "exit 0")
        for bad in ("{ broken", "[]", "null", '{"devin": "not-an-object"}', '{"devin": {"until": 5}}'):
            with self.subTest(bad=bad):
                lim.write_text(bad, encoding="utf-8")
                r = self.launch("T-001", "devin")
                self.assertNotEqual(r.returncode, 0, bad)
                self.assertIn("tool-limits", r.stdout + r.stderr, bad)

    def test_live_argument_is_never_an_empty_string(self):
        """Regression (PS 5.1): a trailing `--live ""` lost its value in Windows PowerShell 5.1, so gate.py
        argparse failed with 'expected one argument'. The launcher emits --live only with a non-empty list.
        Live shells: powershell 5.1 and pwsh in test_launcher_lifecycle; on POSIX run_task.py is the
        launcher itself and needs no shell delegation."""
        gate_calls, task = [], {"id": "T-001", "role": "developer", "workdir": str(self.wt),
                                "worktree": str(self.wt), "checkouts": [], "setup": [], "env": {},
                                "target": "local", "prompt": "p", "model": None, "effort": None,
                                "repos": [""], "baseline": {}}

        def fake_gate(cmd, tid, more=()):
            gate_calls.append((cmd, list(more)))
            return {"ok": True, "problems": [], "task": task} if cmd == "preflight" else task

        def fake_run(argv, **kw):  # inside a manual launch the only subprocess is the ledger transition
            self.assertIn("ledger.py", " ".join(map(str, argv)))
            return subprocess.CompletedProcess(argv, 0, "", "")

        rt_dir = Path(self.tmp.name) / "rt"
        rt_dir.mkdir()
        # Inside a managed worker the inherited AGENTFLOW_ATTEMPT_ROOT names the real checkout, so the
        # fixture's launcher root is its disposable repo - production nested_check stays untouched.
        with patch.object(run_task, "RT_DIR", rt_dir), \
                patch.object(run_task, "ROOT", self.root), \
                patch.object(run_task, "invoke_gate", side_effect=fake_gate), \
                patch.object(run_task.subprocess, "run", side_effect=fake_run):
            self.assertEqual(run_task.cmd_launch("T-001", None, True, None), 0)
            preflight = [m for c, m in gate_calls if c == "preflight"][-1]
            self.assertEqual(preflight, ["--manual"])
            (rt_dir / "T-001.json").unlink()  # end the manual attempt cleanly for the next launch
            (rt_dir / "T-009.json").write_text(json.dumps(
                {"taskId": "T-009", "attempts": [{"n": 1, "manual": True, "status": "running"}]}))
            self.assertEqual(run_task.cmd_launch("T-002", None, True, None), 0)
        preflight = [m for c, m in gate_calls if c == "preflight"][-1]
        self.assertEqual(preflight[:2], ["--live", "T-009"])
        self.assertNotIn("", preflight)

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
        self.assertEqual(self.attempt()["stopReason"], "stopped")
        self.assertTrue(self.attempt()["recovery"]["capturedAt"])
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and (run_task.alive(a["pid"]) or run_task.alive(child_pid)):
            time.sleep(0.2)
        self.assertFalse(run_task.alive(a["pid"]), "worker survived --stop")
        self.assertFalse(run_task.alive(child_pid), "managed descendant survived --stop")

    def test_stop_with_unconfirmed_pid_identity_keeps_the_lock(self):
        """Regression (T-029): a live process on the recorded pid whose start identity cannot be confirmed
        may be a reused pid. --stop must refuse instead of closing the attempt and freeing the lock, and
        no second claim can start beside it. Verified identity (or the process ending) releases it."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        try:
            rt = self.rt_file
            rt.parent.mkdir(exist_ok=True)
            att = {"n": 1, "tool": "devin", "manual": False, "status": "running",
                   "pid": p.pid, "pidStart": None, "taskId": "T-001"}
            rt.write_text(json.dumps({"taskId": "T-001", "attempts": [att]}), encoding="utf-8")
            self.tool("ledger.py", "set", "T-001", "--status", "in progress")
            # --stop refuses: the pid is alive but its identity is unconfirmed - a diagnosable block
            r = self.launch("T-001", "--stop")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("start identity", r.stdout + r.stderr)
            self.assertEqual(self.attempt()["status"], "running", "the attempt must not be closed")
            self.assertTrue(run_task.alive(p.pid), "--stop sent a signal to a possibly reused pid")
            # a second claim beside a possibly live worker is refused the same way
            r = self.launch("T-001", "--manual")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("unconfirmed", r.stdout + r.stderr)
            self.assertEqual(len(json.loads(rt.read_text())["attempts"]), 1)
            self.assertIn("blocked", self.launch("--status").stdout)  # the lock shows as a diagnosable block
            # a recorded start that does not match (a reused pid) blocks identically
            start = run_task.pid_start(p.pid)
            if start is not None:
                att["pidStart"] = start + 10_000_000
                rt.write_text(json.dumps({"taskId": "T-001", "attempts": [att]}), encoding="utf-8")
                r = self.launch("T-001", "--stop")
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(self.attempt()["status"], "running")
            # the process is really gone: --stop closes the dead attempt and releases the lock
            p.kill()
            p.wait()
            r = self.launch("T-001", "--stop")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.attempt()["status"], "error")
        finally:
            p.kill()
            p.wait()

    def test_stop_with_a_confirmed_identity_kills_the_worker(self):
        """A verified identity still releases the lock: recorded pid + matching start is ours to kill."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        try:
            start = run_task.pid_start(p.pid)
            if start is None:
                self.skipTest("process start identity is not measurable on this platform")
            att = {"n": 1, "tool": "devin", "manual": False, "status": "running",
                   "pid": p.pid, "pidStart": start, "taskId": "T-001"}
            self.rt_file.parent.mkdir(exist_ok=True)
            self.rt_file.write_text(json.dumps({"taskId": "T-001", "attempts": [att]}), encoding="utf-8")
            self.tool("ledger.py", "set", "T-001", "--status", "in progress")
            r = self.launch("T-001", "--stop")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(self.attempt()["status"], "error")
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and run_task.alive(p.pid):
                time.sleep(0.2)
            self.assertFalse(run_task.alive(p.pid), "confirmed worker survived --stop")
        finally:
            p.kill()
            p.wait()

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
        self.assertEqual(a["stopReason"], "timeout")
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
        self.assertEqual(a["limitKind"], "quota")
        self.assertTrue(a["limitPhrase"])
        self.assertEqual(a["stopReason"], "limit")
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
        self.assertEqual(a["stopReason"], "verification")
        r = self.launch("T-001", "--recheck")  # cause not fixed yet
        self.assertEqual(r.returncode, 1)
        main_task = self.flow / "tasks" / "T-001-probe.md"
        main_task.write_text(main_task.read_text(encoding="utf-8") + "Outcome: completed\n", encoding="utf-8")
        r = self.launch("T-001", "--recheck")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.attempt()["status"], "exited")

    # --- recovery: classification, draft capture, takeover, Resume --------------------------------------------------
    def test_failed_attempt_captures_drafts_and_hands_over(self):
        """An implementation failure records its classified end plus the worktree's draft state (paths,
        never contents); the next attempt's record and prompt carry the recovery handover."""
        (self.wt / "src").mkdir()
        (self.wt / "src" / "a.txt").write_text("base\n", encoding="utf-8")
        test_endcheck.git(self.wt, "add", "src/a.txt")
        test_endcheck.git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\n'
                        'echo changed>> "%CD%\\src\\a.txt"\r\necho new> "%CD%\\draft-note.txt"\r\nexit /b 2',
                        'if [ "$1" = "auth" ]; then exit 0; fi\n'
                        'echo changed >> "$PWD/src/a.txt"\necho new > "$PWD/draft-note.txt"\nexit 2')
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        a = self.wait_state("error")
        self.assertEqual(a["stopReason"], "implementation")
        self.assertFalse(a["limitHit"])
        repo = a["recovery"]["repos"][0]
        self.assertEqual(repo["branch"], "t-001-probe")
        self.assertTrue(repo["head"])
        self.assertIn("src/a.txt", repo["modified"])
        self.assertIn("draft-note.txt", repo["untracked"])
        self.assertFalse(a["recovery"]["hasResult"])
        # the successor sees the handover: on its record and inside the prompt it receives
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\necho args: %*\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\necho "args: $*"\nexit 0')
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        a = self.wait_state("exited")
        self.assertIn("Recovery handover", a["handover"])
        self.assertIn("'implementation'", a["handover"])
        self.assertIn("1 modified + 1 untracked", a["handover"])
        self.assertIn("Recovery handover", Path(a["log"]).read_text(encoding="utf-8", errors="replace"))
        self.assertEqual(a["stopReason"], "completed")
        self.assertNotIn("recovery", a)  # a completed attempt carries no recovery record

    def test_a_dead_workers_attempt_recovers_and_the_successor_is_told(self):
        """A worker process that died without a final state is closed as 'dead' with a recovery record;
        the draft is preserved and the next attempt is told what happened."""
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        start = run_task.pid_start(p.pid)
        p.kill()
        p.wait()
        att = {"n": 1, "tool": "devin", "manual": False, "status": "running",
               "pid": p.pid, "pidStart": start, "taskId": "T-001", "log": None}
        self.rt_file.parent.mkdir(exist_ok=True)
        self.rt_file.write_text(json.dumps({"taskId": "T-001", "attempts": [att]}), encoding="utf-8")
        self.tool("ledger.py", "set", "T-001", "--status", "in progress")
        (self.wt / "draft.txt").write_text("kept\n", encoding="utf-8")
        self.fake_devin("exit /b 0", "exit 0")
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        attempts = json.loads(self.rt_file.read_text(encoding="utf-8-sig"))["attempts"]
        self.assertEqual(len(attempts), 2)
        old, new = attempts
        self.assertEqual(old["status"], "error")
        self.assertEqual(old["stopReason"], "dead")
        self.assertIn("draft.txt", old["recovery"]["repos"][0]["untracked"])
        self.assertIn("'dead'", new["handover"])
        self.assertTrue((self.wt / "draft.txt").exists(), "the draft must survive the takeover")
        self.wait_state("exited")

    def test_orphaned_descendant_blocks_the_next_launch(self):
        """A managed child that outlives its worker keeps the task locked: the next launch refuses while
        it runs and proceeds once it is gone (POSIX: session scan; Windows: the worker's job object)."""
        child = Path(self.tmp.name) / "orphan.pid"
        spawn = ("import subprocess,sys;"
                 "c=subprocess.Popen([sys.executable,'-c','import time;time.sleep(120)']);"
                 f"open({str(child)!r},'w').write(str(c.pid))")
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\n' + f'"{sys.executable}" -c "{spawn}"\r\nexit /b 0',
                        'if [ "$1" = "auth" ]; then exit 0; fi\n' + f'"{sys.executable}" -c "{spawn}"\nexit 0')
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        self.wait_state("exited")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not child.exists():
            time.sleep(0.1)
        self.assertTrue(child.exists(), "fake worker did not leave its orphan")
        child_pid = int(child.read_text())
        try:
            r = self.launch("T-001", "devin")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("managed processes", r.stdout + r.stderr)
            self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 1)
        finally:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(child_pid), "/F"], capture_output=True)
            else:
                os.kill(child_pid, 9)
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.wait_state("exited")

    def test_resume_sha_keeps_drafts_bad_sha_refuses_and_start_fresh_resets(self):
        """`Resume: <sha>` continues the preserved worktree (the commit must be an ancestor - drafts are
        never silently discarded); `Resume: start fresh` resets and cleans only this worktree."""
        self.fake_devin('if "%~1"=="auth" exit /b 0\r\necho draft> "%CD%\\draft.txt"\r\nexit /b 2',
                        'if [ "$1" = "auth" ]; then exit 0; fi\necho draft > "$PWD/draft.txt"\nexit 2')
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        self.wait_state("error")
        task = self.flow / "tasks" / "T-001-probe.md"
        src = task.read_text(encoding="utf-8")

        def resume(value):
            task.write_text(src.replace("Resume: none", f"Resume: {value}"), encoding="utf-8")

        test_endcheck.git(self.root, "-c", "user.name=t", "-c", "user.email=t@t",
                          "commit", "--allow-empty", "-qm", "elsewhere")
        off_branch = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                             text=True).strip()
        resume(off_branch)
        r = self.launch("T-001", "--manual")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not an ancestor", r.stdout + r.stderr)
        self.assertTrue((self.wt / "draft.txt").exists())
        head = subprocess.check_output(["git", "-C", str(self.wt), "rev-parse", "HEAD"], text=True).strip()
        resume(head)
        self.assertEqual(self.launch("T-001", "--manual").returncode, 0)
        self.assertTrue((self.wt / "draft.txt").exists(), "Resume: <sha> must keep the draft")
        self.assertIn("'implementation'", self.attempt()["handover"])
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        (self.wt / "draft.txt").write_text("draft again\n", encoding="utf-8")
        (self.wt / "src").mkdir(exist_ok=True)
        (self.wt / "src" / "a.txt").write_text("dirty\n", encoding="utf-8")  # untracked + nothing tracked
        resume("start fresh")
        self.assertEqual(self.launch("T-001", "--manual").returncode, 0)
        self.assertFalse((self.wt / "draft.txt").exists())
        self.assertFalse((self.wt / "src" / "a.txt").exists())
        self.assertEqual(subprocess.run(["git", "-C", str(self.wt), "status", "--porcelain"],
                                        capture_output=True, text=True).stdout.strip(), "")
        self.assertIn("start fresh", self.attempt()["handover"])
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)

    def test_group_scoped_limit_blocks_and_quota_group_is_recorded(self):
        """A '<tool>:<group>' hold applies only to that quota group; the attempt records the group its
        tool+model consumes so a successor on another group is not blocked."""
        (self.flow / "docs").mkdir(exist_ok=True)
        (self.flow / "docs" / "model-options.json").write_text(json.dumps({
            "policy": "test", "options": {
                "devin": {"tool": "devin", "quota_group": "dv"},
                "devin-9": {"tool": "devin", "model_by_effort": {"high": "test-model-9"},
                            "quota_group": "dg"}}}), encoding="utf-8")
        task = self.flow / "tasks" / "T-001-probe.md"
        task.write_text(task.read_text(encoding="utf-8")
                        .replace("Tool: devin", "Tool: devin\nModel: test-model-9"), encoding="utf-8")
        lim = self.flow / "tasks" / ".runtime" / "tool-limits.json"
        lim.parent.mkdir(exist_ok=True)
        until = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 3600))
        rec = {"until": until, "reason": "test", "at": until}
        self.fake_devin("exit /b 0", "exit 0")
        lim.write_text(json.dumps({"devin:dg": rec}), encoding="utf-8")
        r = self.launch("T-001", "devin")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("devin group dg is limited", r.stdout + r.stderr)
        lim.write_text(json.dumps({"devin:other": rec}), encoding="utf-8")  # another group's hold stays out
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("exited")
        self.assertEqual(a["quotaGroup"], "dg")
        self.assertEqual(a["resourceCheck"]["quotaGroup"], "dg")

    def test_tool_wide_limit_names_the_tool_not_the_sessions_group(self):
        """A bare '<tool>' hold blocks every session of that tool, and the refusal names the
        tool-wide hold - not the session's own quota group."""
        (self.flow / "docs").mkdir(exist_ok=True)
        (self.flow / "docs" / "model-options.json").write_text(json.dumps({
            "policy": "test", "options": {
                "devin": {"tool": "devin", "quota_group": "dv"},
                "devin-9": {"tool": "devin", "model_by_effort": {"high": "test-model-9"},
                            "quota_group": "dg"}}}), encoding="utf-8")
        task = self.flow / "tasks" / "T-001-probe.md"
        task.write_text(task.read_text(encoding="utf-8")
                        .replace("Tool: devin", "Tool: devin\nModel: test-model-9"), encoding="utf-8")
        lim = self.flow / "tasks" / ".runtime" / "tool-limits.json"
        lim.parent.mkdir(exist_ok=True)
        until = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 3600))
        self.fake_devin("exit /b 0", "exit 0")
        lim.write_text(json.dumps({"devin": {"until": until, "reason": "test", "at": until}}),
                       encoding="utf-8")
        r = self.launch("T-001", "devin")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("devin is limited until", r.stdout + r.stderr)
        self.assertNotIn("devin group dg is limited", r.stdout + r.stderr)

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

- [ ] C-01: checked

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

    # --- bounded autonomy: recorded identity, launch budgets, nested sessions -----------------------------------
    def test_attempt_records_launch_identity(self):
        """B-01: every attempt stores the requested Model/effort, the resolved launch argv in safe
        form (prompt and machine args masked, never serialized), the tool's CLI version, and the
        model/effort the tool itself reported. The managed session carries the attempt marker."""
        task = self.flow / "tasks" / "T-001-probe.md"
        task.write_text(task.read_text(encoding="utf-8").replace(
            "Tool: devin", "Tool: devin\nModel: test-model-x, effort=high"), encoding="utf-8")
        self.fake_devin('if "%~1"=="--version" (echo fake-devin 9.9.9 & exit /b 0)\r\n'
                        'if "%~1"=="auth" exit /b 0\r\n'
                        'echo model: test-model-x\r\n'
                        'echo reasoning effort: high\r\n'
                        'echo attempt-marker %AGENTFLOW_ATTEMPT%\r\n',
                        'if [ "$1" = "--version" ]; then echo fake-devin 9.9.9; exit 0; fi\n'
                        'if [ "$1" = "auth" ]; then exit 0; fi\n'
                        'echo "model: test-model-x"\n'
                        'echo "reasoning effort: high"\n'
                        'echo "attempt-marker $AGENTFLOW_ATTEMPT"\n')
        self.env["AGENTFLOW_DEVIN_ARGS"] = "--token s3cr3t --model machine-default"
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("exited")
        self.assertEqual(a["requestedModel"], "test-model-x")
        self.assertEqual(a["requestedEffort"], "high")
        self.assertEqual(a["toolVersion"], "fake-devin 9.9.9")
        self.assertEqual(a["effectiveModel"], "test-model-x")
        self.assertEqual(a["effectiveEffort"], "high")
        shown = a["launch"]["argv"]
        self.assertIn("<prompt>", shown)
        self.assertIn("test-model-x", shown)                  # the task's Model line is not secret
        self.assertGreaterEqual(shown.count("<env arg>"), 2)  # --token s3cr3t (the machine --model was overridden)
        self.assertNotIn("s3cr3t", " ".join(shown))           # machine args never reach the record
        self.assertNotIn("machine-default", " ".join(shown))
        self.assertIn("attempt-marker T-001#1", Path(a["log"]).read_text(encoding="utf-8", errors="replace"))

    def test_attempt_identity_is_unknown_when_the_tool_reports_nothing(self):
        """Unavailable runtime identity is 'unknown', never guessed; a missing Model line stays null."""
        self.fake_devin('if "%~1"=="--version" exit /b 7\r\n'
                        'if "%~1"=="auth" exit /b 0\r\n'
                        'exit /b 0\r\n',
                        'if [ "$1" = "--version" ]; then exit 7; fi\n'
                        'if [ "$1" = "auth" ]; then exit 0; fi\n'
                        'exit 0\n')
        r = self.launch("T-001", "devin")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.wait_state("exited")
        self.assertIsNone(a["requestedModel"])
        self.assertEqual(a["toolVersion"], "unknown")
        self.assertEqual(a["effectiveModel"], "unknown")
        self.assertEqual(a["effectiveEffort"], "unknown")

    def test_manual_attempt_records_requested_model_and_unknown_runtime(self):
        r = self.launch("T-001", "--manual")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        a = self.attempt()
        self.assertIsNone(a["requestedModel"])
        self.assertEqual(a["toolVersion"], "unknown")
        self.assertEqual(a["effectiveModel"], "unknown")
        self.assertNotIn("launch", a)  # nothing was launched: no resolved argv exists to record

    def test_attempt_and_duration_budgets_refuse_new_attempts(self):
        """B-03: attempts and overall task duration are bounded; a refused launch adds no attempt."""
        env = {"AGENTFLOW_MAX_ATTEMPTS": "2"}
        self.assertEqual(self.launch("T-001", "--manual", env=env).returncode, 0)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        self.assertEqual(self.launch("T-001", "--manual", env=env).returncode, 0)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        r = self.launch("T-001", "--manual", env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("attempt budget", r.stdout + r.stderr)
        self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 2)
        rt = json.loads(self.rt_file.read_text())
        rt["attempts"][0]["startedAt"] = "2020-01-01T00:00:00Z"   # task time is bound to attempt 1's start
        self.rt_file.write_text(json.dumps(rt), encoding="utf-8")
        r = self.launch("T-001", "--manual",
                        env={"AGENTFLOW_MAX_ATTEMPTS": "9", "AGENTFLOW_TASK_TIMEOUT": "3600"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("duration budget", r.stdout + r.stderr)
        self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 2)

    def test_repeated_identical_failures_stop_relaunching(self):
        """B-03/B-06: the same failure signature repeated to the cap refuses another attempt."""
        self.assertEqual(self.launch("T-001", "--manual").returncode, 0)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        rt = json.loads(self.rt_file.read_text())
        for i, secs in ((2, 12), (3, 99)):  # only the volatile detail differs: one signature
            rt["attempts"].append({"n": i, "taskId": "T-001", "tool": "devin", "status": "error",
                                   "exitCode": 1, "stopReason": "implementation",
                                   "note": f"worker died after {secs}s"})
        self.rt_file.write_text(json.dumps(rt), encoding="utf-8")
        r = self.launch("T-001", "--manual", env={"AGENTFLOW_MAX_IDENTICAL_FAILURES": "2"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("identical failures", r.stdout + r.stderr)
        self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 3)
        rt["attempts"].append({"n": 4, "taskId": "T-001", "tool": "devin", "status": "error",
                               "exitCode": 1, "stopReason": "implementation",
                               "note": "a different failure"})
        self.rt_file.write_text(json.dumps(rt), encoding="utf-8")
        r = self.launch("T-001", "--manual", env={"AGENTFLOW_MAX_IDENTICAL_FAILURES": "2"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)  # the chain is broken: launch again
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)

    def test_tool_switch_budget(self):
        """B-03: platform switches are bounded; a manual attempt is not a platform switch."""
        self.assertEqual(self.launch("T-001", "--manual").returncode, 0)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        rt = json.loads(self.rt_file.read_text())
        for i, tool in enumerate(("codex", "claude"), start=2):
            rt["attempts"].append({"n": i, "taskId": "T-001", "tool": tool, "status": "error",
                                   "exitCode": 1, "stopReason": "implementation"})
        self.rt_file.write_text(json.dumps(rt), encoding="utf-8")
        env = {"AGENTFLOW_MAX_TOOL_SWITCHES": "2"}
        r = self.launch("T-001", "devin", env=env)   # a third distinct platform exceeds the cap
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("platform", r.stdout + r.stderr)
        r = self.launch("T-001", "--manual", env=env)  # the human's own session is not a switch
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)

    def test_nested_launches_need_a_delegate_rule(self):
        """B-04: a session marked AGENTFLOW_ATTEMPT/AGENTFLOW_ATTEMPT_ROOT is a worker; a launch whose own
        root equals the marker is a nested helper - refused unless a project Preflight delegates it."""
        nested = {"AGENTFLOW_ATTEMPT": "T-900#1", "AGENTFLOW_ATTEMPT_ROOT": str(Path(self.root).resolve())}
        r = self.launch("T-001", "--manual", env=nested)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("delegat", r.stdout + r.stderr)
        self.assertFalse(self.rt_file.exists())
        r = self.launch("T-001", "--manual",
                        env={"AGENTFLOW_ATTEMPT": "T-900#1",
                             "AGENTFLOW_ATTEMPT_ROOT": str(Path(self.tmp.name) / "elsewhere")})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)  # another checkout is not this helper
        self.assertEqual(self.launch("T-001", "--mark-finished").returncode, 0)
        docs = self.flow / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "engineering-rules.md").write_text(
            "# rules\n\n## Preflight\n\n- delegate: on\n", encoding="utf-8")
        r = self.launch("T-001", "--manual", env=nested)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


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
