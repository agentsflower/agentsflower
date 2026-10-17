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
Outcome: completed
Change: 00852c1698d14ece7dcc56d005ec2eb7f25e803f on t-050-lifecycle-trust-2
Files:
- .agentflow/tools/ledger.py - shared schema validators: check_runtime now requires an attempts list and the file's taskId and validates every attempt (n:int, known status, per-attempt taskId); check_verify requires ok:bool plus typed binding fields; new check_limits for tool-limits.json; verified() returns a diagnostic reason and binds task id + last exited attempt + headerHash + full artifact SHA (legacy records bind only what they carry); claimed()/verified() share _last_attempt with fail-closed reads (no KeyError on {}); tasks.md writes atomically via _write_atomic; shared sha256()/header()/task_header_hash()
- .agentflow/tools/gate.py - header()/sha256() delegate to ledger (single implementation); unused hashlib import removed
- .agentflow/tools/run_task.py - attempt_alive requires a recorded+matching pidStart; new attempt_uncertain (live pid, unconfirmed identity); attempt_held/live_tasks include it; --stop refuses with a diagnosable block instead of closing and releasing; --status reports "blocked"; cmd_launch refuses a second claim beside an unconfirmed pid; limit_until validates tool-limits.json through check_limits
- .agentflow/tools/tick.py - new read_limits() fail-closed reader (record_limit/limit_end/learn_limits/run/status); heartbeat requires holder+at and a malformed record blocks the claim (--force takes over); decide() reports an unconfirmed pid as a need through run_task.attempt_*
- .agentflow/tools/machine_capacity.py - new _pid_start (GetProcessTimes / /proc jiffies / ps lstart); _alive applies the same pid+recorded-start rule on every platform: POSIX honors the recorded start, and unmeasurable identity or GetProcessTimes failure is not alive
- .agentflow/tools/route.py - _log writes T-NNN.route.json through temp file + os.replace, temp removed on failure
- .agentflow/docs/ai-handoff-protocol.md - acceptance binding + the explicit legacy rule, atomic/fail-closed runtime state incl. T-NNN.route.json and tasks.md, the locked unconfirmed pid under --stop and claims, the machine-lease identity rule
- .agentflow/tests/test_tick.py - malformed/empty limits + heartbeat cases, malformed-heartbeat claim block + force takeover, unconfirmed-pid need regression
- .agentflow/tests/test_run_task.py - per-attempt and file-level taskId + {} runtime cases, wrong-shape limits cases, locked --stop + refused second claim + confirmed-identity stop regressions, acceptance-binding suite (stale attempt, other artifact, changed header, other task, truthy ok, live attempt)
- .agentflow/tests/test_machine_capacity.py - _alive pid+start identity on every platform incl. unmeasurable-identity and GetProcessTimes-failure cases; the reuse guard un-gated
- .agentflow/tests/test_approval.py - {} / [] / null runtime refusal cases; atomic tasks.md save regression
- .agentflow/tests/test_route.py - atomic route._log regression
- .agentflow/VERSION - 2.12.2
- AGENTS.md - AgentFlow block version line 2.12.2
- CHANGELOG.md - 2.12.2 entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (36 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (5 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (9 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (223 passed / 0 failed, 3 skipped: platform-gated)
Criteria without a command:
- F-01 - the new shared validators run at every Python reader: check_runtime for T-NNN.json (run_task read_rt/live_tasks/--status, gate.runtime, ledger._last_attempt), check_verify for T-NNN.verify.json (gate.verify, ledger.verified), check_limits for tool-limits.json (run_task.limit_until, tick.read_limits), live_orchestrator requires holder+at; covered by the fail-closed cases in test_tick/test_run_task/test_approval. Legacy shapes readers genuinely accept (attempt without taskId, limit _seen metadata, missing verify binding fields) stay explicitly tolerated.
- F-02 - verified() binds taskId + last attempt n + headerHash + artifact SHA with the attempt exited; test_acceptance_is_bound_to_the_current_attempt_and_task_file covers stale attempt/artifact/header, other-task records, truthy ok, live attempt; {} runtime cases cover the no-KeyError requirement.
- F-03 - test_stop_with_unconfirmed_pid_identity_keeps_the_lock: sleeper + --stop refusal + refused second --manual claim + blocked status + refusal with a mismatched recorded start; test_stop_with_a_confirmed_identity_kills_the_worker: verified identity releases the lock.
- F-04 - per-attempt taskId mismatch and missing file-level taskId in test_structurally_invalid_runtime_state_fails_closed; test_alive_uses_pid_start_identity_on_every_platform covers POSIX/ps measurement, wrong start, unmeasurable identity and the Windows GetProcessTimes-failure case.
- F-05 - test_route_log_is_written_atomically and test_tasks_md_writes_are_atomic.
- F-06 - approval-gate, --live argv, octopus/merge-history and review-isolation regressions stay green in the full suite; the 2.12.2 CHANGELOG entry states the fail-closed behavior as it now actually is.
- F-07 - full suite passes verbatim; VERSION 2.12.2, AGENTS block 2.12.2, CHANGELOG migration notes; decision text proposed below.
Found, not fixed:
- tick.py run/status exit 1 on a malformed heartbeat or limits file - the same exit code as "no live orchestrator", so the conductor may retry an orchestrator launch until the file is repaired (stderr names the file; the behavior is fail closed). conductor.ps1 is outside Allowed files.
- tick.py release cannot remove a non-object heartbeat file (read_map refuses); deleting the file by hand remains the recovery.
- gate.write_atomic and run_task.write_rt leave a stranded .tmp when os.replace fails (pre-existing pattern; the two new writers clean theirs).
- Legacy verify/attempt records bind only what they carry - file + artifact when attempt/headerHash are absent; this is the documented compatibility rule, not a defect.
Proposed memory updates:
- decisions.md, 2026-10-17: "2.12.2 lifecycle trust, round 2 - fixes T-029's four confirmed defects on the T-028 commit. Every runtime-state reader now validates the shape it depends on: wrong-shaped or empty tool-limits/heartbeat/attempt/verify records are diagnosable errors at read time, never 'no limits', 'no live orchestrator' or 'no evidence'; a malformed heartbeat blocks an orchestration claim (--force still takes over). Acceptance is bound: ledger.py set --status done requires a verify record naming the task, the last attempt number, the current requirements hash and the full artifact SHA, with that attempt exited - a stale PASS cannot accept; legacy records bind only what they carry (the file they live in plus the artifact). A live pid whose start identity is unconfirmed keeps the task locked: --stop refuses instead of killing a possibly reused pid or freeing the lock, --status reports blocked, tick surfaces a need; verified stop or verified identity releases. machine_capacity._alive uses the same pid + recorded start identity rule on every platform, so a reused pid no longer fools a stale lease. route._log and tasks.md writes are atomic (temp + os.replace)."
