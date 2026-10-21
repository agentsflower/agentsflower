"""Stage 5 evaluation scenarios (improvement-plan section 6, T-038).

Reproducible fixtures drive the real launcher, gate and acceptance code in
disposable git repositories. Every managed "devin" here is a fake CLI script
written by the test - simulated processes, no real model, account or platform
call. The open-task migration proof installs onto a disposable fixture project.
Anything that needs a real platform is skipped with a stated reason, never faked.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_endcheck  # noqa: E402

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import gate  # noqa: E402
import install  # noqa: E402

TASK = """# T-001: {title}

Role: developer
Tool: devin
Stage: 5
Depends on: none
Branch: t-001-{slug}
Worktree: {wt}
Independent check: none - disposable evaluation fixture (simulated worker)
Resume: none
Routing exception: disposable evaluation fixture - no real model exists

## Goal

{goal}

## Allowed files

{allowed}
## Do not touch

- `.agentflow/`

## Acceptance criteria

{criteria}
## Checks

{checks}

## Result
"""

# A fake worker body is Python executed with cwd = the task worktree; TASK names
# the main Task File and git()/sha() are predefined. Simulated workers only.
WORKER_PREAMBLE = """import subprocess, sys
from pathlib import Path
TASK = {task!r}
def git(*a):
    subprocess.run(["git", *a], check=True, capture_output=True)
def sha():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
"""


def write_result(files, criteria):
    """A worker Result body; `{sha}` is filled by the worker with its own HEAD commit."""
    return ("Outcome: completed\nChange: {sha}\nFiles:\n" + files
            + "\nCriteria:\n" + criteria + "\n")


class ScenarioFixture(unittest.TestCase):
    """A disposable project: git repo + real .agentflow/tools, one ready developer task, a fake devin CLI."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.root, self.wt = base / "p", base / "wt" / "p-t-001-task"
        self.flow = self.root / ".agentflow"
        shutil.copytree(FLOW / "tools", self.flow / "tools",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (self.flow / "tasks").mkdir(parents=True)
        shutil.copy(FLOW / "tasks/_template.md", self.flow / "tasks" / "_template.md")
        (self.root / ".gitignore").write_text("__pycache__/\n.agentflow/tasks/.runtime/\n",
                                              encoding="utf-8")
        test_endcheck.git(base, "init", "-q", "-b", "main", str(self.root))
        test_endcheck.git(self.root, "config", "user.name", "t")
        test_endcheck.git(self.root, "config", "user.email", "t@example.invalid")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        self.env.update(AGENTFLOW_PYTHON=sys.executable, PYTHONUTF8="1",
                        AGENTFLOW_MACHINE_STATE_DIR=str(base / "machine"),
                        AGENTFLOW_DEVIN_MODEL_PROBE="on")  # the built-in check; the fake exits 0 anyway
        self.env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + self.env["PATH"]
        self.rt_file = self.flow / "tasks" / ".runtime" / "T-001.json"

    def tearDown(self):
        if self.wt.exists():
            subprocess.run(["git", "-C", str(self.root), "worktree", "remove", "--force",
                            str(self.wt)], capture_output=True)
        for _ in range(10):  # a just-finished worker may still hold the temp tree briefly
            try:
                self.tmp.cleanup()
                return
            except OSError:
                time.sleep(0.5)

    def tool(self, name, *args, check=True):
        r = subprocess.run([sys.executable, str(self.flow / "tools" / name), *args],
                           cwd=self.root, env=self.env, capture_output=True, text=True, encoding="utf-8")
        if check:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def launch(self, *args, timeout=45):
        return subprocess.run([sys.executable, str(self.flow / "tools" / "run_task.py"), *args],
                              cwd=self.root, env=self.env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout)

    def attempt(self, n=-1):
        return json.loads(self.rt_file.read_text(encoding="utf-8-sig"))["attempts"][n]

    def wait_done(self, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            a = self.attempt()
            if a["status"] != "running":
                return a
            time.sleep(0.2)
        self.fail(f"attempt did not finish: {self.attempt()}")

    def task_file(self):
        return self.flow / "tasks" / "T-001-task.md"

    def make_task(self, slug, title, goal, allowed, criteria, checks, files):
        """Write the Task File and product files, commit the base, register the task as ready."""
        for path, text in files.items():
            p = self.root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        self.task_file().write_text(TASK.format(
            slug=slug, title=title, goal=goal, wt=self.wt, allowed=allowed,
            criteria=criteria, checks=checks), encoding="utf-8")
        test_endcheck.git(self.root, "add", "-A")
        test_endcheck.git(self.root, "commit", "-qm", "scenario base")
        self.tool("ledger.py", "add", "T-001", "--title", title, "--stage", "5",
                  "--role", "developer", "--tool", "devin", "--status", "ready")

    def fake_devin(self, body):
        """A simulated devin CLI: probes answer ok, a worker invocation runs the given Python body."""
        script = Path(self.tmp.name) / "worker.py"
        script.write_text(WORKER_PREAMBLE.format(task=str(self.task_file())) + body, encoding="utf-8")
        py, ws = str(Path(sys.executable)), str(script)
        if os.name == "nt":
            exe = Path(self.tmp.name) / "fake-devin.cmd"
            exe.write_text(
                "@echo off\r\n"
                'if "%~1"=="--version" echo fake-devin 9.9.9 simulated& exit /b 0\r\n'
                'if "%~1"=="auth" exit /b 0\r\n'
                'if "%~2"=="reply with the single word ok" exit /b 0\r\n'
                f'"{py}" "{ws}"\r\nexit /b %ERRORLEVEL%\r\n', encoding="ascii")
        else:
            exe = Path(self.tmp.name) / "fake-devin.sh"
            exe.write_text(
                "#!/bin/sh\n"
                'if [ "$1" = "--version" ]; then echo "fake-devin 9.9.9 simulated"; exit 0; fi\n'
                'if [ "$1" = "auth" ]; then exit 0; fi\n'
                'if [ "$2" = "reply with the single word ok" ]; then exit 0; fi\n'
                f'exec "{py}" "{ws}"\n', encoding="ascii")
            exe.chmod(0o755)
        self.env["AGENTFLOW_DEVIN"] = str(exe)

    def verify(self):
        return self.tool("gate.py", "verify", "T-001", check=False)

    def verify_records(self):
        p = self.flow / "tasks" / ".runtime" / "T-001.verify.json"
        return json.loads(p.read_text(encoding="utf-8"))


class ScenarioTests(ScenarioFixture):
    """The plan's named scenario cases, end to end: launch -> attempt -> verify -> accept."""

    def test_scenario_bug_fix_simulated_worker(self):
        """Bug-fix task, simulated worker: the lifecycle machinery carries a failing project check
        to green through launch, evidence-bound verify and acceptance merge."""
        self.make_task(
            "bug-fix", "Fix the calculator bug (bug-fix scenario)",
            "sub() adds instead of subtracting; make the project check pass.",
            allowed="- `src/calc.py` - the buggy module\n",
            criteria="- [ ] P-01: `python check_calc.py` passes\n",
            checks="- `python check_calc.py` - fails while the bug is present\n",
            files={
                "src/calc.py": "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a + b\n",
                "check_calc.py": ("import importlib.util, sys\n"
                                  "spec = importlib.util.spec_from_file_location('calc', 'src/calc.py')\n"
                                  "m = importlib.util.module_from_spec(spec)\n"
                                  "spec.loader.exec_module(m)\n"
                                  "sys.exit(0 if m.sub(5, 3) == 2 else 1)\n"),
            })
        # the scenario starts red: the project check fails on the base
        base_run = subprocess.run(gate.shell("python check_calc.py"), cwd=self.root, env=self.env,
                                capture_output=True)
        self.assertEqual(base_run.returncode, 1, "the bug must be real on the base")
        self.fake_devin(
            'Path("src/calc.py").write_text("def add(a, b):\\n    return a + b\\n\\n\\n"\n'
            '                             "def sub(a, b):\\n    return a - b\\n")\n'
            'git("add", "-A")\ngit("commit", "-qm", "fix sub()")\n'
            'open(TASK, "a").write(%s.format(sha=sha()))\n'
            % repr(write_result("- src/calc.py - sub() subtracts now\n",
                                "- P-01: pass - evidence: src/calc.py\n")))
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        a = self.wait_done()
        self.assertEqual((a["status"], a["stopReason"]), ("exited", "completed"))
        self.assertEqual(self.verify().returncode, 0, "verify must pass on the fixed artifact")
        self.tool("accept.py", "T-001")
        self.assertIn("done", self.tool("ledger.py", "show", "T-001").stdout)
        self.assertIn("return a - b", (self.root / "src/calc.py").read_text(encoding="utf-8"))
        self.assertFalse(self.wt.exists())
        # the verify record is the Stage 5 evidence binding: task, attempt, header, artifact, base
        rec = self.verify_records()[-1]
        self.assertEqual((rec["taskId"], rec["attempt"]), ("T-001", 1))
        self.assertEqual(rec["headerHash"],
                         gate.sha256(gate.header(self.task_file().read_text(encoding="utf-8"))))
        self.assertRegex(rec["sha"], r"^[0-9a-f]{40}$")
        self.assertEqual(rec["base"][""], subprocess.check_output(
            ["git", "-C", str(self.root), "rev-parse", "HEAD~1"], text=True).strip(),
            "base binds the pre-merge HEAD")
        self.assertEqual(rec["criteria"], {"P-01": "pass"})
        self.assertTrue(rec["ok"])

    def test_scenario_contract_change_reverifies_moved_artifact_and_base(self):
        """Contract-change task, simulated worker: a passed verify binds the exact artifact and
        base - a branch that moved past its reported Change fails verify until re-reported."""
        self.make_task(
            "contract", "Bump the API contract to v2 (contract-change scenario)",
            "contract/api.txt goes to version 2 and the client follows.",
            allowed="- `contract/` - the shared contract folder\n- `src/client.py` - the consumer\n",
            criteria=("- [ ] P-01: contract/api.txt declares version 2\n"
                      "- [ ] P-02: src/client.py consumes version 2\n"),
            checks="- `python check_contract.py` - contract and client must agree\n",
            files={
                "contract/api.txt": "version: 1\n",
                "src/client.py": 'CONTRACT_VERSION = "1"\n',
                "check_contract.py": ("import sys\n"
                                      "api = open('contract/api.txt').read()\n"
                                      "cl = open('src/client.py').read()\n"
                                      "sys.exit(0 if 'version: 2' in api and 'CONTRACT_VERSION = \"2\"' in cl else 1)\n"),
            })
        self.fake_devin(
            'Path("contract/api.txt").write_text("version: 2\\n")\n'
            'Path("src/client.py").write_text(\'CONTRACT_VERSION = "2"\\n\')\n'
            'git("add", "-A")\ngit("commit", "-qm", "contract v2")\n'
            'open(TASK, "a").write(%s.format(sha=sha()))\n'
            % repr(write_result("- contract/api.txt - declared v2\n- src/client.py - follows v2\n",
                                "- P-01: pass - evidence: contract/api.txt\n"
                                "- P-02: pass - evidence: src/client.py\n")))
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        a = self.wait_done()
        self.assertEqual(a["status"], "exited")
        self.assertEqual(self.verify().returncode, 0, "first artifact passes")
        rec1 = self.verify_records()[-1]
        sha1 = rec1["sha"]
        base1 = rec1["base"][""]
        # the artifact moves: a contract amendment lands on the branch after the PASS
        (self.wt / "contract" / "notes.md").write_text("v2 amendment notes\n", encoding="utf-8")
        test_endcheck.git(self.wt, "add", "contract/notes.md")
        test_endcheck.git(self.wt, "commit", "-qm", "contract amendment")
        sha2 = subprocess.check_output(["git", "-C", str(self.wt), "rev-parse", "HEAD"],
                                       text=True).strip()
        # and the base moves too: an unrelated merge reaches main meanwhile
        (self.root / "docs").mkdir()
        (self.root / "docs" / "other.md").write_text("unrelated\n", encoding="utf-8")
        test_endcheck.git(self.root, "add", "docs/other.md")
        test_endcheck.git(self.root, "commit", "-qm", "other work on main")
        r = self.verify()
        self.assertEqual(r.returncode, 1, "a moved artifact must not pass on the stale report")
        self.assertIn("Result Change is " + sha1, r.stdout + r.stderr)
        # the worker re-reports the moved artifact; verify binds the new sha AND the moved base
        task = self.task_file()
        task.write_text(task.read_text(encoding="utf-8").replace(sha1, sha2), encoding="utf-8")
        self.assertEqual(self.verify().returncode, 0)
        rec2 = self.verify_records()[-1]
        self.assertEqual(rec2["sha"], sha2)
        self.assertNotEqual(rec2["base"][""], base1, "evidence re-binds the current base")
        self.assertEqual(rec2["base"][""],
                         subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                                text=True).strip())
        self.tool("accept.py", "T-001")
        merged = (self.root / "contract" / "api.txt").read_text(encoding="utf-8")
        self.assertIn("version: 2", merged)
        self.assertTrue((self.root / "contract" / "notes.md").exists())
        self.assertTrue((self.root / "docs" / "other.md").exists())

    def test_scenario_quota_limit_recovery_simulated(self):
        """Quota/limit recovery, simulated: the fake provider's limit line classifies the end,
        the draft is preserved, the recorded hold refuses a same-tool relaunch, and the
        successor attempt is told what happened and finishes the task."""
        self.make_task(
            "quota", "Repair the draft after a quota hold (quota-recovery scenario)",
            "a worker hit a provider limit mid-task; finish src/draft.py.",
            allowed="- `src/draft.py` - the interrupted draft\n",
            criteria="- [ ] P-01: src/draft.py holds the finished repair\n",
            checks="- `python -c \"print(1)\"` - placeholder check\n",
            files={"src/draft.py": ""})
        self.fake_devin(
            'Path("src/draft.py").write_text("# half-finished repair draft\\n")\n'
            'print("Error: usage limit reached; try again later")\nsys.exit(1)\n')
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        a = self.wait_done()
        self.assertEqual((a["status"], a["stopReason"]), ("error", "limit"))
        self.assertTrue(a["limitHit"])
        self.assertIn("usage limit reached", a["limitPhrase"])
        self.assertIn("src/draft.py", a["recovery"]["repos"][0]["modified"])
        # the Orchestrator records the observed hold; a same-tool relaunch is refused while it stands
        self.tool("tick.py", "limit", "devin", "usage limit reached")
        r = self.launch("T-001", "devin")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("limited until", r.stdout + r.stderr)
        self.assertEqual(len(json.loads(self.rt_file.read_text())["attempts"]), 1,
                         "a refused relaunch creates no attempt")
        # the recorded reset time passes (simulated clock: both holds written to the past)
        limits_file = self.flow / "tasks" / ".runtime" / "tool-limits.json"
        lim = json.loads(limits_file.read_text(encoding="utf-8"))
        lim["devin"]["until"] = "2000-01-01T00:00:00Z"
        limits_file.write_text(json.dumps(lim), encoding="utf-8")
        reg = Path(self.env["AGENTFLOW_MACHINE_STATE_DIR"]) / "registry.json"
        state = json.loads(reg.read_text(encoding="utf-8"))
        state["limits"]["devin"] = 946684800.0
        reg.write_text(json.dumps(state), encoding="utf-8")
        # the successor attempt continues the preserved draft and is told the story
        self.fake_devin(
            'Path("src/draft.py").write_text("finished repair after the quota hold\\n")\n'
            'git("add", "-A")\ngit("commit", "-qm", "finish the interrupted draft")\n'
            'open(TASK, "a").write(%s.format(sha=sha()))\n'
            % repr(write_result("- src/draft.py - finished after the hold\n",
                                "- P-01: pass - evidence: src/draft.py\n")))
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        a2 = self.wait_done()
        self.assertEqual((a2["status"], a2["stopReason"]), ("exited", "completed"))
        self.assertIn("'limit'", a2["handover"])
        self.assertIn("1 modified", a2["handover"])
        self.assertEqual(self.verify().returncode, 0)
        self.tool("accept.py", "T-001")
        self.assertIn("done", self.tool("ledger.py", "show", "T-001").stdout)

    def test_scenario_interrupted_merge_resume_simulated(self):
        """Interrupted-merge recovery, simulated: an acceptance killed after the merge but
        before the ledger step resumes from git state and .accept.json - merged once, never twice."""
        self.make_task(
            "merge", "Land the fix despite an interrupted acceptance (merge-recovery scenario)",
            "accept the fix even when the first accept run dies mid-merge.",
            allowed="- `src/fix.txt` - the fix\n",
            criteria="- [ ] P-01: src/fix.txt reaches main\n",
            checks="- `python -c \"print(1)\"` - placeholder check\n",
            files={})
        self.fake_devin(
            'Path("src").mkdir(exist_ok=True)\nPath("src/fix.txt").write_text("the fix\\n")\n'
            'git("add", "-A")\ngit("commit", "-qm", "the fix")\n'
            'open(TASK, "a").write(%s.format(sha=sha()))\n'
            % repr(write_result("- src/fix.txt - the fix\n",
                                "- P-01: pass - evidence: src/fix.txt\n")))
        self.assertEqual(self.launch("T-001", "devin").returncode, 0)
        self.assertEqual(self.wait_done()["status"], "exited")
        # simulated crash point of accept.py: merge done, ledger not yet updated - the durable
        # progress record shows exactly what an interrupted run leaves behind
        self.assertEqual(self.verify().returncode, 0)
        sha = self.verify_records()[-1]["sha"]
        test_endcheck.git(self.root, "merge", "--no-ff", "t-001-merge", "-m", "Merge T-001: merge")
        progress = {"taskId": "T-001", "integrated": {"": {"ok": True}}, "merged": [""]}
        gate.write_atomic(self.flow / "tasks" / ".runtime" / "T-001.accept.json", progress)
        r = self.tool("accept.py", "T-001")
        self.assertIn("already merged", r.stdout)
        merges = subprocess.check_output(
            ["git", "-C", str(self.root), "log", "--format=%s", "--grep=Merge T-001"],
            text=True).strip().splitlines()
        self.assertEqual(len(merges), 1, "the branch is merged exactly once across the interruption")
        self.assertIn("done", self.tool("ledger.py", "show", "T-001").stdout)
        self.assertFalse(self.wt.exists())
        kept = json.loads((self.flow / "tasks" / ".runtime" / "T-001.accept.json").read_text())
        self.assertEqual(kept["merged"], [""])
        self.assertTrue((self.root / "src/fix.txt").exists())

    @unittest.skipUnless(
        os.environ.get("AGENTFLOW_REAL_PLATFORM") == "1",
        "needs a real authenticated worker CLI and provider quota: set AGENTFLOW_REAL_PLATFORM=1 "
        "to run a genuine tool session; every other scenario in this file uses simulated workers")
    def test_scenario_real_platform_launch_opt_in(self):
        """Real-platform variant (skipped by default): with AGENTFLOW_REAL_PLATFORM=1 and a real
        devin CLI on PATH or AGENTFLOW_DEVIN, prove the tool answers --version. No model call."""
        exe = os.environ.get("AGENTFLOW_DEVIN") or shutil.which("devin")
        self.assertIsNotNone(exe, "opted in but no devin CLI is available")
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


OLD_VERSION = "2.12.0"


class OpenTaskMigrationTests(unittest.TestCase):
    """V-02: `install.py --update` onto a project with open tasks preserves ledger statuses, open
    Task Files and project-owned docs/settings while delivering the current template - the
    migration notes recorded in the Stage 5 CHANGELOG entries then apply to intact state."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.machine_env = patch.dict(os.environ, {"AGENTFLOW_MACHINE_STATE_DIR": self.tmp.name})
        self.machine_env.start()
        self.addCleanup(self.machine_env.stop)
        self.repo = Path(self.tmp.name) / "project"
        old = self.repo / ".agentflow"
        for rel, text in {
            "VERSION": OLD_VERSION + "\n",
            "README.md": "# old AgentFlow readme\n",
            "docs/ai-handoff-protocol.md": "# old protocol (2.12.0)\n",
            "docs/typesafe.md": "# old typesafe note\n",
            "roles/developer.md": "# old developer role\n",
            "commands/start-role.md": "# old command\n",
            "tasks/_template.md": "# old task template\n",
            "tools/gate.py": "# old gate\n",
            "tools/ledger.py": "# old ledger\n",
            "tools/install.py": "# old installer\n",
            "tools/local-helper.py": "# project-added helper, kept by --update\n",
            "dashboard/build.py": "# old dashboard\n",
            "tests/test_install.py": "# old test\n",
            # project-owned memory and settings
            "state/handoff.md": "# Handoff\n\nas of yesterday\n",
            "state/decisions.md": "# Decisions\n\n- our call\n",
            "state/known-issues.md": "# Known issues\n\n- ours\n",
            "state/session-log.md": "# Session log\n",
            "state/current-step.md": "# Current step\n\n- launch T-009\n",
            "state/questions.md": "# Questions\n",
            "docs/project-rules.md": "# Project rules\n\n- Main branch: master.\n- talk in English\n",
            "docs/project-plan.md": "# Roadmap\n\n## Stage 1: ours\n",
            "docs/model-options.json": '{"policy": "devin only", "options": {"devin": {"tool": "devin"}}}\n',
            "template-source.json": '{"template": "C:/old/template", "version": "' + OLD_VERSION + '"}\n',
        }.items():
            p = old / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        # open Task Files and a mixed-status ledger, as a mid-flight project holds them
        (old / "tasks" / "T-007-open-bugfix.md").write_text(
            "# T-007: open bug fix\n\nRole: developer\nTool: devin\nStage: 3\nDepends on: none\n"
            "Branch: t-007-open-bugfix\nWorktree: D:\\tmp\\wt-t-007\nIndependent check: tester\n"
            "Resume: none\n\n## Goal\n\nfix it\n\n## Allowed files\n\n- `src/x.py`\n\n"
            "## Acceptance criteria\n\n- [ ] P-01: fixed\n\n## Checks\n\n- `python -c \"print(1)\"`\n\n"
            "## Result\n", encoding="utf-8")
        (old / "tasks" / "T-009-open-docs.md").write_text(
            "# T-009: open docs task\n\nRole: developer\nTool: codex\nStage: 3\nDepends on: T-007\n"
            "Branch: t-009-open-docs\nWorktree: D:\\tmp\\wt-t-009\nIndependent check: none - docs\n"
            "Resume: none\n\n## Goal\n\nwrite docs\n\n## Allowed files\n\n- `docs/x.md`\n\n"
            "## Acceptance criteria\n\n- [ ] P-01: written\n\n## Checks\n\n- `python -c \"print(1)\"`\n\n"
            "## Result\n", encoding="utf-8")
        (old / "state").mkdir(exist_ok=True)
        (old / "state" / "tasks.md").write_text(
            "# Task Ledger\n\nWritten only through `python .agentflow/tools/ledger.py`.\n\n"
            "| ID | Title | Stage | Role | Tool | Status | Depends on | Commit / artifact | Notes | Updated |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| T-005 | shipped work | 2 | developer | devin | done |  | abc1234 |  | 2026-10-15 10:00 |\n"
            "| T-007 | open bug fix | 3 | developer | devin | in progress |  |  | attempt 2 running | 2026-10-20 09:00 |\n"
            "| T-009 | open docs task | 3 | developer | codex | ready | T-007 |  |  | 2026-10-20 09:30 |\n",
            encoding="utf-8")
        # project-owned docs outside .agentflow and own entry-point text around an old block
        (self.repo / "runbook").mkdir(parents=True)
        (self.repo / "runbook" / "deploy.md").write_text("# own runbook\n", encoding="utf-8")
        (self.repo / "AGENTS.md").write_text(
            "# Own rules\n\nKeep this line.\n\n" + install.BEGIN + "\n## AgentFlow\n\nAgentFlow version: "
            + OLD_VERSION + ". old block text\n" + install.END + "\n", encoding="utf-8")
        (self.repo / "CLAUDE.md").write_text(
            install.BEGIN + "\n## AgentFlow\n\nold claude block\n" + install.END + "\n", encoding="utf-8")
        (self.repo / ".gitignore").write_text(
            "/own/\n" + install.GBEGIN + "\n# old block\n" + install.GEND + "\n", encoding="utf-8")
        (self.repo / ".claude" / "commands").mkdir(parents=True)
        (self.repo / ".claude" / "commands" / "start-role.md").write_text(
            "Read `.agentflow/commands/start-role.md` (old wording).\n", encoding="utf-8")
        test_endcheck.git(self.repo.parent, "init", "-q", "-b", "master", str(self.repo))
        test_endcheck.git(self.repo, "config", "user.name", "t")
        test_endcheck.git(self.repo, "config", "user.email", "t@example.invalid")
        test_endcheck.git(self.repo, "add", "-A")
        test_endcheck.git(self.repo, "commit", "-qm", "project with open tasks on " + OLD_VERSION)
        self.snapshot = {p.relative_to(self.repo).as_posix(): p.read_bytes()
                         for p in self.repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    def tearDown(self):
        self.tmp.cleanup()

    def test_update_preserves_open_tasks_and_delivers_the_template(self):
        plan = install.install(self.repo, update=True, dry=False)
        same = self.snapshot.get  # project-owned bytes must be identical to before
        for rel in (".agentflow/state/tasks.md", ".agentflow/state/handoff.md",
                    ".agentflow/state/decisions.md", ".agentflow/state/known-issues.md",
                    ".agentflow/state/session-log.md", ".agentflow/state/current-step.md",
                    ".agentflow/state/questions.md", ".agentflow/docs/project-rules.md",
                    ".agentflow/docs/project-plan.md", ".agentflow/docs/model-options.json",
                    ".agentflow/tasks/T-007-open-bugfix.md", ".agentflow/tasks/T-009-open-docs.md",
                    "runbook/deploy.md"):
            self.assertEqual((self.repo / rel).read_bytes(), same(rel),
                             f"project-owned {rel} must survive the update byte-for-byte")
        # the template side moved forward: every owned file now equals the shipped template
        for rel in ("VERSION", "README.md", "docs/ai-handoff-protocol.md", "docs/typesafe.md",
                    "roles/developer.md", "commands/start-role.md", "tasks/_template.md",
                    "tools/gate.py", "tools/ledger.py", "tools/install.py", "tools/run_task.py",
                    "tools/route.py", "tools/tick.py", "tools/accept.py", "tools/limit_detection.py",
                    "tools/quota_groups.py", "tools/hooks.py", "dashboard/build.py",
                    "tests/test_install.py", "tests/test_scenarios.py"):
            self.assertEqual((self.repo / ".agentflow" / rel).read_bytes(),
                             (FLOW / rel).read_bytes(), f"template-owned {rel} not updated")
        self.assertEqual((self.repo / ".agentflow/VERSION").read_text().strip(),
                         install.version())
        # a file the project added inside an owned directory is kept and reported, not deleted
        self.assertTrue((self.repo / ".agentflow/tools/local-helper.py").exists())
        self.assertTrue(any("local-helper.py" in n for n in plan.notes))
        # entry points: own text preserved, the block carries the new version
        agents = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(agents.startswith("# Own rules"))
        self.assertIn(f"AgentFlow version: {install.version()}", agents)
        self.assertNotIn("old block text", agents)
        self.assertIn("Keep this line.", agents)
        claude = (self.repo / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("@AGENTS.md", claude)
        self.assertNotIn("old claude block", claude)
        self.assertTrue((self.repo / ".gitignore").read_text(encoding="utf-8").startswith("/own/"))
        self.assertEqual((self.repo / ".claude/commands/start-role.md").read_text(encoding="utf-8"),
                         install.command_pointer("start-role"))
        src = json.loads((self.repo / ".agentflow" / "template-source.json").read_text())
        self.assertEqual(src["version"], install.version())
        # the migration notes' task-side steps apply to operable state: the new tools still read
        # the preserved ledger statuses and parse the preserved open Task File
        env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFLOW_")}
        env["PYTHONUTF8"] = "1"
        show = subprocess.run([sys.executable, str(self.repo / ".agentflow/tools/ledger.py"),
                               "show", "T-007"], cwd=self.repo, env=env,
                              capture_output=True, text=True)
        self.assertEqual(show.returncode, 0, show.stdout + show.stderr)
        self.assertIn("in progress", show.stdout)
        show9 = subprocess.run([sys.executable, str(self.repo / ".agentflow/tools/ledger.py"),
                                "show", "T-009"], cwd=self.repo, env=env,
                               capture_output=True, text=True)
        self.assertIn("ready", show9.stdout)
        out = Path(self.tmp.name) / "task.json"
        r = subprocess.run([sys.executable, str(self.repo / ".agentflow/tools/gate.py"),
                            "task", "T-007", "--out", str(out)], cwd=self.repo, env=env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        parsed = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual((parsed["role"], parsed["branch"]), ("developer", "t-007-open-bugfix"))
        self.assertEqual(parsed["criteria"], ["P-01"])

    def test_stage5_changelog_entries_carry_migration_notes(self):
        """Every Stage 5 release (2.12.1 .. current, the improvement-plan releases) records what
        an installed project must do - the notes this migration test applies mechanically."""
        text = (FLOW.parent / "CHANGELOG.md").read_text(encoding="utf-8")
        entries = re.findall(r"(?ms)^## (\d+\.\d+\.\d+) - \d{4}-\d{2}-\d{2}\n(.*?)(?=^## |\Z)", text)
        stage5 = [(v, body) for v, body in entries
                  if tuple(map(int, v.split("."))) >= (2, 12, 1)]
        self.assertTrue(stage5, "no Stage 5 changelog entries found")
        for v, body in stage5:
            self.assertRegex(body, r"(?im)^-? ?Migration\b|^Migration\b",
                             f"{v} records no migration note for installed projects")


if __name__ == "__main__":
    unittest.main()
