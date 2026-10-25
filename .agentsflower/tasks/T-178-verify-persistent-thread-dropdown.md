# T-178: Verify Persistent Thread Dropdown Behavior

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-177
Independent check: none
Resume: none
Verifies: T-177 @ d1102618b2b052509da71c2a289369317e21c952
Routing exception: human authorized persistent chat dropdown verification (2026-10-26)

## Goal

Independently verify T-177's persistent dropdown behavior: thread selection switches active chat without closing the menu, and the dropdown closes only on blur, outside click, Escape, or toggle pill click.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-178.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-177-persistent-thread-dropdown-on-selection.md
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- none

## Acceptance criteria

- [ ] V-01: Selecting a thread in `#threadDropdown` switches active thread and updates `.thread-item.active` without collapsing the dropdown.
- [ ] V-02: Dropdown closes when clicking outside `#threadSelector`, pressing Escape, or clicking `#threadPill`.
- [ ] V-03: Unit test suite passes: `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"`.
- [ ] V-04: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result
Outcome: completed
Verdict: pass
Checked a disposable detached checkout of T-177 @ d1102618b2b052509da71c2a289369317e21c952; the worktree stayed clean and no product files were touched. Beyond the contract unit tests, the real .agentsflower/studio/studio.js was executed in Node 22 under a minimal DOM stub built for this review (event bubbling, selector queries, innerHTML parsing), driving 22 behavioral assertions on #threadSelector / #threadDropdown / #threadPill; all passed.
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (115 passed / 0 failed) - evidence: .agentsflower/tasks/.runtime/T-178.evidence/T-178.check1_test_studio.txt
- `python -m unittest discover -s .agentsflower/tests` -> pass (619 ran / 0 failed, 4 skipped; the documented Windows temp-fixture flake did not occur) - evidence: .agentsflower/tasks/.runtime/T-178.evidence/T-178.check2_full_suite.txt
Criteria:
- V-01: pass - dynamic run: clicking the research-002 and T-901 .thread-item entries kept threadSelector.open, moved .active onto the clicked button on the same element objects (no dropdown rebuild), refreshed the #threadPill label and rendered the selected thread in the inspector; code review of selectThread confirms no closeThreadDropdown/renderThreadDropdown call - evidence: .agentsflower/tasks/.runtime/T-178.evidence/T-178.dom_check.txt
- V-02: pass - dynamic run: outside document click, Escape inside the dropdown (closes and refocuses the pill), Escape on the pill, and #threadPill click each closed the dropdown; focusout to an element inside #threadSelector or with null relatedTarget kept it open, focusout to an outside element closed it - evidence: .agentsflower/tasks/.runtime/T-178.evidence/T-178.dom_check.txt .agentsflower/tasks/.runtime/T-178.evidence/T-178.dom_check.js
- V-03: pass - 115 tests green - evidence: .agentsflower/tasks/.runtime/T-178.evidence/T-178.check1_test_studio.txt
- V-04: pass - 619 tests green, 4 skipped - evidence: .agentsflower/tasks/.runtime/T-178.evidence/T-178.check2_full_suite.txt
New defects (outside the task):
- none
Cannot verify, needs:
- none; one noted behavior (not a defect): the focusout handler deliberately ignores null relatedTarget - window blur, prompt() dialogs and detached nodes - matching T-177's documented "found, not fixed" note; plain outside clicks still close via the document listener, so the close-only-on contract holds.
Proposed memory updates:
- none
