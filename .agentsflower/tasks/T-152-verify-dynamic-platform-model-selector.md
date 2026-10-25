# T-152: Verify Studio Dynamic Platform & Model Selector

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-151
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-151 @ 2b8e9f352cc64ef0fe845730f3832e84aa953765

## Goal

Independently verify T-151 (Studio dynamic platform and model selector via CLI probing) against the T-151 contract:

1. Serve Studio from the T-151 candidate worktree.
2. Verify switching platform sends `/api/capacity/probe?platform=...` and updates the model dropdown.
3. Verify handling of uninstalled/unauthenticated platforms.
4. Verify persistence of chosen platform and model.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-151-studio-dynamic-platform-model-selector.md
- .agentsflower/studio/studio.js
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

- [ ] V-01: Platform selection switches available model list based on real CLI output.
- [ ] V-02: Uninstalled/unauthenticated platforms degrade gracefully with a visual badge.
- [ ] V-03: Session persistence stores and restores platform/model choices.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (50 passed / 0 failed, 7.9s)
- `python -m unittest discover -s .agentsflower/tests` -> pass (554 passed / 0 failed, 4 skipped, 370.4s)
Criteria:
- V-01: pass - served checkout 2b8e9f3 on port 8901; live `GET /api/capacity/probe?platform=<key>` returns per-platform real CLI output: devin active 816 models parsed from `devin models list` (swe-2-high "Free", families/context/pricing), agy active 6 models from `agy models` (gemini-3.8-flash-*, claude-sonnet-4-6, gpt-oss-120b-medium); `platform=bogus` -> HTTP 400 "unknown platform". Frontend wires the switch end-to-end: selectChatPlatform -> probeChatPlatform -> `/api/capacity/probe?platform=<key>` -> applyPlatformModels -> renderModelDropdown repopulates state.chatModels from the probed record; test_chat_platform_selector_ui_markers plus 7 test_probe_single_platform_* tests cover this and all passed. evidence: .agentsflower/tasks/.runtime/T-152.evidence/T-152.probe_summary.txt .agentsflower/tasks/.runtime/T-152.evidence/T-152.probe_all_platforms.txt .agentsflower/studio/studio.js .agentsflower/tools/studio.py
- V-02: pass - live: claude -> status limited "Limited / Unauthenticated", note "Failed to authenticate: OAuth session expired and could not be refreshed"; codex/ollama -> status missing "Not Installed" with notes ("codex CLI not found on PATH", "no Ollama server answering on 127.0.0.1:11434"). updatePlatformStatusPill renders the status_label into chatPlatformStatus pill (hidden only when active) with fallback-hint title; renderModelDropdown adds a "Not Installed: <note> - pick another platform" info row without breaking selector state; status-badge.active/.limited/.missing styles present; unreachable probe degrades to a synthetic missing record. evidence: .agentsflower/tasks/.runtime/T-152.evidence/T-152.probe_summary.txt .agentsflower/tasks/.runtime/T-152.evidence/T-152.served-index.html .agentsflower/studio/studio.js .agentsflower/studio/studio.css
- V-03: pass - sessionStorage keys af_chat_platform/af_chat_model written in selectChatPlatform, model-option click handler, applyPlatformModels fallback and setDefaultWorkerModel; restored on load in setupModelSelector and re-validated against the probed per-platform list in applyCapacityModels (saved model dropped only if absent from the platform's live list, then default or first model chosen). All sessionStorage access try/catch-guarded. evidence: .agentsflower/studio/studio.js
- V-04: pass - full suite Ran 554 tests OK (skipped=4); commit touches only the 5 Allowed files (index.html, studio.css, studio.js, studio.py, test_studio.py), nothing in Do not touch; worktree clean after checks. evidence: .agentsflower/tasks/.runtime/T-152.evidence/T-152.check2_full_suite.txt .agentsflower/tasks/.runtime/T-152.evidence/T-152.check1_test_studio.txt
New defects (outside the task):
- none observed; note (not a defect): sessionStorage is per-tab-session by contract, so choices do not survive a new browser profile - matches the Task File's explicit sessionStorage requirement.
Cannot verify, needs:
- none
Proposed memory updates:
- none
