# T-133: Verify Studio pixel-perfect mockup alignment

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-132 @ 14dcc0f52b93bf3fd46a1b86cb60798e08615869
Branch: t-133-verify-studio-pixel-perfect-mockup
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-133-verify-studio-pixel-perfect-mockup
Independent check: none
Resume: none

## Goal

Independently verify T-132 (Studio UI pixel-perfect implementation from the visual mockup contract):
1. Run `test_studio.py` and the full test suite.
2. Verify the rendered shell markup against the canonical mockup contract in `.agentsflower/mockups/README.md` (sections 1-4): horizontal topnav with `Explorer`/`Task Board (N)` pills + 5 sub-links, `ACTIVE WORKSPACE` sidebar with `+ Attach`/`+ New` and project accordion, Explorer dual-pane (line-numbered code viewer on `#111625` + Task Inception chat cockpit), Task Board stage pills + metrics row + 4 Kanban columns.
3. Verify the task payload exposes the `branch`, `worktree`, `model` fields parsed from task-file headers.
4. Where feasible, compare served pages against `.agentsflower/mockups/mockup-explorer.png` and `mockup-taskboard.png` (read them in the main checkout `E:\Projects\AgentFlow\code`; they are not part of the verified commit).
5. Record verdict in ## Result.

## Read first

- .agentsflower/tasks/T-132-studio-pixel-perfect-mockup-alignment.md
- .agentsflower/mockups/README.md (in the main checkout E:\Projects\AgentFlow\code)
- .agentsflower/roles/tester.md

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes.
- [ ] V-02: Full regression test suite passes without regressions (the developer reported two test_run_task.py environment flakes - orphaned fixture process - that pass in isolation; re-run and judge whether they are pre-existing environment noise or a T-132 regression).
- [ ] V-03: Served shell markup carries every contract element of mockups/README.md sections 1-4 (topnav pills/sub-links, sidebar accordion markers, explorer dual-pane markers, kanban pills/metrics/columns).
- [ ] V-04: The Studio tasks API payload includes `branch`, `worktree`, `model` for a task that declares them.
- [ ] V-05: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (21 passed / 0 failed) - evidence: .agentsflower/tasks/.runtime/T-133.evidence/T-133.check1_test_studio.txt
- `python -m unittest discover -s .agentsflower/tests` -> pass (513 ran / 0 failed / 0 errors / 4 skipped, 387s) - evidence: .agentsflower/tasks/.runtime/T-133.evidence/T-133.check2_full_suite.txt
Criteria:
- V-01: pass - all 21 tests in test_studio.py pass on the verified commit 14dcc0f, including the new TestStudioShell and dispatch-header tests. evidence: .agentsflower/tasks/.runtime/T-133.evidence/T-133.check1_test_studio.txt
- V-02: pass - the full suite is green on 14dcc0f (513 ran, 0 failed, 0 errors, 4 skipped); the two test_run_task.py flakes the developer reported did not reproduce at all here, confirming they were orphaned-fixture environment noise, not a T-132 regression (T-132 touched only studio files). evidence: .agentsflower/tasks/.runtime/T-133.evidence/T-133.check2_full_suite.txt
- V-03: pass - Studio served from this worktree (python .agentsflower/tools/studio.py --port 8899); GET / returned 200 and the served shell markup carries every mockups/README.md section 1-4 element: horizontal topnav with brand (AgentsFlower / Studio Cockpit v2.17.0), Explorer and Task Board pills with #taskTotalBadge, five icon sub-links (Analytics & Roadmap, Knowledge Graph, Model Quota Hub, Task Contract Creator, Quick Start Guide); sidebar with ACTIVE WORKSPACE, + Attach, + New, JS-rendered project accordion (green square active, "name - vX (N tasks)", v/^ carets, file tree with .agentsflower yellow/.claude purple/.gitignore orange/.md blue icon tints); Explorer dual-pane (breadcrumbs "proj > .agentsflower > VERSION > .." verified live, .cl/.ln line numbers 1-43, syntax tokens on #111625, JetBrains Mono) plus chat cockpit (user bubble, "Worked for 2m", exec card with Task ID/Role/Tool/Worktree/Status bullets, diff widget +add/-del, composer "Ask anything, @ to mention, / for actions", model pill "Devin swe-2-high", send); Task Board stage pills (All Stages active, 5/6/7), metrics row (112 Total white / 0 In Progress amber / 0 In Review purple / 83 Completed emerald) and 4 Kanban columns with colored dots and 112 rendered task cards (T-ID, Stage badge, title, role, tool). evidence: .agentsflower/tasks/.runtime/T-133.evidence/T-133.served_index.html , .agentsflower/tasks/.runtime/T-133.evidence/T-133.dom_accordion.html , .agentsflower/tasks/.runtime/T-133.evidence/T-133.dom_explorer.json , .agentsflower/tasks/.runtime/T-133.evidence/T-133.shot_kanban.png , .agentsflower/tasks/.runtime/T-133.evidence/T-133.shot_explorer.png , .agentsflower/tasks/.runtime/T-133.evidence/T-133.shot_kanban_1920.png
- V-04: pass - GET /api/tasks?project=<worktree> returned 200 with 112 tasks; every task object carries branch, worktree, model keys and 64 tasks have all three populated from task-file headers (e.g. T-001: branch=t-001-python-launcher-parity, model=swe-2-high, worktree=E:\Projects\AgentFlow\worktrees\agentflow-t-001-python-launcher-parity). evidence: .agentsflower/tasks/.runtime/T-133.evidence/T-133.api_tasks.json
- V-05: pass - verdict is pass; all criteria verified on the disposable detached-HEAD checkout of 14dcc0f (review isolation held: worktree clean, HEAD unchanged).
New defects (outside the task):
- .agentsflower/mockups/mockup-explorer.png and mockup-taskboard.png in the main checkout depict the pre-T-132 sidebar-navigation layout, and their contents do not match their filenames (mockup-taskboard.png shows the Model Quota Hub view; mockup-explorer.png shows the Knowledge Graph view). They are stale relative to the canonical mockups/README.md contract sections 1-4, which the served UI does match. Not part of the verified commit; flagged for the Orchestrator.
- Minor: .topnav-menu uses overflow-x:auto, so at <=1920px the last sub-links (Task Contract Creator partially, Quick Start Guide fully) sit off-screen until scrolled horizontally; all elements are present and reachable, consistent with the contract but not one-screen visible as in a wide mockup.
- Reading note: mockups/README.md section 4 lists the stage filter bar before the metrics row; the rendered order is metrics first, then stage pills. The criteria check presence of all elements, which is satisfied; flagged in case ordering was intended as contract.
Cannot verify, needs:
- nothing
Proposed memory updates:
- known-issues.md (2026-10-24): .agentsflower/mockups/*.png are stale (pre-T-132 sidebar-nav layout, filenames mismatched to content); README.md sections 1-4 are the living contract - consider regenerating the PNGs from the current served UI.
