# T-093: Repair fixed-clock hold in routing-scheduler test

Role: developer
Tool: devin
Model: swe-2-high, effort=high
Stage: 5
Depends on: none
Branch: t-093-fixed-clock-test-repair
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-093-fixed-clock-test-repair
Independent check: none - one-line test-constant repair on an artifact whose every other claim was independently verified by T-092; the check is the recorded suite on the exact SHA (no fresh independent session is available: the devin CLI is unauthenticated and codex/claude are resource-exhausted per the human)
Resume: none

## Goal

Successor of rejected T-091. The artifact at
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
(`.runtime` evidence basenames must start `T-093.`); path names inside prose
are mentions.

## Result
