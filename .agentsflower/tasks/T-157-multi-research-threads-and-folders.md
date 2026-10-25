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

<!-- Worker writes its outcome below this block -->
