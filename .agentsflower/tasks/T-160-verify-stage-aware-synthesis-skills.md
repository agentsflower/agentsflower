# T-160: Verify Stage-Aware Task Synthesis and Autonomous Skills Mapping

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-159
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-159

## Goal

Independently verify T-159 (Stage-aware task pool synthesis and autonomous skills mapping) against the T-159 contract:

1. Serve Studio from the T-159 candidate worktree.
2. Exercise `POST /api/task/synthesize` with frontend and SEO prompts; verify generated stages and assigned skills.
3. Verify Task Pool Card rendering in UI with skill badges.
4. Verify batch registration creates Task Files carrying `Skills:` headers.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-159-stage-aware-task-synthesis-and-skills.md
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

- [ ] V-01: `/api/task/synthesize` assigns sequential stage numbers matching dependency order.
- [ ] V-02: Relevant skills are correctly identified and attached to task items.
- [ ] V-03: Registered Task Files carry valid `Skills:` fields.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
