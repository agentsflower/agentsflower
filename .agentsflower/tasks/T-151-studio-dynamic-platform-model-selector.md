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
Outcome: completed
Change: 2b8e9f352cc64ef0fe845730f3832e84aa953765 on t-151-studio-dynamic-platform-model-selector
Files:
- .agentsflower/tools/studio.py - `?platform=<key>` single-platform probe mode on /api/capacity/probe with per-platform TTL cache; new `_probe_codex` (login status auth + configured model-options catalog fallback); claude/codex model lists populated via `parse_cli_models` with `_configured_tool_models` fallback; `_apply_quota_hold` extracted; codex added to the full scan set.
- .agentsflower/studio/index.html - platform selector wrap (`chatPlatformSelector`/`chatPlatformPill`/`chatPlatformDropdown`) and `chatPlatformStatus` pill added to the composer toolbar.
- .agentsflower/studio/studio.js - CHAT_PLATFORMS list, `probeChatPlatform` (GET /api/capacity/probe?platform=<key>), `selectChatPlatform`, platform pill/dropdown/status-pill renderers, dependent model dropdown with empty-state row, `af_chat_platform` + `af_chat_model` sessionStorage persistence.
- .agentsflower/studio/studio.css - `.platform-pill`, `.platform-status-pill`, `.model-empty` styles.
- .agentsflower/tests/test_studio.py - codex fixture coverage in full-scan test; 5 new single-platform probe tests; new chat platform selector UI contract test; per-platform probe cache reset in setUp/tearDown.
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (50 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (554 passed / 0 failed, 4 skipped)
Criteria:
- C-01: pass - composer toolbar holds `chatPlatformSelector` (devin/claude/codex/agy/ollama) + dependent `chatModelSelector`; evidence: .agentsflower/studio/index.html, .agentsflower/studio/studio.js
- C-02: pass - `selectChatPlatform` calls `probeChatPlatform`, which fetches `/api/capacity/probe?platform=<key>` and repopulates the model dropdown from `platform.models`; endpoint verified by `test_probe_single_platform_returns_only_that_platform` and `test_probe_single_platform_serves_own_cache`; evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-03: pass - non-active platforms render `chatPlatformStatus` pill with `status_label` (`Not Installed` / `Limited / Unauthenticated`), note + fallback hint in title; dropdown shows a `model-empty` info row with CHAT_MODELS fallback; evidence: .agentsflower/studio/studio.js, .agentsflower/tests/test_studio.py (`test_probe_single_platform_missing_marks_status`)
- C-04: pass - `af_chat_platform` and `af_chat_model` written on select and restored in `setupModelSelector`/`applyCapacityModels`; evidence: .agentsflower/studio/studio.js
- C-05: pass - 6 new/updated tests in test_studio.py cover platform probing and UI contract; full suite 554 tests green.
Question or reason:
Found, not fixed:
- `claude`/`codex` CLIs expose no reliable catalog command on this machine's versions; their model lists fall back to the project's docs/model-options.json catalog (labeled `configured catalog`) when the CLI listing yields nothing.
Proposed memory updates:
- none
