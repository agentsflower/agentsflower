# T-163: Jev Token & Budget Estimator for Task Pool Synthesis (Plan Model)

Role: developer
Tool: devin
Model: gemini-4-argon-high
Routing exception: human standing policy 2026-10-21 (model-options.json + questions.md): on low confidence evaluate the Devin catalog and take the adequate declared/higher-confidence default instead of halting. Jev option confidence 0.99 for devin-swe-2; only the effort-tier sub-question scored 0.48 while the requirement floor is already high; declared gemini-4-argon-high meets it.
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
Outcome: completed
Change: a5889f24d11a58e0ee888f94c50e574ed974bef3 on t-163-jev-token-budget-estimator
Files:
- .agentsflower/tools/plan_route.py - added `EFFORT_OUTPUT_TOKENS`, `MODEL_PRICING_USD_PER_1M`, `lookup_model_pricing`, `estimate_input_tokens`, `estimate_output_tokens`, and `estimate_task_budget`, and attached planned token and USD cost fields to `recommend`.
- .agentsflower/tools/studio.py - integrated token and USD cost estimation into `synthesize_tasks_from_chat`, wrote `.agentsflower/tasks/T-NNN.plan.json` and `Planned tokens:` / `Planned cost USD:` Task File headers during `register_task_pool`, and surfaced plan metadata in `get_tasks_data`.
- .agentsflower/studio/studio.js - added `formatTokenCount` and `formatUsdCost` helpers and rendered pool-level and per-task token and USD budget badges in `createTaskPoolCardElement`.
- .agentsflower/studio/studio.css - added styles for `.pool-budget-summary`, `.token-badge`, `.cost-badge`, and `.budget-badge`.
- .agentsflower/tests/test_studio.py - added `TestJevTokenBudgetEstimator` unit tests verifying token estimation tiers, blast-radius input scaling, model rate lookup, synthesis metadata, `.plan.json` output, and Task Pool Card UI badges.
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (84 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (584 passed / 0 failed / 4 skipped)
Criteria:
- C-01: pass - `estimate_input_tokens`, `estimate_output_tokens`, and `estimate_task_budget` compute `planned_input_tokens`, `planned_output_tokens` (`low: 1000`, `medium: 4000`, `high: 12000`, `max: 24000`), and `planned_tokens` in `synthesize_tasks_from_chat`; evidence: .agentsflower/tools/plan_route.py, .agentsflower/tools/studio.py
- C-02: pass - `lookup_model_pricing` and `estimate_task_budget` calculate `planned_cost_usd` from `model-options.json` and catalog rates (including Claude Opus $15/1M, Devin `swe-2` $0, local Ollama $0, and Gemini 4 Argon $2.50/1M); evidence: .agentsflower/tools/plan_route.py, .agentsflower/tools/studio.py
- C-03: pass - `createTaskPoolCardElement` renders pool-level and per-task `.token-badge` and `.cost-badge` / `.budget-badge` elements with formatted token counts and USD amounts; evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css
- C-04: pass - `register_task_pool` writes `.agentsflower/tasks/T-NNN.plan.json` with full token/cost metadata and records `Planned tokens:` and `Planned cost USD:` in Task File headers; evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-05: pass - all 84 unit tests in `test_studio.py` and 588 tests in the full suite pass cleanly; evidence: .agentsflower/tests/test_studio.py
Found, not fixed:
- none
Proposed memory updates:
- none
