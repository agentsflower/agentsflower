# T-157: Multi-Research Threads, Folders, and Context Forking

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-156
Branch: t-157-multi-research-threads-and-folders
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-157-multi-research-threads-and-folders
Independent check: tester
Resume: none

## Goal

Provide persistent multi-research management in Studio with folder/category grouping and context referencing:

1. **Multi-Research Lifecycle**:
   - `+` button in `🔍 Researches` creates a new research thread: auto-named `Task Research - 001`, `002`... with inline rename.
   - Per-research chat thread storage persisted in `.agentsflower/state/research/<id>.json`.
2. **Folders & Categorization**:
   - Allow grouping research threads into logical categories/folders (e.g. `Architecture`, `UI Design`, `Infrastructure`).
   - Collapsible folder headers in the Researches dropdown section.
3. **Cross-Referencing & Forking**:
   - When creating or prompting in a research thread, allow linking to previous research (`Fork from Research-001`) or completed tasks (`Ref: T-013`).
   - Injected references automatically append relevant summaries to prompt context.
4. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing research creation, persistence, folder grouping, and context forking.

## Read first

- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8907 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: User can create multiple named research threads with isolated chat histories.
- [ ] C-02: Research threads can be organized into collapsible folders/categories.
- [ ] C-03: Chat histories persist to disk in `.agentsflower/state/research/`.
- [ ] C-04: Cross-referencing previous research or tasks injects summary context into the active thread.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: 38495f2e3923371c06d19539633ef2533906f9d2 on t-157-multi-research-threads-and-folders
Files:
- .agentsflower/tools/studio.py - research thread store (research_store_dir, create/list/load/save/update under .agentsflower/state/research/<id>.json, auto-name Task Research - NNN, folder/refs/parent fields), reference_summary + extract_context_refs injected into format_chat_prompt, maybe_persist_research_turn on chat success, endpoints GET /api/research/list, GET /api/research/thread, POST /api/research/create, POST /api/research/update
- .agentsflower/studio/studio.js - researchMeta state + loadResearchThreads on loadTasks, addResearchThread via /api/research/create with Task Research - NNN naming, dblclick inline rename (startRenameThread), collapsible folder groups (buildFolderGroup) in the Researches section, inspector folder select + ref chips + fork-from select (renderResearchControls), extractRefsFromText for Ref:/Fork from tokens, refs + persist sent on /api/chat
- .agentsflower/studio/studio.css - .thread-folder-* collapsible styles, .thread-rename-input, .ref-chip/.ref-chip-x, .research-ctl-* control styles
- .agentsflower/tests/test_studio.py - added TestResearchThreads (7 tests): auto-naming + persistence, rename/folder grouping, update validation, chat history persistence, opt-in persist guard, ref/context-summary injection incl. inline tokens, fork_from linking, UI markers; store redirected to a temp dir so tests never write real project state
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (70 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (574 passed / 4 skipped / 0 failed)
Criteria:
- C-01: pass - evidence: .agentsflower/tools/studio.py, .agentsflower/studio/studio.js, .agentsflower/tests/test_studio.py
- C-02: pass - evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css, .agentsflower/tools/studio.py
- C-03: pass - evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-04: pass - evidence: .agentsflower/tools/studio.py, .agentsflower/studio/studio.js
- C-05: pass - evidence: .agentsflower/tests/test_studio.py, .agentsflower/tasks/.runtime/T-157.check1_test_studio.txt, .agentsflower/tasks/.runtime/T-157.check2_full_suite.txt
Found, not fixed:
- .agentsflower/state/research/ is not in .gitignore; live research JSON written by real Studio sessions will appear as untracked files. Adding the ignore rule is outside Allowed files.
- Pool-card items in research threads are not persisted to disk (only role/content messages are); deliberate scope choice, not a defect.
Proposed memory updates:
- none
