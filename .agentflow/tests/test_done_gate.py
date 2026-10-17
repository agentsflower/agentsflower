"""The completion gate (improvement-plan section 3): stable `X-NN:` criterion IDs, per-criterion outcome
lines, evidence file paths bound to the task scope, artifact/base binding of the verify record, the
integrated-result check inside accept.py, and the structured `gate.py done` completion command."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FLOW = Path(__file__).resolve().parent.parent
PY = sys.executable


def sh(cwd, *cmd, check=True):
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and p.returncode:
        raise AssertionError(f"{' '.join(map(str, cmd))} failed in {cwd}:\n{p.stdout}\n{p.stderr}")
    return p


def new_repo(path, file="README.md"):
    path.mkdir(parents=True, exist_ok=True)
    sh(path, "git", "init", "-q", "-b", "master")
    sh(path, "git", "config", "user.email", "t@example.invalid")
    sh(path, "git", "config", "user.name", "t")
    (path / file).write_text("base\n", encoding="utf-8")
    sh(path, "git", "add", "-A")
    sh(path, "git", "commit", "-qm", "init")


def task_text(criteria=("- [ ] P-01: the probe file exists.",),
              checks=('- `python -c "print(1)"` - probe',),
              allowed="- `src/`", worktree=""):
    return f"""# T-001: Probe

Role: developer
Tool: codex
Stage: 1
Depends on: none
Branch: t-001-probe
Worktree: {worktree}
Independent check: none - end-to-end probe
Resume: none

## Goal

Probe.

## Allowed files

{allowed}

## Do not touch

- `.agentflow/`

## Setup

nothing

## Port

nothing

## Rebuild together

nothing

## Acceptance criteria

{chr(10).join(criteria)}

## Checks

{chr(10).join(checks)}

## Result
"""


def tester_text(sha, tid="T-002"):
    return f"""# {tid}: Review

Role: tester
Tool: codex
Stage: 1
Depends on: none
Verifies: T-001 @ {sha}
Resume: none

## Goal

Review the probe.

## Allowed files

- nothing

## Do not touch

- `.agentflow/`

## Setup

nothing

## Port

nothing

## Rebuild together

nothing

## Acceptance criteria

- [ ] R-01: the artifact is reviewed.
- [ ] R-02: the claims are checked.

## Checks

- `python -c "print(1)"` - probe

## Result
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        sh(self.base, "git", "--version")  # keep Windows handles calm before cleanup
        self.tmp.cleanup()

    def install_tools(self, root):
        flow = root / ".agentflow"
        shutil.copytree(FLOW / "tools", flow / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        (flow / "tasks").mkdir(parents=True)
        shutil.copy(FLOW / "tasks" / "_template.md", flow / "tasks" / "_template.md")
        (flow / "state").mkdir()
        return flow

    def tool(self, root, name, *args, check=True):
        return sh(root, PY, "-X", "utf8", root / ".agentflow" / "tools" / name, *args, check=check)

    def start_attempt(self, root, tid="T-001", checkouts=True):
        """What run-task.ps1 records and creates: the attempt baseline and the worktrees from 'checkouts'."""
        out = root / ".agentflow" / "task.json"
        self.tool(root, "gate.py", "task", tid, "--out", out)
        t = json.loads(out.read_text(encoding="utf-8"))
        out.unlink()
        rt = root / ".agentflow" / "tasks" / ".runtime"
        rt.mkdir(parents=True, exist_ok=True)
        (rt / f"{tid}.json").write_text(json.dumps({"taskId": tid, "attempts": [
            {"n": 1, "status": "exited", "exitCode": 0, "baseline": t["baseline"]}]}), encoding="utf-8")
        if checkouts:
            for c in t["checkouts"]:
                Path(c["path"]).parent.mkdir(parents=True, exist_ok=True)
                if "branch" in c:
                    sh(c["repo"], "git", "worktree", "add", c["path"], "-b", c["branch"])
                else:
                    sh(c["repo"], "git", "worktree", "add", "--detach", c["path"], c["sha"])
        return t

    def commit_in(self, path, rel, content="probe\n"):
        f = Path(path) / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
        sh(path, "git", "add", "-A")
        sh(path, "git", "commit", "-qm", "[T-001] feat: probe")
        return sh(path, "git", "rev-parse", "HEAD").stdout.strip()

    def finish(self, root, tid="T-001", role="developer", result=""):
        """The worker's Result plus the ledger moves the launcher and acceptance make around it."""
        p = next((root / ".agentflow" / "tasks").glob(f"{tid}-*.md"))
        p.write_text(p.read_text(encoding="utf-8") + result, encoding="utf-8")
        self.tool(root, "ledger.py", "add", tid, "--title", "Probe", "--stage", "1", "--role", role,
                  "--tool", "codex", "--status", "ready")
        rt = root / ".agentflow" / "tasks" / ".runtime" / f"{tid}.json"
        state = json.loads(rt.read_text(encoding="utf-8"))
        state["attempts"][-1]["status"] = "running"
        rt.write_text(json.dumps(state), encoding="utf-8")
        self.tool(root, "ledger.py", "set", tid, "--status", "in progress")
        state["attempts"][-1]["status"] = "exited"
        rt.write_text(json.dumps(state), encoding="utf-8")
        sh(root, "git", "add", ".agentflow")
        sh(root, "git", "commit", "-qm", "memory")

    def dev_project(self, file="README.md", **task_kwargs):
        """A single-repository project with a developer task, an exited attempt and a worktree."""
        root = self.base / "project"
        new_repo(root, file=file)
        flow = self.install_tools(root)
        wt = self.base / "wt" / "project-t-001-probe"
        (flow / "tasks" / "T-001-probe.md").write_text(task_text(worktree=str(wt), **task_kwargs), encoding="utf-8")
        self.start_attempt(root)
        return root, wt

    def done(self, root, tid="T-001", check=False):
        out = root / ".agentflow" / "done.json"
        r = self.tool(root, "gate.py", "done", tid, "--out", out, check=check)
        data = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        return r, data

    def dev_result(self, sha, criteria="Criteria:\n- P-01: pass - evidence: src/probe.txt\n"):
        return f"Outcome: completed\nChange: {sha}\n{criteria}"

    def verified_project(self):
        """A finished developer task whose `gate.py verify` already passed."""
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        self.assertEqual(self.tool(root, "gate.py", "verify", "T-001").returncode, 0)
        return root, wt, sha


class CriterionIdsTests(Base):
    """E-01: required criteria carry stable `X-NN:` IDs; preflight refuses missing or duplicate IDs."""

    def test_preflight_refuses_criteria_without_ids(self):
        root, wt = self.dev_project(criteria=("- [ ] a plain criterion",))
        self.tool(root, "ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--status", "ready")
        out = root / ".agentflow" / "pre.json"
        self.tool(root, "gate.py", "preflight", "T-001", "--out", out, check=False)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(data["ok"])
        self.assertTrue(any("criterion" in p and "ID" in p for p in data["problems"]), data["problems"])

    def test_preflight_refuses_duplicate_ids(self):
        root, wt = self.dev_project(criteria=("- [ ] P-01: first", "- [ ] P-01: second"))
        self.tool(root, "ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--status", "ready")
        out = root / ".agentflow" / "pre.json"
        self.tool(root, "gate.py", "preflight", "T-001", "--out", out, check=False)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(data["ok"])
        self.assertTrue(any("P-01" in p for p in data["problems"]), data["problems"])

    def test_preflight_accepts_stable_ids(self):
        root, wt = self.dev_project()
        self.tool(root, "ledger.py", "add", "T-001", "--title", "Probe", "--stage", "1", "--role", "developer",
                  "--tool", "codex", "--status", "ready")
        out = root / ".agentflow" / "pre.json"
        r = self.tool(root, "gate.py", "preflight", "T-001", "--out", out, check=False)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["problems"], [], r.stdout + r.stderr)
        self.assertEqual(r.returncode, 0)


class OutcomeLinesTests(Base):
    """E-01: the Result maps every required criterion ID to `- <id>: <verdict> - <evidence>`."""

    def test_verify_needs_an_outcome_line_per_criterion(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=f"Outcome: completed\nChange: {sha}\n")
        r = self.tool(root, "gate.py", "verify", "T-001", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("P-01", r.stdout)
        self.assertIn("outcome line", r.stdout)

    def test_verify_fails_on_worse_than_pass_verdict(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha, "Criteria:\n- P-01: partial - flaky probe\n"))
        r = self.tool(root, "gate.py", "verify", "T-001", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("P-01", r.stdout)
        self.assertIn("partial", r.stdout)


class EvidenceTests(Base):
    """E-02: file paths declared in criteria/Result are validated against the task scope."""

    def test_in_scope_evidence_must_exist(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/other.txt")
        self.finish(root, result=self.dev_result(sha))
        r = self.tool(root, "gate.py", "verify", "T-001", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("src/probe.txt", r.stdout)
        self.assertIn("not found", r.stdout)

    def test_evidence_outside_scope_is_rejected(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(
            sha, "Criteria:\n- P-01: pass - evidence: ../outside/ev.txt\n"))
        r = self.tool(root, "gate.py", "verify", "T-001", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("outside the task's scope", r.stdout)

    def test_evidence_in_another_tasks_runtime_is_rejected(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(
            sha, "Criteria:\n- P-01: pass - evidence: .agentflow/tasks/.runtime/T-999.verify.1.log\n"))
        r = self.tool(root, "gate.py", "verify", "T-001", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("T-999", r.stdout)
        self.assertIn("scope", r.stdout)


class BindingTests(Base):
    """E-02: a bound verify record is invalidated by a new attempt, a moved artifact or base, or an
    edited header."""

    def test_moved_base_invalidates_the_bound_record(self):
        root, wt, sha = self.verified_project()
        (root / "later.txt").write_text("moved\n", encoding="utf-8")
        sh(root, "git", "add", "later.txt")
        sh(root, "git", "commit", "-qm", "main moved")
        self.tool(root, "ledger.py", "set", "T-001", "--status", "review")
        r = self.tool(root, "ledger.py", "set", "T-001", "--status", "done", "--commit", sha, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("stale", (r.stdout + r.stderr).lower())

    def test_same_base_accepts(self):
        root, wt, sha = self.verified_project()
        self.tool(root, "ledger.py", "set", "T-001", "--status", "review")
        r = self.tool(root, "ledger.py", "set", "T-001", "--status", "done", "--commit", sha, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_new_attempt_invalidates_the_bound_record(self):
        root, wt, sha = self.verified_project()
        rt = root / ".agentflow" / "tasks" / ".runtime" / "T-001.json"
        state = json.loads(rt.read_text(encoding="utf-8"))
        state["attempts"].append({"n": 2, "status": "exited", "exitCode": 0,
                                  "baseline": state["attempts"][0]["baseline"]})
        rt.write_text(json.dumps(state), encoding="utf-8")
        self.tool(root, "ledger.py", "set", "T-001", "--status", "review")
        r = self.tool(root, "ledger.py", "set", "T-001", "--status", "done", "--commit", sha, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("stale", (r.stdout + r.stderr).lower())

    def test_header_edit_invalidates_the_bound_record(self):
        root, wt, sha = self.verified_project()
        p = root / ".agentflow" / "tasks" / "T-001-probe.md"
        p.write_text(p.read_text(encoding="utf-8").replace("## Goal", "## Goal\n\nExtra requirement.", 1),
                     encoding="utf-8")
        self.tool(root, "ledger.py", "set", "T-001", "--status", "review")
        r = self.tool(root, "ledger.py", "set", "T-001", "--status", "done", "--commit", sha, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("stale", (r.stdout + r.stderr).lower())

    def test_moved_artifact_has_no_bound_record(self):
        root, wt, sha = self.verified_project()
        sha2 = self.commit_in(wt, "src/probe2.txt")
        self.tool(root, "ledger.py", "set", "T-001", "--status", "review")
        r = self.tool(root, "ledger.py", "set", "T-001", "--status", "done", "--commit", sha2, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no passing verify record", r.stdout + r.stderr)


class IntegratedTests(Base):
    """E-03: acceptance checks the trial-merge result on the current base and records its progress."""

    def test_accept_checks_the_integrated_result(self):
        check = ('- `python -c "import pathlib,sys;sys.exit('
                 "0 if pathlib.Path('mode.txt').read_text().strip()=='base' else 1)\"` - mode stays 'base'")
        root, wt = self.dev_project(file="mode.txt", checks=(check,))
        sha = self.commit_in(wt, "src/probe.txt")
        (root / "mode.txt").write_text("v2\n", encoding="utf-8")  # the base moves: the check passes on the
        sh(root, "git", "commit", "-qam", "mode v2")            # artifact but fails on the merged result
        self.finish(root, result=self.dev_result(sha))
        r = self.tool(root, "accept.py", "T-001", check=False)
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("integrated", r.stdout)
        self.assertFalse((root / "src" / "probe.txt").exists(), "the failed integrated check stopped the merge")
        self.assertEqual((root / "mode.txt").read_text(encoding="utf-8").strip(), "v2")

    def test_accept_records_integrated_progress(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r = self.tool(root, "accept.py", "T-001", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        prog = json.loads((root / ".agentflow" / "tasks" / ".runtime" / "T-001.accept.json")
                          .read_text(encoding="utf-8"))
        self.assertTrue(prog["integrated"][""]["ok"])
        self.assertIn("", prog["merged"])


class DoneTests(Base):
    """E-04/E-05: one structured completion command; pre-existing failures are reported separately."""

    def test_done_outputs_structured_json(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r, data = self.done(root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(data["ok"])
        self.assertEqual(data["criteria"], {"P-01": "pass"})
        self.assertEqual(data["sha"], sha)
        self.assertEqual(data["checks"][0]["exit"], 0)
        rec = json.loads((root / ".agentflow" / "tasks" / ".runtime" / "T-001.verify.json")
                         .read_text(encoding="utf-8"))[-1]
        self.assertTrue(rec["ok"])
        head = sh(root, "git", "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(rec["base"], {"": head})

    def test_done_reuses_a_bound_record(self):
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r1, d1 = self.done(root)
        self.assertTrue(d1["ok"])
        r2, d2 = self.done(root)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertEqual(d2.get("reused"), 1, d2)
        recs = json.loads((root / ".agentflow" / "tasks" / ".runtime" / "T-001.verify.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual(len(recs), 1, "a bound PASS is reused, not re-measured")

    def test_done_reuse_is_bound_to_check_definitions_and_environment(self):
        """B-06: a bound PASS is reused only while its checksHash - the check definitions, the task's
        env and the OS/shell - still matches this evaluation; a changed input or a legacy record
        without the field is re-measured, never trusted."""
        root, wt = self.dev_project()
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r1, d1 = self.done(root)
        self.assertTrue(d1["ok"])
        vpath = root / ".agentflow" / "tasks" / ".runtime" / "T-001.verify.json"
        recs = json.loads(vpath.read_text(encoding="utf-8"))
        self.assertTrue(recs[0].get("checksHash"), "a done record binds its check definitions")
        recs[0]["checksHash"] = "0" * 64  # a changed input: the same artifact is re-measured
        vpath.write_text(json.dumps(recs), encoding="utf-8")
        r2, d2 = self.done(root)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertEqual(d2.get("reused"), 0)
        self.assertEqual(len(json.loads(vpath.read_text(encoding="utf-8"))), 2)
        recs = json.loads(vpath.read_text(encoding="utf-8"))
        for rec in recs:
            rec.pop("checksHash", None)    # a pre-checksHash record carries no evidence of that binding
        vpath.write_text(json.dumps(recs), encoding="utf-8")
        r3, d3 = self.done(root)
        self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
        self.assertEqual(d3.get("reused"), 0)
        self.assertEqual(len(json.loads(vpath.read_text(encoding="utf-8"))), 3)

    def test_done_reports_a_merge_conflict(self):
        root, wt = self.dev_project()
        (root / "src").mkdir()
        (root / "src" / "probe.txt").write_text("main version\n", encoding="utf-8")
        sh(root, "git", "add", "src/probe.txt")
        sh(root, "git", "commit", "-qm", "main adds probe")  # the worktree branch adds the same path
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r, data = self.done(root, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(data["ok"])
        self.assertTrue(any("conflict" in p or "merge" in p for p in data["problems"]), data["problems"])

    def test_done_marks_a_preexisting_failure(self):
        root, wt = self.dev_project(checks=('- `python -c "import sys;sys.exit(3)"` - always fails',))
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r, data = self.done(root, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(data["ok"])
        self.assertTrue(any("pre-existing" in p for p in data["problems"]), data["problems"])
        self.assertEqual(data["preExisting"], ['python -c "import sys;sys.exit(3)"'])

    def test_done_marks_an_introduced_failure(self):
        check = ('- `python -c "import pathlib,sys;sys.exit('
                 "0 if not pathlib.Path('src/probe.txt').exists() else 1)\"` - probe must not exist")
        root, wt = self.dev_project(checks=(check,))
        sha = self.commit_in(wt, "src/probe.txt")
        self.finish(root, result=self.dev_result(sha))
        r, data = self.done(root, check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(data["ok"])
        self.assertTrue(any("this change" in p or "introduced" in p for p in data["problems"]), data["problems"])
        self.assertEqual(data["preExisting"], [])


class TesterReviewTests(Base):
    """E-01: a completed negative review stays representable; the Tester verdict is the worst criterion."""

    def test_completed_negative_review_is_representable(self):
        root = self.base / "project"
        new_repo(root)
        flow = self.install_tools(root)
        wt = self.base / "wt" / "project-t-001-probe"
        (flow / "tasks" / "T-001-probe.md").write_text(task_text(worktree=str(wt)), encoding="utf-8")
        self.start_attempt(root)
        sha = self.commit_in(wt, "src/probe.txt")
        (flow / "tasks" / "T-002-review.md").write_text(tester_text(sha), encoding="utf-8")
        self.start_attempt(root, tid="T-002", checkouts=False)
        p = flow / "tasks" / "T-002-review.md"
        p.write_text(p.read_text(encoding="utf-8")
                     + "Outcome: completed\nVerdict: fail\nCriteria:\n"
                     + "- R-01: pass - evidence: src/probe.txt\n"
                     + "- R-02: fail - evidence: src/probe.txt - the probe is empty\n", encoding="utf-8")
        r = self.tool(root, "gate.py", "verify", "T-002", check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rec = json.loads((root / ".agentflow" / "tasks" / ".runtime" / "T-002.verify.json")
                         .read_text(encoding="utf-8"))[-1]
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["criteria"], {"R-01": "pass", "R-02": "fail"})


if __name__ == "__main__":
    unittest.main()
