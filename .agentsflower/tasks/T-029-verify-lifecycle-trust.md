# T-029: Independently verify trustworthy task lifecycle

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-028
Verifies: T-028 @ 2c5815718d19448ce6ac15cc66b2c38ff6f605e2

## Goal

Independently evaluate the exact T-028 artifact (2.12.1 lifecycle changes)
against every L-01..L-07 criterion in its Task File, in a disposable checkout.
Never repair the checked artifact; report the worst criterion as the verdict.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Roles and memory ownership, Task lifecycle)
- .agentflow/tasks/T-028-lifecycle-trust.md (the contract and the worker's Result)
- .agentflow/docs/improvement-plan.md section 1 (the requirement source)
- .agentflow/tasks/.runtime/T-029.1.log - attempt 1 (codex) found concrete defects but its sandbox denied every write outside the checkout, including this Result file and Python tempdirs; its findings are listed there verbatim. Re-verify the artifact independently; do not copy the verdict.
- .agentflow/state/known-issues.md
- The candidate diff `git diff main...2c5815718d19448ce6ac15cc66b2c38ff6f605e2` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-028 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Approval-gate bypass is genuinely closed on the exact SHA: `ledger.py set --status in progress`/`ready`/`review` on an awaiting-approval task is refused, `--status in progress` requires a recorded running attempt, and terminal tasks cannot acquire attempts - while legitimate protocol transitions still pass. Reproduce the refused and allowed directions in a disposable repo, not only by reading tests.
- [ ] V-02: Runtime JSON writes are atomic and malformed/truncated runtime, verify, tool-limits and heartbeat files fail closed with diagnosable errors at every claiming/read point (launcher, gate, tick, ledger) - prove with corrupted fixtures, including that a corrupt file never reads as "no active work" or "no limits".
- [ ] V-03: Verify/attempt records bind task id, attempt, requirements/header hash and full artifact SHA; legacy records keep working (file-bound tolerance). Check the actual record files, not just code paths.
- [ ] V-04: The `--live` empty-argv defect is really resolved since 2.11.3 and merge-history audit neither false-positives on legitimate merges nor misses real Task File commits - re-run the disposable-repo octopus/merge fixtures.
- [ ] V-05: pid+pidStart identity is used consistently where a process is declared dead/alive (spot-check the actual call sites, not only the delegated tick.alive claim).
- [ ] V-06: The four verbatim checks pass on the exact SHA in the disposable checkout (215 full-suite green is claimed; re-run); VERSION 2.12.1, AGENTS block and CHANGELOG migration notes are in sync; nothing outside Allowed files changed in the diff.
- [ ] V-07: Found-not-fixed notes in the Result are truthful and the right severity (spot-check machine_capacity._alive and route.py write claims); report anything material they missed.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - launcher lifecycle and state binding (V-01/V-02).
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` - launch/state/preflight regressions (V-01/V-04).
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-history and baseline audits (V-04).
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - runtime state handling (V-02).
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA (V-06).
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` - approval-gate refusal coverage (V-01).

## Result
Outcome: completed
Verdict: fail
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (33 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (9 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (215 passed / 0 failed, 3 skipped: optional mcp SDK not installed)
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (4 passed / 0 failed)
All six commands re-run verbatim on the exact SHA 2c5815718d19448ce6ac15cc66b2c38ff6f605e2 in the disposable checkout; logs in .agentflow/tasks/.runtime/T-029.evidence/check-*.log. Attempt 1 (codex) was sandbox-blocked; this attempt re-verified everything independently in a real environment (Python 3.13.7, git 2.53, Windows). Disposable-repo probes: t029-probes.py/.json, t029_probes2.py/.json, t029_probes3(b).py/.json, inner-state.json in the evidence folder.
Criteria:
- V-01 approval-gate bypass closed - pass - evidence: t029-probes.json cases A/V01. Real CLI in a disposable repo: `ledger.py set --status in progress|ready|review` on an awaiting-approval row all exit 1 with "awaits the human's approval"; clearing the prefix via --notes refused; prefix-keeping --notes and `approve` pass (exit 0). `--status in progress` refused without a running attempt and with only an exited attempt; allowed with a running attempt record. Terminal tasks cannot acquire attempts: rejected/cancelled/done rows refuse `--status in progress` ("final"); a genuinely rejected task is refused by `gate.py preflight` ("missing or final ledger status") and by a real `run_task.py --manual` launch. Legitimate transitions (ready->in progress->review, ready->cancelled, in progress->rejected) all pass.
- V-02 atomic writes + fail-closed malformed state - fail - steps: atomic writes verified (intercepted os.replace: old file intact, temp holds complete valid JSON before swap, no .tmp left; run_task.write_rt, gate.write_atomic, tick.write - t029-probes2.json section C). Truncated/non-JSON files are diagnosable everywhere (LaunchError/TaskError/StateError/sys.exit, `state-error` lines). But structurally-invalid JSON still fails OPEN at claiming points, reproduced verbatim: (a) run_task.limit_until returns None ("no limits") for tool-limits.json = `[]`, `null`, `{"codex":{}}`, `{"codex":[]}`; (b) tick.limit_end returns None for `{"codex":{}}` and `{"codex":[]}`; (c) orchestrator.json `{"holder":"existing-owner"}` (no `at`) reads as no live orchestrator and `tick.heartbeat("new-owner")` silently overwrote the claim - a malformed heartbeat steals orchestration; (d) runtime `{}` makes ledger.claimed crash with an undiagnosed KeyError (traceback, not a refusal message); (e) verify records `[{"sha":...,"ok":"false"}]` return truthy 'false' and grant acceptance, `[{"sha":...}]` crashes KeyError, `[{}]` is silently ignored (inner-state.json). A corrupt file does read as "no limits"/"no active work"/"no evidence" at multiple points - criterion not met.
- V-03 record binding - fail - steps: binding fields exist and were checked on a REAL attempt record produced by `run_task.py --manual` in the disposable repo (taskId + baseline.taskHash bound; no artifact-SHA field in the attempt record; gate.verify writes taskId/attempt/headerHash/full SHA - t029-probes2.json section A). Legacy file-bound records accepted; a verify record naming taskId T-999 refused. However the binding is decorative at the decision points, reproduced end-to-end: `ledger.verified` only matches taskId + SHA-prefix and trusts `ok` - a stale verify record for attempt 1 (`attempt:1, headerHash:h1, ok:true`) granted `ledger.py set --status done` (exit 0) while attempt 2 was running and requirements had moved; `done` does not require the current attempt exited or the record's attempt/headerHash to match. A running attempt labeled taskId T-999 inside T-005.json passed check_runtime and `set --status in progress` was granted. If the criterion is read as "fields exist on records", it is partial; read as "the binding is enforced where claims/acceptance happen", it fails - I read it as enforcement, and it fails.
- V-04 --live defect + merge-history audit - pass - evidence: t029-probes3.json B2 and t029-probes3b.json E2. Captured gate argv: empty live list produces `["--manual"]` only (no `--live` flag at all - the empty-argv defect is closed); live=[T-002,T-003] produces `["--live","T-002,T-003","--manual"]`. Real disposable git fixtures (repo+worktree, git 2.53, real `git merge`): clean commit -> `[]`; legitimate no-ff merge with no task changes -> `[]` (no false positive); worker commit adding .agentflow/tasks/T-999-evil.md -> flagged "branch t-099-x commits Task Files (1e8de3f...)"; task file arriving through a real merge -> flagged (7d4587e...); a 3-parent commit built via git commit-tree -> "cannot audit octopus merge 0bae986...: use two-parent merges".
- V-05 pid+pidStart consistency - fail - steps: tick.alive delegates to run_task.alive; attempt_alive, cmd_status, cmd_launch, cmd_stop all pass the recorded start; a mismatched measured start is correctly refused as "not ours" (identity probes on a live sleeper, t029-probes2.json section D). But where the recorded start is missing the system degrades to pid-only: alive(pid,None) and attempt_alive({running,pid}) returned True, `run_task.py --status` printed "running" for a pid-only attempt. Worse, `run_task.py T-007 --stop` on a live pid with pidStart=null warned, refused to kill (correct), yet still closed the attempt as error/dead and released the lock - the sleeper stayed alive (confirmed), the attempt became 'error', and a second claim (`set --status in progress` for attempt 2) was granted while the original process still ran. One task ended up with two live workers - the unsafe recovery path is inside the task's own Allowed files.
- V-06 verbatim checks + release sync + diff scope - pass - evidence: check-*.log, candidate.diff, candidate-files.txt. All six commands green on the exact SHA (33/8/9/21/215/4; full suite 215 pass 0 fail, 3 environmental skips). VERSION=2.12.1, AGENTS block line synced, CHANGELOG 2.12.1 entry with migration notes. 15 changed files all inside Allowed files; AGENTS diff is the version line only; run-task.ps1 and accept.py untouched as claimed. Note: the CHANGELOG's blanket claim that "a malformed or structurally invalid record fails closed... never as 'no evidence'" overstates observed behavior (see V-02).
- V-07 found-not-fixed truthfulness - pass - evidence: code spot-checks. machine_capacity._alive (tools/machine_capacity.py lines 52-75) confirmed: POSIX branch ignores `started` entirely (os.kill only), and on Windows a failed GetProcessTimes falls through to `return True` - a stale machine lease can still be fooled by a reused pid; severity is right (scoped follow-up, outside Allowed files). route._log (route.py line 372) writes T-NNN.route.json via direct write_text - non-atomic; ledger.save writes tasks.md non-atomically; both correctly scoped as out-of-scope notes. Material omissions in the Result's found-not-fixed section are the in-scope defects reported under V-02/V-03/V-05.
New defects (outside the task):
- none beyond the already-noted machine_capacity identity gap and route.py/tasks.md non-atomic writes; the material defects found are inside the checked task's own scope.
Cannot verify, needs:
- Live POSIX/macOS behavior of pid_start/alive was not executed on this Windows host; the POSIX code path is confirmed by inspection only. Platform simulations are labeled as such.
- The merged-main behavior after acceptance is out of scope; checks ran on the exact unmerged SHA.
Proposed memory updates:
- Do not accept T-028 as meeting the lifecycle exit criteria; this is an independently completed negative review of SHA 2c5815718d19448ce6ac15cc66b2c38ff6f605e2.
- Scope a successor for: fail-closed structural validation of tool-limits/heartbeat/verify records at every reader (no silent "no limits"/"no orchestrator"/"no evidence"); enforce verify-record attempt + headerHash + full-SHA binding and a current exited attempt at `set --status done`; keep the task locked in --stop when a live pid's identity is unconfirmed; validate per-attempt taskId in check_runtime; fix the ledger.claimed KeyError on `{}`.
- Keep machine_capacity._alive and route.py/tasks.md atomicity as separate scoped follow-ups (outside T-028's Allowed files).
