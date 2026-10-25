# T-170: Verify Model Quota Hub UI, Auto-Scan, and Interactive Toggles

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-169
Independent check: none
Resume: none
Verifies: T-169 @ <SHA>
Routing exception: human authorized Model Quota Hub UI verification (2026-10-25)

## Goal

Independently verify T-169's UI overhaul of Model Quota Hub: auto-scan on tab switch, skeleton loading, interactive platform and model toggle switches, OpenRouter modal with masked keys, and project isolation.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-169-model-quota-hub-ui.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- nothing

## Acceptance criteria

- [ ] V-01: Switching to `Model Quota Hub` triggers auto-scan and renders live platform cards without DOM or JavaScript errors.
- [ ] V-02: Platform and model toggles interactively update state and persist per project.
- [ ] V-03: OpenRouter connection modal accepts API key, displays masked credentials, and renders fetched models.
- [ ] V-04: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
