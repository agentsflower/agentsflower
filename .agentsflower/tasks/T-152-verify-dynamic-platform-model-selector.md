# T-152: Verify Studio Dynamic Platform & Model Selector

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-151
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-151

## Goal

Independently verify T-151 (Studio dynamic platform and model selector via CLI probing) against the T-151 contract:

1. Serve Studio from the T-151 candidate worktree.
2. Verify switching platform sends `/api/capacity/probe?platform=...` and updates the model dropdown.
3. Verify handling of uninstalled/unauthenticated platforms.
4. Verify persistence of chosen platform and model.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-151-studio-dynamic-platform-model-selector.md
- .agentsflower/studio/studio.js
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

- [ ] V-01: Platform selection switches available model list based on real CLI output.
- [ ] V-02: Uninstalled/unauthenticated platforms degrade gracefully with a visual badge.
- [ ] V-03: Session persistence stores and restores platform/model choices.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
