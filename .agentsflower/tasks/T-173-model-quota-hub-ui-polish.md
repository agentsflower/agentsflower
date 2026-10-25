# T-173: Model Quota Hub UI Polish: Clean Card Layout, Badge & Toggle Alignment, Analytics Sub-Tabs Cleanup, and Disambiguated Project Names

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-172
Branch: t-173-model-quota-hub-ui-polish
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-173-model-quota-hub-ui-polish
Independent check: tester
Resume: none
Routing exception: human authorized Model Quota Hub UI polish and cockpit cleanup (2026-10-25)

## Goal

Resolve visual clutter, card element collisions, and cockpit UX regressions across Model Quota Hub, Analytics, and Chat Task Selection:

1. **Model Quota Hub Card Hierarchy & Layout Polish**:
   - In `studio.js` (`renderCapacityCards`) & `studio.css`:
     - Fix element collision on platform cards: Separate `.capacity-card-top` into a clean two-row header:
       - **Top Row (`.capacity-card-header`)**: Platform name (`.capacity-tool-title`) on the left, Active/Inactive state label and toggle switch (`.platform-enable-toggle`) aligned to the right.
       - **Badge Row (`.capacity-card-status-row`)**: Dedicated row for the status badge (`.status-badge` e.g., `ACTIVE & AUTHENTICATED`, `NOT INSTALLED`, `LIMITED / UNAUTHENTICATED`), so the badge NEVER wraps over or collides with the title or toggle switch.
     - Increase `.tools-capacity-grid` column min-width from 280px to 320px (`grid-template-columns: repeat(auto-fill, minmax(320px, 1fr))`) to give cards ample breathing space.
     - Ensure `.status-badge`, `.toggle-state-label`, and `.platform-version` have clean typography, proper margins, and do not overflow card boundaries on any viewport.

2. **Restore Clean 3-Tab Analytics Sub-Navigation (Remove Unsolicited Cost & ROI Dashboard)**:
   - In `index.html`: Remove `#btnSubtabCosts` button and `#costRoiDashboard` container injected in T-165.
   - In `studio.js`: Remove the `'costs'` subtab handling branch in `updateAnalyticsFrame()` and remove redundant `loadCostAnalytics()` calls.
   - Keep strictly the 3 mock-aligned subtabs: **Tasks & Overview**, **Gantt & Dependency Graph**, and **Roadmap & Milestones**.
   - Ensure cache-busting timestamp (`ts=Date.now()`) is appended on project switch so switching projects immediately updates the embedded iframe.

3. **Disambiguate Project Names & Smart Flow Root Resolution**:
   - In `studio.py` (`get_project_info` and `find_projects`):
     - If a project directory has a generic folder name (`code`, `site`, `v1`, `v2`), format its display name with its parent directory (e.g. `AntiBrowser / code`, `AgentFlow / code`, `Gemini to Word / v2`) so multiple projects are never indistinguishable.
     - In `get_project_flow_root`: If the target folder has no `.agentsflower` at root, check immediate children (`target / "code"`, `target / "src"`) so parent folders like `AntiBrowser` resolve to their actual template root.
     - If a project dashboard has not been built yet, return a clean HTML placeholder explaining the dashboard is not yet generated with a rebuild hint, rather than raw 404 text.

4. **Fix Chat Task Selector (Image 2 UX)**:
   - In `studio.js` & `index.html`: Replace the broken multi-level nested accordion in `#threadDropdown` with a clean, flat, searchable dropdown:
     - Search input at the top for instant filtering by task ID or title.
     - Top option: "Research & Inception (General Chat)".
     - List of tasks displaying Task ID (`T-XXX`), title, stage pill, and status badge without nested collapsed sub-trees.

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

- [ ] C-01: Model Quota Hub cards display a clean two-row header with platform title + toggle switch on top, and status badge on its own row without visual collision or overlap.
- [ ] C-02: Analytics toolbar has strictly 3 subtabs (Tasks & Overview, Gantt & Dependency Graph, Roadmap & Milestones); `#btnSubtabCosts` and `#costRoiDashboard` are removed.
- [ ] C-03: Projects with generic folder names (`code`, `site`, `v2`) display disambiguated parent paths in the project list.
- [ ] C-04: Chat task dropdown provides a flat, searchable selection list without broken nested accordions.
- [ ] C-05: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
