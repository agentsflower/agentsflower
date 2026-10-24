# T-129: Studio Classic Dashboard Integration: Analytics & Roadmap views

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-128
Branch: t-129-studio-classic-dashboard
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-129-studio-classic-dashboard
Independent check: tester
Resume: none
Routing exception: human authorized dashboard integration (2026-10-24)

## Goal

Integrate the classic HTML dashboard into Studio under `/dashboard/out/`, embedding overview, Gantt, and roadmap views with an on-demand rebuild action.

## Read first

- .agentsflower/tools/studio.py
- .agentsflower/studio/index.html

## Allowed files

- `.agentsflower/tools/studio.py`
- `.agentsflower/studio/index.html`
- `.agentsflower/studio/studio.js`
- `.agentsflower/studio/studio.css`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: Studio backend serves classic dashboard files under `/dashboard/out/`.
- [ ] C-02: Analytics tab embeds iframe with subtab navigation.
- [ ] C-03: On-demand rebuild button triggers `build.py`.

## Checks

- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: d129001
Criteria:
- C-01: pass - Dashboard static files served correctly by studio.py.
- C-02: pass - Analytics view renders embedded iframe cleanly.
- C-03: pass - Rebuild button triggers dashboard build and reloads view.
