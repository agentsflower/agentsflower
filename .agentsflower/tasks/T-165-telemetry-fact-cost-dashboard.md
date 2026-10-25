# T-165: Telemetry Fact Tracking and Studio Cost & ROI Dashboard (Plan vs Fact)

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: T-164
Branch: t-165-telemetry-fact-cost-dashboard
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-165-telemetry-fact-cost-dashboard
Independent check: tester
Resume: none

## Goal

Capture actual execution telemetry and provide a dedicated Cost & ROI Dashboard comparing Plan vs Fact in AgentsFlower Studio:

1. **Telemetry Fact Ingestion**:
   - In `.agentsflower/tools/studio.py`: implement `/api/analytics/costs`:
     - Reads planned metrics from `.plan.json` files.
     - Reads actual token usage, execution time, and model calls from worker telemetry in `.agentsflower/tasks/.runtime/`.
     - Calculates `actual_tokens`, `actual_cost_usd`, and variance `delta_usd = actual - plan`.
2. **Dedicated Cost & ROI Dashboard View**:
   - Add new navigation subtab / panel in Studio: **Cost & ROI Dashboard**.
   - Interactive breakdown:
     - Project summary cards: Total Planned ($), Total Actual ($), Net Savings ($), Local/Free Tokens (%).
     - Per-Stage cost distribution bar.
     - Detailed Task Table: `Stage | Task ID | Title | Model | Plan ($) | Fact ($) | Delta (%) | Status`.
3. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing `/api/analytics/costs` calculation, empty telemetry fallbacks, and UI rendering.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8915 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Endpoint `/api/analytics/costs` aggregates Plan vs Fact metrics across project tasks.
- [ ] C-02: Studio features a dedicated Cost & ROI Dashboard view.
- [ ] C-03: Summary cards report Total Planned, Total Actual, and Net Savings in USD.
- [ ] C-04: Task table renders Plan, Fact, and Delta per task with stage grouping.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
