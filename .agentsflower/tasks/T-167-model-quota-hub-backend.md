# T-167: Model Quota Hub Backend: Dynamic CLI Probing (Devin, Codex, Claude, Agy, Ollama) & Secure Third-Party Provider Engine (OpenRouter)

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Branch: t-167-model-quota-hub-backend
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-167-model-quota-hub-backend
Independent check: tester
Resume: none
Routing exception: human authorized Model Quota Hub dynamic CLI scanning, per-project activation and secure OpenRouter integration (2026-10-25)

## Goal

Build the robust, deterministic backend for Model Quota Hub supporting multi-CLI dynamic scanning, per-project activation/deactivation, and secure third-party provider integration:

1. **Multi-Platform Dynamic CLI Probing**:
   - Add native probing for `codex` CLI (`codex --version`, configuration check, and available model families).
   - Ensure dynamic discovery for `devin` (`devin models list`), `claude` (`claude models`), `agy` (`agy models`), and `ollama` (`/api/tags`).
   - Hardcoded model lists are strictly forbidden; all models must originate from live CLI queries or active catalog APIs.
2. **Third-Party Provider Engine (OpenRouter & Custom OpenAI-compatible)**:
   - Provide an extensible client to query live models dynamically from OpenRouter (`GET https://openrouter.ai/api/v1/models`) or custom base URLs using an API key.
   - **Secure Key Storage**: Store credentials in `.agentsflower/tasks/.runtime/secrets.json` or `.agentsflower/state/.secrets.json` (strictly ignored by Git, never checked in). Never return raw unmasked keys to the client.
3. **Per-Project Platform & Model Activation State**:
   - Provide endpoints to toggle active/inactive status for any platform and any individual model on a per-project basis (`GET /api/capacity/project-state`, `POST /api/capacity/project-toggle`).
   - Persist configuration deterministically in `.agentsflower/state/project-models.json` under the target project's root.
4. **Endpoints**:
   - `GET /api/capacity/probe?project=<path>&refresh=<1|0>`: returns all detected platforms, dynamically probed models, and project-specific active/disabled flags.
   - `POST /api/capacity/project-toggle`: toggles platform or model enabled state for a project.
   - `POST /api/capacity/provider/add`: securely stores provider config and API key, verifies connection, and fetches live models.
   - `POST /api/capacity/provider/remove`: removes custom provider and purges credentials.

## Read first

- .agentsflower/tools/studio.py
- .agentsflower/tools/machine_capacity.py
- .agentsflower/docs/model-options.json
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py
- .gitignore

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css

## Setup

- nothing

## Port

- 8890

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Probing includes `devin`, `codex`, `claude`, `agy`, and `ollama` dynamically from their CLIs with zero hardcoded model arrays.
- [ ] C-02: OpenRouter and custom OpenAI-compatible providers can be added with an API key, dynamically querying `https://openrouter.ai/api/v1/models` for available models.
- [ ] C-03: API keys are stored securely in a git-ignored file and masked (`sk-or-••••••••`) in all API responses; no secrets are committed.
- [ ] C-04: Per-project toggle endpoint allows enabling and disabling platforms and models, persisting state per project without polluting other projects.
- [ ] C-05: Unit tests in `test_studio.py` cover codex probing, OpenRouter model fetching, secret masking, and project-specific toggle persistence; full test suite passes.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
