# T-169: Model Quota Hub UI: Auto-Scan on Tab Open, Platform & Model Toggle Switches, and Third-Party Key Manager

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-168, T-150
Branch: t-169-model-quota-hub-ui
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-169-model-quota-hub-ui
Independent check: tester
Resume: none
Routing exception: human authorized Model Quota Hub UI reconstruction (2026-10-25)

## Goal

Completely overhaul the Model Quota Hub frontend view (`#view-capacity`) to make it interactive, reliable, and project-aware:

1. **Auto-Scan on Tab Open**:
   - In `studio.js`: whenever the user switches to the `capacity` tab (`switchTab('capacity')`), trigger a fresh scan (`loadCapacity()`) automatically.
   - Display an animated skeleton / progress scanner while the CLI probe is executing so the view is never empty, broken, or unresponsive.
2. **Platform & Model Activation Toggles**:
   - For every detected platform card:
     - Add a master toggle switch: **Active / Inactive** for the current project.
     - For each model row inside the platform:
       - Add an **Enabled / Disabled** toggle checkbox.
       - Disabled models appear dimmed and are excluded from active usage.
   - When toggled, immediately call `POST /api/capacity/project-toggle` to persist changes for the active project.
3. **Third-Party Provider & API Key Modal**:
   - In `#view-capacity`: add a "Connect Custom Provider" button (OpenRouter, Groq, custom OpenAI-compatible).
   - Modal interface allowing user to input:
     - Provider Name
     - Base URL (defaulting to `https://openrouter.ai/api/v1`)
     - API Key (password-masked input field).
   - "Test & Save" button triggers backend verification and fetches available models dynamically.
   - Connected custom providers render as cards with status, model list, and delete action.
4. **Project Switching Awareness**:
   - When the user selects a different project in Studio, the Model Quota Hub view immediately updates to reflect that project's specific enabled platforms and models.

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
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- nothing

## Port

- 8891

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Navigating to the Model Quota Hub tab automatically triggers CLI probing with a visible loading/scanning state; no blank or broken view.
- [ ] C-02: Each platform card features an Active/Inactive switch, and each model row features an Enable/Disable toggle that saves to the active project.
- [ ] C-03: Custom provider interface allows connecting OpenRouter with an API key (safely masked), dynamically rendering its fetched models.
- [ ] C-04: Changing the active project re-renders the platform and model states specifically configured for that project.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly; full suite passes.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: 83e28f224e3757067f2d1b6cc612f32ff3cd5aa1 on t-169-model-quota-hub-ui
Files:
- .agentsflower/studio/index.html - "Connect Custom Provider" button in hub actions + provider modal (name, kind select, Base URL defaulting to https://openrouter.ai/api/v1, password-masked API key, inline status); asset version bumps
- .agentsflower/studio/studio.js - switchTab('capacity') triggers loadCapacity(); renderCapacitySkeleton() shows animated placeholder during probe and on failure a non-empty error state; renderCapacityHub renders platform-enable-toggle and per-model model-enable-toggle switches + provider meta/remove button; toggleCapacityItem() POSTs /api/capacity/project-toggle and applies returned project state; removeCapacityProvider() POSTs /api/capacity/provider/remove; provider modal posts /api/capacity/provider/add with inline error display; platformModelList excludes disabled platforms/models from active usage
- .agentsflower/studio/studio.css - capacity-skeleton shimmer (.sk-line + capacityScanShimmer), .scan-pulse, .af-switch/.af-switch-sm toggle styles, .platform-disabled/.model-disabled dimming, provider card/modal styles
- .agentsflower/tests/test_studio.py - test_quota_hub_ui_markers asserts served index.html/studio.js/studio.css carry all T-169 hooks
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (97 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (601 passed / 0 failed, 4 skipped on first run; second run had 1 transient Windows temp-file PermissionError in test_run_task.RoutingAdmissionTests.test_codex_config_alias_effort_downgrade_is_refused - unrelated environment flake, passes in isolation)
Criteria:
- C-01: pass - switchTab() calls loadCapacity() when tab is 'capacity' (studio.js); renderCapacitySkeleton fills #toolsCapacityGrid with animated .capacity-skeleton cards + .scan-pulse meta during every probe; probe failure renders capacity-scan-error empty-state, never a blank view
- C-02: pass - each platform card has an Active/Inactive .platform-enable-toggle switch and each model row an Enabled/Disabled .model-enable-toggle; toggleCapacityItem() POSTs {project, platform, model?, enabled} to /api/capacity/project-toggle and re-renders from the authoritative res.state; disabled rows dimmed (.model-disabled/.platform-disabled) and their Set-default buttons disabled
- C-03: pass - #modalProviderBackdrop captures name/kind/base_url/api_key via type=password input and posts to /api/capacity/provider/add (key never echoed back); provider cards render api_key_masked, base_url, model list and Remove action -> /api/capacity/provider/remove
- C-04: pass - switchProject() awaits loadCapacity() which probes with ?project=<active project>; backend overlays that project's enabled flags and providers, and the view re-renders with skeleton during the refresh
- C-05: pass - test_quota_hub_ui_markers added to TestCapacityHub; both ## Checks commands green (see Checks)
Found, not fixed:
- None
Proposed memory updates:
- test_run_task disposable-fixture runs can hit transient Windows os.replace PermissionError (file-lock race); a rerun passes.
