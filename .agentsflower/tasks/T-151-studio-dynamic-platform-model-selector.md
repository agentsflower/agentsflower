# T-151: Studio Dynamic Platform & Model Selector via CLI Probing

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-150
Branch: t-151-studio-dynamic-platform-model-selector
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-151-studio-dynamic-platform-model-selector
Independent check: tester
Resume: none

## Goal

Upgrade the Studio Chat model selector into a dynamic two-level Platform & Model switcher backed by real-time CLI probing:

1. **Platform & Model UI Component**:
   - Split the model selector in the chat composer into:
     - Platform Selector (`Devin`, `Claude Code`, `Codex`, `Antigravity`, `Local Ollama`).
     - Dynamic Model Dropdown populated specifically from the selected platform.
2. **CLI Model List Fetching**:
   - When switching platform in UI, trigger request to `/api/capacity/probe?platform=<tool>`.
   - Populate models dynamically from the probed CLI output:
     - `devin`: models parsed from `devin models list`.
     - `ollama`: models parsed from `/api/tags`.
     - `claude` / `agy` / `codex`: models discovered for the authenticated account.
   - If a platform is not installed or unauthenticated, display an informative status pill (`Not Installed` / `Limited`) and suggest fallback.
3. **Session Persistence**:
   - Persist selected platform and model in `sessionStorage` (`af_chat_platform`, `af_chat_model`).
4. **Unit Tests**:
   - Add comprehensive tests in `.agentsflower/tests/test_studio.py` verifying dynamic model dropdown population and platform probe queries.

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

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8901 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Chat header/composer features a Platform selector (`devin`, `claude`, `codex`, `agy`, `ollama`) and a dependent Model selector.
- [ ] C-02: Switching platform dynamically queries `/api/capacity/probe` and populates the Model selector with live models returned by that platform's CLI.
- [ ] C-03: Missing or unauthenticated platforms gracefully render a status pill without breaking UI state.
- [ ] C-04: Selected platform and model persist across page reloads.
- [ ] C-05: Unit tests in `test_studio.py` cover dynamic platform probing and model list rendering; full suite passes.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
