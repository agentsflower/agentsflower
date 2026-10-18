# T-080: Prevent idle sleep during a bounded Windows worker attempt

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-072
Branch: t-080-worker-idle-sleep-guard
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-080-worker-idle-sleep-guard
Independent check: tester
Resume: none

## Goal

Fix the confirmed T-040 interruption cause: Windows entered connected standby
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
- .agentflow/tasks/T-072-urgent-worker-watchdog.md
- .agentflow/tools/run_task.py cmd_worker
- .agentflow/tests/test_worker_watchdog.py

## Allowed files

- .agentflow/tools/power_guard.py (small Windows adapter; no new dependency)
- .agentflow/tools/run_task.py (worker lifetime integration only)
- .agentflow/tests/test_power_guard.py
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
- [ ] P-02: POSIX is a no-op. API failure is reported explicitly without pretending protection succeeded; no global settings or persistent power changes. Retain T-072 deadlines and watchdog behavior after actual user-initiated sleep.
- [ ] P-03: Tests mock Windows API to prove acquire/release and exception/failure paths; live Windows probe confirms request succeeds and releases. Full suite passes; patch release and migration describe limits accurately.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_power_guard.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`
- `python -m unittest discover -s .agentflow/tests`
- Live Windows acquire/release probe without changing power configuration; record observed API result and OS version.

## Execution bounds

15-minute attempt cap. Implement a small process/thread-scoped Windows API
adapter, not a power-management subsystem. Checkpoint exact blockers promptly.

## Result
