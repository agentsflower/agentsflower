# T-063: Independently verify merge-audit scope fix

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-062
Verifies: T-062 @ 8373c54

## Goal

Independently evaluate the T-062 artifact (merge-history audit scope fix) in a
disposable checkout at the exact commit. The artifact makes
`_template.md` product-file commits pass the audit while real Task-File
(t-*.md) and .runtime commits still fail it - the unblock for T-032/T-060.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-062-audit-scope-fix.md (contract + Result)
- The candidate diff `git diff main...8373c54` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-062 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] Z-01: Reproduce the claimed matrix on the exact SHA in a disposable repo (use the shipped test fixtures plus your own live probe if cheap): template-only commit -> audit clean; committed t-*.md -> flagged; committed .runtime/ file -> flagged; template+Task-File commit -> flags only the Task File path (the flag names the actual offending file).
- [ ] Z-02: Fail-closed paths unchanged: an octopus merge or un-auditable history still blocks (do not weaken the guard). Check the rename edge the worker documented.
- [ ] Z-03: The claimed checks pass verbatim on the exact SHA; VERSION/AGENTS/CHANGELOG 2.13.3 in sync with migration notes; diff inside Allowed files; the "rename onto _template.md still flags" found-not-fixed claim is truthful.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-audit regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checked: 8373c54f3a45b9364bc89cc0f8ebadfe51aa8b7d (detached HEAD, disposable checkout; worktree clean at end)
Environment: Python 3.13.7, git 2.53.0.windows.3, target local
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (269 passed / 0 failed, 3 skipped)
Criteria:
- Z-01 - pass - independent probe in a disposable repo (own fixture built from the shipped gate.py + _template.md, not the shipped test): template-only commit -> clean; committed T-999-evil.md -> flagged naming .agentflow/tasks/T-999-evil.md; committed .agentflow/tasks/.runtime/T-001.json -> flagged naming the path; template+task-file commit -> one flag naming only T-999-evil.md, not _template.md. Evidence: .agentflow/tasks/.runtime/T-063.evidence/probe.py and probe-output.txt. Shipped tests confirm the same matrix.
- Z-02 - pass - octopus merge -> "cannot audit octopus merge ... use two-parent merges" (probe + test_octopus_merge_fails_closed_as_unauditable); the returncode fail-closed branch is unchanged in the diff; a task-file edit introduced inside a two-parent merge still flags via the --remerge-diff path. Rename edge verified live both directions: T-999-evil.md -> _template.md flags (names the source path), _template.md -> T-999-evil.md flags (names the destination). Evidence: probe-output.txt.
- Z-03 - pass - both claimed checks pass verbatim on the exact SHA (numbers identical to the T-062 Result); VERSION=2.13.3, AGENTS.md block=2.13.3, CHANGELOG 2.13.3 dated 2026-10-17 with migration notes; `git diff main...8373c54 --stat` touches only gate.py, test_endcheck.py, ai-handoff-protocol.md, VERSION, AGENTS.md, CHANGELOG.md - all inside T-062 Allowed files; the "rename onto _template.md still flags" claim is truthful (probe scenario 5).
New defects (outside the task):
- none
Cannot verify, needs:
- nothing
Proposed memory updates:
- none (the worker's proposed dated decisions.md text for the _template.md carve-out stands; no additions)
