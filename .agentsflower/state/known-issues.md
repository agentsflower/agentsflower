# Known Issues

- 2026-10-17 - Codex CLI Windows sandbox denies every write outside the task
  checkout: T-029 attempt 1 on codex completed a real review of 2c58157
  (verdict fail, per-criterion evidence in .runtime/T-029.1.log) but could not
  write the Result file despite the launcher's --add-dir tasks grant, and
  unittest runs were environment-blocked because Python could not create temp
  dirs (sandbox backend windows_sandbox permission_denied). Codex is therefore
  unusable for AgentFlow worker tasks on this Windows machine until that
  sandbox write path works; testers fall back to devin per Recovery.
- 2026-10-17 - Remote CI run 39026298541 (main@50adf65) FAILED: all three
  windows-latest and all three macos-latest test jobs exit 1 at
  `python -m unittest discover`; all three ubuntu-latest jobs and both
  package-integration jobs pass; mcp job skipped by dependency. Local Windows
  10 / Python 3.13 reproduces green (204 tests) even with the CI env
  (AGENTFLOW_MACHINE_STATE_DIR, PYTHONUTF8), so the failure is specific to the
  windows-2025/macos-arm64 runner environments. Job logs are not publicly
  readable (API 403) - exact failing tests need authenticated log access or a
  rerun. Candidates: the never-verified Darwin ps/killpg fallback, the Windows
  registry os.replace flake, junction/symlink privilege assumptions. No macOS
  pass is claimed anywhere.
- 2026-10-17 - T-022/T-023 independently verified bounded registry replacement
  retry and removal of conductor plaintext env handover at 0420265 (main 2.11.11).
  Earlier registry/conductor entries are mitigated by this accepted fix; reopen
  registry reliability on observed retry exhaustion. Real handover tested on
  pwsh 7; Windows PowerShell 5.1 compatibility is static evidence only.
- 2026-10-17 - Built-in CLI probes originally missed Devin workspace-trust and
  Codex non-Git flags. Fixed/independently verified in accepted T-024/T-025. Real
  Devin probe passed; no probe bypass/custom command was used as model proof.

- 2026-10-16 - Registry os.replace WinError 5 is recurring, not just one observed
  incident: final main (2.11.8) checkpoint suite ran 124 tests with one error in
  test_tick.test_disabled_subscription_access_temporarily_skips_the_tool; stack
  ends in machine_capacity._locked replacing a disposable registry JSON. T-017's
  candidate 151-test run passed. T-021 independently reproduced it twice in two
  full-suite runs on the bafc2a0 checkout (one error each: test_tick, then
  test_dispatch; both green standalone) - likely a scanner/AV briefly locking
  registry.json; a retry-with-backoff on os.replace would harden it, and it may
  also explain T-020's one-off test_route exit-1-vs-4 flake (same subprocess
  registry path). Scope a bounded Windows registry reliability investigation
  separately; do not hide this behind an eventual rerun pass.

- 2026-10-16 - T-014 worker env-file/custom model-probe defects were independently
  verified fixed in candidate 1e0bd87 by T-017 (151 Windows tests). This resolves
  the earlier probe-gap entry for that candidate only; main is still 2.11.8.
- 2026-10-16 - conductor.ps1 Start-Orchestrator still writes AGENTFLOW_* raw into
  conductor.env.json. Pre-existing Windows-only path, outside launcher repair
  ownership. Review a separate bounded secret-handover repair before public launch.
- 2026-10-16 - Old main limitHit regex misreads successful reports discussing
  quota tests as exhaustion. Candidate 1e0bd87 requires nonzero exit and includes
  a regression. Do not treat the flag alone as provider evidence; inspect exit/log.
- 2026-10-16 - test_route fixture environment/registry leakage is independently
  verified fixed in 1e0bd87; a transient Windows registry os.replace Access denied
  occurred once during developer runs but not T-017's independent full run.

- 2026-10-16 - Resolved at bafc2a0 (merged eb59c7c): T-019's real Linux run
  (Docker python:3.12-slim, WSL2 kernel) had found two product defects
  (run_logged spawned the tool without start_new_session, so killpg self-killed
  the worker on timeout; accept.py `merge-tree --write-tree --quiet` unsupported
  by Debian git 2.47.3) plus one env-dependent fixture (test_endcheck merge
  without git identity). T-020 repaired all three and T-021 independently
  re-verified 151 tests green on the real Linux kernel (git 2.47.3). macOS
  (Darwin ps-based pid_start/tree_pgroups fallback) remains fully unverified;
  Linux pass never implies macOS.
- 2026-10-16 - Candidate resource probes establish account/catalog access, not
  entitlement to the selected model. T-014 closes this and raw probe argv secret
  persistence; do not accept the stronger AC-06 guarantee on existing evidence.
- 2026-10-16 - Main baseline had one transient WinError 5 replacing a disposable
  registry during test_dispatch; narrow rerun passed 5/5. Candidate independently
  passed full suite 147/147 verbatim. Investigate if reproducible.

Errors, dead ends, and constraints of the AgentFlow template. Each entry: date, issue, when to look again.

- 2026-10-03 - Claude as Tester cannot be sandboxed on Windows: review isolation is detected after the attempt (attempt `error`), not prevented. Reopen if Claude Code gets a Bash sandbox on Windows.
- 2026-10-03 - `limitHit` is a text match ("usage limit", "rate limit", "quota") on the last 50 log lines; a task whose output mentions these words can be misread. Reopen if a tool reports limits in a structured way.
- 2026-10-03 - Runtime state is not committed: on a fresh clone `ledger.py set --status done` needs `gate.py verify` to run again.
- 2026-10-03 - `## Checks` commands run in PowerShell on Windows and `sh` elsewhere; a command written for another shell fails verify.
- 2026-10-03 - Antigravity IDE cannot be automated: its attempts are `-Manual` and end with `-MarkFinished`. CLI note (2026-10-21): the `agy` CLI is automated - developer and tester run non-interactive `-p --output-format stream-json`; only the IDE stays `-Manual`.

- 2026-10-18 - Resolved at fc2c37c (T-082, independently verified by T-083): backup_ok
  did not consult quota-group holds - an adequate backup held after assessment was
  admitted by the artifact API (T-075 P3 probe). backup_ok now consults
  machine_capacity.limit_until for the backup tool+quota_group at call time.
- 2026-10-18 - test_plan_route.py still reads the real machine registry through
  eligibility->limit_until (T-075 V-06 disclosure; T-083 confirmed it a real
  test-isolation defect: a disposable codex hold reproduces an assertion failure
  and a NoDecision error). Passes today against agy holds; fix in a separate
  scoped task - recheck when a codex/devin hold exists.
- 2026-10-18 - ledger.py _write_atomic can hit transient WinError 5 on os.replace
  (seen once in test_approval during the T-082 full suite; isolated rerun 5/5,
  T-083 did not reproduce). machine_capacity._replace_retry guards the same
  pattern elsewhere; a bounded hardening task may apply it to ledger writes.
- 2026-10-18 - REPEATED authoring defect (T-052->T-056, now T-082->T-084): a
  successor contract that inherits an unmerged base must declare the whole
  git diff main...HEAD file set in Allowed files, not only the delta commit -
  scope verification diffs the branch. Orchestrator checklist item until the
  rule lives in a template or gate.
- 2026-10-18 - test_routing_scheduler.py wrote its "live" holds at the fixed
  module constant AT (2026-10-18T12:00Z) + 1h; after 13:00Z the hold is
  permanently expired and test_a_held_backup_group_stays_scoped_and_refused
  fails deterministically (T-092 V-03). Lesson: "future" test data must derive
  from the run time, never a fixed wall-clock constant. Repair: T-094
  (T-093 consumed its duration budget on stopped attempts; its attempt 2
  committed the fix as 0b82f61, preserved on branch
  t-093-fixed-clock-test-repair for T-094 to carry).
- 2026-10-21 - gate.py endcheck crashes when the task worktree is already
  deleted at attempt end: worktree_copy_problems() -> commits.splitlines() on
  None (observed stopping T-093 attempt 2 after its worktree folder was
  removed first). The attempt still records stopped/error, but the crash hides
  the real endcheck outcome. Fix: tolerate a missing worktree in endcheck;
  recheck on the next stale-worktree stop.
- 2026-10-18 - devin CLI authentication is restored (`devin auth status`:
  logged in, Vladimir Chernetsov); the 21:27 launch block is resolved and
  managed devin launches are usable again.
- 2026-10-21 - RESOLVED (rotation commit, 2026-10-21): gate.py `paths()` now
  splits comma-separated bullets and strips trailing punctuation. Formerly it
  parsed only the FIRST whitespace token of each `Allowed files` bullet, so
  comma-separated path lists silently failed (a trailing comma broke the first
  path and the rest never registered) and `verify` flagged genuinely-allowed
  inherited files as out of scope (cost T-094 an otherwise green artifact).
  One path per bullet remains the authored convention.
- 2026-10-21 - install.py:269's 2.1-layout refusal tells readers to see
  GUIDE.md "Migration from the root layout", but the guide's section is
  "C. Migrate the old layout" (found by T-102, pre-existing in both files).
- 2026-10-21 - Quoting an `evidence:` marker inside Result prose makes the
  evidence-path validator count the following tokens as claims (T-100 V-03
  flagged '/' and 'roles/_template/protocol' from a quoted example; fixed by
  rewording). Authoring rule for workers: the literal `evidence:` may appear
  once per line, before the real claim paths only.
- 2026-10-24 - Evidence files under `.agentsflower/tasks/.runtime/` must have a
  basename starting `T-NNN.` (the task's own id), not just live inside a
  `T-NNN.evidence/` folder (gate.py `evidence_problems` checks the basename).
  Cost T-131 a verify refusal on otherwise complete work (`check1_test_studio.txt`
  -> renamed `T-131.check1_test_studio.txt`). Task Files already instruct
  workers via AGENTFLOW_EVIDENCE; the devin worker missed the prefix rule.
- 2026-10-24 - `gate.py stage 7` FAIL: ledger rows T-121, T-123, T-124,
  T-126, T-127, T-128, T-129 are `done` but their Task Files do not exist in
  `.agentsflower/tasks/` (never committed - no trace in git history or
  worktrees). Stage 7 cannot close until the human decides how to reconcile.
- 2026-10-24 - test_run_task.py on Windows: an orphaned fixture child
  (notepad.exe, PID seen 38452) can outlive its test under a full-suite run,
  failing a later launch test ("process still running" refusal) and a runtime
  temp-file read (PermissionError). Both tests pass in isolated rerun; T-132
  hit this, unrelated to its change. Candidate fix: harden fixture teardown
  or serialize those tests.
