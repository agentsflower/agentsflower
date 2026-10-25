# T-171: End-to-End Integration: Project Model Filtering in Studio Chat & Task Inception with Fallback Guards

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-170
Branch: t-171-model-quota-hub-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-171-model-quota-hub-integration
Independent check: tester
Resume: none
Routing exception: human authorized Model Quota Hub end-to-end integration (2026-10-25)

## Goal

Connect the Model Quota Hub project activation state across the entire Studio experience:

1. **Chat Composer Model Selector Filter**:
   - Ensure the chat model dropdown only contains models from platforms and model lists that are currently ACTIVE for the selected project.
   - Disabled models and inactive platforms are filtered out from the selection list.
2. **Task Contract Creator & Inception Alignment**:
   - When generating new task contracts or synthesizing tasks, ensure the primary model selection adheres to the project's activated model whitelist.
3. **Graceful Fallback & Status Awareness**:
   - If a project's default model belongs to an inactive platform or unauthenticated CLI, highlight with a warning pill and automatically offer the nearest activated fallback model.
4. **Unit & Integration Tests**:
   - In `test_studio.py`, verify that changing project settings dynamically updates the available models in the chat composer and creator.

## Read first

- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- nothing

## Port

- 8892

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Chat composer model selector displays exclusively models activated for the current project.
- [ ] C-02: Deactivating a platform or model in Model Quota Hub immediately removes it from the chat composer dropdown.
- [ ] C-03: Task creator model options conform to the project's active model set.
- [ ] C-04: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: a95f84e on t-171-model-quota-hub-integration
Files:
- .agentsflower/tools/studio.py - added project_model_allowed / project_model_fallback / enforce_project_model_whitelist guards; applied in synthesize_tasks_from_chat and register_task_pool (substituted model lands in the generated contract header, plan.json and ledger payload, with model_warning recorded on the task dict)
- .agentsflower/studio/studio.js - composer dropdown now lists only project-activated models (probed platform with no activated models yields an empty list plus a "deactivated for this project" info row instead of the static CHAT_MODELS list); platform dropdown marks deactivated platforms; stale default worker model gets a status-badge limited warning pill offering the nearest activated fallback via defaultModelIssue/nearestActivatedModel (click adopts it)
- .agentsflower/tests/test_studio.py - new TestModelQuotaHubIntegration class: flag semantics, dynamic toggle -> synthesize substitution -> re-activation restore, pool registration fallback written to contract/plan, no-fallback warning path, composer/warning-pill JS markers
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (102 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (606 passed / 0 failed, 4 skipped)
Criteria:
- C-01: pass - platformModelList/chatModelList in .agentsflower/studio/studio.js filter to m.enabled !== false on enabled platforms only; empty activated set no longer falls back to CHAT_MODELS once the platform is probed
- C-02: pass - toggleCapacityItem -> applyProjectStateToCapacity -> applyCapacityModels re-renders the dropdown; test_dynamic_toggle_updates_inception_model_pool in .agentsflower/tests/test_studio.py proves the creator side flips immediately
- C-03: pass - enforce_project_model_whitelist in .agentsflower/tools/studio.py guards /api/task/synthesize and /api/task/pool/register; test_register_pool_writes_activated_fallback_model verifies contract header Model: gets the activated fallback
- C-04: pass - full suite green: 606 tests OK (4 skipped)
Found, not fixed:
- /api/chat execution (sendChatMessage) does not re-validate the selected model server-side against the whitelist; a stale pick could still reach the CLI. Out of scope: criteria cover the dropdown contents, not chat dispatch.
- Synthesized task cards show the substituted model but not the model_warning text in the pool UI; the warning is in the API payload and plan.json only.
Proposed memory updates:
- none
