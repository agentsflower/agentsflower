# T-121: AgentsFlower Studio Local Web UI & Multi-Project Gateway

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Branch: t-121-studio-local-web-ui
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-121-studio-local-web-ui
Independent check: tester
Resume: none
Routing exception: human authorized Studio architecture (2026-10-24)

## Goal

Implement the core AgentsFlower Studio Local Web UI server (`.agentsflower/tools/studio.py`) using Python standard library `http.server` with zero pip dependencies, accompanied by the responsive dark-mode glassmorphic frontend (`.agentsflower/studio/`).

## Read first

- .agentsflower/docs/ai-handoff-protocol.md

## Allowed files

- `.agentsflower/tools/studio.py`
- `.agentsflower/studio/index.html`
- `.agentsflower/studio/studio.css`
- `.agentsflower/studio/studio.js`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: Zero-pip-dep HTTP server in `studio.py` serves REST endpoints and static assets.
- [ ] C-02: Kanban board with visual stages and cards.
- [ ] C-03: Machine capacity and quota status display.

## Checks

- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: d121001
Criteria:
- C-01: pass - Zero-pip-dep HTTP server serves REST endpoints and static files cleanly.
- C-02: pass - Visual Kanban board renders tasks from ledger.
- C-03: pass - Quota monitor displays live slots and engine capacity.
