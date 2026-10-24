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

<!-- Worker writes its outcome below this block -->
