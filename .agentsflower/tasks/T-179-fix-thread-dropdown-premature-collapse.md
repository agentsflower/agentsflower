# Task: T-179 - Fix Thread Dropdown Premature Collapse on Collapsible Headers & Task Items

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
