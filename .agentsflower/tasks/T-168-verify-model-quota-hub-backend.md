# T-168: Verify Model Quota Hub Backend Engine and Secure Provider Integration

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-167
Independent check: none
Resume: none
Verifies: T-167 @ <SHA>
Routing exception: human authorized Model Quota Hub verification (2026-10-25)

## Goal

Independently verify T-167's dynamic CLI probing, per-project activation/deactivation persistence, OpenRouter provider fetching, and secret storage hygiene.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-167-model-quota-hub-backend.md
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py
- .gitignore

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- nothing

## Acceptance criteria

- [ ] V-01: Probing `/api/capacity/probe` dynamically scans `codex`, `devin`, `claude`, `agy`, and `ollama` with live model discovery.
- [ ] V-02: Adding an OpenRouter provider with an API key dynamically fetches live models; keys are stored securely outside Git and masked in outputs.
- [ ] V-03: Per-project toggles accurately enable/disable platforms and individual models independently across different project roots.
- [ ] V-04: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
