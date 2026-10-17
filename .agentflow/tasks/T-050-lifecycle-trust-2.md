# T-050: Lifecycle trust round 2 - fail-closed structural state, acceptance binding, locked --stop identity, machine pid identity

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: none
Branch: t-050-lifecycle-trust-2
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-050-lifecycle-trust-2
Independent check: tester
Resume: none

## Goal

Successor of rejected T-028: fix the four in-scope defects an independent
review (two separate sessions, codex log T-029.1.log and devin T-029 attempt 2)
confirmed on 2c58157, while preserving everything that review verified as
working (approval gate, atomic writes on the completed set, --live fix,
merge-history audit, review isolation). The prepared worktree already sits on
branch t-050-lifecycle-trust-2 at the preserved rejected commit 2c58157 - keep
that base, do not reset or rebase it.

## Read first

- .agentflow/tasks/T-028-lifecycle-trust.md (original contract + worker Result)
- .agentflow/tasks/T-029-verify-lifecycle-trust.md (independent Result - the failing criteria are your defect list)
- .agentflow/tasks/.runtime/T-029.1.log (codex attempt's findings; environment-blocked, do not copy its verdict)
- .agentflow/docs/improvement-plan.md section 1 (exit criteria)
- .agentflow/docs/ai-handoff-protocol.md (Task lifecycle, Recovery, Runtime state)
- .agentflow/tools/ledger.py, run_task.py, gate.py, tick.py, machine_capacity.py, route.py
- .agentflow/tests/test_approval.py, test_run_task.py, test_endcheck.py, test_tick.py, test_launcher_lifecycle.py, test_machine_capacity.py

## Allowed files

- .agentflow/tools/ledger.py
- .agentflow/tools/run_task.py
- .agentflow/tools/gate.py
- .agentflow/tools/tick.py
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/route.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/accept.py
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
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

- [ ] F-01: Structural fail-closed validation at EVERY reader of runtime state: a syntactically-valid-but-wrong-shape or empty-container state file (e.g. tool-limits.json = `[]`/`null`, heartbeat/orchestrator.json, T-NNN.json attempt files, T-NNN.verify.json, tick.json) produces a diagnosable error - never reads as "no limits", "no orchestrator live" or "no evidence". Malformed JSON still fails closed. Legacy shapes that readers genuinely accept stay tolerated explicitly.
- [ ] F-02: Acceptance binding enforced: `ledger.py set --status done` requires a verify record bound to task id + the LAST attempt number + headerHash (requirements hash) + full artifact SHA(s) for THAT attempt, with the attempt currently `exited` - a stale PASS from an earlier attempt or a different artifact cannot satisfy it, and legacy records are handled per an explicit documented rule. `ledger.claimed`/`verified` raise no KeyError on `{}` or missing fields.
- [ ] F-03: `--stop` and dead-worker's recovery keep the task locked whenever a live pid's identity is unconfirmed: closing an attempt as error/dead and releasing the launch lock must never happen while the recorded pid might still run. Verified stop or verified process identity releases; uncertain ownership stays a diagnosable block. A second claim can never coexist with a live original worker - add the regression the reviewer demonstrated (sleeper + second claim attempt refused).
- [ ] F-04: Per-attempt taskId validation inside check_runtime (an attempt file that names another task or none is diagnosed), and machine_capacity._alive uses the same pid+pidStart identity rule on every platform: POSIX honors the recorded start, a failed/unmeasurable Windows GetProcessTimes is not alive. Stale machine leases can no longer be fooled by a reused pid.
- [ ] F-05: Atomic writes extended to the remaining runtime/memory writers this task owns: route._log (T-NNN.route.json) and the ledger's tasks.md save use the same temp+replace pattern as the rest.
- [ ] F-06: The T-028-verified parts still hold (approval gate, --live argv, merge-history audit incl. octopus refusal, atomic writes, review isolation); the CHANGELOG 2.12.x entry that claims fail-closed structural validation is true after this task - align text if the claim still overshoots.
- [ ] F-07: Full suite passes verbatim in the task worktree; increment VERSION (next patch), sync AGENTS block and CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - locked-stop identity, claim binding, classification regressions.
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` - approval/acceptance binding.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-history and baseline audits.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - structural fail-closed readers.
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` - cross-platform pid identity.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
