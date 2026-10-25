# T-156: Verify Studio Hierarchical Thread Switcher UI

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-155
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-155 @ 772f3211e65442c28dd0d5810a274ec4cbd88773

## Goal

Independently verify T-155 (Studio hierarchical thread switcher dropdown with Researches and Implementations sections) against the T-155 contract:

1. Serve Studio from the T-155 candidate worktree.
2. Verify visual appearance matches reference mockup (Researches header, Implementations header, nested Stages).
3. Test expanding and collapsing each section and stage block.
4. Verify clicking items loads the respective chat/task context.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-155-studio-hierarchical-thread-dropdown.md
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
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

- [ ] V-01: Dropdown displays two primary collapsible headers (`🔍 Researches` and `Implementations`).
- [ ] V-02: Tasks correctly render nested inside collapsible Stage blocks.
- [ ] V-03: Switching threads updates chat stream context.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (62 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (566 passed / 0 failed, 4 skipped)
Criteria:
- V-01: pass - live DOM via headless Chrome CDP against Studio on :8905: .thread-section[data-section="researches"] header "Researches" with count badge 1, '+' add button, caret; .thread-section[data-section="implementations"] header "Implementations" with count badge 152, caret; both aria-expanded toggles work. evidence: .agentsflower/tasks/.runtime/T-156.evidence/T-156.cdp_results.json, .agentsflower/tasks/.runtime/T-156.evidence/T-156.cdp_results2.json, .agentsflower/tasks/.runtime/T-156.evidence/T-156.explorer-dropdown-expanded.png
- V-02: pass - 3 .thread-stage-group blocks (Stage 05 - 69 items, Stage 06 - 31, Stage 07 - 52) nested inside Implementations, each with .thread-stage-header "Stage NN" + task count; items render "T-NNN — Title". Collapse then expand of stage groups verified live: collapsed class + aria-expanded=false + grid-template-rows 0fr, re-expands to 1fr. evidence: .agentsflower/tasks/.runtime/T-156.evidence/T-156.cdp_results.json, .agentsflower/tasks/.runtime/T-156.evidence/T-156.cdp_results2.json
- V-03: pass - selectTask: click on item T-028 changed pill to "T-028 — Trustworthy lifecycle: ...", dropdown closed (aria-expanded=false), chatStream innerText changed from research thread to T-028 thread context; selectResearch click on research item switched back, stream changed again. evidence: .agentsflower/tasks/.runtime/T-156.evidence/T-156.cdp_results.json
- V-04: pass - both ## Checks commands run verbatim at commit 772f3211e65442c28dd0d5810a274ec4cbd88773, all green. evidence: .agentsflower/tasks/.runtime/T-156.evidence/T-156.checks-transcript.txt
Beyond contract (verified while checking): full keyboard navigation works in the visible Explorer view (cdp_results5.json): ArrowDown/ArrowUp move focus across headers/items, Enter activates focused element, Escape closes dropdown and refocuses the pill, ArrowLeft/ArrowRight collapse/expand stage groups; '+' creates and selects a new research-N thread; theme confirmed via computed styles (dropdown background rgb(6,10,18)=#060a12, #134e9e accent border on section headers, 0.2s grid-template-rows transitions)
New defects (outside the task):
- none observed beyond the orphaned .chat-header-controls CSS rule already reported by the developer
Cannot verify, needs:
- nothing
Proposed memory updates:
- none
