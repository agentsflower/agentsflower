# T-062: Merge-audit Task-File scope fix (product template must not flag)

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-056
Branch: t-062-audit-scope-fix
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-062-audit-scope-fix
Independent check: tester
Resume: none

## Goal

Narrow the merge-history audit in gate.py (worktree_copy_problems) so a
committed `.agentflow/tasks/_template.md` change does NOT flag "commits Task
Files" while committed `t-*.md` and `.agentflow/tasks/.runtime/` files still
do. This unblocks the verified T-032 artifact (a4f0642) and every future task
that legitimately edits the product template. Keep every other audit behavior
intact (fail-closed on un-auditable history is a feature).

## Read first

- .agentflow/tools/gate.py worktree_copy_problems (~line 427)
- .agentflow/tests/test_endcheck.py (merge-audit fixtures)
- .agentflow/docs/ai-handoff-protocol.md (Task File rule)

## Allowed files

- .agentflow/tools/gate.py
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/t-*.md (other Task Files)
- .agentflow/tasks/.runtime/
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] A-01: A committed `_template.md` change on a task branch does not flag; committed `t-*.md` or `.runtime/` changes still flag; un-auditable history still fails closed (octopus/other errors still block).
- [ ] A-02: Regression coverage in test_endcheck.py: template-only commit clean, template+Task-File commit flags only the Task File, runtime-file commit flags.
- [ ] A-03: Full suite passes verbatim; increment VERSION (patch), sync AGENTS block, CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-audit regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 8373c54f3a45b9364bc89cc0f8ebadfe51aa8b7d on t-062-audit-scope-fix
Files:
- .agentflow/tools/gate.py - worktree_copy_problems audits --name-only output under .agentflow/tasks with :(exclude) pathspec for _template.md (diff-tree gains -r: -p implied recursion, --name-only does not); the flag now names the offending paths
- .agentflow/tests/test_endcheck.py - fixture baseline gains the real _template.md; three new WorktreeCopyTests
- .agentflow/docs/ai-handoff-protocol.md - Runtime state item 2 notes the _template.md carve-out (behavior change only)
- .agentflow/VERSION - 2.13.2 -> 2.13.3
- AGENTS.md - AgentFlow block version line -> 2.13.3
- CHANGELOG.md - 2.13.3 entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (269 passed / 0 failed, 3 skipped)
Criteria without a command:
- A-01 - covered by the merge-audit command: template-only commit -> []; committed t-*.md and .runtime/ still flag; octopus merge and diff-error paths still fail closed (test_octopus_merge_fails_closed_as_unauditable and the returncode branch unchanged)
- A-02 - exactly the three new tests: test_template_commit_alone_is_clean, test_template_and_task_file_commit_flags_only_the_task_file (flag names T-999-evil.md, not _template.md), test_runtime_file_commit_flags
- A-03 - full suite pass above; VERSION/AGENTS/CHANGELOG updated in the same commit; decisions.md text proposed below
Found, not fixed:
- None. Rename edge verified: renaming a Task File onto the _template.md path still flags via the source name (rename pairs match pathspec on both sides).
Proposed memory updates:
- .agentflow/state/decisions.md, dated 2026-10-17: "The merge-history audit (gate.py worktree_copy_problems) excludes .agentflow/tasks/_template.md: it is template-owned product, not a Task File. The broad .agentflow/tasks/ pathspec made every legitimate template edit fail endcheck and blocked the verified T-032 artifact a4f0642. Rejected: whitelisting only T-*.md/.runtime/ - any other committed path under tasks/ must still flag."
