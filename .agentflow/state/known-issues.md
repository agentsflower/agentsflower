# Known Issues

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
- 2026-10-03 - Antigravity IDE cannot be automated: its attempts are `-Manual` and end with `-MarkFinished`.
