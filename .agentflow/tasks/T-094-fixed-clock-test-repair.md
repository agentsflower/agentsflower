# T-094: Repair fixed-clock hold in routing-scheduler test

Role: developer
Tool: devin
Model: swe-2-high, effort=high
Stage: 5
Depends on: none
Branch: t-094-fixed-clock-test-repair
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-094-fixed-clock-test-repair
Independent check: none - one-line test-constant repair on an artifact whose every other claim was independently verified by T-092; the check is the recorded suite on the exact SHA (the T-093 attempt produced no draft: clean worktree, no commit, no Result section)
Resume: none

## Goal

Successor of rejected T-093 (its stopped attempts left a Result-less branch).
Same scope: the artifact at
0bf4ac09fa08ef2c7cd77f6591993460511ebe07 passed every T-092 criterion except
one diagnosed defect: `.agentflow/tests/test_routing_scheduler.py`
`AT = datetime(2026, 10, 18, 12, 0, ...)` is a fixed wall-clock constant, and
`test_a_held_backup_group_stays_scoped_and_refused` records its "live" quota
holds at `AT + timedelta(hours=1)` = 2026-10-18T13:00Z. Once wall clock
passed 13:00Z the recorded hold is already expired, `limit_until` cleans it
and the test fails deterministically forever (switched=True), breaking every
future suite/CI run. Branch from the preserved commit, make those recorded
holds relative to `datetime.now(timezone.utc)`, and change nothing else.
Do not re-implement what T-078/T-091 proved.

T-093's last attempt completed the repair itself before its stop: commit
0b82f61acf1e8c6c2e1e1d763995d91bcdbdc3fa on branch
t-093-fixed-clock-test-repair (parent 0bf4ac0, "test: record backup-hold
expiries relative to now, not fixed AT"). Cherry-pick it onto this task's
branch (reworded as [T-094]) or reproduce the same two-line change - the
delta vs 0bf4ac0 is what R-01 measures. The suite evidence (R-03) must still
be produced fresh on this branch.

## Read first

- E:\Projects\AgentFlow\code\.agentflow\tasks\T-092-verify-tester-preference.md (the fail verdict: V-03 evidence + live repro)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-091-tester-independence-preference.md (the base contract + Result)
- .agentflow/tests/test_routing_scheduler.py (AT uses at lines 22, 181, 242, 247)

## Allowed files

The branch inherits T-091's unmerged base - per the authoring rule the
Allowed set is the whole `git diff main...HEAD` file set, not only the delta:

- .agentflow/tools/tick.py, route_report.py, cli.py, route.py
- .agentflow/tests/ (any file)
- .agentflow/tasks/_template.md (routing fields only)
- .agentflow/docs/ai-handoff-protocol.md, typesafe.md, model-options.json (policy text only)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

The actual change is expected only in .agentflow/tests/test_routing_scheduler.py.

## Do not touch

- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- Preserved draft worktrees (read only)
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Branch moved onto 0bf4ac09fa08ef2c7cd77f6591993460511ebe07 once; the delta vs that commit is only the hold-time repair and `git diff main...HEAD` stays inside this contract's Allowed files.
- [ ] R-02: `test_a_held_backup_group_stays_scoped_and_refused` passes at the current wall-clock time (holds recorded relative to now, not the fixed AT); the same repair applied to the second hold at line ~247.
- [ ] R-03: The three scoped Checks pass verbatim on branch HEAD, and the one required full-suite run on branch HEAD is recorded verbatim (the suite must stay green for any reader after 2026-10-18T13:00Z).
- [ ] R-04: VERSION/AGENTS/CHANGELOG stay consistent at 2.15.4 (a single clarifying line under the existing 2.15.4 entry is allowed, no second release); T-040 not claimed complete.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change and record it for R-03.

## Execution bounds

20-minute cap (the full suite takes ~7.5 min - start it early). Result must
include explicit `- R-01: pass - <evidence>` outcome lines for R-01..R-04;
put `evidence:` markers at line end followed only by intended claim paths
(`.runtime` evidence basenames must start `T-094.`); path names inside prose
are mentions.

## Result
Outcome: completed
Change: 04773311aafce6c3f98831a5f862c8c745566da6 on t-094-fixed-clock-test-repair
Files:
- .agentflow/tests/test_routing_scheduler.py - the two recorded backup holds in test_a_held_backup_group_stays_scoped_and_refused now use datetime.now(timezone.utc) + timedelta(hours=1) instead of the fixed AT + timedelta(hours=1); the staged delta of 0b82f61 applied verbatim and committed as [T-094]
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_tick.txt
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py` -> pass (11 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_routing_scheduler.txt
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (25 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_routing_core.txt
- `python -m unittest discover -s .agentflow/tests` -> pass on branch HEAD 0477331, verbatim tail "Ran 424 tests in 338.978s / OK (skipped=3)", exit 0. evidence: .agentflow/tasks/.runtime/T-094.full-suite.txt
Criteria outcomes:
- R-01: pass - the branch was moved onto 0bf4ac09fa08ef2c7cd77f6591993460511ebe07 once (git reset --hard from the launcher-created main-lineage start) and holds exactly one commit, 0477331, whose parent is 0bf4ac0; the delta vs 0bf4ac0 is only the hold-time repair (identical to the delta of 0b82f61); `git diff main...HEAD` lists the same 16 files as at 0bf4ac0, all inside this contract's Allowed files. evidence: .agentflow/tests/test_routing_scheduler.py
- R-02: pass - test_a_held_backup_group_stays_scoped_and_refused was reproduced failing at 0bf4ac0 (switched=True: the hold recorded at fixed AT+1h was already expired) and passes at the current wall-clock time after the repair; the same repair was applied to both record_limit calls in that test (the devin hold at line ~242 and the agy hold at line ~247). evidence: .agentflow/tests/test_routing_scheduler.py .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_routing_scheduler.txt
- R-03: pass - the three scoped Checks pass verbatim on branch HEAD (52/11/25, all OK, recorded above); the one required full-suite run on branch HEAD is recorded verbatim: "Ran 424 tests in 338.978s / OK (skipped=3)", exit 0, well after 2026-10-18T13:00Z. evidence: .agentflow/tasks/.runtime/T-094.full-suite.txt .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_tick.txt .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_routing_scheduler.txt .agentflow/tasks/.runtime/T-094.evidence/T-094.check-test_routing_core.txt
- R-04: pass - .agentflow/VERSION reads 2.15.4, the AGENTS.md version block reads 2.15.4 and the CHANGELOG 2.15.4 entry (2026-10-18) is unchanged by this task (the delta vs 0bf4ac0 touches only the test file); T-040 is not claimed complete. evidence: .agentflow/VERSION CHANGELOG.md AGENTS.md
Question or reason: -
Found, not fixed:
- none
Proposed memory updates:
- known-issues.md, 2026-10-21: T-094 closed the fixed-AT hold defect diagnosed by T-092 V-03; on commit 0477331 (t-094-fixed-clock-test-repair) the holds in test_a_held_backup_group_stays_scoped_and_refused derive from now()+1h and the suite stays green after 2026-10-18T13:00Z.
- session-log.md, 2026-10-21: T-094 commit 0477331 on t-094-fixed-clock-test-repair; scoped checks 52+11+25 green; full suite 424 green in 339s; Result written; awaits orchestrator review (Independent check: none).
