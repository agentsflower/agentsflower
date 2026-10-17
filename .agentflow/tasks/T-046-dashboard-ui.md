# T-046: Roadmap view UI - stage cards, drill-down, diagnostics area, themes

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-044
Branch: t-046-dashboard-ui
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-046-dashboard-ui
Independent check: tester
Resume: none

## Goal

Implement the Roadmap page and its stage-to-task drill-down per the human's
selected mockup and the T-044 payload schema, preserving every existing view
and interaction (Overview, Gantt & timeline, filters, cards, themes, metrics,
demo mode, offline stdlib build).

## Read first

- .agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md (sections 3-4)
- .agentflow/dashboard/mockups/ (the selected variant - from decisions.md record)
- .agentflow/dashboard/UI-RULES.md (all of it)
- .agentflow/dashboard/README.md (payload data contract from T-044)
- .agentflow/dashboard/template.html, graph_template.html, common.css, common.js, filterbar.js, filterbar.css, build.py, snapshot.py
- .agentflow/tests/test_dashboard*.py

## Allowed files

- .agentflow/dashboard/template.html
- .agentflow/dashboard/graph_template.html
- .agentflow/dashboard/common.css
- .agentflow/dashboard/common.js
- .agentflow/dashboard/filterbar.js
- .agentflow/dashboard/filterbar.css
- .agentflow/dashboard/roadmap*.{html,css,js} (new roadmap page assets)
- .agentflow/dashboard/build.py (only the wiring needed to emit the new page from the shared payload)
- .agentflow/dashboard/README.md (data contract deltas only)
- .agentflow/tests/test_dashboard*.py
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, .agentflow/tasks/ (other Task Files), .agentflow/docs/project-plan.md
- .agentflow/tools/, .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md (integration task owns docs)
- pyproject.toml, setup.py, MANIFEST.in
- other projects and their machine leases

## Setup

- python .agentflow/dashboard/snapshot.py save "pre-roadmap-ui" (record output in Result)

## Port

- nothing (offline pages; browser verification is the Tester's)

## Rebuild together

- nothing

## Acceptance criteria

- [ ] U-01: Roadmap navigation added with the shared header/theme/build-timestamp chrome identical to existing pages; every declared stage renders regardless of task filters; task filters slice the execution data only, with filtered vs total counts explicit.
- [ ] U-02: Stage card shows title/ID, declared status, task counts, evidence summary, active work/blockers, source link; expand reveals exact exit criteria and evidence rows; drill-down reaches existing task cards and checks; unmapped/ambiguous tasks stay visible in their own group.
- [ ] U-03: The three facts never merge: declared status, execution counts, criterion evidence each keep their own labels; unknown vs fail vs stale are visually distinct; a stale link/badge is marked stale; no invented Done badges on zero-task stages; recurring stage shows its ongoing declaration separately from a recorded cycle.
- [ ] U-04: Safe attempt history in task drill-down: recorded attempts with the P-06 allowlist fields; assessment/floor/selection/availability summary where records exist; missing fields shown as unknown.
- [ ] U-05: Diagnostics area: source freshness (build time + source fingerprints), mismatches, parse diagnostics - labeled as a build snapshot, never live monitoring.
- [ ] U-06: UI-RULES conformance: one scrolling region, no horizontal scroll at 390/1280/1920/3840px, reserved space for dynamic counters, light/dark themes, keyboard navigation, readable labels beyond color, DEMO DATA badge in demo mode, English UI.
- [ ] U-07: Zero regression on Overview, Gantt & timeline, filters/counts/resets/chips/search, task cards, inter-task links, successor/check/dependency edges, metrics and demo mode (existing tests plus the Plan's regression expectations).
- [ ] U-08: No new runtime dependency: offline self-contained pages, stdlib build, no UI framework, no server, no external fetch.
- [ ] U-09: Full suite passes verbatim; increment VERSION, sync AGENTS block, CHANGELOG with migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` - UI/payload wiring tests.
- `python .agentflow/dashboard/build.py` and `python .agentflow/dashboard/build.py --demo` - all pages build.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
