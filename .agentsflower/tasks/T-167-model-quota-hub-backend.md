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
Outcome: completed
Change: d610b8a on t-167-model-quota-hub-backend
Files:
- .agentsflower/tools/studio.py - provider engine (OpenRouter / OpenAI-compatible via a patchable _provider_request seam), masked secret storage in <project>/<flow>/state/.secrets.json with per-project .gitignore enforcement, project-models.json state (platform/model enabled flags + provider configs), project overlay in probe_capacity with project-scoped probe caches, endpoints GET /api/capacity/project-state, POST /api/capacity/project-toggle, POST /api/capacity/provider/add, POST /api/capacity/provider/remove; providers also join /api/capacity/probe platforms and ?platform=<provider-id>
- .agentsflower/tests/test_studio.py - new TestProviderEngineAndProjectState (9 tests): codex live-CLI probing, OpenRouter model fetch + masking, verify-failure/400 paths, remove credential purge, per-project toggle persistence/isolation, provider in probe, bad-input rejects, repo .gitignore coverage
- .gitignore - .agentsflower/state/.secrets.json and .agentflow/state/.secrets.json added outside the template-managed block (install.py GITIGNORE untouched)
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (96 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (600 passed / 0 failed, 4 skipped)
Criteria:
- C-01: pass - all five platforms probed dynamically: devin `models list` (parse_devin_models), codex `--version`/`login status`/`models` (_probe_codex), claude `models`, agy `models`, ollama /api/tags; no hardcoded model arrays in code (codex/claude fall back to the project's own model-options.json catalog only when the live CLI catalog fails, labelled "configured catalog"); evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-02: pass - POST /api/capacity/provider/add supports openrouter (default base https://openrouter.ai/api/v1) and openai-compatible custom base_url, verifies via live GET <base>/models and stores fetched models; evidence: .agentsflower/tools/studio.py (add_provider, fetch_provider_models), .agentsflower/tests/test_studio.py
- C-03: pass - keys persist only in .agentsflower/state/.secrets.json under the target project; repo .gitignore covers it and save_project_secrets enforces the ignore inside the target project; all responses expose only api_key_masked (sk-or-••••••••); tests assert the raw key never appears in any response or in project-models.json; evidence: .gitignore, .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-04: pass - GET /api/capacity/project-state and POST /api/capacity/project-toggle toggle platforms and individual models per project, persisted in <project>/.agentsflower/state/project-models.json; probe overlay marks platform/model enabled flags and probe caches are project-scoped; tests show project B unaffected by project A toggles; evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-05: pass - 9 new tests cover codex dynamic probing, OpenRouter fetching, secret masking and per-project toggle persistence; full suite 600 tests green; evidence: .agentsflower/tests/test_studio.py
Found, not fixed:
- _capacity_probe_cache held the last full scan globally without a project key; this change adds a "scope" field, but cross-project serving within the 60s TTL for pre-existing entries is still theoretically possible in a long-lived process (harmless: enabled flags are re-applied at request time).
- Provider models are re-fetched live during every uncached full probe with a 15s timeout each; a project with many providers could see a slow first probe.
- Frontend wiring of the new endpoints (project-state, project-toggle, provider add/remove) is not in studio.js/index.html; those files are outside this task's scope.
Proposed memory updates:
- Model Quota Hub backend endpoints now exist: GET /api/capacity/project-state, POST /api/capacity/project-toggle, POST /api/capacity/provider/add|remove; secrets convention <project>/.agentsflower/state/.secrets.json (git-ignored), state convention <project>/.agentsflower/state/project-models.json.
