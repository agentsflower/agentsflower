# T-155: Studio Hierarchical Thread Switcher UI: Researches & Implementations

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-154
Branch: t-155-studio-hierarchical-thread-dropdown
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-155-studio-hierarchical-thread-dropdown
Independent check: tester
Resume: none

## Goal

Replace the flat select dropdown in the Studio chat header with an interactive two-section hierarchical accordion matching the user's reference mockup:

1. **Collapsible Header Sections**:
   - Section 1: `🔍 Researches` (accent header `#134e9e`, item count badge, `+` create action, collapse caret).
   - Section 2: `Implementations` (accent header `#134e9e`, task count badge, collapse caret).
2. **Nested Stages in Implementations**:
   - Inside `Implementations`, group tasks by sequential stage (`Stage 01`, `Stage 02`...).
   - Each Stage group is collapsible, showing stage title and task count.
   - Tasks display formatted identity: `T-NNN — Short Title`.
3. **Selection State & Keyboard Navigation**:
   - Clicking an item sets `state.inspectorTaskId` and closes popup.
   - Active thread highlighted with blue accent border and pill.
   - Full keyboard accessibility (Arrow keys, Enter, Esc).
4. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing DOM elements, stage grouping logic, and click handlers.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8905 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Thread selector renders two distinct collapsible sections: `🔍 Researches` and `Implementations`.
- [ ] C-02: Tasks in `Implementations` are grouped under collapsible `Stage XX` subheaders.
- [ ] C-03: Visual styling matches dark theme (`#060a12`, accent `#134e9e`) with smooth accordion transitions.
- [ ] C-04: Clicking any research or task item switches active chat thread.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
