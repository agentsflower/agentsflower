# T-170: Verify Model Quota Hub UI, Auto-Scan, and Interactive Toggles

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-169
Independent check: none
Resume: none
Verifies: T-169 @ 83e28f224e3757067f2d1b6cc612f32ff3cd5aa1
Routing exception: human authorized Model Quota Hub UI verification (2026-10-25)

## Goal

Independently verify T-169's UI overhaul of Model Quota Hub: auto-scan on tab switch, skeleton loading, interactive platform and model toggle switches, OpenRouter modal with masked keys, and project isolation.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-169-model-quota-hub-ui.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- nothing

## Acceptance criteria

- [ ] V-01: Switching to `Model Quota Hub` triggers auto-scan and renders live platform cards without DOM or JavaScript errors.
- [ ] V-02: Platform and model toggles interactively update state and persist per project.
- [ ] V-03: OpenRouter connection modal accepts API key, displays masked credentials, and renders fetched models.
- [ ] V-04: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (97 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass on rerun (601 tests, 4 skipped); first run failed 1 unrelated test (details under V-04)

Verification was live, not marker-only: the real served index.html + studio.js ran in a jsdom DOM against a real studio.py backend (127.0.0.1:8891), with fetch instrumented so every request/response was logged; all UI actions below are real DOM clicks. Two disposable temp projects (projA/projB under %TEMP%\t170-verify, attached via /api/project/attach) carried all writes, so the reviewed worktree stayed clean (`git status`: nothing to commit). A local mock OpenAI-compatible /models endpoint stood in for OpenRouter because no real API key may be used.
Criteria:
- V-01: pass - clicking [data-tab="capacity"] synchronously rendered 5 .capacity-skeleton cards plus the "Scanning installed CLIs and connected providers..." meta and fired exactly 1 new /api/capacity/probe request; 5 live platform cards rendered (Devin 3000.11.3 Active, Claude Code Limited/Unauthenticated, Antigravity 1.4.7 Active, Codex and Ollama Not Installed) with "Scanned 5 platforms" meta; 0 console errors and 0 window errors in the whole session - evidence: .agentsflower/tasks/.runtime/T-170.evidence/T-170.dom-drive.json .agentsflower/tasks/.runtime/T-170.evidence/T-170.capacity-dom.html
- V-02: pass - platform toggle on claude -> POST /api/capacity/project-toggle {project: projA, platform: claude, enabled:false} RES 200 -> card re-rendered unchecked + .platform-disabled + label "Inactive" and the flag persisted in projA `project-models.json`; model toggle agy/gemini-3.8-flash-high -> POST {..., enabled:false} RES 200 -> row .model-disabled and flag persisted; projB `/api/capacity/project-state` returned empty platforms/models/providers maps (per-project isolation) - evidence: .agentsflower/tasks/.runtime/T-170.evidence/T-170.dom-drive.json
- V-03: pass - "Connect Custom Provider" modal opened (display:flex); "Test & Save" POSTed {name, kind, base_url, api_key} to /api/capacity/provider/add -> RES 200 after live Bearer-auth verification against the OpenAI-compatible mock; modal closed and a MockRouter card rendered the masked key (sk-t17 followed by bullets), its base_url, 3 fetched model rows and a Remove button; the raw key appears nowhere in the DOM, in `project-models.json`, or in /api/capacity/probe output - it is stored only in the git-ignored `.secrets.json` of projA; projB providers stayed empty - evidence: .agentsflower/tasks/.runtime/T-170.evidence/T-170.dom-drive.json .agentsflower/tasks/.runtime/T-170.evidence/T-170.capacity-dom.html
- V-04: pass - scoped suite green 97/97; full suite green on rerun 601 tests / 4 skipped; the first full-suite run failed only test_worker_watchdog.test_watchdog_gone_worker_is_closed_dead_once_cleanup_is_verified because an orphaned notepad.exe fixture child (PID 66888) from an earlier test in the same run still ran - the exact 2026-10-24 known-issues environment flake; the file passes 14/14 in isolation and its area is untouched by T-169 - evidence: .agentsflower/tasks/.runtime/T-170.evidence/T-170.check1_test_studio.txt .agentsflower/tasks/.runtime/T-170.evidence/T-170.check2_full_suite.txt .agentsflower/tasks/.runtime/T-170.evidence/T-170.check2_full_suite_rerun.txt .agentsflower/tasks/.runtime/T-170.evidence/T-170.check2_watchdog_isolated.txt
New defects (outside the task):
- None in scope. Unrelated observation: the analytics iframe requests /dashboard/out/graph.html which 404s in a checkout where the dashboard was never built (pre-existing, not part of the Model Quota Hub view).
Cannot verify, needs:
- Real OpenRouter credentials cannot be used (keys must not be requested or stored); the flow was verified end-to-end through the identical OpenAI-compatible /models code path (fetch_provider_models), and OpenRouter defaulting (kind -> https://openrouter.ai/api/v1) was confirmed in the modal code and markup.
Proposed memory updates:
- The known-issues orphan-fixture flake (2026-10-24) recurred under a full-suite run as a watchdog "managed processes still run" refusal on PID 66888 (notepad.exe); recurrence supports prioritizing fixture teardown hardening or serializing those tests.
