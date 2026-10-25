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
Verifies: T-165 @ 30bd454f3ba1418a92067fb2b94ec87ce0f7770d

## Goal

Independently verify T-165 (Telemetry fact tracking and Studio Cost & ROI Dashboard) against the T-165 contract:

1. Serve Studio from the T-165 candidate worktree.
2. Verify `/api/analytics/costs` calculations against fixture telemetry and plan files.
3. Verify visual rendering of Cost & ROI Dashboard cards, stage distribution, and task table.
4. Verify responsiveness and calculations accuracy.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

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

Outcome: completed
Verdict: pass

Served Studio from the T-165 candidate worktree on port 8915 and verified all
four criteria independently. Endpoint math was checked against a synthetic
fixture project (4 tasks, 2 stages, mixed explicit/derived pricing, free local
model, missing-telemetry and empty-project fallbacks): 57 assertions, all
matching hand-computed values. Real main-repo telemetry was also traced to
source: T-153's reported 4949 in / 904 out / 5853 total tokens decompose into
jev route usage (4949/341) plus the log-size estimate (2253//4=563), and
5853 x $2.5/1M = $0.014632 as returned. UI rendering was verified by running
the real renderCostDashboard (extracted from studio.js) in Node over a DOM stub
fed the fixture API response: 35 assertions covering the four summary cards,
stage filter options, stacked stage bar, dual plan/fact distribution rows,
stage-grouped task table, filter behavior and empty-state fallbacks all pass.
The served page exposes every required element and the task table header reads
exactly "Stage Task ID Title Model Plan ($) Fact ($) Delta (%) Status".
Unregistered project paths return 403.

Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (87 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (591 passed / 0 failed, 4 skipped)

Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-166.evidence/T-166.math_check.txt .agentsflower/tasks/.runtime/T-166.evidence/T-166.costs_fixture_response.json .agentsflower/tasks/.runtime/T-166.evidence/T-166.costs_live_response.json
- V-02: pass - evidence: .agentsflower/tasks/.runtime/T-166.evidence/T-166.render_check.txt
- V-03: pass - evidence: .agentsflower/tasks/.runtime/T-166.evidence/T-166.render_check.txt .agentsflower/tasks/.runtime/T-166.evidence/T-166.costs_live_response.json
- V-04: pass - evidence: .agentsflower/tasks/.runtime/T-166.evidence/T-166.check1_test_studio.txt .agentsflower/tasks/.runtime/T-166.evidence/T-166.check2_full_suite.txt

Observations (not defects):
- Cosmetic rounding: a $0.225 aggregate displays as "$0.23" on the summary card
  but "$0.22" in the stage-group meta line (adjacent float representations run
  through toFixed); full-precision values are exact, so this is display noise.
- The 4-card summary grid keeps fixed columns on narrow screens; the task table
  compensates with horizontal scroll. Workable responsiveness, cramped on phones.
- local_free_tokens_pct falls back to planned-token share when a project has no
  actuals yet (worktree response showed 91.0%); the field is labeled as a
  percentage without signaling which basis was used.

New defects (outside the task):
- none

Cannot verify, needs:
- nothing blocked; no pixel screenshot was taken, rendering was verified at DOM
  level plus served-markup level over HTTP.

Proposed memory updates:
- none
