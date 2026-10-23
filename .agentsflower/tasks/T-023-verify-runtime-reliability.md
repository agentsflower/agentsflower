# T-023: Independently verify runtime reliability repair

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-022
Verifies: T-022 @ 0420265a1e2a5a35136f3b80039adc2bb8a5a177

## Goal

Verify bounded Windows registry recovery and secret-free conductor handover
without weakening real guards. Same tool is necessary under the human's resource
policy; use a fresh isolated session. No product changes or real model probes.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-022-runtime-reliability.md
- .agentflow/tools/machine_capacity.py (replacement and locking ranges)
- .agentflow/tools/conductor.ps1 (handover ranges)
- .agentflow/tools/gate.py (rebuild parse/preflight ranges)
- .agentflow/tests/test_machine_capacity.py
- .agentflow/tests/test_conductor.py
- .agentflow/tests/test_parallel.py

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/
- .agentflow/tests/
- .agentflow/state/
- other projects, real machine leases and credentials

## Setup

- nothing

## Port

- nothing

## Rebuild together

<!-- No shared rebuild resources. -->

## Acceptance criteria

- [ ] V-01: Retry is bounded, Windows-error-specific and keeps atomicity/old registry on failure; permanent denial fails closed, no false lease or temp leak. Existing locking, capacity and fairness are preserved. Test transient/non-retryable/permanent cases with isolated fixtures.
- [ ] V-02: Dummy secret reaches the child but no raw secret is in runtime/generated wrapper files. Old conductor.env.json is removed safely for its own project. Inspect DPAPI CurrentUser trust boundary and actual Windows PowerShell compatibility; do not claim protection from another process of the same OS user. No daemon/user trust changes or real secret reads.
- [ ] V-03: Exact `nothing` sentinel is not a shared rebuild resource; actual shared resources, files, ports, dependency and approval failures still block. Probe argv remains explicit and non-escalating.
- [ ] V-04: Full suite runs verbatim; report all failures/skips and source versus environment causes. Source branch/worktree/task baselines unchanged. Review only these code changes; broader macOS CI remains pending and is not a fake pass.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` - atomic registry failure handling.
- `python -m unittest discover -s .agentflow/tests -p test_conductor.py` - secret-free memory handover.
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` - real overlap guards vs sentinel.
- `python -m unittest discover -s .agentflow/tests` - full regression suite.

## Result


Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` -> pass (11 passed / 0 failed, 0.339s; log: .agentflow/tasks/.runtime/T-023.evidence/test_machine_capacity.log)
- `python -m unittest discover -s .agentflow/tests -p test_conductor.py` -> pass (10 passed / 0 failed, 23.854s; log: .agentflow/tasks/.runtime/T-023.evidence/test_conductor.log)
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` -> pass (3 passed / 0 failed, 1.197s; log: .agentflow/tasks/.runtime/T-023.evidence/test_parallel.log)
- `python -m unittest discover -s .agentflow/tests` -> pass (158 passed / 0 failed, 146.813s; log: .agentflow/tasks/.runtime/T-023.evidence/test_full.log)
Criteria:
- V-01 bounded retry - pass - evidence: machine_capacity.py _replace_retry retries only winerror 5/32, REPLACE_ATTEMPTS=10 x REPLACE_DELAY=0.05s, raises on last attempt or any non-transient OSError; os.replace stays the single atomic swap; temp.unlink(missing_ok=True) in finally so no .tmp leak; locking, claim/release fairness and dead-process cleanup code unchanged in the diff; new tests prove transient-then-success (3 calls), permanent winerror 32 (exactly 10 calls, registry bytes preserved, no lease left behind - a later claim correctly reports "no free machine slot", not a false lease), non-retryable FileNotFoundError (1 call). All ran (Windows, skipUnless(nt) satisfied).
- V-02 secret-free handover - pass - evidence: conductor.ps1 builds {PATH + AGENTFLOW_*} -> ConvertTo-Json -> DPAPI ProtectedData::Protect CurrentUser -> base64 -> -Handover argv; the -Orchestrate branch Unprotects in memory and Set-Item env:, no file written; conductor.env.json legacy file is Removed each Start-Orchestrator in its own $rtDir; test_environment_reaches_the_session_window_without_a_plaintext_file proves dummy secret "shh-dummy-secret" reaches the fake child via stdout log and appears in no other .runtime file; run_task passes worker env via the subprocess env dict (worker_env), not a wrapper file. DPAPI boundary: blob sits on the child command line and any same-OS-user process could unprotect it - the code and developer Result do not claim otherwise; it still removes the on-disk plaintext file and resists other OS users. Windows PowerShell 5.1 compatibility verified by static review (ProtectedData lives in System.Security with an Add-Type fallback for 5.1, ConvertTo-Json -Compress and ::new() are 5.1-safe); live tests ran under pwsh 7 only, no WinPS 5.1 execution was exercised - flagged, not blocking.
- V-03 sentinel - pass - evidence: gate.py parse line ~196 adds `and w != "nothing"`; test_rebuild_nothing_sentinel_is_not_a_shared_resource proves "- nothing" x2 does not block while "- shared-lib" still produces "Rebuild together 'shared-lib' is shared with T-001"; allowed-files overlap, PORT collision, dependency/approval and Preflight deny/require/parallel checks are untouched by the diff; MODEL_PROBE_ARGS in run_task.py are explicit per tool (codex --skip-git-repo-check --sandbox read-only, claude -p with empty --allowedTools, agy stream-json, devin --respect-workspace-trust false --permission-mode auto) and pinned by test_builtin_probes_match_installed_cli_help_without_escalation, which forbids escalation flags. Note: exclusion keys on the first word, so "- nothing <extra words>" would also be skipped - consistent with the documented sentinel; not a weakening.
- V-04 suite and baselines - pass - evidence: full discover run verbatim at HEAD 0420265a1e2a5a35136f3b80039adc2bb8a5a177, 158 tests OK, no skips reported; `git status --porcelain` in this checkout empty before and after the runs (only runtime logs under tasks/.runtime, which are untracked by design); only the reviewed commit changed tools/tests/protocol (11 files, +173/-15); broader macOS CI remains genuinely pending and is not counted as a pass.
New defects (outside the task):
- none
Cannot verify, needs:
- Windows PowerShell 5.1 live execution of the -Handover path (tests use pwsh 7; static review found no 5.1 incompatibility and the Add-Type System.Security fallback is present)
Proposed memory updates:
- known-issues.md: the 2026-10-16 "Registry os.replace WinError 5" and "conductor.ps1 writes AGENTFLOW_* raw into conductor.env.json" entries can be closed - bounded retry and in-memory DPAPI handover independently verified at 0420265
