# T-138: Dynamic Model Quota Hub, Real CLI Model Probing, and Default Model Configuration

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Branch: t-138-dynamic-model-quota-hub
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-138-dynamic-model-quota-hub
Independent check: tester
Resume: none
Routing exception: human authorized dynamic CLI model probe and capacity hub (2026-10-25)

## Goal

Replace the static mock/hardcoded capacity dashboard in AgentsFlower Studio with a real-time, deterministic system scanner and model configuration center:

1. **Backend Real-Time CLI Probing (`/api/capacity/probe`):**
   - Probe installed CLI platforms asynchronously with strict subprocess timeouts:
     - `devin.exe models list`: parse available live model families, active model IDs (e.g. `swe-2-high`, `gemini-4-argon-high`, `claude-opus-4-6-thinking`, `gpt-5-5-high`), and pricing metadata.
     - `claude.exe --version` and auth status.
     - `agy.exe --version` and `agy.exe models`.
     - Local Ollama API (`http://127.0.0.1:11434/api/tags` or `localhost:11434`): detect offline zero-cost local models (e.g. `qwen2.5-coder`, `deepseek-r1`, `llama3.3`).
   - Identify offline/free models and cloud models with active authentication.
   - Cache results with a short TTL (60s) to keep queries instantaneous.

2. **Dynamic Model Quota Hub UI (`#view-capacity`):**
   - Render live cards for each detected platform:
     - Platform Name & Version (Devin, Claude Code, Antigravity, Ollama/Local).
     - Status badge: `Active & Authenticated` (green), `Limited / Unauthenticated` (amber), `Not Installed` (gray).
     - Collapsible list of available models with context length and pricing/token rate.
   - Dedicated Section: **`Free & Local Offline Models`**
     - Lists currently installed zero-token local models.
     - Suggested installable open-weight models for autonomous local execution.

3. **Default Worker Model Selector & Persistence:**
   - Allow user to set the project's Default Worker Model in 1 click (e.g. `swe-2-high` vs `gemini-4-argon-high` vs local model).
   - Endpoint `/api/capacity/default-model` (POST) to persist choice in `.agentsflower/docs/model-options.json` or project settings.
   - Studio immediately updates chat composer default pill and task inception defaults.

## Read first

- .agentsflower/mockups/README.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.css
- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tools/machine_capacity.py
- .agentsflower/docs/model-options.json

## Allowed files

- `.agentsflower/studio/index.html`
- `.agentsflower/studio/studio.css`
- `.agentsflower/studio/studio.js`
- `.agentsflower/tools/studio.py`
- `.agentsflower/tests/test_studio.py`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: Endpoint `/api/capacity/probe` dynamically scans devin, claude, agy, and local ollama, returning real available models.
- [ ] C-02: `#view-capacity` renders live platform cards with status badges and available model listings (no hardcoded static cards).
- [ ] C-03: UI includes a dedicated Free & Local Offline Models section.
- [ ] C-04: User can select and persist default worker model via `/api/capacity/default-model`.
- [ ] C-05: Unit test suite in `test_studio.py` passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
