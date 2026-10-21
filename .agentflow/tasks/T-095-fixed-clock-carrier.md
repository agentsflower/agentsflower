# T-095: Fixed-clock repair carrier - T-094 artifact under corrected scope declaration

Role: developer
Tool: devin
Model: swe-2-high, effort=high
Stage: 5
Depends on: none
Branch: t-095-fixed-clock-carrier
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-095-fixed-clock-carrier
Independent check: none - the artifact at 0477331 is byte-identical to what T-092 verified except the two-line constant repair; the recorded full suite on that exact SHA is the proof (T-094 contract, unchanged rationale)
Resume: none

## Goal

Mechanical carrier task: T-094 was rejected for an authoring defect in its
contract (comma-separated `Allowed files` lines never parse - only the first
token of each bullet counts), so the verified artifact could not pass scope
verification. The artifact itself is complete at commit
04773311aafce6c3f98831a5f862c8c745566da6 on branch
t-094-fixed-clock-test-repair. Move this task's new branch onto that commit
(git reset --hard from the launcher-created start, clean tree), run the three
scoped Checks, write the Result section. No code edits.

## Read first

- .agentflow/tasks/T-094-fixed-clock-test-repair.md (the artifact and its Result section)

## Allowed files

- .agentflow/tools/tick.py
- .agentflow/tools/route_report.py
- .agentflow/tools/cli.py
- .agentflow/tools/route.py
- .agentflow/tests/ (any file)
- .agentflow/tasks/_template.md (routing fields only)
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (policy text only)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- Preserved draft worktrees and branches t-093-*, t-094-* (read only)
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] C-01: The branch HEAD is exactly the commit 04773311aafce6c3f98831a5f862c8c745566da6 (its parent is 0bf4ac09fa08ef2c7cd77f6591993460511ebe07); `git diff main...HEAD` file set stays inside this contract's Allowed files. Add a consolidation commit ONLY if something verified is actually missing - none is expected.
- [ ] C-02: The carried artifact is complete: the whole inherited T-078+T-091 stack plus the T-094 repair - both recorded backup holds in test_a_held_backup_group_stays_scoped_and_refused derive from datetime.now(timezone.utc) + timedelta(hours=1) instead of the fixed AT; the delta of HEAD vs 0bf4ac0 is only that repair - nothing re-implemented, nothing dropped.
- [ ] C-03: The three scoped Checks pass verbatim on the branch HEAD; the already-recorded full-suite evidence on this exact SHA (T-094: 424 ran / 0 failed / 3 skipped in ~339s, verbatim tail in .agentflow/tasks/.runtime/T-094.full-suite.txt) is reported honestly in prose, not re-run without a changed input.
- [ ] C-04: VERSION = 2.15.4 on the branch, the AGENTS.md version block agrees, and the CHANGELOG 2.15.4 entry is unchanged by this task; T-040 is not claimed complete. main having since moved to 2.15.5 is a merge-time matter, not a contract defect.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Execution bounds

20-minute cap. Carrier: reset the branch onto
04773311aafce6c3f98831a5f862c8c745566da6, verify completeness and metadata,
run the scoped Checks, write the Result section. No new full suite without a
changed input; no product edits unless a verified gap is actually found.
Result must include explicit `- C-01: pass - <evidence>` outcome lines for
C-01..C-04; put `evidence:` markers at line end followed only by intended
claim paths (`.runtime` evidence basenames must start `T-095.`); path names
inside prose are mentions.
