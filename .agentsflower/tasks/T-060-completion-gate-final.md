# T-060: Evidence and completion gate - carry verified artifact + fix audit Task-File scope

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-056
Branch: t-060-completion-gate-final
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-060-completion-gate-final
Independent check: tester
Resume: none

## Goal

Successor of rejected T-032: its artifact (a4f0642a911befd8769a40fbbe13feeb579a045c,
the complete E-01..E-06 completion gate, 289 tests green in its own run) is
blocked only by a defect in the merge-history audit - the audit flags ANY
committed `.agentflow/tasks/` change as a Task-File commit, including the
contract-declared `_template.md` product file. The prepared worktree already
sits on branch t-060-completion-gate-final at the preserved commit a4f0642 -
keep that base. Carry the verified artifact AND fix the audit scope so the
flag no longer trips on product files under tasks/.

## Read first

- .agentflow/tasks/T-032-completion-gate.md (rejected contract + Result - the artifact you inherit)
- .agentflow/tools/gate.py worktree_copy_problems (~line 427) - the over-broad `.agentflow/tasks` path filter
- .agentflow/docs/improvement-plan.md (section 3) and .agentflow/docs/ai-handoff-protocol.md
- .agentflow/tests/test_endcheck.py, test_parallel.py, test_cli.py, test_done_gate.py (from the artifact)

## Allowed files

- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/ledger.py
- .agentflow/tools/cli.py
- .agentflow/tools/run_task.py
- .agentflow/tasks/_template.md
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/docs/model-options.json (inherited T-032 base carries it)
- .agentflow/docs/release-validation.md
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/t-*.md (other Task Files)
- .agentflow/tasks/.runtime/
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- .agentflow/roles/, .agentflow/commands/, .claude/commands/
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] M-01: The merge-history audit no longer flags a committed `.agentflow/tasks/_template.md` change as a Task-File commit (product template); it still flags committed `t-*.md` files and `.agentflow/tasks/.runtime/` files (worker memory + launcher-owned state).
- [ ] M-02: The T-032 scenario is reproduced: a branch carrying a _template.md change + real Task-File commit flags only the latter; the artifact's own _template.md edit passes the audit.
- [ ] M-03: Every T-032 criterion still holds on this branch (E-01..E-06: criterion IDs, evidence binding, integrated checks, agentflow done, pre-existing-defect separation, release metadata) - the artifact is complete; fix only the audit scope and consolidate the release record.
- [ ] M-04: All T-050/T-056-verified behaviors stay green: fail-closed readers, bound acceptance, locked --stop, group-scoped holds, classification, takeover block, recovery capture, Resume.
- [ ] M-05: Full suite passes verbatim; VERSION/AGENTS/CHANGELOG reflect 2.14.0 (or the consolidation patch) accurately with migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-audit and baseline regressions.
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` - preflight criteria-ID enforcement.
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - the artifact's own gate tests.
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` - completion command surface.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result

Outcome: completed
Change: 9c7450ae4ffa7b8a1d648cb3727365b9e298f731 on t-060-completion-gate-final
Files:
- .agentflow/tools/gate.py - worktree_copy_problems: per-commit diffs now exclude the template-owned .agentflow/tasks/_template.md; docstring names the audit scope
- .agentflow/tests/test_endcheck.py - _template.md added to the fixture baseline; 3 audit-scope regression tests
- .agentflow/docs/ai-handoff-protocol.md - endcheck bullet: the audit covers Task Files and launcher runtime state, not the product template
- CHANGELOG.md - 2.14.0 entry consolidated with the audit-scope bullet
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` -> pass (3 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (292 passed / 0 failed / 3 skipped)
Criteria without a command:
- M-01: pass - .agentflow/tools/gate.py filters per-commit diffs through an exclude pathspec for .agentflow/tasks/_template.md; T-file and launcher runtime-state commits still flagged per .agentflow/tests/test_endcheck.py
- M-02: pass - .agentflow/tests/test_endcheck.py reproduces the T-032 scenario (template-only commit clean; template plus Task File commit flags only the latter); artifact commit a4f0642 diffs empty under the excluded product path on the real branch
- M-03: pass - the T-032 artifact rides unchanged at a4f0642; E-01..E-06 stay green incl. .agentflow/tests/test_done_gate.py and .agentflow/tests/test_parallel.py
- M-04: pass - full verbatim suite green; no regression in the T-050 and T-056 verified behaviors
- M-05: pass - .agentflow/VERSION, the AGENTS.md block and CHANGELOG.md read 2.14.0 with migration notes; the 2.14.0 record is consolidated rather than a patch bump; decisions.md text proposed below
Found, not fixed:
- none
Proposed memory updates:
- decisions.md, dated 2026-10-17: "T-060 carries the verified T-032 completion-gate artifact (a4f0642) into 2.14.0 and fixes the merge-history audit defect that rejected it: worktree_copy_problems excludes the template-owned product template under .agentflow/tasks via an exclude pathspec, so product template commits on a task branch pass while Task File and launcher runtime-state commits still fail. Rejected alternative: enumerating only Task File and runtime patterns as positive pathspecs would let other stray files under tasks pass silently; the exclusion stays fail-closed. Consolidated into the unreleased 2.14.0 record."
