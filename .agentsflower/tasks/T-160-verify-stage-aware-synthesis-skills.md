# T-160: Verify Stage-Aware Task Synthesis and Autonomous Skills Mapping

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-159
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-159 @ 142d600be8fa7af6ca356d01b6ebee839b33735b

## Goal

Independently verify T-159 (Stage-aware task pool synthesis and autonomous skills mapping) against the T-159 contract:

1. Serve Studio from the T-159 candidate worktree.
2. Exercise `POST /api/task/synthesize` with frontend and SEO prompts; verify generated stages and assigned skills.
3. Verify Task Pool Card rendering in UI with skill badges.
4. Verify batch registration creates Task Files carrying `Skills:` headers.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-159-stage-aware-task-synthesis-and-skills.md
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

- [ ] V-01: `/api/task/synthesize` assigns sequential stage numbers matching dependency order.
- [ ] V-02: Relevant skills are correctly identified and attached to task items.
- [ ] V-03: Registered Task Files carry valid `Skills:` fields.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Verdict: pass
Checked T-159 at commit 142d600be8fa7af6ca356d01b6ebee839b33735b on a detached, clean checkout. Studio was served live from this worktree on 127.0.0.1:8913; both Checks ran verbatim, and synthesize plus pool registration were exercised over real HTTP. Batch registration ran against a disposable probe project under worktrees/ (auto-discovered by find_projects) so no real ledger or task folder was touched; the probe was deleted afterwards and `git status` stayed clean.
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (74 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass on verbatim rerun (578 ran, 4 skipped / 0 failed); the first verbatim run reported 2 transient failures in test_done_gate fixture projects (PermissionError WinError 5 on os.replace inside ledger.py _write_atomic, the documented 2026-10-18 flake), both green in isolated rerun and absent in the clean full rerun
Criteria:
- V-01: pass - three live POST /api/task/synthesize calls returned strictly sequential stage numbers (1-4, 1-3 and 1-2 task chains) and every depends reference pointed at a task in a strictly lower stage, no inversions; evidence: .agentsflower/tasks/.runtime/T-160.evidence/T-160.synthesize_frontend.json .agentsflower/tasks/.runtime/T-160.evidence/T-160.synthesize_seo.json .agentsflower/tasks/.runtime/T-160.evidence/T-160.synthesize_mv3.json
- V-02: pass - all four contract mappings observed live against skills/INDEX.md: frontend-art-direction on HTML/CSS/UI items, geo-seo-audit on llms.txt and schema.org/OpenGraph items, perf-benchmark on the latency benchmark item, chrome-extension-mv3 on manifest.json/service-worker items; evidence: .agentsflower/tasks/.runtime/T-160.evidence/T-160.synthesize_frontend.json .agentsflower/tasks/.runtime/T-160.evidence/T-160.synthesize_seo.json .agentsflower/tasks/.runtime/T-160.evidence/T-160.synthesize_mv3.json
- V-03: pass - real POST /api/task/pool/register wrote four Task Files, each carrying a valid Skills header (frontend-art-direction) plus matching stage and dependency fields, and the probe ledger rows preserved skills= in Notes; evidence: .agentsflower/tasks/.runtime/T-160.evidence/T-160.pool_register_response.json .agentsflower/tasks/.runtime/T-160.evidence/T-160.registered_task_file_T-176.md .agentsflower/tasks/.runtime/T-160.evidence/T-160.probe_ledger_tasks.md
- V-04: pass - evidence: .agentsflower/tasks/.runtime/T-160.evidence/T-160.check1_test_studio.txt .agentsflower/tasks/.runtime/T-160.evidence/T-160.check2_full_suite_rerun.txt .agentsflower/tasks/.runtime/T-160.evidence/T-160.check2_full_suite.txt .agentsflower/tasks/.runtime/T-160.evidence/T-160.check2_failed_tests_rerun.txt
The Task Pool Card UI goal item (not a numbered criterion) was verified at code level: served studio.js builds skill-badge skill-pill spans from t.skills inside .pool-task-top, served studio.css defines the styles at line 2708, and test_task_pool_card_ui_renders_skill_badges passed in check 1. No interactive browser automation was available for a visual screenshot.
New defects (outside the task):
- Cosmetic only: synthesized titles for list items after the second can keep their leading enumeration (e.g. "3. Wire the UI buttons..."), which also leaks into generated Task File names like T-175-3-wire-.... All metadata fields stay correct.
Cannot verify, needs:
- A rendered-browser screenshot of the skill pills; covered instead by served-asset markers and the passing UI unit test.
Proposed memory updates:
- known-issues: the 2026-10-18 ledger.py _write_atomic WinError 5 flake reproduced twice in one full-suite run on this checkout (test_done_gate fixture projects); isolated reruns pass and a clean full rerun passes. The suggested bounded os.replace-retry hardening remains open.
