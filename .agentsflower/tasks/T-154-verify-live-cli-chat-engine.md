# T-154: Verify Studio Live CLI Chat Execution Engine

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-153
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-153

## Goal

Independently verify T-153 (Studio live CLI chat execution engine and `/api/chat` integration) against the T-153 contract:

1. Serve Studio from the T-153 candidate worktree.
2. Exercise `POST /api/chat` with mocked CLI runner and verify response shape and error handling.
3. Verify conversational threading in UI with real responses.
4. Verify timeout bounding and safety guards.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-153-studio-live-cli-chat-engine.md
- .agentsflower/tools/studio.py
- .agentsflower/studio/studio.js
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

- [ ] V-01: `POST /api/chat` executes prompt against designated tool/model and returns reply payload.
- [ ] V-02: Multi-turn history is preserved and sent in context.
- [ ] V-03: UI displays live assistant replies with thinking indicator.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
