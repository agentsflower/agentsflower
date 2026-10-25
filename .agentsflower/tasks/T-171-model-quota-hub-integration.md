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

<!-- Worker writes outcome below -->
