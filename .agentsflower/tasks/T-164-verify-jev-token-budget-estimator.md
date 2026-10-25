# T-164: Verify Jev Token & Budget Estimator (Plan Model)

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-163
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-163

## Goal

Independently verify T-163 (Jev token and budget estimation for task synthesis) against the T-163 contract:

1. Serve Studio from the T-163 candidate worktree.
2. Exercise `POST /api/task/synthesize` and verify presence and accuracy of `planned_tokens` and `planned_cost_usd`.
3. Verify visual rendering of budget metrics in Task Pool Card.
4. Verify `T-NNN.plan.json` generation upon registration.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-163-jev-token-budget-estimator.md
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

none

## Do not touch

- *

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: `/api/task/synthesize` returns mathematically consistent `planned_tokens` and `planned_cost_usd`.
- [ ] V-02: Task Pool Card renders token and USD badges.
- [ ] V-03: `T-NNN.plan.json` files are generated on registration.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
