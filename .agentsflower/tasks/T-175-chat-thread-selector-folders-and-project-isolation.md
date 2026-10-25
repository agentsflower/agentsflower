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

<!-- Worker writes outcome below -->
