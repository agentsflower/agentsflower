# T-028: Trustworthy task lifecycle - state enforcement, atomic runtime, PS 5.1 --live, merge-history audit

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-028-lifecycle-trust
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-028-lifecycle-trust
Independent check: tester
Resume: none

## Goal

Implement improvement-plan.md section 1 in the template: a task can only be
claimed, attempted and transitioned through verified state; malformed runtime
state blocks rather than silently passes; the known launcher defects are closed.
Reconcile first - part of this exists since 2.11.3/2.11.11; do not duplicate.

## Read first

- .agentflow/docs/improvement-plan.md (section 1, exit criteria)
- .agentflow/docs/ai-handoff-protocol.md (Task lifecycle, Launching workers, Runtime state)
- .agentflow/docs/project-rules.md
- .agentflow/state/known-issues.md
- .agentflow/tools/run_task.py, .agentflow/tools/run-task.ps1, .agentflow/tools/gate.py, .agentflow/tools/ledger.py, .agentflow/tools/tick.py, .agentflow/tools/accept.py
- .agentflow/tests/test_run_task.py, test_launcher_lifecycle.py, test_endcheck.py, test_parallel.py, test_tick.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/gate.py
- .agentflow/tools/ledger.py
- .agentflow/tools/tick.py
- .agentflow/tools/accept.py
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files; branch may not commit under it)
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

- [ ] L-01: Launch-state enforcement is verified end to end, including paths that do not go through preflight: `ledger.py set --status in progress` on an awaiting-approval task is refused (the approval gate cannot be bypassed by a direct CLI call), and terminal tasks (done/rejected/cancelled) cannot acquire a new attempt. Retry states that the protocol allows keep working. Prove both the refused and the allowed directions in tests.
- [ ] L-02: The empty `--live` argument defect on Windows PowerShell 5.1 is reproduced and fixed (locate it: gate.py preflight `--live` parsing, run_task.py argv construction, or run-task.ps1 delegation). The supported shells (powershell 5.1, pwsh 7, sh) each get a regression test or a documented static check where a live PS 5.1 host is unavailable.
- [ ] L-03: Merge-history false positives in gate.py are reproduced and fixed: a developer branch whose merge commits are legitimately empty of Task File changes passes `worktree_copy_problems`, while an actual worker commit under .agentflow/tasks/ is still rejected. Cover octopus-merge audit failure path and ordinary merges in disposable-repo tests.
- [ ] L-04: Runtime writes are atomic (attempt JSON, verify JSON, tick.json, tool-limits.json, conductor-side runtime records this task owns): write-temp-then-os.replace, and a malformed or truncated runtime file fails closed with a diagnosable error, never reads as "no active work" or "no evidence". Schema validation rejects structurally invalid attempt/verify records at read time.
- [ ] L-05: Every result and verification record binds task ID, attempt number, requirements hash (Task File header hash) and full artifact SHA(s) - extend the existing records where a field is missing; legacy verify/attempt records and open tasks keep working (define and test the migration path).
- [ ] L-06: Process-identity checks (pid + pidStart) are used consistently wherever a process is claimed dead or alive; a reused pid cannot impersonate a live worker.
- [ ] L-07: Full suite passes verbatim in the task worktree; increment VERSION (next patch), sync the AGENTS.md block version line and CHANGELOG entry with migration notes. Propose dated decisions.md text in the Result - do not write canonical memory.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - launcher lifecycle and state binding.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` - launch/state/preflight regressions.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-history and baseline audits.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - runtime state handling.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 2c5815718d19448ce6ac15cc66b2c38ff6f605e2 on t-028-lifecycle-trust
Files:
- .agentflow/tools/ledger.py - `set` can no longer bypass awaiting-approval (status moves and note-clearing refused; only approve, terminal rejected/cancelled, or a prefix-keeping --notes passes); `--status in progress` requires a recorded running attempt (`claimed()`); shared schema validators `check_runtime`/`check_verify`; `verified()` binds verify records to taskId (missing = legacy, file-bound)
- .agentflow/tools/run_task.py - `read_rt`/`live_tasks` schema-validate at read (LaunchError, never "no active work"); `--status` prints `state-error` per unreadable file; `limit_until` fails closed on a corrupt tool-limits.json; attempt records carry `taskId`
- .agentflow/tools/gate.py - `runtime()` validates and raises TaskError; `verify()` reads records through `check_verify` (malformed = gate error exit 2), writes records atomically (`write_atomic`) and binds `taskId`/`headerHash`/full SHA; `--out` hand-off files written atomically
- .agentflow/tools/tick.py - `StateError` + `read_map`: malformed heartbeat/tool-limits fails closed instead of reading as no limits/no orchestrator; `alive()` delegates to `run_task.alive` (same pid+pidStart rule on every platform); `decide()`/`learn_limits` turn an unreadable attempt into a `need`, not a crash; main reports StateError cleanly
- .agentflow/tools/run-task.ps1, .agentflow/tools/accept.py - unchanged (no edits needed: delegation and acceptance were already correct)
- .agentflow/tests/ - new coverage: approval-gate bypass refusals and claim binding (test_approval), terminal-state launch refusals incl. legacy-verify `done` (test_run_task), structural runtime schema, malformed verify/limits files, `--live` argv construction, octopus-merge audit refusal (test_endcheck), tick StateError/need/alive-identity (test_tick), verify-record binding fields (test_launcher_lifecycle); fixtures updated to the enforced lifecycle (test_workspace, test_route)
- .agentflow/docs/ai-handoff-protocol.md - transitions paragraph (direct-set gates), Runtime state (atomic writes, fail-closed malformed records), Acceptance (verify-record binding + legacy tolerance), process-identity rule
- .agentflow/VERSION - 2.12.1; AGENTS.md - block version line synced; CHANGELOG.md - entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (33 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (9 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (215 passed / 0 failed, 3 skipped: optional `mcp` SDK not installed in this interpreter - pre-existing environmental)
Criteria without a command:
- L-01 - verified end to end in tests: `set --status in progress`/`ready`/`review` and note-clearing on an awaiting-approval task refused (test_approval); `in progress` additionally needs a recorded running attempt (refused without, on exited attempt, and on corrupt runtime; allowed through the launcher's record); rejected and `done` (via a legacy verify record) cannot acquire an attempt, cancelled already covered (test_run_task). Retry states the protocol allows still work: every launch in the suite still passes.
- L-02 - defect located in argv construction (the pre-2.11.3 launcher passed `--live ""`, which PS 5.1 dropped, breaking gate.py argparse); the fix (emit `--live` only when non-empty) is present in run_task.py since 2.11.3 - reconciled, not duplicated. Regression: `test_live_argument_is_never_an_empty_string` asserts the gate argv; powershell 5.1 + pwsh 7 live-host coverage runs in test_launcher_lifecycle (both shells present here, tests ran green); for `sh` a documented check: on POSIX run_task.py is the launcher itself (no shell delegation, argv passed as a list), and the launch-path tests exercise it - verified on real Linux in T-021.
- L-03 - merge-history audit (rev-list --parents + --remerge-diff, ordinary commits audited individually, merges only for merge-introduced changes) exists since 2.11.3 - reconciled. New disposable-repo test covers the octopus-merge refusal (three parents -> "cannot audit"); ordinary merges already covered by existing tests (main-memory merge passes, merge-introduced and reverted worker edits rejected).
- L-04 - writes atomic: attempt JSON, verify JSON, tick.json, tool-limits.json, orchestrator.json, gate `--out` hand-offs (temp + os.replace; machine registry already retried-atomic and outside Allowed files). Malformed/truncated state fails closed with a diagnosable error at every read: launcher (LaunchError / `state-error` line), gate (TaskError exit 2), tick (StateError/need), ledger (refused claim/acceptance). Schema checked at read time via check_runtime/check_verify.
- L-05 - attempts record `taskId` + baseline.taskHash (requirements hash); verify records bind taskId, attempt n, headerHash, full artifact SHA. Legacy/open-task migration: validators require only the shape readers use (taskId optional), `verified()` counts a record without `taskId` as file-bound - proven by the forged legacy `done` in test_terminal_states_acquire_no_attempt.
- L-06 - pid+pidStart now used consistently: tick.alive delegates to run_task.alive (previously POSIX ignored pidStart and Windows fail-open'd an unmeasurable start); run_task.attempt_alive/cmd_stop/cmd_status/preflight `live`/`parallel` already used the same rule; covered by test_alive_requires_the_recorded_process_identity.
- L-07 - full suite green verbatim above; VERSION 2.12.1, AGENTS.md version line synced, CHANGELOG entry with migration notes; decisions.md text proposed below (not written - workers do not touch canonical memory).
Found, not fixed:
- machine_capacity._alive (outside Allowed files) has the same POSIX pidStart gap tick had: it ignores the recorded start on POSIX and treats an unmeasurable Windows GetProcessTimes as alive - a stale machine lease could still be fooled by a reused pid. Worth a scoped follow-up.
- route.py writes T-NNN.route.json non-atomically (outside Allowed files); the ledger's own tasks.md write (Canonical Memory, not a runtime record) is also non-atomic - out of this task's runtime scope.
- Reporting readers (route_report.py, dashboard build.py, mcp_server.py) deliberately stay tolerant of missing/malformed runtime files - they are descriptive views, not gates.
Proposed memory updates:
- decisions.md, 2026-10-17: "T-028 (2.12.1) - task lifecycle now binds claims to recorded running attempts: a direct `ledger.py set` cannot clear the awaiting-approval gate or mark `in progress` without the launcher's attempt. Rejected alternative: enforcing claims only in preflight would have left every non-launch path open. Runtime JSON is atomic and schema-checked; malformed records fail closed rather than reading as 'no active work', because a silently-empty state is how double launches and lost limits happen. Verify/attempt records gained taskId/headerHash binding with file-bound legacy tolerance so open tasks and old evidence keep working. tick.alive now shares run_task's pid+pidStart rule: one identity check, no platform diverging."
