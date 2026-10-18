# T-081: Independently verify combined urgent worker recovery

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-080
Verifies: T-080 @ c7cc37b7e09ddef1e732cd4797d0c39e343e928e

## Goal

Independently verify the exact combined T-080 artifact, including inherited
T-072 watchdog behavior. Human explicitly allowed swe-2-max for this urgent
repair's independent tester despite low Jev effort confidence. This is a fresh
session, not the developer conversation. Same CLI is necessary: Codex worker
sandbox writes were environment-blocked on this machine; observed agy holds
remain honored. Never downgrade or invent available quota.

## Read first

- .agentflow/roles/tester.md
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-080-worker-idle-sleep-guard.md (current contract and Result, not the older checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-072-urgent-worker-watchdog.md (W-01 through W-05)
- .agentflow/tools/power_guard.py
- .agentflow/tools/run_task.py (deadline, stop lock, kill and worker lifetime paths)
- .agentflow/tools/conductor.ps1 (watchdog placement)
- .agentflow/tests/test_power_guard.py
- .agentflow/tests/test_worker_watchdog.py
- CHANGELOG.md (2.15.1 migration)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact, product code, tests and configuration
- Canonical memory, other Task Files, existing attempt history
- Other repositories, global Windows power settings, manual sleep/lid behavior

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: P-01..P-03: system-only execution request is acquired/released on worker lifetime paths and OS process death cleans it; no display/away/global changes. Failure is durably reported without claiming held protection. POSIX is a no-op. Run the live Windows acquire/release command and report actual results; do not suspend the user's computer.
- [ ] V-02: P-05 / W-01..W-03: invalid/zero timeouts stay positive; deadline and resolved bound persist; external watchdog enforces overdue nonmanual workers, preserves drafts and leases/identity guards, leaves manual/unexpired attempts alone, and runs even while the coordinator is alive. Reproduce with disposable processes or the tests, not just code reading.
- [ ] V-03: P-06: stale stop cannot overwrite a newly launched attempt, including a concurrent launch between the initial decision and stop's re-read; lock/cleanup failures remain diagnosable, process identity is never guessed. Inspect bounded taskkill/post-kill handling and retained writer/lease safeguards; do not mark a failed cleanup as safe to relaunch.
- [ ] V-04: P-04: test_run_task passes verbatim with your inherited managed-worker markers still present; its fixture uses a disposable root without weakening production nested_check. Review the developer's one full-suite result on this artifact; do not repeat that whole suite just for a second display format.
- [ ] V-05: P-05 / W-04..W-05: stop records distinguish cli/watchdog without claiming a human actor; conductor restart migration is accurate; standby and invalid-timeout causation are not conflated. Version/block/changelog and Allowed files agree, artifact remains clean and at the checked SHA.
- [ ] V-06: Map all T-080 P-01..P-06 and inherited W-01..W-05 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified, never infer success from a green summary alone.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_power_guard.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -c "import sys; sys.path.insert(0, '.agentflow/tools'); import power_guard as p; a=p.acquire(); print(a); assert a[0]; r=p.release(); print(r); assert r[0]"`

## Execution bounds

20-minute cap. Run scoped checks, probe the relevant failure/race paths, give
an evidence-based verdict. No code fixes, no repeated broad architecture reads
or gratuitous whole-suite runs. Save evidence in AGENTFLOW_EVIDENCE.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06. The older role example
without colon/verdict is obsolete; do not omit explicit per-criterion outcomes.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_power_guard.py` -> pass (8 passed / 0 failed) - evidence: .agentflow/tasks/.runtime/T-081.evidence/check1_power_guard.txt
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed) - evidence: .agentflow/tasks/.runtime/T-081.evidence/check2_worker_watchdog.txt
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (49 passed / 0 failed) - evidence: .agentflow/tasks/.runtime/T-081.evidence/check3_run_task.txt
- `python -c "import sys; sys.path.insert(0, '.agentflow/tools'); import power_guard as p; a=p.acquire(); print(a); assert a[0]; r=p.release(); print(r); assert r[0]"` -> pass: (True, 'ES_SYSTEM_REQUIRED held (previous state 0x80000000)') then (True, 'released (previous state 0x80000001)'), Windows 10 Pro 10.0.19045 - evidence: .agentflow/tasks/.runtime/T-081.evidence/check4_live_probe.txt
Criteria:
- V-01: pass - P-01..P-03 verified on the checked SHA c7cc37b in a disposable checkout: power_guard.py requests only ES_CONTINUOUS|ES_SYSTEM_REQUIRED on acquire and ES_CONTINUOUS on release (display/away constants defined but never requested; mock tests assert the flag set); cmd_worker acquires after lease activation (run_task.py:1531), logs the outcome into the attempt log via _attempt_log (stdout is DEVNULL), releases in finally covering normal exit, wall-clock timeout and exceptions, and records a["powerGuard"]; process death drops the thread-scoped request at OS level. API failure returns (False, "...failed...") and is recorded without pretending held; POSIX returns (False, "not Windows...") as a no-op. Live probe actually acquired and released on this Windows 10 Pro 19045 host (check4); no power plan/registry/scheduled task touched.
- V-02: pass - P-05 / W-01..W-03 reproduced by my own run of the 14 watchdog tests with real disposable sleeper processes and real launches (check2): invalid/zero/negative/non-numeric AGENTFLOW_WORKER_TIMEOUT keeps the positive 1200s default and the resolved bound plus absolute deadline persist on the attempt record; the watchdog stopped an overdue real worker tree, classified it timeout with initiator watchdog, captured recovery and released the machine lease; manual and unexpired attempts were left alone and no attempt was created; a possibly reused pid was refused, not killed; a gone worker closed as dead; a legacy record got the bounded startedAt+timeout fallback; conductor.ps1 invokes --watchdog at the top of every round before the Orchestrator-liveness branch (skipped in -DryRun). Live `run_task.py --watchdog` on the checkout's empty runtime exits 0 quiet.
- V-03: pass - P-06: external stops share launch.lock with launches (_launch_lock, O_EXCL, bounded STOP_LOCK_WAIT=15s wait, stale sweep >300s); stop_attempt re-reads the record inside the lock and refuses on expected-attempt mismatch, so a stale watchdog decision cannot kill or overwrite a newer attempt - proven by the deterministic threaded regression test_stop_serialized_with_launch_never_overwrites_a_newer_attempt (lock held, attempt 2 lands mid-wait, refusal verified, newer record intact, nothing killed). taskkill carries AGENTFLOW_KILL_TIMEOUT (default 30s) with _job_terminate fallback; post-kill waits bounded by POST_KILL_WAIT=30; leftover-process checks are grace-bounded; a failed cleanup raises before the status changes so the attempt stays locked, the lease stays held and the persisted stoppedBy keeps the watchdog initiator on retry. Process identity is never guessed: unconfirmed pid identity is a diagnosable block, never a kill target.
- V-04: pass - P-04: test_run_task.py ran verbatim (49 tests) inside this managed tester with inherited AGENTFLOW_ATTEMPT=T-081#1 / AGENTFLOW_ATTEMPT_ROOT markers and passed; the fix is a single added patch.object(run_task, "ROOT", self.root) pinning the fixture's launcher root to its disposable repo - nested_check/_same_root bodies are untouched (diff shows them only as context) and the nested-launch refusal tests still pass. The developer's one full-suite result on this artifact was reviewed in .agentflow/tasks/.runtime/T-080.1.log: 372 passed / 0 failed / 3 skipped, run verbatim once inside managed worker T-080#1 after the final change; not repeated per task bounds.
- V-05: pass - P-05 / W-04..W-05: stop records distinguish initiator "cli" (--stop) from "watchdog" with fixed safe reason strings, no raw argv/env, and no claim that a human issued every CLI stop (code + test_cli_stop_records_a_different_initiator and the watchdog initiator tests). CHANGELOG 2.15.1 separates confirmed connected-standby hours from the separately reproduced invalid-timeout gap (no conflation), states accurate guard limits, and the migration correctly requires restarting an already loaded conductor plus install.py --update (install.py ships tools/ wholesale via rglob). VERSION=2.15.1, AGENTS.md block=2.15.1 and the changelog agree; `git diff main...HEAD --stat` touches only T-080 Allowed files; the artifact is clean and at the checked SHA c7cc37b.
- V-06: pass - every T-080 criterion and inherited W-01..W-05 maps to concrete evidence above and in .agentflow/tasks/.runtime/T-081.evidence/verification-notes.md; no criterion was accepted from the green summary alone (each was either re-run by me or reproduced by disposable processes/tests on this SHA). One expected observation, not a defect: the T-080 and T-081 attempt records carry no workerTimeout/deadline/powerGuard because they were launched by the pre-merge 2.15.0 launcher - the fields are written by the artifact under review, not retroactively.
New defects (outside the task):
- none found
Cannot verify, needs:
- nothing; all six criteria verified with command output, live probes or deterministic reproductions
Proposed memory updates:
- none (worker: no canonical memory writes)
