# AgentsFlower Studio Visual Mockup Specifications

This directory contains the canonical visual mockups approved by the human:
- `mockup-explorer.png` - Explorer Dual-Pane Code & Task Inception View
- `mockup-taskboard.png` - Task Board Kanban & Metrics View

## 1. Global Shell & Top Navigation Bar

The top navigation bar is HORIZONTAL across the entire application width:
- **Far Left Brand:** Purple icon with layered flower, `AgentsFlower`, subtitle `Studio Cockpit v2.17.0`.
- **Horizontal Primary Navigation Tabs:**
  - `Explorer` — Pill button, highlighted with blue border/background when active.
  - `Task Board` — Pill button with task count badge (e.g. `110`), highlighted when active.
  - Sub-navigation links directly next to primary tabs:
    - `Analytics & Roadmap` (bar chart icon)
    - `Knowledge Graph` (AST node icon)
    - `Model Quota Hub` (signal/capacity icon)
    - `Task Contract Creator` (plus circle icon)
    - `Quick Start Guide` (compass icon)
- **Top-level navigation tabs MUST NOT be placed in the left sidebar.**

## 2. Left Sidebar (Active Workspace & Portfolio)

The left sidebar is dedicated strictly to workspace and project tree navigation:
- **Header:** `ACTIVE WORKSPACE` in small tracking font, accompanied by `+ Attach` and `+ New` pill buttons.
- **Multi-Project Accordion Cards:**
  - **Active Workspace Card:**
    - Green square indicator.
    - Name and count: `code - v2.17.0 (110 tasks)`.
    - Caret icon `v` (expanded).
    - Nested file tree:
      - `.agentsflower` (yellow folder icon)
      - `.claude` (purple folder icon)
      - `.github` (gray folder icon)
      - `runbook` (gray folder icon)
      - `src` (gray folder icon)
      - `.gitignore` (orange git icon)
      - `AGENTS.md` (blue markdown icon, glowing border when selected)
  - **Inactive Workspace Cards:**
    - Square checkbox indicator, e.g. `code - v2.17.0 (11 tasks)`, collapse caret `^`.

## 3. Explorer View (Dual-Pane Layout)

When `Explorer` is active in top navigation:
- **Center Pane (Code Viewer):**
  - Top breadcrumbs bar: `src > agentsflower > cli.py > AGENTS.md > ..`
  - Code Editor container:
    - Line numbers column (`1, 2, 3...`)
    - Syntax-highlighted code block with dark editor background (`#111625`).
    - Monospace JetBrains Mono font.
- **Right Pane (Task Inception & AI Copilot Chat):**
  - Header: Task title / action ("Upload Latest") with `+` and panel controls.
  - Chat stream with rich execution cards:
    - User prompt bubble (e.g. "приступай к T-030").
    - Collapsible status line: "Worked for 2m >".
    - Execution status card:
      - Bold announcement: "Задача T-030: Stealth verification harness успешно разблокирована, утверждена в реестре и запущена на исполнение!".
      - Status bullets: Задача, Исполнитель (Devin swe-2-high), Worktree path, Статус (RUNNING Attempt 1).
    - Diff summary widget:
      - "3 files changed +4 -9 >"
      - Colored + / - file badges with paths.
  - Bottom chat bar:
    - Textarea placeholder: "Ask anything, @ to mention, / for actions".
    - Bottom toolbar: `+` action button, model selector dropdown (e.g. `Gemini 1.5 Flash Medium ^` / active model), send button.

## 4. Task Board View (Kanban & Metrics)

When `Task Board` is active in top navigation:
- **Stage Filter Bar:** `All Stages` (active blue pill), `Stage 5`, `Stage 6`, `Stage 7`.
- **Metrics Summary Row:**
  - `110 Total Tasks` (white)
  - `0 In Progress` (amber)
  - `0 In Review` (purple)
  - `81 Completed` (emerald)
- **4 Kanban Columns:**
  - `Ready to Launch (29)` with blue dot
  - `In Progress (0)` with amber dot
  - `Verification / Review (0)` with purple dot
  - `Done & Merged (81)` with green dot
- **Task Cards:** Task ID badge (`T-001`), Stage badge (`Stage 6`), Title text, Role (`Developer`), Tool (`devin`).

## 5. Explorer Interactive Features & Refinements (Mockup 3 / Screenshot 3)

Approved visual enhancements from `mockup-explorer-splitters-tabs.png`:
- **Draggable Vertical Splitters (`||` grip handles):**
  - Gutter 1: between left workspace sidebar and center code viewer.
  - Gutter 2: between center code viewer and right chat pane.
  - Distinct vertical grip icon `||` centered on the divider.
  - Fluid dragging with mouse to resize panels; persists custom widths in `localStorage`.
  - Boundaries: sidebar (220px..450px), chat (320px..650px), code pane flex-shrinks/expands.
- **Editor File Tabs Bar:**
  - Above code viewer: horizontal tabs bar with open files (e.g. `[icon] AGENTS.md ×`, `[icon] Scratchpad ×`).
  - Active tab highlighted with blue/accent border.
  - Clicking file in tree opens a new tab or switches to it.
  - Close button `×` closes tab.
- **Top Navigation Cleanliness:**
  - Strictly 4 core tabs: `Explorer`, `Task Board [N]`, `Analytics & Roadmap`, `Model Quota Hub`.
  - Removed junk tabs (`Task Contract Creator`, `Quick Start`, etc.).
  - Zero horizontal scrollbars (`overflow-x: hidden`).
- **Chat Model Selector:**
  - Interactive pill in chat composer (`Devin swe-2-high ^`) that opens a dropdown to switch models (`swe-2-high`, `gemini-4-argon-high`, `claude-opus-4-6-thinking`, `gpt-5-5-high`, local options).
