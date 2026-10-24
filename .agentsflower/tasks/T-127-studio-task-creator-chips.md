# T-127: Studio Task Contract Creator: interactive file tags and criteria builder

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-126
Branch: t-127-studio-task-creator-chips
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-127-studio-task-creator-chips
Independent check: tester
Resume: none
Routing exception: human authorized task creator fixes (2026-10-24)

## Goal

Enhance Task Contract Creator with interactive allowed files tag chips and auto-numbered acceptance criteria items (`C-01:`, `C-02:`), replacing unstructured text areas.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js

## Allowed files

- `.agentsflower/studio/index.html`
- `.agentsflower/studio/studio.js`
- `.agentsflower/studio/studio.css`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: Allowed files input adds removable tag chips.
- [ ] C-02: Criteria builder auto-numbers C-01, C-02 with quick chips.
- [ ] C-03: Generated markdown aligns with Task File protocol.

## Checks

- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: d127001
Criteria:
- C-01: pass - Allowed files chips are interactive and removable.
- C-02: pass - Criteria items are structured and auto-numbered.
- C-03: pass - Task creation produces valid markdown contract.
