# T-150: Verify Studio UI Strict Cleanup: Clean Topnav, Simplified Composer, and Header Suppression

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-149
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-149 @ d72d033b9ad7ead15def4b5a893698cff39049df

## Goal

Independently verify T-149 (Studio UI strict cleanup: removal of topnav search, new task, and chip; composer controls cleanup; embedded header suppression) against the T-149 contract:

1. Serve the Studio from the T-149 candidate worktree/branch.
2. Verify `.topnav` has only brand and 4 nav items; `#activeProjectChip`, `#globalSearchInput`, `#btnQuickCreate` are absent.
3. Verify `.composer-toolbar` contains only model selector, spacer, and send button; `#btnChatNew`, `#btnChatRefresh`, `#btnChatPlus`, `#btnSynthesizeTasks` are absent.
4. Verify embedded `#hdr` suppression in `dashboard/common.css` and `studio.js`.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-149-studio-ui-cleanup-and-mockup-alignment.md
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/dashboard/common.css
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

- [ ] V-01: Top navigation bar right side is clean (no search, no new task button, no project chip).
- [ ] V-02: Composer toolbar contains only model selector and send button.
- [ ] V-03: Embedded analytics frame suppresses duplicate `#hdr`.
- [ ] V-04: Full regression suite passes cleanly (`python -m unittest discover -s .agentsflower/tests`).

## Checks

- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` - proves V-01, V-02, V-03 partially via updated DOM contract tests
- `python -m unittest discover -s .agentsflower/tests` - proves V-04

## Result

<!-- Worker writes its outcome below this block -->

Outcome: completed
Verdict: pass
Checked: T-149 @ d72d033b9ad7ead15def4b5a893698cff39049df (HEAD of this disposable checkout; tree clean)
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (44 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (548 ran: 544 passed / 4 skipped / 0 failed)
Criteria:
- V-01: pass - `.topnav` in `.agentsflower/studio/index.html` holds only `.brand-header` and `.topnav-menu` with exactly 4 `data-tab` items (explorer, kanban, analytics, capacity); `activeProjectChip`, `globalSearchInput`, `btnQuickCreate`, `search-box` absent. Served Studio on 127.0.0.1:8899 and grepped the live DOM: 0 hits for all removed ids. evidence: .agentsflower/tasks/.runtime/T-150.evidence/T-150.served_index.html, .agentsflower/tasks/.runtime/T-150.evidence/T-150.check1_test_studio.txt
- V-02: pass - `.composer-toolbar` contains only `#chatModelSelector` (model pill + dropdown wrap), `.composer-spacer`, and `#btnChatSend`; `.chat-header` contains only `#inspectorTaskSelect`. `btnChatNew`, `btnChatRefresh`, `btnChatPlus`, `btnSynthesizeTasks` absent from served DOM (0 hits). evidence: .agentsflower/tasks/.runtime/T-150.evidence/T-150.served_index.html
- V-03: pass - `dashboard/common.css:62-66` has `html[data-embedded] #hdr{display:none!important;margin:0!important}` with `.fbcard` pinned to `grid-row:1;margin-top:0!important` so the Filter Bar renders at top; `studio.js:449-462` sets `data-embedded` on the frame documentElement and `#hdr.style.display='none'` inside try/catch on `analyticsFrame` load. Contract tests `test_studio_js_embedded_query_and_dashboard_bridge` and `test_dashboard_embedded_hides_hdr_and_dark_palette` pass. evidence: .agentsflower/tasks/.runtime/T-150.evidence/T-150.check1_test_studio.txt
- V-04: pass - full suite: `Ran 548 tests in 367.550s`, `OK (skipped=4)`, 0 failures. evidence: .agentsflower/tasks/.runtime/T-150.evidence/T-150.check2_full_suite.txt
Notes:
- Every remaining reference to removed elements in `studio.js` is null-guarded (`if (btnQuickCreate)`, `if (globalSearchInput)`, `if (activeProjectChip)`, `if (btnChatNew)` etc.), so no console errors from removed controls; matches T-149 C-04 claim.
- Studio was served on port 8899 (task declares no port; 8888 left untouched).
New defects (outside the task):
- none observed
Cannot verify, needs:
- nothing
Proposed memory updates:
- none
