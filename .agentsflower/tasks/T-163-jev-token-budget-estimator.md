# T-163: Jev Token & Budget Estimator for Task Pool Synthesis (Plan Model)

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: T-162
Branch: t-163-jev-token-budget-estimator
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-163-jev-token-budget-estimator
Independent check: tester
Resume: none

## Goal

Integrate Jev complexity scoring and token/pricing metrics into task pool synthesis to establish a formal Plan Model:

1. **Token Estimation Formula**:
   - In `.agentsflower/tools/studio.py` and `plan_route.py`:
     - Calculate `planned_input_tokens`: prompt size + estimated context from AST blast radius files.
     - Calculate `planned_output_tokens`: derived from Jev complexity / effort rating (low: 1K, medium: 4K, high: 12K, max: 24K).
     - Calculate `planned_cost_usd`: using published rates from `.agentsflower/docs/model-options.json` or model catalog (e.g. Claude Opus $15/M, Devin free/swe-2, local Ollama $0).
2. **Metadata Integration**:
   - Synthesized tasks carry `planned_tokens` and `planned_cost_usd`.
   - Task Pool Card renders estimated token count and estimated cost in USD.
   - Batch registration records plan metrics into `.agentsflower/tasks/T-NNN.plan.json` and Task File headers.
3. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing estimation calculations, rate lookup, and JSON metadata generation.

## Read first

- .agentsflower/tools/studio.py
- .agentsflower/tools/plan_route.py
- .agentsflower/tools/route.py
- .agentsflower/docs/model-options.json
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/tools/studio.py
- .agentsflower/tools/plan_route.py
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8913 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Synthesis calculates `planned_tokens` based on blast radius context and Jev complexity.
- [ ] C-02: Planned cost in USD is calculated per model pricing configuration.
- [ ] C-03: Task Pool Card displays planned token count and budget ($).
- [ ] C-04: Batch registration outputs `.agentsflower/tasks/T-NNN.plan.json` with budget metadata.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
