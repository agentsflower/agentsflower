# T-126: Studio Navigation: breadcrumb links, cancel handler, and version sync

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-125
Branch: t-126-studio-navigation-breadcrumbs
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-126-studio-navigation-breadcrumbs
Independent check: tester
Resume: none
Routing exception: human authorized navigation fixes (2026-10-24)

## Goal

Add clickable breadcrumb navigation, Studio home button handler, cancel button in Task Creator, and synchronize the dynamic version badge in the brand header.

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

- [ ] C-01: Breadcrumb root `Studio` and brand icon return user to Task Board.
- [ ] C-02: Cancel button in task creator closes the creator form.
- [ ] C-03: Dynamic version badge reads active AgentsFlower version.

## Checks

- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: d126001
Criteria:
- C-01: pass - Clickable Studio breadcrumb navigates back to kanban.
- C-02: pass - Cancel button returns user to task board.
- C-03: pass - Version badge displays current version.
