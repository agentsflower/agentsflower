# T-166: Verify Telemetry Fact Tracking and Studio Cost & ROI Dashboard

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-165
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-165

## Goal

Independently verify T-165 (Telemetry fact tracking and Studio Cost & ROI Dashboard) against the T-165 contract:

1. Serve Studio from the T-165 candidate worktree.
2. Verify `/api/analytics/costs` calculations against fixture telemetry and plan files.
3. Verify visual rendering of Cost & ROI Dashboard cards, stage distribution, and task table.
4. Verify responsiveness and calculations accuracy.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-165-telemetry-fact-cost-dashboard.md
- .agentsflower/tools/studio.py
- .agentsflower/studio/studio.js
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

- [ ] V-01: `/api/analytics/costs` returns mathematically verified Plan vs Fact aggregations.
- [ ] V-02: Cost & ROI Dashboard displays summary metrics and task comparison table.
- [ ] V-03: Stage-based cost distribution renders correctly.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
