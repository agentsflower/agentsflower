# Task: T-180 - Verify Thread Dropdown Stays Open on Header Toggles & Task Selection

## Context

Independent verification of T-179: ensuring that clicking section headers (Researches, Implementations), stage headers, and task items inside `#threadDropdown` does NOT close the dropdown.

## Goal

Independently verify that `#threadDropdown` remains open when toggling sections/stages and selecting tasks, and closes only on outside click, Escape, or `#threadPill` toggle.

## Read first

- .agentsflower/tasks/T-179-fix-thread-dropdown-premature-collapse.md
- .agentsflower/studio/studio.js
- .agentsflower/studio/index.html
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Section headers (`Researches`, `Implementations`) toggle without collapsing `#threadDropdown`.
- [ ] V-02: Stage headers toggle without collapsing `#threadDropdown`.
- [ ] V-03: Clicking task items switches active task in inspector without collapsing `#threadDropdown`.
- [ ] V-04: `#threadDropdown` closes only when clicking outside `#threadSelector`, pressing Escape, or clicking `#threadPill`.
- [ ] V-05: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-06: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
