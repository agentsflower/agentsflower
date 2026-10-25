# T-156: Verify Studio Hierarchical Thread Switcher UI

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-155
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-155

## Goal

Independently verify T-155 (Studio hierarchical thread switcher dropdown with Researches and Implementations sections) against the T-155 contract:

1. Serve Studio from the T-155 candidate worktree.
2. Verify visual appearance matches reference mockup (Researches header, Implementations header, nested Stages).
3. Test expanding and collapsing each section and stage block.
4. Verify clicking items loads the respective chat/task context.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-155-studio-hierarchical-thread-dropdown.md
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
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

- [ ] V-01: Dropdown displays two primary collapsible headers (`🔍 Researches` and `Implementations`).
- [ ] V-02: Tasks correctly render nested inside collapsible Stage blocks.
- [ ] V-03: Switching threads updates chat stream context.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
