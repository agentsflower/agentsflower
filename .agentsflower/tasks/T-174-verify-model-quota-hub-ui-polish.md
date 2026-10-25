# T-174: Verify Model Quota Hub UI Polish, Responsive Layout, and Cockpit Cleanup

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-173
Independent check: none
Resume: none
Routing exception: human authorized Model Quota Hub UI verification (2026-10-25)

## Goal

Independently verify T-173's visual polish and layout fixes across Model Quota Hub, Analytics Sub-Tabs, Chat Task Selector, and Project Name Disambiguation.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-174.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-173-model-quota-hub-ui-polish.md
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

- [ ] V-01: Model Quota Hub cards render cleanly with zero element collisions between title, toggle switch, and status badge on cards at 320px+ width.
- [ ] V-02: Analytics view strictly contains the 3 original subtabs (`Tasks & Overview`, `Gantt & Dependency Graph`, `Roadmap & Milestones`); Cost & ROI dashboard button and pane are removed.
- [ ] V-03: Multiple projects sharing names like `code` display disambiguated parent prefixes in the project list.
- [ ] V-04: Chat thread selector opens a clean searchable task dropdown.
- [ ] V-05: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-06: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests
