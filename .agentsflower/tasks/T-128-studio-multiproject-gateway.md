# T-128: Studio Multi-Project Gateway: dynamic project query, attach and scaffold

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-127
Branch: t-128-studio-multiproject-gateway
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-128-studio-multiproject-gateway
Independent check: tester
Resume: none
Routing exception: human authorized multi-project gateway (2026-10-24)

## Goal

Add multi-project querying (`?project=`), workspace attachment modal, and uninitialized project banner with installation prompt to Studio.

## Read first

- .agentsflower/tools/studio.py
- .agentsflower/studio/studio.js

## Allowed files

- `.agentsflower/tools/studio.py`
- `.agentsflower/studio/index.html`
- `.agentsflower/studio/studio.js`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: Endpoints accept `?project=` query parameter.
- [ ] C-02: Modal allows attaching external project directories.
- [ ] C-03: Banner detects uninitialized projects.

## Checks

- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: d128001
Criteria:
- C-01: pass - Studio serves tasks and status scoped to ?project= parameter.
- C-02: pass - External projects attach and persist in attached_projects.json.
- C-03: pass - Uninitialized banner displays when workspace lacks framework.
