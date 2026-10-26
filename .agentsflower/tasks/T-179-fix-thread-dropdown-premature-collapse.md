# T-179: Fix Thread Dropdown Premature Collapse on Collapsible Headers & Task Items

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-178
Branch: t-179-fix-thread-dropdown-premature-collapse
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-179-fix-thread-dropdown-premature-collapse
Independent check: tester
Resume: none
Routing exception: human authorized thread dropdown collapse fixes (2026-10-26)

## Context

In AgentsFlower Studio, the thread selector dropdown (`#threadDropdown`) provides navigation between Researches (with folders) and Implementations (grouped by stages).
However, clicking on collapsible headers (`Researches`, `Implementations`, `Stage XX`) or task items causes the entire dropdown to prematurely collapse/close.

Root Cause:
1. When clicking collapsible headers, `toggleThreadCollapse` calls `fillThreadList` which wipes `list.innerHTML = ''`, destroying the clicked element from the DOM during event bubbling. The bubbling click event reaches `document.addEventListener('click')`, where `threadSelector.contains(ev.target)` evaluates to `false` because `ev.target` is now a detached DOM node. This triggers `closeThreadDropdown()`.
2. Any unhandled click inside `#threadDropdown` bubbles to `document` and risks triggering outside-click handlers or focusout edge cases. Adding `stopPropagation()` on `#threadDropdown` (or checking `ev.composedPath().includes(threadSelector)`) prevents clicks inside the dropdown from ever being misidentified as outside clicks.
3. Bumping `studio.js?v=6` in `index.html` prevents stale browser caching of script logic.

## Goal

Ensure that clicking collapsible headers (Researches, Implementations, Stages, Folders) and clicking task items keeps `#threadDropdown` open and interactive, closing ONLY on actual outside clicks, Escape, or clicking `#threadPill`.

## Read first

- .agentsflower/studio/studio.js
- .agentsflower/studio/index.html
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/studio.js
- .agentsflower/studio/index.html
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- none

## Acceptance criteria

- [ ] C-01: Clicking section headers (`Researches`, `Implementations`) toggles collapsed state without closing `#threadDropdown`.
- [ ] C-02: Clicking stage headers (`Stage 05`, etc.) toggles collapsed state without closing `#threadDropdown`.
- [ ] C-03: Clicking task items (`.thread-item`) switches active task in inspector and updates `.active` styling without closing `#threadDropdown`.
- [ ] C-04: `#threadDropdown` closes only when clicking outside `#threadSelector`, pressing Escape, or clicking `#threadPill`.
- [ ] C-05: `index.html` cache-busting version bumped to `studio.js?v=6`.
- [ ] C-06: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Result

<!-- Worker writes outcome below -->
Outcome: completed
Change: 570b0d2 on t-179-fix-thread-dropdown-premature-collapse
Files:
- .agentsflower/studio/studio.js - setupThreadSelector adds threadDropdown.addEventListener('click', ev => ev.stopPropagation()); clicks inside the dropdown (incl. headers detached mid-bubble by fillThreadList) no longer reach the document outside-click handler
- .agentsflower/studio/index.html - cache-busting bump studio.js?v=5 -> studio.js?v=6
- .agentsflower/tests/test_studio.py - new class TestThreadDropdownInsideClicks (3 contract tests)
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (118 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` (whole suite) -> pass (622 ran, 4 skipped, 0 failed)
Criteria:
- C-01: pass - section headers (Researches, Implementations) go buildCollapsibleHeader -> toggleThreadCollapse -> fillThreadList rebuild; the re-render detaches the clicked node mid-bubble but the event still bubbles along the precomputed path to threadDropdown, where the new guard stops it before document; test_inside_clicks_stop_before_document_handler in .agentsflower/tests/test_studio.py
- C-02: pass - stage headers use the same data-collapse-key path via buildStageGroup; test_toggle_collapse_does_not_close_dropdown asserts toggleThreadCollapse contains no closeThreadDropdown call
- C-03: pass - .thread-item click calls selectThread which sets state.inspectorTaskId and toggles .active in place via data-thread match (T-177), and the click is stopped at threadDropdown so the outside-click handler never fires
- C-04: pass - close paths unchanged: document click on !threadSelector.contains(ev.target), Escape in onThreadKeydown, threadPill toggle, focusout to an outside element; TestPersistentThreadDropdown.test_close_triggers_outside_click_escape_and_blur still green
- C-05: pass - .agentsflower/studio/index.html serves studio.js?v=6; test_studio_js_cache_busting_version
- C-06: pass - checks command verbatim green, 118 tests
Found, not fixed:
- clicks inside #threadDropdown now also skip other document-level click handlers (e.g. the model-selector outside-close); consistent with the existing stopPropagation on .thread-sec-btn and the search input
Proposed memory updates:
- none
