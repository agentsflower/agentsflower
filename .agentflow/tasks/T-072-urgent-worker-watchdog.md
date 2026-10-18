# T-072: Urgent external worker deadline enforcement

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-070
Branch: t-072-urgent-worker-watchdog
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-072-urgent-worker-watchdog
Independent check: tester
Resume: none

## Goal

Repair missed worker deadlines exposed by T-040. Human authorized urgent
repair on 2026-10-18. Conductor and background Orchestrator are stopped;
preserve T-040 drafts. Human explicitly authorized swe-2-max for this task
and its independent tester despite low Jev effort confidence (persisted
T-072.route.json). This exception does not waive any quota/access gate.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tools/run_task.py
- .agentflow/tools/conductor.ps1
- .agentflow/tests/test_run_task.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/conductor.ps1
- .agentflow/tests/test_worker_watchdog.py
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- Other product repositories
- T-040 worktree and drafts (except explicit stop/recovery through launcher)
- Other Task Files and existing runtime history

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] W-01: Invalid/zero worker timeout retains a positive default; persist resolved timeout and deadline at launch.
- [ ] W-02: External watchdog stops overdue nonmanual workers with timeout classification, identity guards and recovery; no blind relaunch. Manual and unexpired attempts remain untouched. Legacy attempts use bounded fallback.
- [ ] W-03: Conductor runs watchdog each round, including while Orchestrator is alive. Stop uses expected-attempt guard so an old watchdog cannot stop a new attempt.
- [ ] W-04: Regression tests, full suite, patch release and migration note; no external rollout.
- [ ] W-05: Explicit stops record safe initiator/reason metadata (no raw argv/environment or secrets); watchdog stops are distinguishable from a human stop. Preserve default CLI compatibility.

## Implementation bounds

Keep the repair small: timeout parsing, persisted launch deadline, expected-attempt
guard and a launcher watchdog command called by conductor every round. Reuse
existing stop/recovery/identity/lease code; do not build a new scheduler. Do not
kill solely because a model is silent; deadline is authoritative. Bound post-kill
waits; failed cleanup stays locked and diagnosable. Emit a progress update after
the first focused regression check. Attempt budget is 15 minutes. If blocked,
checkpoint immediately with the exact failing check; no repeated broad rereads.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`
- `python -m unittest discover -s .agentflow/tests`

## Result
