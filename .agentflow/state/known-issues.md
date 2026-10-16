# Known Issues

- 2026-10-16 - Registry os.replace WinError 5 is recurring, not just one observed
  incident: final main (2.11.8) checkpoint suite ran 124 tests with one error in
  test_tick.test_disabled_subscription_access_temporarily_skips_the_tool; stack
  ends in machine_capacity._locked replacing a disposable registry JSON. T-017's
  candidate 151-test run passed. Scope a bounded Windows registry reliability
  investigation separately; do not hide this behind an eventual rerun pass.

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

- 2026-10-16 - Python launcher candidate 87de72c: Windows independently passed
  147 tests; real Linux/macOS spawn, killpg, PID identity and symlink paths remain
  unverified. Reopen with actual Unix hosts or the planned multi-OS CI.
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
