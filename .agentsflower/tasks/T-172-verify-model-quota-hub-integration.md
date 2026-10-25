# T-172: Verify End-to-End Model Quota Hub Project Filtering and Fallback Guards

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-171
Independent check: none
Resume: none
Verifies: T-171 @ a95f84e174f30a091b00b702c61319b321b04a6f
Routing exception: human authorized Model Quota Hub integration verification (2026-10-25)

## Goal

Independently verify T-171's end-to-end integration: ensuring disabled platforms and models are cleanly filtered out of Studio composer and task creation workflows.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-171-model-quota-hub-integration.md
- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- nothing

## Acceptance criteria

- [ ] V-01: Verifies that deactivating models in Model Quota Hub prevents them from showing in the chat composer dropdown.
- [ ] V-02: Verifies graceful fallback and warning badges when selected models become unauthenticated.
- [ ] V-03: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->

Independent verification of T-171 at a95f84e in a disposable checkout
(AGENTFLOW_TARGET=local, attempt T-172#1). Both `## Checks` commands were run
verbatim and pass. Beyond the suite I ran a live HTTP check against a temporary
Studio instance on port 8897: attached a scratch project, deactivated
`devin/swe-2-high` via /api/capacity/project-toggle, and confirmed the
/api/capacity/probe payload then marks that model `enabled: false` while sibling
models stay enabled; a platform-level toggle marks the platform and every model
disabled, which studio.js platformModelList/chatModelList translate into an
empty composer dropdown (the static CHAT_MODELS list is never resurrected once a
platform was probed). The fallback/warning path was verified by code inspection
plus test_chat_composer_filter_and_default_warning_markers: defaultModelIssue
reports deactivated or unauthenticated platforms, updateDefaultModelPill renders
the limited status-badge with a nearest-activated-fallback adopt-on-click offer
(nearestActivatedModel only picks platforms with status 'active'),
updatePlatformStatusPill shows a status badge for non-active platforms, and
server-side enforce_project_model_whitelist substitutes the nearest activated
fallback or emits a warning at synthesis and pool registration. The Hub's
Set-default button is disabled on deactivated models, so ensureChatModelListed
cannot reintroduce them. One reading note for V-02: the warning badge +
fallback offer targets the persisted default worker model and the platform
status pill; a non-active platform's already-listed models are not removed from
the dropdown, only badged. DOM-level click-through in a real browser was not
performed; the full data path (toggle -> persisted state -> probe payload ->
dropdown filter functions -> render) was verified.

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (102 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (606 passed / 0 failed, 4 skipped)
Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-172.evidence/T-172.live_check.txt .agentsflower/tasks/.runtime/T-172.evidence/T-172.check1_test_studio.txt
- V-02: pass - evidence: .agentsflower/tasks/.runtime/T-172.evidence/T-172.check1_test_studio.txt
- V-03: pass - evidence: .agentsflower/tasks/.runtime/T-172.evidence/T-172.check2_full_suite.txt
New defects (outside the task):
- none
Cannot verify, needs:
- browser-level DOM click-through of the composer dropdown (no browser harness in this checkout); data path verified end-to-end instead, see prose above
Proposed memory updates:
- none
