# T-180: Verify Thread Dropdown Stays Open on Header Toggles & Task Selection

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-179
Branch: t-179-fix-thread-dropdown-premature-collapse
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-179-fix-thread-dropdown-premature-collapse.t-180
Independent check: none
Resume: none
Verifies: T-179 @ 570b0d23cf4d022abf82925593c89c8cf70a2f83
Routing exception: human authorized thread dropdown collapse fixes verification (2026-10-26); standing policy 2026-10-21 (model-options.json): Jev low-confidence roll - option confidence 0.87 for devin-swe-2, only the effort-tier sub-question scored 0.39 while the requirement floor is already high and swe-2-high meets it

## Context

Independent verification of T-179: ensuring that clicking section headers (Researches, Implementations), stage headers, and task items inside `#threadDropdown` does NOT close the dropdown.

## Goal

Independently verify that `#threadDropdown` remains open when toggling sections/stages and selecting tasks, and closes only on outside click, Escape, or `#threadPill` toggle.

## Read first

- .agentsflower/tasks/T-179-fix-thread-dropdown-premature-collapse.md
- .agentsflower/studio/studio.js
- .agentsflower/studio/index.html
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Section headers (`Researches`, `Implementations`) toggle without collapsing `#threadDropdown`.
- [ ] V-02: Stage headers toggle without collapsing `#threadDropdown`.
- [ ] V-03: Clicking task items switches active task in inspector without collapsing `#threadDropdown`.
- [ ] V-04: `#threadDropdown` closes only when clicking outside `#threadSelector`, pressing Escape, or clicking `#threadPill`.
- [ ] V-05: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-06: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (118 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (622 passed / 0 failed, 4 skipped)
Criteria:
- V-01: pass - Researches/Implementations headers are built via buildThreadSection -> buildCollapsibleHeader (studio.js:2370); their click handler calls only toggleThreadCollapse (studio.js:2259), which flips state.threadCollapsed and re-renders via fillThreadList (studio.js:2389-2399) with no closeThreadDropdown call; the new stopPropagation listener (studio.js:2617) stops the click inside #threadDropdown before the document outside-click handler (studio.js:2618-2620), so the detached-node-after-rerender root cause can no longer misfire - evidence: .agentsflower/tasks/.runtime/T-180.evidence/T-180.code_review.txt
- V-02: pass - stage headers use the same buildCollapsibleHeader path (studio.js:2356, class thread-stage-header -> toggleThreadCollapse); identical non-closing flow as V-01 - evidence: .agentsflower/tasks/.runtime/T-180.evidence/T-180.code_review.txt
- V-03: pass - .thread-item click calls selectThread (studio.js:2292), which sets state.inspectorTaskId, toggles .active on the items, updates the pill and re-renders the inspector (studio.js:2496-2505); no closeThreadDropdown call and the click is stopped inside the dropdown - evidence: .agentsflower/tasks/.runtime/T-180.evidence/T-180.code_review.txt
- V-04: pass - all closeThreadDropdown callers enumerated: Escape inside the dropdown (studio.js:2568, 2586), Escape on #threadPill (2613), #threadPill click toggle (2605), document click with target outside #threadSelector (2619); the focusout handler (2621-2625) closes only when focus moves outside #threadSelector, i.e. an outside interaction, not an inside-click path - evidence: .agentsflower/tasks/.runtime/T-180.evidence/T-180.code_review.txt
- V-05: pass - 118 tests ran, OK, exit 0; includes TestThreadDropdownInsideClicks (3 tests added by T-179) - evidence: .agentsflower/tasks/.runtime/T-180.evidence/T-180.check1_test_studio.txt
- V-06: pass - 622 tests ran, OK (skipped=4), exit 0 - evidence: .agentsflower/tasks/.runtime/T-180.evidence/T-180.check2_full_suite.txt
New defects (outside the task):
- none observed
Cannot verify, needs:
- nothing
Proposed memory updates:
- none
