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
Outcome: completed
Change: d110261 on t-177-persistent-thread-dropdown-on-selection
Files:
- .agentsflower/studio/studio.js - selectThread no longer calls closeThreadDropdown()/renderThreadDropdown(); toggles .active on .thread-item[data-thread] in place; new focusout listener on #threadSelector closes only when relatedTarget is a real element outside it
- .agentsflower/tests/test_studio.py - new class TestPersistentThreadDropdown (3 contract tests)
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (115 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` (whole suite, pre-commit) -> 619 ran, 1 error: test_scenarios.test_scenario_quota_limit_recovery_simulated PermissionError on temp .runtime\T-001.json - documented Windows temp-fixture flake (known-issues 2026-10-25), passes on isolated rerun, unrelated to this change
Criteria:
- C-01: pass - selectThread in .agentsflower/studio/studio.js sets state.inspectorTaskId and calls updateThreadPill()+renderInspector() without closeThreadDropdown; test_select_thread_keeps_dropdown_open asserts it
- C-02: pass - selectThread toggles .thread-item.active in place via classList.toggle on data-thread match; styling exists in studio.css .thread-item.active; test_select_thread_marks_active_item_in_place
- C-03: pass - document click handler closes on !threadSelector.contains(ev.target); Escape handled in onThreadKeydown and pill keydown; threadPill click toggles .open closed; focusout closes only when relatedTarget is a concrete element outside #threadSelector; test_close_triggers_outside_click_escape_and_blur
- C-04: pass - checks command green, 115 tests
Found, not fixed:
- focusout ignores null relatedTarget on purpose: window blur, detached nodes after renderThreadDropdown rebuild, and the prompt() dialog in addResearchFolder fire blur/focusout with no relatedTarget; closing there would violate the "stays open while adding folders" requirement. Plain outside clicks still close via the document click listener.
- + New thread flow (addResearchThread -> selectThread -> chatInput.focus()) now leaves the dropdown open per the persistence contract; previously selectThread closed it.
Proposed memory updates:
- none
