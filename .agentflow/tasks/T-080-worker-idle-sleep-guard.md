# T-080: Prevent idle sleep during a bounded Windows worker attempt

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-070
Branch: t-080-worker-idle-sleep-guard
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-080-worker-idle-sleep-guard
Independent check: tester
Resume: none

## Goal

Consolidate the tested T-072 watchdog draft with the confirmed T-040
interruption fix, then review the combined repair once. T-072's 11 focused
tests and full suite (361 tests, 3 skipped) passed; the coordinator stopped a
redundant third suite run before a commit. Apply its preserved tracked patch
to this fresh main-based checkout after git apply --check, and copy its exact
new regression file from the companion runtime file. Do not reimplement it.
Windows entered connected standby
at 2026-10-18 04:49:19 Moscow (Kernel-Power 506, Idle Timeout) and exited at
07:45:24 (507, Lid). A background coordinator stopped/retried the worker at
07:48. Request system execution only while a bounded worker is actually running,
without changing global power settings, keeping the display on, or defeating
explicit user sleep/lid actions. Human authorized this urgent repair in chat.
Human explicitly extended the conservative swe-2-max exception to this task
and its independent tester after the persisted low-confidence T-080 assessment
(request req_01a14d6b07c67795ba87831f8ed31bc4). Preserve this as a human
exception, not a claim of high Jev confidence.

## Read first

- .agentflow/docs/project-rules.md
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-072-urgent-worker-watchdog.md
- E:\Projects\AgentFlow\code\.agentflow\tasks\.runtime\T-072-preserved-draft.patch
- E:\Projects\AgentFlow\code\.agentflow\tasks\.runtime\T-072-test_worker_watchdog.py (copy to .agentflow/tests/test_worker_watchdog.py)
- .agentflow/tools/run_task.py cmd_worker
- .agentflow/tests/test_worker_watchdog.py
- .agentflow/tests/test_run_task.py test_live_argument_is_never_an_empty_string

## Allowed files

- .agentflow/tools/power_guard.py (small Windows adapter; no new dependency)
- .agentflow/tools/run_task.py (inherited T-072 watchdog, review corrections and worker lifetime integration)
- .agentflow/tools/conductor.ps1 (inherited T-072 watchdog call and related corrections)
- .agentflow/tests/test_worker_watchdog.py (inherited T-072 regressions and review corrections)
- .agentflow/tests/test_power_guard.py
- .agentflow/tests/test_run_task.py (isolate the direct-launch fixture root only)
- .agentflow/docs/ai-handoff-protocol.md (Windows idle sleep behavior only)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, other Task Files, runtime history, preserved T-040 worktree
- Windows global power plans, registry, scheduled tasks and other projects
- Display timeout or explicit user sleep/lid policy

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] P-01: A Windows worker holds an OS execution request against automatic idle system sleep during its bounded managed lifetime. Release on normal exit, timeout and exceptions; OS cleanup handles process death. Do not request display-on or away mode.
- [ ] P-02: POSIX is a no-op. API failure is reported durably in the attempt log or record (supervisor stdout is discarded), without pretending protection succeeded; no global settings or persistent power changes. Retain T-072 deadlines and watchdog behavior after actual user-initiated sleep.
- [ ] P-03: Tests mock Windows API to prove acquire/release and exception/failure paths; live Windows probe confirms request succeeds and releases. Full suite passes; patch release and migration describe limits accurately.
- [ ] P-04: Repair the observed test-only environment leak: test_live_argument_is_never_an_empty_string directly calls cmd_launch while run_task.ROOT still names the actual managed checkout, so inherited AGENTFLOW_ATTEMPT_ROOT triggers nested_check. Make that fixture use its disposable root (or isolate its marker locally), without weakening production nested_check or clearing markers for the entire suite. Prove the full suite passes verbatim inside the managed worker environment.
- [ ] P-05: Preserve and independently verify T-072 W-01 through W-05 in this combined candidate. Correct two known documentation defects: T-040's observed hours were mostly confirmed standby (invalid timeout was a separate reproduced gap, not proven its cause); an already running PowerShell conductor must be restarted after update to load the new loop. Stop audit metadata must distinguish CLI invocation from watchdog without claiming an actual human issued every CLI stop.
- [ ] P-06: Prove a stale watchdog cannot overwrite a later attempt during a concurrent launch, not only when the new attempt already existed before stop_attempt's first read. Serialize external stop with launch using existing launch lock semantics or equivalent bounded protection; keep identity/cleanup guards. Bound Windows taskkill itself as well as post-kill process waits. Add deterministic race regression coverage.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_power_guard.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`
- Live Windows acquire/release probe without changing power configuration; record observed API result and OS version.

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change, as required by root AGENTS.md, and record its output for P-03/P-04.
The Checks above are the scoped acceptance/integration commands; do not put
the whole suite in every repeated acceptance stage without a changed risk.

## Execution bounds

20-minute attempt cap (the measured full suite takes about six minutes).
First apply the patch and companion test, then work only on P-01..P-06 deltas.
Avoid broad rereads of inherited implementation. Run one required full suite
after the final coherent change, with inherited worker markers still present
(P-04 fixes the leak). Do not repeat a green whole suite just to remove output
redirection or obtain a different display. Finish the single commit and Result
immediately after the required green checks.
Implement a small process/thread-scoped Windows API
adapter, not a power-management subsystem. Checkpoint exact blockers promptly.

## Result

Outcome: completed
Change: c7cc37b7e09ddef1e732cd4797d0c39e343e928e on t-080-worker-idle-sleep-guard
Files:
- .agentflow/tools/power_guard.py - new thread-scoped idle-sleep adapter: SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED) on acquire, ES_CONTINUOUS on release; no display/away flags; POSIX explicit no-op; (ok, detail) never pretends
- .agentflow/tools/run_task.py - preserved T-072 patch applied (worker_bound/attempt_deadline/parse_ts, workerTimeout+deadline persisted, --watchdog + --expect-attempt, bounded taskkill/post-kill waits); cmd_worker acquires the guard after lease activation, logs its outcome into the attempt log, releases in finally, records a["powerGuard"]; new _launch_lock serializes launches and external stops (re-read + expected-attempt check inside the lock); stop_attempt shared by --stop (initiator "cli") and watchdog (initiator "watchdog", hint timeout)
- .agentflow/tools/conductor.ps1 - watchdog invoked at the top of every round before the Orchestrator liveness branch (skipped in -DryRun)
- .agentflow/tests/test_power_guard.py - new: 8 tests, mocked Windows API acquire/release/failure/exception paths plus a real managed-worker acquire/release
- .agentflow/tests/test_worker_watchdog.py - preserved T-072 regression file plus P-06 deterministic race coverage and initiator cli/watchdog distinction
- .agentflow/tests/test_run_task.py - P-04 fix: the empty-live-argument test pins run_task.ROOT to its disposable root so inherited AGENTFLOW_ATTEMPT_ROOT no longer triggers nested_check; production nested_check untouched
- .agentflow/docs/ai-handoff-protocol.md - Windows idle-sleep scope/limits; stoppedBy initiator "cli" (not "human"); launch.lock also serializes external stops
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.15.1: combined release notes with corrected T-040 causation (hours mostly confirmed standby; invalid timeout a separate reproduced gap), conductor-restart migration note, and guard limits
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_power_guard.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed)
- Live Windows acquire/release probe -> pass: acquire (True, "ES_SYSTEM_REQUIRED held (previous state 0x80000000)"), release (True, "released (previous state 0x80000001)"); Microsoft Windows 10 Pro 10.0.19045; thread-scoped request only, no power configuration touched
- `python -m unittest discover -s .agentflow/tests` -> pass (372 passed / 0 failed, 3 skipped) run verbatim once after the final coherent change inside this managed worker (AGENTFLOW_ATTEMPT=T-080#1)
Criteria without a command:
- P-01 - guard held for the bounded managed lifetime in cmd_worker; release on normal exit/timeout/exception via finally; OS drops the thread request on process death; only ES_SYSTEM_REQUIRED, never ES_DISPLAY_REQUIRED or ES_AWAYMODE_REQUIRED
- P-02 - POSIX returns (False, "not Windows...") as an explicit no-op; a failed Windows request lands in the attempt log line and a["powerGuard"] record because worker stdout is discarded; no power plan/registry/scheduled-task changes; T-072 deadlines/watchdog retain authority across user-initiated sleep
- P-03 - mock tests cover held/released/API-failure/exception and POSIX; live probe above confirms real acquire/release; 2.15.1 release notes state the limits accurately
- P-04 - full suite above ran verbatim inside the managed worker with markers inherited; the leaking fixture now uses its disposable root; suite-wide env not cleared
- P-05 - all 14 watchdog tests (incl. preserved W-01..W-05) pass; CHANGELOG corrects the T-040 attribution, documents that a running conductor must be restarted to load the new loop; stoppedBy.initiator records "cli" for --stop without claiming a human
- P-06 - stop_attempt takes launch.lock (bounded 15s wait via _launch_lock, stale-lock sweep >300s) then re-reads the record and checks the expected attempt inside the lock; taskkill bounded by AGENTFLOW_KILL_TIMEOUT (default 30s) with _job_terminate fallback; post-kill waits bounded by POST_KILL_WAIT; deterministic concurrent-launch race regressions added
Found, not fixed:
- run-task.ps1 deliberately exposes only the legacy flags; --watchdog/--expect-attempt are reached via run_task.py (or conductor.ps1). Adding pass-throughs would exceed Allowed files.
Proposed memory updates:
- none (worker: no canonical memory writes)

Coordinator formatting normalization (2026-10-18): the entries below preserve the developer's stated outcomes and evidence above; no new measurement or acceptance is claimed. Independent review remains required.
- P-01: pass - Developer-stated outcome: guard held for the bounded managed lifetime in cmd_worker; release on normal exit/timeout/exception via finally; OS drops the thread request on process death; only ES_SYSTEM_REQUIRED, never ES_DISPLAY_REQUIRED or ES_AWAYMODE_REQUIRED
- P-02: pass - Developer-stated outcome: POSIX returns (False, "not Windows...") as an explicit no-op; a failed Windows request lands in the attempt log line and a["powerGuard"] record because worker stdout is discarded; no power plan/registry/scheduled-task changes; T-072 deadlines/watchdog retain authority across user-initiated sleep
- P-03: pass - Developer-stated outcome: mock tests cover held/released/API-failure/exception and POSIX; live probe above confirms real acquire/release; 2.15.1 release notes state the limits accurately
- P-04: pass - Developer-stated outcome: full suite above ran verbatim inside the managed worker with markers inherited; the leaking fixture now uses its disposable root; suite-wide env not cleared
- P-05: pass - Developer-stated outcome: all 14 watchdog tests (incl. preserved W-01..W-05) pass; CHANGELOG corrects the T-040 attribution, documents that a running conductor must be restarted to load the new loop; stoppedBy.initiator records "cli" for --stop without claiming a human
- P-06: pass - Developer-stated outcome: stop_attempt takes launch.lock (bounded 15s wait via _launch_lock, stale-lock sweep >300s) then re-reads the record and checks the expected attempt inside the lock; taskkill bounded by AGENTFLOW_KILL_TIMEOUT (default 30s) with _job_terminate fallback; post-kill waits bounded by POST_KILL_WAIT; deterministic concurrent-launch race regressions added
