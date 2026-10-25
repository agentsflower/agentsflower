# T-178: Verify Persistent Thread Dropdown Behavior

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-177
Independent check: none
Resume: none
Routing exception: human authorized persistent chat dropdown verification (2026-10-26)

## Goal

Independently verify T-177's persistent dropdown behavior: thread selection switches active chat without closing the menu, and the dropdown closes only on blur, outside click, Escape, or toggle pill click.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-178.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-177-persistent-thread-dropdown-on-selection.md
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Selecting a thread in `#threadDropdown` switches active thread and updates `.thread-item.active` without collapsing the dropdown.
- [ ] V-02: Dropdown closes when clicking outside `#threadSelector`, pressing Escape, or clicking `#threadPill`.
- [ ] V-03: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-04: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests
