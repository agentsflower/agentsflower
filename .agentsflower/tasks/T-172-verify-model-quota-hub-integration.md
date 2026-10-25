# T-172: Verify End-to-End Model Quota Hub Project Filtering and Fallback Guards

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-171
Independent check: none
Resume: none
Verifies: T-171 @ <SHA>
Routing exception: human authorized Model Quota Hub integration verification (2026-10-25)

## Goal

Independently verify T-171's end-to-end integration: ensuring disabled platforms and models are cleanly filtered out of Studio composer and task creation workflows.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-171-model-quota-hub-integration.md
- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- nothing

## Acceptance criteria

- [ ] V-01: Verifies that deactivating models in Model Quota Hub prevents them from showing in the chat composer dropdown.
- [ ] V-02: Verifies graceful fallback and warning badges when selected models become unauthenticated.
- [ ] V-03: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
