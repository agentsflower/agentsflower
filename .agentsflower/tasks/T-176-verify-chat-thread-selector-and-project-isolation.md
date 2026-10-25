# T-176: Verify Chat Thread Selector, Folder Grouping, Project Isolation, and Inactive Probing Bypass

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-175
Independent check: none
Resume: none
Verifies: T-175 @ e3ab0ecb3002e45abdaee909580147c73052654e
Routing exception: human authorized chat thread selector folder grouping and per-project capacity probing verification (2026-10-25)

## Goal

Independently verify T-175's implementation of the two-section thread selector with folder grouping, per-project scoping of researches and tasks, and CLI probe skipping for deactivated platforms.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-176.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-175-chat-thread-selector-folders-and-project-isolation.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Thread selector dropdown displays two distinct accented sections: `Researches` and `Implementations`.
- [ ] V-02: Researches section groups items under collapsible folders (`📁 <Folder>`) and supports creating folders.
- [ ] V-03: Implementations section cleanly groups tasks by stage with `T-XXX — Title` formatting and status pills.
- [ ] V-04: Research threads and tasks strictly reload per project without leaking across workspace boundaries.
- [ ] V-05: Deactivated platforms in `project-models.json` bypass CLI subprocess probes during capacity scanning.
- [ ] V-06: Analytics toolbar includes "Cost & ROI Dashboard" subtab displaying project-scoped Plan vs Fact telemetry.
- [ ] V-07: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-08: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result
Verified T-175 at e3ab0ecb3002e45abdaee909580147c73052654e in a disposable worktree checkout (this session's worktree, HEAD equals the Verifies SHA, tree clean). Both ## Checks commands were run verbatim; every criterion was confirmed by reading the implementation and the covering tests. The two-section selector, folder grouping, stage grouping, per-project isolation, deactivated-probe bypass, and the restored Cost & ROI subtab are all present and functionally wired, not just markup.
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (112 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (616 passed / 0 failed, 4 skipped; first verbatim run hit one transient fixture failure, clean pass on rerun - details below)
Criteria:
- V-01: pass - fillThreadList builds two sections via buildThreadSection: 'researches-header' titled with a count badge and '+ New'/folder actions, and 'implementations-header' titled with a count badge; CSS gives them distinct accents (blue rgba(19,78,158) vs emerald rgba(16,185,129)) inside a glassmorphism dropdown with a top search row - evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css, .agentsflower/tasks/.runtime/T-176.evidence/T-176.criteria.txt
- V-02: pass - buildFolderGroup renders collapsible 'thread-folder-group' items headed by a folder icon plus name and count (caret rotates on collapse via aria-expanded); the section '+ Folder' action runs addResearchFolder which creates a folder entry that appears even while empty, and the inspector folder select merges session folders and persists assignment through updateResearchThread - evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css, .agentsflower/tasks/.runtime/T-176.evidence/T-176.criteria.txt
- V-03: pass - groupTasksByStage sorts numeric stage keys and buildStageGroup renders collapsible 'Stage 0N - label' groups; each task item renders the 'T-XXX -' id span, a title span, and a status badge via threadStatusClass - evidence: .agentsflower/studio/studio.js, .agentsflower/tasks/.runtime/T-176.evidence/T-176.criteria.txt
- V-04: pass - switchProject resets state.threads, state.researchMeta and state.researchFolders, then awaits loadResearchThreads(path) alongside loadTasks(path); all research calls carry the project parameter; server side resolve_known_project only serves registered project roots and research_store_dir scopes strictly under the target project's flow state/research dir; test test_research_threads_scoped_per_project proves project B sees none of A's threads and a B update never writes into A's store - evidence: .agentsflower/studio/studio.js, .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py, .agentsflower/tasks/.runtime/T-176.evidence/T-176.criteria.txt
- V-05: pass - probe_capacity reads project state first; bulk path excludes enabled-false platforms from the probe thread list and returns a deactivated record with enabled False and the 'probe skipped' note, the ?platform= path returns the same record without calling _single_platform_probe, and _probe_provider with live_probe False skips the /models request; covering tests assert no deactivated argv reaches _probe_run and no provider request fires - evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py, .agentsflower/tasks/.runtime/T-176.evidence/T-176.criteria.txt
- V-06: pass - btnSubtabCosts with data-sub="costs" and the costRoiDashboard panel (summary cards, stage bar, stage filter, Plan vs Fact task table) are restored; updateAnalyticsFrame shows the panel on the costs subtab and loadCostAnalytics fetches the project-scoped /api/analytics/costs endpoint, which get_analytics_costs resolves per project root - evidence: .agentsflower/studio/index.html, .agentsflower/studio/studio.js, .agentsflower/tools/studio.py, .agentsflower/tasks/.runtime/T-176.evidence/T-176.criteria.txt
- V-07: pass - 112 tests ran with zero failures - evidence: .agentsflower/tasks/.runtime/T-176.evidence/T-176.test-studio.txt
- V-08: pass - rerun of the verbatim full suite: 616 tests, 0 failures, 4 skipped; the first run's only failure (test_run_task.test_manual_attempt_records_requested_model_and_unknown_runtime, PermissionError WinError 5 on an os.replace inside a disposable temp fixture) is the documented transient Windows flake class, also passed standalone, and is unrelated to this diff (flake already recorded in known-issues) - evidence: .agentsflower/tasks/.runtime/T-176.evidence/T-176.checks.txt, .agentsflower/tasks/.runtime/T-176.evidence/T-176.full-suite.txt
New defects (outside the task):
- none new; the WinError 5 os.replace flake under full-suite load is already recorded in known-issues (2026-10-16/10-18 entries on ledger.py _write_atomic)
Cannot verify, needs:
- nothing; every criterion was checkable in this environment
Proposed memory updates:
- none
