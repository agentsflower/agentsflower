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

