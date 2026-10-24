# T-136: Conversational Task Inception, AST Blast Radius, and Task Pool Synthesis from Chat

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: none
Branch: t-136-conversational-task-inception
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-136-conversational-task-inception
Independent check: tester
Resume: none
Routing exception: human authorized argon model for high-reasoning conversational task synthesis (2026-10-24)

## Goal

Transform the Studio Explorer Chat Cockpit into an autonomous conversational task inception engine, completely replacing the manual contract wizard:

1. **Research & Ideation Chat Threads:**
   - Add a `+` / Thread switcher in the chat header to toggle between:
     - `🔍 Research & Inception` (general architecture, ideation, and project-level queries)
     - Specific task threads (`T-001`, `T-134`, etc.)
   - Research thread allows free-form dialogue with the selected model (Argon / swe-2 / Claude).

2. **Automated Task Pool Synthesis from Chat:**
   - Add a prominent action button in the chat or composer: `✨ Synthesize Tasks from Discussion`.
   - Endpoint `/api/task/synthesize`:
     - Analyzes conversation history and proposed deliverables.
     - Leverages local Graft AST (`graft.py`) to inspect repository symbols and calculate affected files (Blast Radius).
     - Decomposes work into atomic, verifiable task contracts (Title, Stage, Role, Effort, Allowed Files, Acceptance Criteria).
     - Assesses complexity per task (Floor `swe-2-high` vs Escalation `gemini-4-argon-high`).

3. **Interactive Task Pool Card in Chat Stream:**
   - Renders a rich execution card in chat displaying the synthesized tasks:
     - Task ID, Title, Stage badge, Effort badge, and Assigned Model pill.
     - Collapsible preview of proposed Allowed Files and Acceptance Criteria (`C-01:`, `C-02:`).
     - Button `Approve & Register Pool in Ledger`: atomic batch registration into `.agentsflower/state/tasks.md` and automated Task File generation.

4. **Task Context Threading & Discussion:**
   - Selecting a task thread in the dropdown loads its specific contract, allowed files, recent log, and diffs, allowing focused discussion and adjustments directly in chat.

## Read first

- .agentsflower/mockups/README.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.css
- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tools/graft.py
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

- [ ] C-01: Chat header supports switching between Research/Inception thread and specific task threads.
- [ ] C-02: Endpoint `/api/task/synthesize` generates structured task pool candidates from dialogue context.
- [ ] C-03: Chat stream renders an interactive Task Pool Card with complexity/model assessment and Blast Radius file scope.
- [ ] C-04: Batch registration button commits synthesized tasks into ledger and generates task files.
- [ ] C-05: Unit test suite in `test_studio.py` passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
