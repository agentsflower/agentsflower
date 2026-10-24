# T-134: Studio Interactive Enhancements: Draggable Splitters, Editor File Tabs, and Model Selector

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Branch: t-134-studio-splitters-tabs
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-134-studio-splitters-tabs
Independent check: tester
Resume: none
Routing exception: human authorized interactive enhancements per mockup 3 (2026-10-24)

## Goal

Implement interactive refinements in AgentsFlower Studio matching `.agentsflower/mockups/mockup-explorer-splitters-tabs.png` and `.agentsflower/mockups/README.md` (Section 5):

1. **Draggable Resizers (Splitters with `||` grip handles):**
   - Resizer 1: between left workspace sidebar and center code viewer.
   - Resizer 2: between center code viewer and right chat pane.
   - Centered visual grip icon `||` on the divider bar.
   - Smooth mouse drag resizing with bounded min/max limits:
     - Sidebar: min 200px, max 450px.
     - Chat pane: min 320px, max 650px.
     - Center code pane expands / shrinks dynamically.
   - Widths persisted in `localStorage` (`af_sidebar_width`, `af_chat_width`) and restored on load.

2. **Editor File Tabs Bar:**
   - Positioned directly above the code viewer (above or replacing the static breadcrumb bar).
   - Supports multiple open file tabs (e.g. `AGENTS.md`, `studio.js`, `Scratchpad`).
   - Each tab renders file icon, filename, and a close button `×`.
   - Active tab highlighted with blue glowing border.
   - Clicking a file in the workspace tree opens a new tab or switches to the already open tab.
   - Closing a tab switches to the previous open tab or clears the viewer if empty.

3. **Top Navigation Cleanliness:**
   - Keep strictly 4 core tabs: `Explorer`, `Task Board (N)`, `Analytics & Roadmap`, `Model Quota Hub`.
   - Remove junk tabs (`Task Contract Creator`, `Quick Start`, etc.).
   - Ensure zero horizontal scrollbars across the topbar at standard resolutions (`overflow-x: hidden`).

4. **Chat Model Selector:**
   - The model pill in the chat composer (`Devin swe-2-high ^`) must be interactive.
   - Clicking it toggles a dropdown menu with available models:
     - `Devin swe-2-high` (Floor default)
     - `Gemini 4 Argon High` (`gemini-4-argon-high`)
     - `Claude Opus 4.6 Thinking` (`claude-opus-4-6-thinking`)
     - `GPT-5.5 High` (`gpt-5-5-high`)
     - `Local / Ollama Model` (Offline zero-token)
   - Selecting a model updates the active pill display and persists in session state for chat requests.

## Read first

- .agentsflower/mockups/README.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.css
- .agentsflower/studio/studio.js
- .agentsflower/tests/test_studio.py

## Allowed files

- `.agentsflower/studio/index.html`
- `.agentsflower/studio/studio.css`
- `.agentsflower/studio/studio.js`
- `.agentsflower/tools/studio.py`
- `.agentsflower/tests/test_studio.py`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: Draggable splitters with `||` handles allow resizing sidebar and chat pane, persisting widths in localStorage.
- [ ] C-02: Editor file tabs bar renders above code viewer, allowing opening, switching, and closing file tabs.
- [ ] C-03: Top navigation bar contains strictly 4 core tabs with zero horizontal scrollbars.
- [ ] C-04: Chat composer model selector pill toggles an interactive dropdown to switch models.
- [ ] C-05: All tests in `test_studio.py` pass without regressions.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: f5355b5 on t-134-studio-splitters-tabs
Files:
- .agentsflower/studio/index.html - removed junk nav tabs (Knowledge Graph, Task Contract Creator, Quick Start Guide) keeping 4 core tabs; added #sidebarResizer between sidebar and main content and #chatResizer between code viewer and chat pane, each with a centered || .resizer-grip; added #editorTabsBar above the breadcrumbs in the code pane; wrapped #chatModelPill in .model-selector-wrap with #chatModelDropdown menu; bumped asset versions
- .agentsflower/studio/studio.css - .topnav-menu overflow-x:hidden; .explorer-grid now 3 columns (code | 10px resizer | chat width, JS-driven); .pane-resizer/.resizer-grip/dragging styles with hover glow; body.pane-resizing cursor/selection lock and iframe pointer-events guard; .editor-tabs/.editor-tab/.editor-tab-close styles with blue glowing active border; .model-selector-wrap/.model-dropdown/.model-option dropdown styles; 1200px media query updated for the resizer column
- .agentsflower/studio/studio.js - CHAT_MODELS (5 options) and PANE_LIMITS (sidebar 200-450px, chat 320-650px); bindResizer mouse-drag with clamping and localStorage persistence (af_sidebar_width, af_chat_width) plus restorePaneWidths on init; state.openTabs with renderEditorTabs/closeFileTab wired into openExplorerFile and resetExplorerPane; interactive model pill: setupModelSelector, renderModelDropdown, updateChatModelPill, selection persisted in state.chatModel + sessionStorage af_chat_model
- .agentsflower/tests/test_studio.py - topnav marker test aligned to 4 core tabs; new tests: exactly 4 data-tab items and junk tabs absent, resizer/tabs-bar/dropdown HTML markers, studio.js persistence and model-id markers, topnav-menu overflow-x hidden in studio.css
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (26 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (518 passed / 0 failed / 4 skipped)
Criteria:
- C-01: pass - .agentsflower/studio/index.html #sidebarResizer/#chatResizer with || .resizer-grip; .agentsflower/studio/studio.js bindResizer + PANE_LIMITS bounds 200-450 (sidebar) / 320-650 (chat), localStorage keys af_sidebar_width and af_chat_width written on mouseup and restored on load; center code pane is a minmax(0,1fr) grid track that flexes dynamically
- C-02: pass - .agentsflower/studio/index.html #editorTabsBar above .explorer-breadcrumbs in the code pane; .agentsflower/studio/studio.js state.openTabs, renderEditorTabs (icon + filename + x close, .active blue glowing border), closeFileTab switching to the previous tab or resetting the viewer when empty; tree clicks reuse openExplorerFile which opens or focuses the tab
- C-03: pass - .agentsflower/studio/index.html .topnav-menu contains exactly 4 data-tab buttons (explorer, kanban + badge, analytics, capacity); .agentsflower/studio/studio.css .topnav-menu uses overflow-x:hidden; test_index_topnav_has_only_four_core_tabs asserts count 4 and junk tabs absent
- C-04: pass - .agentsflower/studio/index.html .model-selector-wrap > #chatModelPill + #chatModelDropdown; .agentsflower/studio/studio.js CHAT_MODELS with Devin swe-2-high (floor default), gemini-4-argon-high, claude-opus-4-6-thinking, gpt-5-5-high and Local/Ollama; selection updates the pill, persists in state.chatModel and sessionStorage af_chat_model
- C-05: pass - 26/26 tests in test_studio.py pass including 5 new marker tests; full suite 518 pass / 4 skipped (see Checks)
Found, not fixed:
- view-graft and view-guide sections remain in the DOM but are unreachable through the top nav (their nav tabs were removed per mockup 3); view-creator stays reachable via the New Task and chat + buttons
- Sidebar minimum is 200px per the Task File; mockups/README.md Section 5 says 220px - contract text followed
Proposed memory updates:
- none
