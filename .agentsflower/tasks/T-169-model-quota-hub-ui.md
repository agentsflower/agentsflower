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

<!-- Worker writes outcome below -->
