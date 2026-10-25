# T-158: Verify Multi-Research Threads, Folders, and Context Forking

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-157
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-157

## Goal

Independently verify T-157 (Multi-research threads, folder categorization, and context referencing) against the T-157 contract:

1. Serve Studio from the T-157 candidate worktree.
2. Test creating multiple researches, renaming, and grouping into folders.
3. Verify persistence across page refresh.
4. Verify context cross-referencing between threads.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-157-multi-research-threads-and-folders.md
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

- [ ] V-01: Multiple research threads can be created and independently switched.
- [ ] V-02: Folder organization works and state persists to disk.
- [ ] V-03: Context referencing accurately pulls in referenced task/research context.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
