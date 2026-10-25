# T-177: Persistent Thread Dropdown on Selection: Close Only on Blur, Outside Click, or Escape

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-176
Branch: t-177-persistent-thread-dropdown-on-selection
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-177-persistent-thread-dropdown-on-selection
Independent check: tester
Resume: none
Routing exception: human authorized persistent chat dropdown on thread selection (2026-10-26)

## Goal

Ensure the chat thread selector dropdown remains open and interactive when selecting a chat thread or task, closing only on blur / outside click / Escape:

1. **Keep Dropdown Open on Thread Selection**:
   - In `studio.js`: in `selectThread(id)`:
     - Remove `closeThreadDropdown()`.
     - Update `state.inspectorTaskId = id`.
     - Update active state on `.thread-item` in the dropdown DOM so the clicked thread immediately reflects active styling without collapsing the menu.
     - Call `updateThreadPill()` to refresh the header chip label.
     - Call `renderInspector()` to switch the chat view to the selected thread.
2. **Close Exclusively on Focus Loss, Outside Click, or Escape**:
   - The dropdown must remain visible while the user interacts within it (clicking threads, expanding/collapsing folders, searching, adding folders).
   - The dropdown closes ONLY when:
     - The user clicks anywhere outside `#threadSelector` (`document.addEventListener('click', ...)`).
     - Focus leaves the `#threadSelector` component (`focusout` event where `relatedTarget` is outside `#threadSelector`).
     - The user presses `Escape`.
     - The user clicks `#threadPill` to toggle the selector closed.
3. **Contract Tests**:
   - In `test_studio.py`: add unit tests asserting that selecting a thread does not close the dropdown, and that closing is restricted to outside click, escape, and blur.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- none

## Acceptance criteria

- [ ] C-01: Selecting a research thread or implementation task in `#threadDropdown` switches the active chat without closing the dropdown.
- [ ] C-02: The selected item reflects active styling (`.thread-item.active`) while the dropdown remains open.
- [ ] C-03: Dropdown closes when clicking outside `#threadSelector`, pressing Escape, or clicking `#threadPill`.
- [ ] C-04: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Result

<!-- Worker writes outcome below -->
