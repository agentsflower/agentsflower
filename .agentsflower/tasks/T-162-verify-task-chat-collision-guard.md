# T-162: Verify Task-Level Chat and DAG Stage Move Collision Checker

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-161
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-161

## Goal

Independently verify T-161 (Task-level chat context, Implementations creation guard, and DAG stage move collision checking) against the T-161 contract:

1. Serve Studio from the T-161 candidate worktree.
2. Confirm UI prevents manual task creation in Implementations.
3. Test task thread discussion.
4. Test moving tasks between stages: verify cycle and dependency inversion rejections, verify valid moves update ledger.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-161-task-level-chat-and-stage-collision-guard.md
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

none

## Do not touch

- *

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Manual task creation in Implementations is prevented.
- [ ] V-02: Task-level chat functions with task context preserved.
- [ ] V-03: Cyclic or inversion stage moves are rejected with descriptive errors.
- [ ] V-04: Valid stage moves mutate ledger safely.
- [ ] V-05: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
