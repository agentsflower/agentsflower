# T-132: Studio UI Pixel-Perfect Implementation from Visual Mockup Contract

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Branch: t-132-studio-pixel-perfect-mockup
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-132-studio-pixel-perfect-mockup
Independent check: tester
Resume: none
Routing exception: human authorized visual mockup contract execution (2026-10-24)

## Goal

Pixel-perfect implementation of AgentsFlower Studio matching the exact visual mockups provided by the human:

1. **Top Navigation Bar:**
   - Brand block at top-left: purple gradient icon with layered flower, title `AgentsFlower`, subtitle `Studio Cockpit v2.17.0`.
   - Top horizontal navigation:
     - Primary pill button: `Explorer` (active blue glow when selected).
     - Primary pill button: `Task Board` with task count badge (e.g. `110`).
     - Sub-navigation links with icons: `Analytics & Roadmap`, `Knowledge Graph`, `Model Quota Hub`, `Task Contract Creator`, `Quick Start Guide`.
2. **Left Sidebar (Active Workspace & Portfolio):**
   - Header: `ACTIVE WORKSPACE` in small uppercase tracking.
   - Action buttons: `+ Attach` and `+ New`.
   - Multi-project accordion items:
     - Active item: green square indicator, name format `code - v2.17.0 (110 tasks)`, expand caret `v`.
     - Nested file tree: colored icons (yellow folder for `.agentsflower`, purple folder for `.claude`, gray folders, orange git for `.gitignore`, blue document for `AGENTS.md` with active highlighted border).
     - Inactive items: checkbox square, name `code - v2.17.0 (11 tasks)`, collapse caret `^`.
3. **Explorer View (Center & Right Dual-Pane):**
   - Center Code Viewer:
     - Top breadcrumbs bar: `src > agentsflower > cli.py > AGENTS.md > ..`
     - Editor container: line numbers column (`1, 2, 3...`), syntax-highlighted code block, monospace typography, dark `#111625` editor background.
   - Right Task Inception & Chat Cockpit:
     - Header: Task title / action ("Upload Latest") with `+` and panel controls.
     - Chat stream with rich SDLC execution cards:
       - User prompt bubble (e.g. "приступай к T-030").
       - Collapsible status line: "Worked for 2m >".
       - Execution status block: "Задача T-030: ... успешно разблокирована, утверждена в реестре и запущена на исполнение!".
       - Status metadata bullets: Task ID, Role, Tool (`Devin swe-2-high`), Worktree path, Status (`RUNNING Attempt 1`).
       - Diff summary widget: "3 files changed +4 -9 >" with green/red additions/deletions badges and clickable file paths.
     - Bottom chat bar:
       - Textarea placeholder: "Ask anything, @ to mention, / for actions".
       - Bottom toolbar: `+` action button, model selector pill (e.g. `Gemini 1.5 Flash Medium ^` / active model), send button.
4. **Task Board View (Matching Mockup 2):**
   - Stage filter pills: `All Stages` (active blue), `Stage 5`, `Stage 6`, `Stage 7`.
   - Metrics summary row:
     - `110 Total Tasks` (white)
     - `0 In Progress` (amber)
     - `0 In Review` (purple)
     - `81 Completed` (emerald)
   - 4 Kanban columns:
     - `Ready to Launch (29)` with blue dot
     - `In Progress (0)` with amber dot
     - `Verification / Review (0)` with purple dot
     - `Done & Merged (81)` with green dot
   - Kanban cards: Task ID (`T-001`), Stage badge (`Stage 6`), Title, Role (`Developer`), Tool (`devin`).

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.css
- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py

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

- [ ] C-01: Top navigation matches mockup with `Explorer`, `Task Board (N)` pills and sub-links.
- [ ] C-02: Left sidebar renders `ACTIVE WORKSPACE`, `+ Attach`, `+ New`, and expandable project accordion with file tree.
- [ ] C-03: Explorer dual-pane renders center code viewer with line numbers and breadcrumbs, and right chat cockpit with diff cards.
- [ ] C-04: Task Board renders stage filter pills, big metric summary numbers, and 4 Kanban columns with task cards.
- [ ] C-05: All unit tests in `test_studio.py` pass without regressions.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: 14dcc0f on t-132-studio-pixel-perfect-mockup
Files:
- .agentsflower/studio/index.html - top horizontal nav bar (brand, Explorer/Task Board pills with task-count badge, five icon sub-links, search/New Task); slim sidebar (ACTIVE WORKSPACE, + Attach/+ New, project accordion); Explorer reduced to dual pane (code viewer + Task Inception chat cockpit); legacy topbar/breadcrumbs and separate explorer tree/inspector panes removed
- .agentsflower/studio/studio.css - topnav/pill/link styles with active blue glow, sidebar accordion square indicators and caret styles, name-version-taskcount format, file-tree icon tints (.agentsflower yellow, .claude purple, .gitignore orange git, .md blue doc, selected border), #111625 code viewer with .cl/.ln line-number gutter, full chat cockpit styles (bubbles, worked line, exec card, diff badges/files, composer, model pill, send button)
- .agentsflower/studio/studio.js - accordion markup (square, "name - vX (N tasks)", v/^ carets), per-name file icons, auto-expand active project, line-numbered code render with ">" breadcrumbs and trailing "..", chat stream render (user bubble, "Worked for 2m" toggle, status text, Task ID/Role/Tool/Worktree/Status bullets, diff widget driven by /api/project/git), model pill from task tool+model, composer send/Enter, header controls
- .agentsflower/tools/studio.py - get_tasks_data parses task-file Branch/Worktree/Model header fields into the tasks payload
- .agentsflower/tests/test_studio.py - added TestStudioShell (topnav/sidebar/chat markers on GET /) and test_tasks_include_dispatch_header_fields
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> fail (511 passed / 1 failed / 1 error / 4 skipped); both failures are test_run_task.py environment flakes (fixture notepad.exe child PID 38452 still running between tests -> launch refused; temp runtime file PermissionError), unrelated to studio files; both tests pass in isolated rerun (2 passed in 61.4s)
Criteria:
- C-01: pass - .agentsflower/studio/index.html: header.topnav with brand block, .nav-pill Explorer and Task Board + #taskTotalBadge, .nav-link items with SVG icons for Analytics & Roadmap, Knowledge Graph, Model Quota Hub, Task Contract Creator, Quick Start Guide
- C-02: pass - .agentsflower/studio/index.html + studio.js renderProjectAccordion: ACTIVE WORKSPACE label, + Attach/+ New buttons, .project-acc-box square (emerald fill active, checkbox inactive), "name - vX (N tasks)" name, v caret expanded / ^ collapsed, nested .project-acc-tree file tree with tinted icons
- C-03: pass - .agentsflower/studio/index.html + studio.js openExplorerFile/renderInspector: center .explorer-code-pane with crumb "> " breadcrumbs + .cl/.ln line numbers + syntax tokens on #111625; right .explorer-chat-pane with header (+ and panel controls, task select), chat-bubble user, collapsible "Worked for 2m", .exec-status-text, exec-meta bullets (Task ID/Role/Tool/Worktree/Status), exec-diff widget with +add/-del badges and clickable file paths, chat-composer textarea + toolbar (+ / model pill / send)
- C-04: pass - .agentsflower/studio/index.html view-kanban: stage filter pills (All Stages active), metrics row Total/In Progress (amber)/In Review (purple)/Completed (emerald), 4 kanban columns with colored dots, task cards with T-ID, Stage badge, title, role, tool
- C-05: pass - all 21 tests in test_studio.py pass (see Checks), including the new shell/payload tests
Found, not fixed:
- test_run_task.py: orphaned-descendant fixture child (notepad.exe, PID 38452) outlives its test under a full-suite run, failing the next launch test and a runtime-file read; passes in isolation - pre-existing environment flake outside this task's scope; the leftover process may still be running
- Code viewer line numbers force per-line highlighting; multi-line tokens (e.g. triple-quoted strings) are not colored across the break (trade-off for the gutter)
Proposed memory updates:
- known-issues.md (2026-10-24): test_run_task.py orphaned fixture process can leak between tests on Windows (notepad.exe child); consider hardening fixture teardown or serializing those tests
