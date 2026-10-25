# T-150: Verify Studio UI Strict Cleanup: Clean Topnav, Simplified Composer, and Header Suppression

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-149
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-149 @ d72d033b9ad7ead15def4b5a893698cff39049df

## Goal

Independently verify T-149 (Studio UI strict cleanup: removal of topnav search, new task, and chip; composer controls cleanup; embedded header suppression) against the T-149 contract:

1. Serve the Studio from the T-149 candidate worktree/branch.
2. Verify `.topnav` has only brand and 4 nav items; `#activeProjectChip`, `#globalSearchInput`, `#btnQuickCreate` are absent.
3. Verify `.composer-toolbar` contains only model selector, spacer, and send button; `#btnChatNew`, `#btnChatRefresh`, `#btnChatPlus`, `#btnSynthesizeTasks` are absent.
4. Verify embedded `#hdr` suppression in `dashboard/common.css` and `studio.js`.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-149-studio-ui-cleanup-and-mockup-alignment.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/dashboard/common.css
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

- [ ] V-01: Top navigation bar right side is clean (no search, no new task button, no project chip).
- [ ] V-02: Composer toolbar contains only model selector and send button.
- [ ] V-03: Embedded analytics frame suppresses duplicate `#hdr`.
- [ ] V-04: Full regression suite passes cleanly (`python -m unittest discover -s .agentsflower/tests`).

## Checks

- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` - proves V-01, V-02, V-03 partially via updated DOM contract tests
- `python -m unittest discover -s .agentsflower/tests` - proves V-04

## Result

<!-- Worker writes its outcome below this block -->

