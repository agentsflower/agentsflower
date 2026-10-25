# T-174: Verify Model Quota Hub UI Polish, Responsive Layout, and Cockpit Cleanup

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-173
Independent check: none
Resume: none
Verifies: T-173 @ 3f28f31f80ad29509e7d6e5a16a614c706e53095
Routing exception: human authorized Model Quota Hub UI verification (2026-10-25)

## Goal

Independently verify T-173's visual polish and layout fixes across Model Quota Hub, Analytics Sub-Tabs, Chat Task Selector, and Project Name Disambiguation.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-174.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-173-model-quota-hub-ui-polish.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Model Quota Hub cards render cleanly with zero element collisions between title, toggle switch, and status badge on cards at 320px+ width.
- [ ] V-02: Analytics view strictly contains the 3 original subtabs (`Tasks & Overview`, `Gantt & Dependency Graph`, `Roadmap & Milestones`); Cost & ROI dashboard button and pane are removed.
- [ ] V-03: Multiple projects sharing names like `code` display disambiguated parent prefixes in the project list.
- [ ] V-04: Chat thread selector opens a clean searchable task dropdown.
- [ ] V-05: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-06: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result
Outcome: completed
Verdict: pass

Independent verification of T-173 @ 3f28f31f80ad29509e7d6e5a16a614c706e53095 in detached-HEAD checkout
worktrees\agentsflower-t-173-model-quota-hub-ui-polish.t-174 (git status clean before and after; disposable
checkout left unchanged). Live UI checks ran against a sandbox copy of the checked commit
(%TEMP%\af-t174-9mx8Bx, studio.py on 127.0.0.1:8899) driven by headless Chrome over CDP, so the server
never wrote into the checked worktree.

Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (106 ran, 0 failed; OK)
- `python -m unittest discover -s .agentsflower/tests` -> pass (610 ran, 0 failed, 4 skipped; OK on rerun; first verbatim run hit 1 flaky ERROR, see V-06 note)

Criteria:
- V-01: pass - headless-Chrome DOM measurement of all 5 live platform cards at 1366/480/320 px: title never enters the toggle rect, .capacity-card-header never overlaps .capacity-card-status-row, .status-badge always inside the card and below the header; no horizontal scroll. Card grid column min is 320px (studio.css:812) and card DOM is two-row header + dedicated badge row (studio.js:1192-1204). evidence: .agentsflower/tasks/.runtime/T-174.evidence/T-174.dom_report.json, .agentsflower/tasks/.runtime/T-174.evidence/T-174.capacity_1366px.png, .agentsflower/tasks/.runtime/T-174.evidence/T-174.capacity_480px.png, .agentsflower/tasks/.runtime/T-174.evidence/T-174.capacity_320px.png
- V-02: pass - live DOM and source: exactly 3 .btn-subtab buttons (index/Tasks & Overview, graph/Gantt & Dependency Graph, roadmap/Roadmap & Milestones at index.html:477-479); #btnSubtabCosts and #costRoiDashboard absent; updateAnalyticsFrame pathMap holds only index/graph/roadmap and appends ts=Date.now() on project switch (studio.js:584-595,1576); no 'costs' branch or loadCostAnalytics anywhere in studio.js. evidence: .agentsflower/tasks/.runtime/T-174.evidence/T-174.dom_report.json
- V-03: pass - attached synthetic projects projA\code, projB\code, projC\site, projD\v2 to the sandbox server; GET /api/projects and the rendered .project-acc-name sidebar entries show "projA / code", "projB / code", "projC / site", "projD / v2" (GENERIC_PROJECT_DIR_NAMES + project_display_name, studio.py:94-111). evidence: .agentsflower/tasks/.runtime/T-174.evidence/T-174.v03_projects.txt, .agentsflower/tasks/.runtime/T-174.evidence/T-174.dom_report.json, .agentsflower/tasks/.runtime/T-174.evidence/T-174.capacity_320px.png
- V-04: pass - live dropdown opens from #threadPill: search input ("Filter by task ID or title..."), top item "Research & Inception (General Chat)", then a flat .thread-list of 156 .thread-item buttons each a direct child (no nested accordion/details); items carry task ID, title, stage pill, status badge; typing "t-17" filters 156 -> 5, "zzzz-nomatch" shows "No threads match this filter". evidence: .agentsflower/tasks/.runtime/T-174.evidence/T-174.dom_report.json, .agentsflower/tasks/.runtime/T-174.evidence/T-174.thread_dropdown.png, .agentsflower/tasks/.runtime/T-174.evidence/T-174.thread_dropdown_filtered.png
- V-05: pass - check 1 verbatim: 106 tests, OK. evidence: .agentsflower/tasks/.runtime/T-174.evidence/T-174.check1_test_studio.txt
- V-06: pass - check 2 verbatim first run: 610 tests, 1 error (test_scenarios.test_scenario_interrupted_merge_resume_simulated, PermissionError on a temp .runtime\T-001.json - Windows file-lock flake, unrelated to T-173 files); same test passes isolated and the full-suite rerun is clean: 610 tests, OK (skipped=4). evidence: .agentsflower/tasks/.runtime/T-174.evidence/T-174.check2_full_suite.txt, .agentsflower/tasks/.runtime/T-174.evidence/T-174.check2_full_suite_rerun.txt, .agentsflower/tasks/.runtime/T-174.evidence/T-174.dom_check.mjs

New defects (outside the task):
- Pre-existing (unchanged by T-173): the Studio sidebar is fixed 200-450px and never collapses; at ~600px viewport or narrower the workspace content pane is smaller than the 320px card minimum, so capacity cards are clipped with no horizontal scroll. Card-internal layout itself stays collision-free; only whole-card visibility suffers. Candidate for a future responsive-layout task, not a T-173 regression.

Cannot verify, needs:
- none

Proposed memory updates:
- known-issues: test_scenarios.ScenarioTests.test_scenario_interrupted_merge_resume_simulated is flaky on Windows (PermissionError reading its temp tasks\.runtime\T-001.json while a simulated attempt file is still held); passes on isolated and full-suite rerun. Reopen if it starts failing deterministically.
