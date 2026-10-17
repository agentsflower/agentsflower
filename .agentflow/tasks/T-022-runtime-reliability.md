# T-022: Harden registry writes and conductor environment handover

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-024
Branch: t-022-runtime-reliability
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-022-runtime-reliability
Independent check: tester
Resume: none

## Goal

Close the two repeatedly observed release risks before adding public interfaces:
bounded Windows registry replace recovery and secret-free conductor handover.
Keep the accepted Windows/Linux launcher behavior. No changes to other projects.

## Read first

- AGENTS.md
- .agentflow/docs/project-rules.md
- .agentflow/state/known-issues.md
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/conductor.ps1 (Start-Orchestrator/environment handover ranges)
- .agentflow/tools/run_task.py (probe argv and environment ranges)
- .agentflow/tests/test_machine_capacity.py
- .agentflow/tests/test_conductor.py

## Allowed files

- .agentflow/tools/machine_capacity.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/conductor-panel.ps1
- .agentflow/tools/run_task.py
- .agentflow/tools/gate.py
- .agentflow/tests/test_machine_capacity.py
- .agentflow/tests/test_conductor.py
- .agentflow/tests/test_run_task.py
- .agentflow/tests/test_parallel.py
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .github/
- pyproject.toml
- README.md
- GUIDE.md
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

<!-- No shared rebuild resources. -->

## Acceptance criteria

- [ ] R-01: Registry replacement retries only transient Windows sharing/access failures with a short bounded backoff. Successful atomic replacement stays atomic; permanent failure preserves the previous registry and fails closed. Locking, lease fairness and cleanup remain intact. Cover transient success, permanent failure, non-retryable errors and temp-file cleanup; no infinite loops.
- [ ] R-02: Conductor passes environment in memory to the spawned process and never persists raw AGENTFLOW_* or argv secrets to conductor.env.json or generated wrapper content. Preserve effective PATH/tool flags, background stdout/logs, process identity and Windows-only behavior. Use dummy secrets in tests; do not read real credentials or stop other projects.
- [ ] R-03: Review built-in model probes against installed CLI help: noninteractive inference in an empty temporary directory must work with normal trust settings without repository writes or permission escalation. If a supported trust/repository flag is required, make it explicit and test argv. Never substitute auth/catalog for inference. No paid requests in automated tests.
- [ ] R-04: Full suite passes verbatim. Increment the current intermediate 2.11 patch VERSION, synchronize AGENTS template block and changelog migration notes. Only relevant protocol text changes. Propose dated decision in Result; do not write canonical memory.
- [ ] R-05: gate.parse currently treats the documented Rebuild together sentinel `nothing` as a real shared resource, blocking independent tasks. Exclude that exact documented sentinel, preserve real resource overlap checks, and add regression tests. Do not weaken file/port/dependency/approval checks. Current task contracts use empty rebuild lists where no resource exists.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` - bounded registry recovery.
- `python -m unittest discover -s .agentflow/tests -p test_conductor.py` - in-memory environment and secret handling.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - supported probe and launcher regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result

Outcome: completed
Change: 0420265 on t-022-runtime-reliability
Files:
- .agentflow/tools/machine_capacity.py - _replace_retry: bounded backoff only for winerror 5/32 on registry.json os.replace; temp file always unlinked; previous registry preserved on permanent failure
- .agentflow/tools/conductor.ps1 - AGENTFLOW_* handover moved to a DPAPI CurrentUser-encrypted -Handover argv blob decrypted in memory by -Orchestrate; conductor.env.json no longer written and a leftover one is removed at each handover
- .agentflow/tools/gate.py - parse: the documented "Rebuild together: - nothing" sentinel is excluded; real overlap checks unchanged
- .agentflow/tests/test_machine_capacity.py - transient retry success, bounded permanent failure (registry preserved, no lease, no temp leak), non-retryable error single-attempt
- .agentflow/tests/test_conductor.py - dummy secret reaches the session window via memory only; legacy env file removed; no runtime file serializes it
- .agentflow/tests/test_parallel.py - "nothing" sentinel no longer blocks independent tasks; "shared-lib" still does
- .agentflow/tests/test_run_task.py - built-in probe argv now asserted for all four tools; no escalation flags; trust/repo flags explicit
- .agentflow/docs/ai-handoff-protocol.md - one clause: "- nothing" declares no shared resource
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.11.11 with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` -> pass (11 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_conductor.py` -> pass (10 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (28 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (158 passed / 0 failed)
Criteria without a command:
- R-01 - _replace_retry retries only ERROR_ACCESS_DENIED(5)/ERROR_SHARING_VIOLATION(32), REPLACE_ATTEMPTS=10 x 0.05s; atomicity kept (single os.replace per attempt); locking/fairness untouched; tests cover transient success, permanent failure, non-retryable, temp cleanup, bounded loop
- R-02 - handover is DPAPI-encrypted on the child argv and decrypted in memory; effective PATH/AGENTFLOW_* reach the spawned tool (proven by fake-tool echo); stdout logs, pid/pidStart identity, Windows-only path unchanged; only dummy secrets used
- R-03 - reviewed MODEL_PROBE_ARGS against installed `codex exec --help`, `claude --help`, `agy --help`, `devin --help`: every needed trust/repository flag exists and is explicit (codex --skip-git-repo-check, devin --respect-workspace-trust false --permission-mode auto, claude print mode skips trust with empty --allowedTools, agy stream-json); argv pinned by tests; no probe run (no paid calls)
- R-05 - sentinel `- nothing` excluded in gate.parse; overlap, file, PORT, dependency and approval checks unchanged; regression test proves both directions
Found, not fixed:
- DPAPI protects the handover blob only for the same OS user on this machine; another process running as the same user could read it - same trust boundary as the previous env file, now without disk persistence
Proposed memory updates:
- decisions.md (2026-10-17): conductor environment handover uses DPAPI CurrentUser-encrypted argv instead of conductor.env.json - chosen over Start-Process -Environment (pwsh 7.4+ only) because the same mechanism must also serve Windows PowerShell 5.1 and Store-packaged pwsh; rejected: plaintext file, wrapper script with embedded secrets
- known-issues.md: resolve the 2026-10-16 "conductor.ps1 writes AGENTFLOW_* raw into conductor.env.json" entry and the recurring WinError 5 registry os.replace entry (bounded retry now in place; reopen if REPLACE_ATTEMPTS exhaustion is observed)
