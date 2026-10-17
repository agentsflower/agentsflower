"""The Task File header (everything above "## Result") ignores trailing blank lines. Regression: a worker that
appended the missing "## Result" heading after an empty line failed the end check although nothing above changed."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gate  # noqa: E402

TASK = "# T-1: Probe\n\nRole: developer\n\n## Checks\n\n- `npm test` - unit\n"


class HeaderTests(unittest.TestCase):
    def test_appended_result_after_blank_line_keeps_the_hash(self):
        later = TASK + "\n## Result\nOutcome: completed\n"
        self.assertEqual(gate.sha256(gate.header(later)), gate.sha256(gate.header(TASK)))

    def test_existing_baselines_stay_valid(self):
        self.assertEqual(gate.header(TASK), TASK)  # a file ending in one newline hashes as before
        self.assertEqual(gate.header(TASK.replace("\n", "\r\n")), TASK)

    def test_a_real_change_above_result_still_counts(self):
        changed = TASK.replace("- `npm test` - unit", "- `npm test -- --grep x` - unit") + "\n## Result\n"
        self.assertNotEqual(gate.header(changed), gate.header(TASK))


DEV = """# T-001: Probe

Role: developer
Tool: devin
Stage: 1
Depends on: none
Branch: t-001-probe
Worktree: {wt}
Independent check: none - probe
Resume: none

## Allowed files

- `src/a.txt` - probe

## Acceptance criteria

- [ ] P-01: probe

## Checks

- `python -c "print(1)"` - probe

## Result
"""


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


class WorktreeCopyTests(unittest.TestCase):
    """Regression: Devin wrote and committed its Result in the Task File copy inside its worktree."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.root, self.wt = base / "p", base / "wt" / "p-t-001-probe"
        flow = self.root / ".agentflow"
        shutil.copytree(Path(__file__).resolve().parents[1] / "tools", flow / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        (flow / "tasks").mkdir(parents=True)
        (flow / "tasks" / "T-001-probe.md").write_text(DEV.format(wt=self.wt), encoding="utf-8")
        (flow / "tasks" / "_template.md").write_text("# Task File template\n", encoding="utf-8")
        git(base, "init", "-q", "-b", "main", str(self.root))
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
        git(self.root, "worktree", "add", "-q", str(self.wt), "-b", "t-001-probe")

    def tearDown(self):
        subprocess.run(["git", "-C", str(self.root), "worktree", "remove", "--force", str(self.wt)], capture_output=True)
        self.tmp.cleanup()

    def problems(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import gate; "
                "print('\\n'.join(gate.worktree_copy_problems(gate.parse('T-001'))))")
        r = subprocess.run([sys.executable, "-c", code, str(self.root / ".agentflow" / "tools")], capture_output=True,
                           text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return [line for line in r.stdout.splitlines() if line]

    def test_clean_worktree_has_no_problem(self):
        self.assertEqual(self.problems(), [])

    def commit(self, repo, message):
        git(repo, "add", "-A")
        git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message)

    def test_merge_of_main_memory_is_not_a_worker_edit(self):
        (self.root / ".agentflow/tasks/other.md").write_text("main memory\n")
        self.commit(self.root, "main memory")
        (self.wt / "product.txt").write_text("work\n")
        self.commit(self.wt, "product")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "merge", "--no-ff", "main", "-m", "sync")
        self.assertEqual(self.problems(), [])

    def test_reverted_task_edit_still_rejected(self):
        (self.wt / ".agentflow/tasks/other.md").write_text("worker memory\n")
        self.commit(self.wt, "bad edit")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "revert", "--no-edit", "HEAD")
        self.assertTrue(any("commits Task Files" in x for x in self.problems()))

    def test_task_edit_introduced_in_merge_rejected(self):
        (self.root / "main.txt").write_text("main\n")
        self.commit(self.root, "main product")
        (self.wt / "product.txt").write_text("work\n")
        self.commit(self.wt, "product")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "merge", "--no-ff", "--no-commit", "main")
        (self.wt / ".agentflow/tasks/other.md").write_text("merge edit\n")
        self.commit(self.wt, "merge with forbidden edit")
        self.assertTrue(any("commits Task Files" in x for x in self.problems()))

    def test_octopus_merge_fails_closed_as_unauditable(self):
        """A merge with three parents cannot be reconstructed by --remerge-diff; the audit refuses
        instead of silently passing."""
        (self.wt / "product.txt").write_text("work\n", encoding="utf-8")
        self.commit(self.wt, "product")
        for name in ("b1", "b2"):
            git(self.wt, "checkout", "-q", "-b", name)
            (self.wt / f"{name}.txt").write_text(f"{name}\n", encoding="utf-8")
            self.commit(self.wt, name)
            git(self.wt, "checkout", "-q", "t-001-probe")
        # a commit of our own, so neither merged head fast-forwards: the merge gets three parents
        (self.wt / "head.txt").write_text("head\n", encoding="utf-8")
        self.commit(self.wt, "own work")
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "merge", "b1", "b2", "-m", "octopus")
        self.assertTrue(any("octopus" in x for x in self.problems()), self.problems())

    def test_product_template_commit_is_not_a_task_commit(self):
        """_template.md is template-owned product (protocol: What goes where), not a worker Task File."""
        (self.wt / ".agentflow/tasks/_template.md").write_text("# edited template\n", encoding="utf-8")
        self.commit(self.wt, "template edit")
        self.assertEqual(self.problems(), [])

    def test_template_edit_plus_task_file_flags_only_the_task_commit(self):
        """T-032 scenario: a branch carrying a _template.md change and a real Task-File
        commit is flagged for the Task File only."""
        (self.wt / ".agentflow/tasks/_template.md").write_text("# edited template\n", encoding="utf-8")
        self.commit(self.wt, "template edit")
        (self.wt / ".agentflow/tasks/T-002-other.md").write_text("# T-2\n", encoding="utf-8")
        self.commit(self.wt, "task file")
        found = [x for x in self.problems() if "commits Task Files" in x]
        self.assertEqual(len(found), 1, found)

    def test_runtime_state_commit_still_rejected(self):
        rt = self.wt / ".agentflow" / "tasks" / ".runtime"
        rt.mkdir()
        (rt / "T-001.json").write_text("{}\n", encoding="utf-8")
        self.commit(self.wt, "runtime state")
        self.assertTrue(any("commits Task Files" in x for x in self.problems()))

    def test_result_in_the_copy_and_its_commit_are_reported(self):
        copy = self.wt / ".agentflow" / "tasks" / "T-001-probe.md"
        copy.write_text(copy.read_text(encoding="utf-8") + "Outcome: completed\n", encoding="utf-8")
        found = self.problems()
        self.assertEqual(len(found), 1, found)
        self.assertIn("worktree copy", found[0])
        git(self.wt, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "chore: T-001 result")
        found = self.problems()
        self.assertEqual(len(found), 2, found)
        self.assertTrue(any("commits Task Files" in f for f in found), found)
        main = self.root / ".agentflow" / "tasks" / "T-001-probe.md"  # recovery: the Result in the main Task File
        main.write_text(main.read_text(encoding="utf-8") + "Outcome: completed\n", encoding="utf-8")
        git(self.wt, "reset", "-q", "--hard", "HEAD~1")
        self.assertEqual(self.problems(), [])


if __name__ == "__main__":
    unittest.main()
