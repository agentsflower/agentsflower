# T-147: Verify Studio analytics roadmap pixel-perfect mockup alignment

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-144 @ 9446803015678288cc95f6fa09c4dc65415e1144
Branch: t-147-verify-analytics-roadmap-mockup
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-147-verify-analytics-roadmap
Independent check: none
Resume: none

## Goal

Independently verify T-144 (Studio `Analytics & Roadmap` view aligned to the
reference UI mockup: workspace subheader with project path, persistent sidebar,
pill sub-tabs with solid-blue active state, Built timestamp, theme toggle,
Rebuild/Fullscreen actions, `?embedded=1` `#hdr` suppression with cockpit-dark
palette, Gantt filter bar/controls/scrubber/detail panel) against the T-144
contract:

1. Run `test_studio.py` and the full test suite.
2. Serve the Studio from this disposable checkout on PORT and exercise the Analytics & Roadmap view: persistent sidebar, subheader project path, three pill sub-tabs (active `Gantt & Dependency Graph` solid #2b5fd9 white text), Built stamp populated from the embedded dashboard payload, theme toggle, Rebuild and Fullscreen buttons.
3. Verify the embedded dashboard (`?embedded=1`) hides its internal `#hdr` topbar and renders the Studio dark palette (#111625/#161c2d, dark scrollbars) without breaking card grid rows.
4. Verify the Gantt view carries the filter bar chips, TIME/GANTT-VIEW control panels, segmented view switcher, playback scrubber, stage grouping, task rows with commit ticks/links, and the pinned task detail panel - no overlap/overflow defects.
5. Judge the developer's "Found, not fixed" notes (transient WinError 5 fixture flake; unrelated older Studio instance on port 8888 with find_free_port fallback) and record verdict in the Result section.

## Read first

- .agentsflower/tasks/T-144-studio-analytics-roadmap-mockup-alignment.md
- .agentsflower/roles/tester.md
- .agentsflower/mockups/ (the reference UI mockup files, if present)

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- PORT=8904

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes.
- [ ] V-02: Full regression test suite passes without regressions attributable to T-144.
- [ ] V-03: Served Analytics & Roadmap view carries the contract chrome: persistent sidebar, subheader project path, pill sub-tabs with correct active styling, Built stamp, theme toggle, Rebuild/Fullscreen actions.
- [ ] V-04: `?embedded=1` suppresses the dashboard `#hdr` and applies the cockpit-dark palette without layout breakage.
- [ ] V-05: Gantt view renders filter bar, control panels, view switcher, scrubber, stage groups, task rows and pinned detail panel per the mockup contract.
- [ ] V-06: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (44 passed / 0 failed) - .agentsflower/tasks/.runtime/T-147.evidence/T-147.check1_test_studio.txt
- `python -m unittest discover -s .agentsflower/tests` -> fail (535 passed / 1 failed, 4 skipped) - sole failure is the known WinError 5 temp-fixture os.replace flake in test_scenarios, not a T-144 regression - .agentsflower/tasks/.runtime/T-147.evidence/T-147.check2_full_suite.txt
Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-147.evidence/T-147.check1_test_studio.txt (Ran 44 tests, OK)
- V-02: pass - read as "no regressions attributable to T-144": the one failure is test_scenarios.test_scenario_contract_change_reverifies_moved_artifact_and_base dying on PermissionError [WinError 5] os.replace of a Temp fixture ledger (documented Windows flake class in known-issues.md, outside T-144's file scope); test_scenarios.py rerun in isolation: 8 passed / 0 failed / 1 skipped. evidence: .agentsflower/tasks/.runtime/T-147.evidence/T-147.check2_full_suite.txt .agentsflower/tasks/.runtime/T-147.evidence/T-147.test_scenarios_isolated.txt
- V-03: pass - .sidebar (250px, #projectAccordion 31 items) stays mounted beside view-analytics; .workspace-subheader shows the worktree path; three pill sub-tabs, active "Gantt & Dependency Graph" computed rgb(43,95,217)=#2b5fd9 fill, white text, 8px radius; analyticsBuiltStamp populated "Built 2026-10-25 02:29" from the embedded af-dash-meta postMessage; theme toggle flips shared localStorage and the iframe documentElement data-theme (observed light); Rebuild Analytics POST /api/dashboard/build -> 200 ok; Open Fullscreen href tracks the active sub-tab as the standalone URL (no embedded=1). evidence: .agentsflower/tasks/.runtime/T-147.evidence/T-147.studio_analytics_settled.png .agentsflower/tasks/.runtime/T-147.evidence/T-147.cdp_result.json .agentsflower/tasks/.runtime/T-147.evidence/T-147.cdp_result2.json .agentsflower/tasks/.runtime/T-147.evidence/T-147.cdp_result3.json
- V-04: pass - ?embedded=1 sets html[data-embedded="1"], #hdr display:none (standalone: flex, 40px); body bg rgb(17,22,37)=#111625; grid rows pinned in common.css so cards do not shift; dark scrollbars; hOverflow=0, vOverflow=0. evidence: .agentsflower/tasks/.runtime/T-147.evidence/T-147.gantt_embedded_full.png .agentsflower/tasks/.runtime/T-147.evidence/T-147.dashboard_graph_nonembedded.png .agentsflower/tasks/.runtime/T-147.evidence/T-147.cdp_result2.json
- V-05: pass - 11 fb-dd filter chips (Status..Closed) + "Waiting on owner"/"Waiting on a task" toggles + search + Reset all; TIME panel (Calendar/Active only, unit scale, gap slider), GANTT VIEW (Stages/Statuses/No groups + zoom fit/x2/x4/x8), LINK LINES panel; segmented vGantt/vBoard/vSum switcher; "State as of" scrubber (prev/#asof/next/Play/Now, asofLbl live); stage group rows, task rows with status dots + commit ticks (389 rects), bottom legend; pinned #detail populates on task click (TASK T-028: title, stage/role/agent, set-by, ledger status, outcome). evidence: .agentsflower/tasks/.runtime/T-147.evidence/T-147.gantt_embedded_full.png .agentsflower/tasks/.runtime/T-147.evidence/T-147.studio_detail_click.png .agentsflower/tasks/.runtime/T-147.evidence/T-147.cdp_result2.json .agentsflower/tasks/.runtime/T-147.evidence/T-147.cdp_result3.json
- V-06: pass - all criteria pass
New defects (outside the task):
- Commit 9446803 modified .agentsflower/dashboard/common.css, which is absent from T-144's "Allowed files" (only dashboard/common.js was listed). Functionally justified - the embedded palette and #hdr suppression live in common.css - so it reads as a task-file omission rather than scope creep, but the letter of the contract was exceeded. Orchestrator to decide.
- Developer "Found, not fixed" notes judged accurate: (a) WinError 5 fixture flake reproduced independently in this session (test_scenarios os.replace on a Temp fixture; green in isolation), matching the known-issues.md class; (b) port 8888 confirmed occupied by a live older Studio instance (GET /api/status -> 200, version 2.17.0) and studio.py carries the find_free_port fallback; this check ran on PORT=8904 as assigned.
Cannot verify, needs:
- none
Proposed memory updates:
- none
