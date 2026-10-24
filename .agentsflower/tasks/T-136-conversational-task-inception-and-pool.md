# T-136: Conversational Task Inception, AST Blast Radius, and Task Pool Synthesis from Chat

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: none
Branch: t-136-conversational-task-inception
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-136-conversational-task-inception
Independent check: tester
Resume: 1afb577c9c500ad5d250e22c2127c357dde7b551
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

Outcome: completed
Change: 1afb577c9c500ad5d250e22c2127c357dde7b551 on t-136-conversational-task-inception
Files:
- .agentsflower/studio/index.html - added Research & Inception option to chat header thread selector and Synthesize Tasks from Discussion button in composer
- .agentsflower/studio/studio.css - styled assistant chat bubbles, synthesize button, interactive task pool card, blast radius badge, model tier pills, and batch approve button
- .agentsflower/studio/studio.js - implemented Research vs task context thread switching, task context loading, task pool synthesis invocation, interactive Task Pool Card rendering, and batch ledger registration
- .agentsflower/tools/studio.py - added AST symbol indexing + Graft blast radius calculation, complexity floor vs escalation assessment, task synthesis, pool batch registration, and task context endpoints
- .agentsflower/tests/test_studio.py - added unit tests covering dialogue task pool synthesis, floor vs escalation model routing, Graft blast radius integration, batch registration, task context, and UI markers
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (33 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (525 passed / 0 failed, 4 skipped)
Criteria:
- C-01: pass - chat header thread selector switches between Research & Inception and task threads; evidence: .agentsflower/studio/index.html, .agentsflower/studio/studio.js, .agentsflower/tests/test_studio.py
- C-02: pass - synthesize_tasks_from_chat endpoint generates structured task pool candidates with AST blast radius; evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-03: pass - chat stream renders interactive Task Pool Card with complexity/model assessment and Blast Radius file scope; evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css, .agentsflower/tests/test_studio.py
- C-04: pass - batch registration button and register_task_pool commit synthesized tasks into ledger and generate task files; evidence: .agentsflower/tools/studio.py, .agentsflower/studio/studio.js, .agentsflower/tests/test_studio.py
- C-05: pass - unit test suite in test_studio.py passes cleanly (33 tests); evidence: .agentsflower/tests/test_studio.py
Found, not fixed:
- none
Proposed memory updates:
- none
