# T-175: Chat Thread Selector: Researches & Implementations Separation with Folders, Per-Project Isolation, and Inactive Probing Bypass

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-174
Branch: t-175-chat-thread-selector-folders-and-project-isolation
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-175-chat-thread-selector-folders-and-project-isolation
Independent check: tester
Resume: none
Routing exception: human authorized chat thread selector folder grouping and per-project capacity probing optimization (2026-10-25)

## Goal

Implement the structured two-section Thread Selector matching the user's mockup (Вложение 2) with folder support, ensure strict per-project isolation of research threads and tasks, and bypass CLI probing for deactivated platforms:

1. **Two-Section Thread Selector with Folder Support (Mockup 2 Alignment)**:
   - In `studio.js` (`renderThreadDropdown`, `fillThreadList`) & `studio.css`:
     - **Top Search Bar**: Instant search input filtering across research thread names, folders, task IDs, titles, and stage labels.
     - **Section 1: 🔍 Researches**:
       - Prominent accented header bar (`.thread-section-header.researches-header`) with total research count badge and actions:
         - `+ New Thread` button (creates research thread).
         - `📁 + Folder` button (prompts for / creates a new folder category).
       - Fixed top item: `🔍 Research & Inception (General Chat)` (pinned root).
       - **Folder Grouping**:
         - Threads with `folder` field are grouped under collapsible folder items: `📁 <Folder Name> (<count>) ▾`.
         - Uncategorized threads appear at the root level under Researches.
         - Ability to double-click / context action to rename or move threads to a folder.
     - **Section 2: ⚙️ Implementations**:
       - Prominent accented header bar (`.thread-section-header.implementations-header`) with total task count badge.
       - **Stage Grouping**:
         - Tasks are cleanly grouped by Stage (`Stage 01 — <Label>`, `Stage 02 — <Label>`).
         - Each stage is collapsible; within each stage, render tasks with clean typography: `T-XXX — <Title>` + status badge (`DONE`, `IN PROGRESS`, `READY`, `REJECTED`, `CANCELLED`).
     - **Modern UX/UI Polish**:
       - Glassmorphism backdrop, clear visual separation between the two sections, smooth hover states, custom scrollbars, keyboard navigation (ArrowUp, ArrowDown, Enter, Escape).

2. **Strict Per-Project Scoping of Researches & Tasks**:
   - In `studio.js`:
     - In `switchProject(path)`: explicitly call `await loadResearchThreads(path)` alongside `loadTasks(path)`.
     - Reset `state.threads` and `state.researchMeta` on project switch so Project A's research threads and messages never appear or persist when Project B is active.
     - Pass `?project=<current>` in all research API calls (`/api/research/list`, `/api/research/thread`, `/api/research/create`, `/api/research/update`).
   - In `studio.py`:
     - Ensure `list_research_threads`, `load_research_thread`, `create_research_thread`, `update_research_thread` strictly resolve and write under the target project's `state/research/` directory.

3. **Model Quota Hub: Skip Probing for Deactivated Platforms**:
   - In `studio.py` (`probe_capacity`):
     - Read `load_project_state(project_root)` prior to launching probe threads.
     - If a platform is marked inactive (`state["platforms"][name]["enabled"] is False`), DO NOT spawn a background thread, execute CLI commands, or make network calls for it.
     - Directly assign an inactive platform record: `_platform(name, name, True, False, note="deactivated for this project - probe skipped")` with `enabled=False`.
     - Similarly, skip live model network requests for custom providers that are marked `enabled=False`.
     - Persist per-project platform and model preferences strictly in `<project>/<flow>/state/project-models.json`.

4. **Restore Cost & ROI Dashboard Subtab (Plan vs Fact Telemetry)**:
   - In `index.html`: restore `<button type="button" class="btn-subtab" data-sub="costs" id="btnSubtabCosts">Cost &amp; ROI Dashboard</button>` and the `#costRoiDashboard` container.
   - In `studio.js`: restore `costs` subtab handling in `updateAnalyticsFrame()` and `loadCostAnalytics(projPath)`.
   - Ensure Cost & ROI telemetry (`/api/analytics/costs?project=...`) correctly reflects the active project's tasks, planned token budgets, and actual telemetry.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- none

## Acceptance criteria

- [ ] C-01: Thread selector displays two distinct accented sections: `Researches` and `Implementations`.
- [ ] C-02: Researches section supports folder grouping (`📁 <Folder>`) with collapsible folders and creation of new folders.
- [ ] C-03: Implementations section groups tasks by stage with clean `T-XXX — Title` layout and status badges.
- [ ] C-04: Research threads and tasks are strictly isolated per project; switching projects reloads both and clears previous project state.
- [ ] C-05: Model Quota Hub bypasses CLI and network probes for platforms and providers marked `enabled: false` in `project-models.json`.
- [ ] C-06: Analytics toolbar includes "Cost & ROI Dashboard" subtab displaying project-scoped Plan vs Fact telemetry.
- [ ] C-07: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Result

Outcome: completed
Change: e3ab0ec on t-175-chat-thread-selector-folders-and-project-isolation
Files:
- .agentsflower/studio/index.html - restored `data-sub="costs"` subtab button `#btnSubtabCosts` and the `#costRoiDashboard` panel (summary cards, stage bar, stage filter, Plan vs Fact task table)
- .agentsflower/studio/studio.js - two-section thread selector: `buildThreadSection`/`buildFolderGroup`/`buildStageGroup`/`buildCollapsibleHeader`/`buildCollapsibleBody`/`toggleThreadCollapse`/`groupTasksByStage`/`threadSearchText`/`addResearchFolder`, `fillThreadList` renders `🔍 Researches` (pinned General Chat, folder groups, unfiled) and `⚙️ Implementations` (stage groups, `T-XXX — Title` + status badge), top search filters names/folders/ids/titles/stage labels, ArrowUp/Down/Enter/Escape + ArrowLeft/Right collapse; `switchProject` resets `state.threads`/`state.researchMeta`/`state.researchFolders` and explicitly awaits `loadResearchThreads(path)` + `loadCostAnalytics(path)`; `?project=` on `/api/research/create` and `/api/research/update`; restored `loadCostAnalytics`/`renderCostDashboard`/`formatSignedUsd`/`formatDeltaPct`, `costs` branch in `updateAnalyticsFrame`, `costStageFilter` listener
- .agentsflower/studio/studio.css - glassmorphism dropdown (`backdrop-filter`, custom scrollbar), `.thread-section*`/`.researches-header`/`.implementations-header` accents (blue / emerald), `.thread-folder-*`, `.thread-stage-*`, `.thread-sec-btn`, collapsed grid transitions; restored `.cost-roi-*`/`.cost-stage-*`/`.cost-task-table`/`.cost-delta-pill`/`.cost-status-badge` styles
- .agentsflower/tools/studio.py - `probe_capacity` loads project state before spawning probes and skips threads/CLI/network calls for `platforms[name].enabled is False` (bulk and `?platform=` paths, `_platform(...note="deactivated for this project - probe skipped")` + `enabled=False`); `_probe_provider(..., live_probe=)` and `_provider_probe` skip the live `/models` request for `enabled=False` providers
- .agentsflower/tests/test_studio.py - new `test_probe_skips_deactivated_platform_and_provider`, `test_probe_single_platform_respects_deactivation`, `test_research_threads_scoped_per_project`; `TestFlatThreadSwitcher` reworked to `TestStructuredThreadSwitcher` (the T-173 flat-list/removal markers contradicted this task's contract); `test_cost_and_roi_dashboard_subtab_in_analytics_view` replaces the removed-subtab test; `test_project_toggle_persists_and_scopes_to_project` asserts deactivated platforms carry no probed models
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (112 passed / 0 failed)
Criteria:
- C-01: pass - `.thread-section-top.researches-header` ("🔍 Researches" + count badge + `+ New`/`📁 + Folder` actions) and `.implementations-header` ("⚙️ Implementations" + count badge), glassmorphism dropdown with custom scrollbar - evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css
- C-02: pass - folder meta groups threads under collapsible `📁 <name> (<count>)` headers (`buildFolderGroup`); `📁 + Folder` prompts and creates a session folder category (`addResearchFolder` -> `state.researchFolders`, merged into the inspector folder select for assignment); dblclick inline rename retained - evidence: .agentsflower/studio/studio.js
- C-03: pass - `groupTasksByStage` + `buildStageGroup` render collapsible `Stage 01`-style groups; items show `T-XXX —` + `.thread-item-title` + `.thread-item-status` badge - evidence: .agentsflower/studio/studio.js
- C-04: pass - `switchProject` resets `state.threads`/`state.researchMeta`/`state.researchFolders` and explicitly awaits `loadResearchThreads(path)`; research API calls carry `?project=`; server resolves strictly under `<project>/<flow>/state/research/` - evidence: .agentsflower/tests/test_studio.py (`test_research_threads_scoped_per_project`)
- C-05: pass - `probe_capacity` spawns no thread/CLI/network call for `enabled: false` platforms or providers, returning `_platform(..., note="deactivated for this project - probe skipped")` with `enabled=False` - evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py (two new probe-bypass tests)
- C-06: pass - `#btnSubtabCosts` (`data-sub="costs"`) + `#costRoiDashboard` restored; `updateAnalyticsFrame` costs branch shows the panel and `loadCostAnalytics` fetches `/api/analytics/costs?project=` (init, switchProject, rebuild) - evidence: .agentsflower/studio/index.html, .agentsflower/studio/studio.js
- C-07: pass - 112 tests, 0 failures
Found, not fixed:
- The frontend never calls GET `/api/research/thread` (it loads `/api/research/list`); the endpoint already honors `?project=` server-side, so no client call site existed to parameterize.
- `📁 + Folder` folders are session-scoped (`state.researchFolders`): a folder persists on disk only once a thread is assigned to it, because folders live on thread records (no folder registry in the data model).
- `loadTasks` still invokes `loadResearchThreads` internally for its other callers (init, refresh, move-stage), so `switchProject` now issues a duplicate idempotent GET `/api/research/list` per the contract's explicit-call requirement.
- The task contract was extended mid-attempt (goal 4 / C-06 added at 22:27); covered by this change.
Proposed memory updates:
- none
