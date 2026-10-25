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
Verifies: T-163 @ a5889f24d11a58e0ee888f94c50e574ed974bef3

## Goal

Independently verify T-163 (Jev token and budget estimation for task synthesis) against the T-163 contract:

1. Serve Studio from the T-163 candidate worktree.
2. Exercise `POST /api/task/synthesize` and verify presence and accuracy of `planned_tokens` and `planned_cost_usd`.
3. Verify visual rendering of budget metrics in Task Pool Card.
4. Verify `T-NNN.plan.json` generation upon registration.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

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

Verified T-163 @ a5889f2 in the disposable tester worktree. Studio was served on 127.0.0.1:8913 and `POST /api/task/synthesize` exercised live: every task carries `planned_input_tokens`, `planned_output_tokens`, `planned_tokens` (= in + out) and `planned_cost_usd` matching `tokens x rate_per_1m / 1e6` (claude-opus-5.5 @15.0 -> 0.244755/0.484695/0.42774; gemini-4-argon-high @2.5; swe-2-high and qwen2.5-coder -> free, $0.00); pool-level totals equal the per-task sums. The Task Pool Card was rendered end-to-end in headless Chrome via the real `synthesizeTasksFromDiscussion` click path: pool summary "Jev Plan Budget: 73K tokens $0.12" and per-task badges "48.5K tokens / $0.12", "24.5K tokens / $0.00" with `data-planned-*` attributes (screenshot + DOM captured). `register_task_pool` against a temp project wrote `T-001.plan.json`/`T-002.plan.json` with consistent math plus `Planned tokens:`/`Planned cost USD:` task-file headers. Both check commands pass cleanly.

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (84 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (588 ran, 0 failed, 4 skipped)
Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-164.evidence/T-164.synthesize-opus.json
  .agentsflower/tasks/.runtime/T-164.evidence/T-164.synthesize-default.json
- V-02: pass - evidence: .agentsflower/tasks/.runtime/T-164.evidence/T-164.pool-card.png
  .agentsflower/tasks/.runtime/T-164.evidence/T-164.pool-card.html
  .agentsflower/tasks/.runtime/T-164.evidence/T-164.pool-card.txt
  .agentsflower/tasks/.runtime/T-164.evidence/T-164.cdp-render.py
- V-03: pass - evidence: .agentsflower/tasks/.runtime/T-164.evidence/T-164.register-plan-json.txt
- V-04: pass - evidence: .agentsflower/tasks/.runtime/T-164.evidence/T-164.checks-studio.txt
  .agentsflower/tasks/.runtime/T-164.evidence/T-164.checks-full.txt
New defects (outside the task):
- Pre-existing, introduced by T-149 (d72d033), not by T-163: `btnSynthesizeTasks` was removed from `index.html`, so `synthesizeTasksFromDiscussion` is bound to a non-existent element and the Task Pool Card is unreachable in the shipping UI (pool items are also never persisted to research thread records). Rendering was verified by re-injecting the button via CDP before DOMContentLoaded so the real app handler bound to it; a user-facing trigger for `/api/task/synthesize` should be restored.
Cannot verify, needs:
- none
Proposed memory updates:
- none
