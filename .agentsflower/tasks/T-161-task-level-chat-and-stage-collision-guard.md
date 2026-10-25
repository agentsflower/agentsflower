# T-161: Task-Level Chat Context, Implementations Guard, and DAG Stage Move Collision Checker

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: T-160
Branch: t-161-task-level-chat-and-stage-collision-guard
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-161-task-level-chat-and-stage-collision-guard
Independent check: tester
Resume: none

## Goal

Provide focused task-level discussion, enforce AI-only task addition in Implementations, and implement a DAG collision checker for stage reassignment:

1. **Implementations Isolation & Guard**:
   - Strictly disable manual task creation inside the `Implementations` section (tasks only enter via approved synthesis pool).
2. **Task-Level Chat Context**:
   - Selecting a task in `Implementations` loads its contract, criteria, and worktree status.
   - User can chat with the AI specifically about this task (scope adjustments, clarification).
3. **DAG Stage Move Collision Guard**:
   - Implement stage reassignment request handler (`/api/task/move-stage`):
     - Parses DAG dependencies (`Depends on:`).
     - Checks if moving a task to a target stage creates a dependency inversion or cyclic dependency.
     - If collision detected: rejects move with diagnostic explanation (e.g. *Cannot move T-014 to Stage 01: depends on T-002 in Stage 01*).
     - If safe: updates stage in ledger and Task File, re-links ordering, and updates UI.
4. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing DAG cycle detection, valid/invalid stage moves, and ledger updates.

## Read first

- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/state/tasks.md
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8911 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Manual task addition inside Implementations is disabled in UI; tasks arrive exclusively through synthesis approval.
- [ ] C-02: User can chat specifically within individual task threads.
- [ ] C-03: Stage move requests are validated against dependency graph (DAG) before mutation.
- [ ] C-04: Invalid stage moves (cycles, dependency inversions) are blocked with a clear diagnostic explanation.
- [ ] C-05: Valid stage moves atomically update `tasks.md` and Task Files.
- [ ] C-06: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
