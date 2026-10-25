# T-176: Verify Chat Thread Selector, Folder Grouping, Project Isolation, and Inactive Probing Bypass

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-175
Independent check: none
Resume: none
Routing exception: human authorized chat thread selector folder grouping and per-project capacity probing verification (2026-10-25)

## Goal

Independently verify T-175's implementation of the two-section thread selector with folder grouping, per-project scoping of researches and tasks, and CLI probe skipping for deactivated platforms.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-176.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-175-chat-thread-selector-folders-and-project-isolation.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Thread selector dropdown displays two distinct accented sections: `Researches` and `Implementations`.
- [ ] V-02: Researches section groups items under collapsible folders (`📁 <Folder>`) and supports creating folders.
- [ ] V-03: Implementations section cleanly groups tasks by stage with `T-XXX — Title` formatting and status pills.
- [ ] V-04: Research threads and tasks strictly reload per project without leaking across workspace boundaries.
- [ ] V-05: Deactivated platforms in `project-models.json` bypass CLI subprocess probes during capacity scanning.
- [ ] V-06: Analytics toolbar includes "Cost & ROI Dashboard" subtab displaying project-scoped Plan vs Fact telemetry.
- [ ] V-07: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-08: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests
