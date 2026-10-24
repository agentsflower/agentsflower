# T-135: Verify Studio splitters, editor tabs, topnav cleanliness, and model selector

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-134 @ f5355b5941673a91ad1702f7d727f8e588aa5d9f
Branch: t-135-verify-studio-splitters-tabs-model-selector
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-135-verify-studio-splitters-tabs
Independent check: none
Resume: none

## Goal

Independently verify T-134 (Studio interactive enhancements: draggable splitters, editor file tabs, clean topnav, chat model selector) against the mockup 3 contract in `.agentsflower/mockups/README.md` (Section 5) and `.agentsflower/mockups/mockup-explorer-splitters-tabs.png`:

1. Run `test_studio.py` and the full test suite.
2. Serve the Studio from this worktree and verify the markup carries the contract elements: `#sidebarResizer` and `#chatResizer` with centered `||` `.resizer-grip`, `#editorTabsBar` above the code viewer, exactly 4 `data-tab` topnav items (Explorer, Task Board, Analytics & Roadmap, Model Quota Hub) with no horizontal scrollbar (`overflow-x: hidden`), and `#chatModelPill` with `#chatModelDropdown` listing the 5 contract models.
3. In `studio.js`, verify bounded drag logic (`PANE_LIMITS`: sidebar 200-450px, chat 320-650px), `localStorage` persistence keys `af_sidebar_width` / `af_chat_width` written and restored, `state.openTabs` tab open/switch/close behavior, and `CHAT_MODELS` containing `gemini-4-argon-high`, `claude-opus-4-6-thinking`, `gpt-5-5-high` plus the Local/Ollama option, with selection persisted (`af_chat_model`).
4. Where feasible, exercise the served page in a browser/DOM to confirm resizer drag, tab open/close, and dropdown toggle actually work; the mockup PNG lives in the main checkout `E:\Projects\AgentFlow\code` and is not part of the verified commit.
5. Judge the developer's "Found, not fixed" notes: `view-graft`/`view-guide` unreachable via topnav is a mockup-3 consequence, sidebar min 200px follows the Task File over the mockup's 220px - confirm neither contradicts the contract; flag if it does.
6. Record verdict in ## Result.

## Read first

- .agentsflower/tasks/T-134-studio-splitters-tabs-and-model-selector.md
- .agentsflower/mockups/README.md (in the main checkout E:\Projects\AgentFlow\code)
- .agentsflower/roles/tester.md

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- PORT=8901

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes.
- [ ] V-02: Full regression test suite passes without regressions.
- [ ] V-03: Served shell markup carries the mockup-3 interactive elements (two resizers with `||` grips, `#editorTabsBar`, exactly 4 topnav `data-tab` items, `#chatModelPill` + `#chatModelDropdown`).
- [ ] V-04: `studio.js` implements bounded splitter drag (200-450 / 320-650) with `af_sidebar_width`/`af_chat_width` persistence, `state.openTabs` tab lifecycle, and `CHAT_MODELS` with the 5 contract options.
- [ ] V-05: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (26 passed / 0 failed) - evidence: .agentsflower/tasks/.runtime/T-135.evidence/T-135.check1_test_studio.txt
- `python -m unittest discover -s .agentsflower/tests` -> fail (518 ran / 1 failed / 4 skipped, 349s); the sole failure test_run_task.RunTaskTests.test_wrong_grant_is_refused is the documented Windows fixture flake (PermissionError WinError 5 on os.replace of fixture tasks.md.tmp in setUp), unrelated to T-134's studio-only diff; it passes in isolated rerun - evidence: .agentsflower/tasks/.runtime/T-135.evidence/T-135.check2_full_suite.txt , .agentsflower/tasks/.runtime/T-135.evidence/T-135.check2_rerun_failed_test.txt
Criteria:
- V-01: pass - all 26 tests in test_studio.py pass on the verified commit f5355b5, including T-134's new marker tests (4 data-tab items, resizer/tabs-bar/dropdown HTML markers, persistence and model-id JS markers, topnav overflow-x hidden). evidence: .agentsflower/tasks/.runtime/T-135.evidence/T-135.check1_test_studio.txt
- V-02: pass - no regression: full suite ran 518 tests with 1 failure, the pre-existing test_run_task.py temp-fixture PermissionError flake already recorded in known-issues.md (hit T-132 the same way); the failed test passes in isolated rerun, and the verified commit touches only .agentsflower/studio/index.html, studio.css, studio.js and test_studio.py (git show --stat f5355b5). evidence: .agentsflower/tasks/.runtime/T-135.evidence/T-135.check2_full_suite.txt , .agentsflower/tasks/.runtime/T-135.evidence/T-135.check2_rerun_failed_test.txt
- V-03: pass - Studio served from this disposable checkout (python .agentsflower/tools/studio.py --port 8901): GET /, /studio.css, /studio.js all 200 and served bytes are identical to the worktree files. Served markup carries: #sidebarResizer (line 126) and #chatResizer (line 229), each with a centered `||` .resizer-grip span; #editorTabsBar (line 218) above the code viewer; exactly 4 data-tab topnav items - explorer (Explorer), kanban (Task Board), analytics (Analytics & Roadmap), capacity (Model Quota Hub) - with no junk nav tabs; .topnav-menu uses overflow-x:hidden (served studio.css:207); #chatModelPill + #chatModelDropdown inside .model-selector-wrap (lines 254-256). evidence: .agentsflower/tasks/.runtime/T-135.evidence/T-135.served_index.html , .agentsflower/tasks/.runtime/T-135.evidence/T-135.served_studio.css , .agentsflower/tasks/.runtime/T-135.evidence/T-135.dom_harness.txt
- V-04: pass - served studio.js: PANE_LIMITS sidebar 200-450 / chat 320-650; bindResizer clamps during drag and writes af_sidebar_width / af_chat_width to localStorage on mouseup, restorePaneWidths re-applies clamped values on init; state.openTabs lifecycle via openExplorerFile / renderEditorTabs / closeFileTab / resetExplorerPane; CHAT_MODELS = swe-2-high (Floor default), gemini-4-argon-high, claude-opus-4-6-thinking, gpt-5-5-high, local-ollama; selection persisted via sessionStorage af_chat_model (T-134 contracted "session state", so sessionStorage is correct). Exercised live in a jsdom-24 harness against the running server: 30/30 assertions - sidebar drag to 300px, clamps at 200/450, af_sidebar_width written; chat drag clamps at 320/650, af_chat_width written; tree click opens tab, second file opens 2nd tab, reopen switches without duplicating, close switches to previous tab, last close resets the viewer; pill click opens dropdown with 5 options, Claude selection updates the pill and stores af_chat_model, outside click closes. evidence: .agentsflower/tasks/.runtime/T-135.evidence/T-135.dom_harness.txt , .agentsflower/tasks/.runtime/T-135.evidence/T-135.served_studio.js
- V-05: pass - verdict is pass; all criteria verified on the detached-HEAD disposable checkout of f5355b5 (review isolation held: HEAD unchanged, worktree clean after the attempt).
Found, not fixed - contract judgment (task step 5):
- view-graft / view-guide unreachable via topnav: consistent with the contract, not a defect. mockups/README.md Section 5 mandates strictly 4 core topnav tabs and junk-tab removal; the two view-panels remain dormant in the DOM (hidden, no functional break) and view-creator stays reachable via btnQuickCreate / btnChatNew / btnChatPlus (studio.js:197, 288-289).
- Sidebar min 200px vs mockup's 220px: the T-134 Task File and this task's V-04 both specify 200-450px; the task contract supersedes the mockup README's generic 220px. Implementation matches the contract; the discrepancy is documentation-level only.
New defects (outside the task):
- none in the artifact. The test_run_task.py full-suite flake recurred here (PermissionError on fixture os.replace); already documented in known-issues.md.
Cannot verify, needs:
- Real-browser rendering was not exercised (no browser automation in this environment); behavior was verified in jsdom with getBoundingClientRect stubbed for the chat pane (jsdom returns zero rects). Drag math, clamping, persistence writes, tab lifecycle and dropdown logic all executed against the live served page; pixel-level appearance in a real browser remains unchecked.
Proposed memory updates:
- none
