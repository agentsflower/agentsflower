# T-130: AgentsFlower Studio: Multi-Project Explorer, Global Context Sync, and Explicit Authorization Gate

Role: developer
Tool: devin
Model: swe-2-max
Stage: 7
Depends on: T-128, T-129
Branch: t-130-studio-multiproject-explorer
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-130-studio-multiproject-explorer
Independent check: tester
Resume: none
Routing exception: human authorized via AgentsFlower Studio (2026-10-24): devin swe-2-max assigned for multi-project architectural synchronization

## Goal

Align AgentsFlower Studio with the dual-pane IDE/Explorer mockups and resolve the project-state disconnect across all cockpit sections:
1. **Sidebar Multi-Project Accordion & File Trees:** Transform the project selector from a plain dropdown into an interactive accordion listing all projects (current, attached, and newly scaffolded). Expanding a project dynamically loads its file and folder hierarchy via `/api/project/tree`.
2. **Integrated `Explorer` Code Viewer Tab:** Implement the `Explorer` topbar view matching the reference design:
   - File breadcrumbs and syntax-highlighted code viewer in the center area.
   - Live Task Context Inspector in the right panel showing contract metadata, acceptance criteria checklists, and git diff summaries.
3. **Global Project Synchronization (Zero-Disconnect):** Ensure switching the active project updates the entire application context synchronously:
   - Task Board (`/api/tasks?project=...`).
   - Analytics & Roadmap (`/dashboard/out/?project=...` with project-scoped rebuilds).
   - Knowledge Graph (Graft AST queries executed in the active project directory).
   - Task Contract Creator (scoping target files and tasks to the active project).
4. **Explicit Authorization Gate for Scaffolding:** Any project creation or attachment without AgentsFlower must display an `[Uninitialized]` status and explicitly ask for human authorization before running `install.py` (no implicit or background installation).
5. **Secure Backend APIs:** Add `/api/project/tree` and `/api/file/read` in `studio.py` with strict path traversal protection.

## Read first

- .agentsflower/docs/ai-handoff-protocol.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py

## Allowed files

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py
- .agentsflower/state/tasks.md
- .agentsflower/state/current-step.md

## Do not touch

- All other files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] C-01: Sidebar displays multi-project accordion with file tree expansion for each registered workspace.
- [ ] C-02: `Explorer` tab provides center-pane code viewer and right-pane task context inspector matching the reference mockup.
- [ ] C-03: Switching active project updates Kanban, Analytics & Roadmap, Knowledge Graph, and Contract Creator without stale state.
- [ ] C-04: Project initialization requires explicit user consent via authorization modal (no background install).
- [ ] C-05: Backend `/api/project/tree` and `/api/file/read` endpoints validate directory boundaries against path traversal.
- [ ] C-06: Autonomous regression suite passes cleanly: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Change: 1d2aafe on t-130-studio-multiproject-explorer
Files:
- .agentsflower/tools/studio.py - new endpoints /api/project/tree, /api/file/read, /api/project/git; resolve_known_project + safe_under boundary validation; authorized:true required on project create/update; project-scoped graft, dashboard build and dashboard static serving; criteria payload in /api/tasks
- .agentsflower/studio/index.html - project accordion replaces dropdown, Explorer view (tree/code/inspector), authorization modal, active-project chip, creator target hint
- .agentsflower/studio/studio.css - accordion, file tree, explorer grid, code viewer, inspector and modal styles
- .agentsflower/studio/studio.js - renderProjectAccordion, lazy fetchTree/renderTreeNodes, switchProject global broadcast, Explorer file open + breadcrumbs + highlightCode, Task Context Inspector, requestInstallAuthorization gate on all install paths
- .agentsflower/tests/test_studio.py - 18 HTTP-level tests for the new endpoints, traversal protection, auth gate and criteria payload
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (18 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (510 passed / 0 failed, 4 skipped)
Criteria:
- C-01: pass - sidebar accordion lists every registered workspace with expandable lazy file tree: .agentsflower/studio/index.html #projectAccordion, studio.js renderProjectAccordion/fetchTree/renderTreeNodes, backend /api/project/tree in .agentsflower/tools/studio.py
- C-02: pass - Explorer view view-explorer with workspace tree, breadcrumb + syntax-highlighted code viewer (highlightCode, /api/file/read), and right-pane Task Context Inspector (contract metadata, criteria checklist, git diff via /api/project/git)
- C-03: pass - switchProject() broadcasts the active project: /api/tasks, /api/status, dashboard iframe ?project= plus project-scoped /api/dashboard/build, graft query/impact and task creation all carry the selected project
- C-04: pass - every install path routes through the authorization modal (requestInstallAuthorization); backend returns 403 requires_authorization for create/update without authorized:true, enforced before any mkdir/install run
- C-05: pass - /api/project/tree and /api/file/read resolve the project against the registered workspace set and enforce safe_under (absolute paths, .., NUL, symlink escapes rejected); unregistered projects get 403
- C-06: pass - full suite ran green as listed in Checks
Found, not fixed:
- /api/status and /api/tasks still accept an arbitrary existing directory for read-only ledger/status reads (pre-existing behavior, out of scope); new file/git/graft endpoints require a registered project
- The referenced dual-pane IDE/Explorer mockup file is not in the repository; the view implements the layout described in the Goal text
- Task criteria checkboxes in the inspector are read-only by design (contract state, not UI toggles)
Proposed memory updates:
- Studio now exposes file-content and git-summary APIs bound to registered workspaces only; future file-write or execute endpoints should reuse resolve_known_project + safe_under
