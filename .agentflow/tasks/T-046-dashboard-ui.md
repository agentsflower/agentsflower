# T-046: Roadmap view UI - stage cards, drill-down, diagnostics area, themes

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-107
Branch: t-046-dashboard-ui
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-046-dashboard-ui
Independent check: tester
Resume: 822c3ecff773e40427197d16098d8531703f0d95

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
Outcome: completed
Change: 822c3ecff773e40427197d16098d8531703f0d95 on t-046-dashboard-ui

Recovery note: attempt 2 timed out after committing the finished artifact; this attempt verified the preserved commit, ran all Checks and filled this Result. Setup snapshot output (attempt 1): `python .agentflow/dashboard/snapshot.py save "pre-roadmap-ui"` -> `v1-20261021-1847-pre-roadmap-ui`; post-work snapshot `v2-20261021-1920-roadmap-ui`.

Files:
- .agentflow/dashboard/roadmap_template.html - new page: shared filter bar + three-view selector (Cards/Journey/Matrix, persisted), stage column, diagnostics + drill-down side panel; drill-down reuses C.taskCard
- .agentflow/dashboard/roadmap.js - stage renderers: three separated facts, evidence table, recurring cycles, blockers, unmapped group, allowlisted attempts/routing/gate records, diagnostics and provenance cards
- .agentflow/dashboard/roadmap.css - page styles on shared tokens; one scrolling region, columns hidden by width (390-3840px), keyboard focus outlines
- .agentflow/dashboard/build.py - emits out/roadmap.html from the same payload; inlines ROADMAP_CSS/ROADMAP_JS markers
- .agentflow/dashboard/common.js - header nav gains the Roadmap link (all pages share it via initHeader)
- .agentflow/dashboard/README.md - data-contract delta: third page, view switch, diagnostics rendering
- .agentflow/tests/test_dashboard.py - RoadmapPageTests (self-containment, nav on all pages, three-facts vocabulary, demo badge, allowlist) + GOLDEN_DEMO/GOLDEN_TASKS field-level regression
- .agentflow/VERSION, AGENTS.md (AgentFlow block), CHANGELOG.md - 2.15.9 with migration notes

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (36 passed / 0 failed)
- `python .agentflow/dashboard/build.py` -> pass (92 tasks, 6 stages, 93 dependencies, 21 successors, 214 commits -> out)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out [DEMO DATA])
- `python -m unittest discover -s .agentflow/tests` -> pass (459 run, 0 failed, 4 skipped)

Criteria:
- U-01: pass - evidence: .agentflow/dashboard/common.js (Roadmap link in shared initHeader), .agentflow/dashboard/roadmap_template.html (stage list rendered from DATA.stages independent of pass(); counter text "Showing N of M tasks · stage list unaffected"; "N of M shown" per stage)
- U-02: pass - evidence: .agentflow/dashboard/roadmap.js (shead title/id + source link, factsHtml, blockersHtml, extrasHtml folds with full exit-criteria text and per-criterion evidence rows, taskTable rows data-go -> shared task card, unmapped section in all three views)
- U-03: pass - evidence: .agentflow/dashboard/roadmap.js (distinct labels "Declared status" / "Local tasks" / "Exit-criteria evidence"; EV map separates pass/fail/stale/pending/unknown by color AND text; stalemark badges; "No local tasks" on zero-task stages; recurring declaration chip vs recorded cycles block)
- U-04: pass - evidence: .agentflow/dashboard/roadmap.js (attemptsHtml, routingHtml with assessment/floor/selection/availability, verifyHtml with stale-artifact flag; allowlist-only fields - test_roadmap_runtime_sections_allowlist_only; missing -> "not recorded"/"unknown")
- U-05: pass - evidence: .agentflow/dashboard/roadmap.js diagCard ("Diagnostics — build snapshot", per-source mtime + fingerprint table, warnings, gaps, freshnessNote) and provenanceCard
- U-06: pass - evidence: .agentflow/dashboard/roadmap.css (.stagecol single scroller, .tablewrap overflow-x, column-hiding media queries, :focus-visible outlines) and roadmap_template.html (tabindex/Enter/Space handlers, DEMO DATA badge via C.initHeader, English-only asserted by test_english_labels_in_both_pages); browser-width verification left to the Tester per the task's Port section
- U-07: pass - evidence: .agentflow/tests/test_dashboard.py TaskFieldRegressionTests (GOLDEN_TASKS/GOLDEN_DEMO field equality vs pre-roadmap build) and test_all_pages_carry_roadmap_navigation; full suite green (459 tests)
- U-08: pass - evidence: .agentflow/dashboard/build.py (stdlib only, marker inlining; test_roadmap_page_is_self_contained: no unresolved markers, embedded const DATA, no external fetch)
- U-09: pass - evidence: .agentflow/VERSION (2.15.9), AGENTS.md (block version synced), CHANGELOG.md (2.15.9 entry with migration notes); decisions.md text proposed below

Found, not fixed:
- snapshot.py's source list does not cover the new roadmap_template.html/roadmap.css/roadmap.js, so `snapshot.py save/restore` versions the pre-existing source set only; documented in the 2.15.9 CHANGELOG migration notes. snapshot.py is outside this task's Allowed files - candidate for a follow-up.
- Pre-existing demo fixture contains a duplicate stage id and an unmapped task (T-108); the page renders both as diagnostics/warnings as designed.

Proposed memory updates:
- decisions.md, dated 2026-10-21: "T-046 implemented the Roadmap page (out/roadmap.html) with all three human-approved layouts (Cards, Journey, Matrix) behind a persisted selector. The three facts (declared status, local task counts, exit-criteria evidence) render with separate labels in every view; unmapped tasks and plan/ledger mismatches surface as warnings in a dedicated diagnostics card labeled as a build snapshot. snapshot.py does not yet version the new roadmap source files - noted in the 2.15.9 migration notes for a possible follow-up."
