# T-149: Studio UI Strict Cleanup: Strip Redundant Topnav & Chat Controls, Suppress Embedded Duplicate Header

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: none
Verifies: none
Branch: t-149-studio-ui-cleanup-and-mockup-alignment
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-149-studio-ui-cleanup-and-mockup-alignment
Independent check: tester
Resume: none
Routing exception: human mandated devin with gemini-4-argon-high for pixel-perfect mockup alignment (2026-10-25)

## Goal

Align AgentsFlower Studio strictly with the user's visual markup and reference UI mockups (Images 1-4):

1. **Top Navigation Right Side Cleanup (Image 1 & Image 4)**:
   - In `.agentsflower/studio/index.html`: Completely remove the right-side controls from `<header class="topnav">`:
     - Remove `#activeProjectChip` (`<span class="active-project-chip" id="activeProjectChip">`)
     - Remove `.search-box` and `#globalSearchInput` (`<input type="text" id="globalSearchInput" placeholder="Filter tasks, symbols, criteria...">`)
     - Remove `#btnQuickCreate` (`<button class="btn btn-primary" id="btnQuickCreate"><span>New Task</span></button>`)
   - The top navigation bar must have ONLY the brand on the left (`AgentsFlower Studio Cockpit v2.17.0`) and the 4 central navigation items (`Explorer`, `Task Board [N]`, `Analytics & Roadmap`, `Model Quota Hub •`), with the right side completely clean per Image 4.
   - In `.agentsflower/studio/studio.js`: safely guard or remove references to `globalSearchInput`, `btnQuickCreate`, and `activeProjectChip` without runtime errors.

2. **Chat & Inception Panel Cleanup (Image 2)**:
   - In `.agentsflower/studio/index.html`:
     - In `.chat-header`: Remove `#btnChatNew` (`+` button to the left of `#inspectorTaskSelect`) and `#btnChatRefresh` (reload button on the right).
     - In `.composer-toolbar`: Remove `#btnChatPlus` (`+` context attachment button) and remove `#btnSynthesizeTasks` (`✨ Synthesize Tasks from Discussion`).
   - The composer toolbar must cleanly contain only `#chatModelSelector` (model pill dropdown), `.composer-spacer`, and `#btnChatSend` (send message button).
   - In `.agentsflower/studio/studio.js`: remove or safely guard event listeners and bindings for `#btnChatNew`, `#btnChatRefresh`, `#btnChatPlus`, and `#btnSynthesizeTasks`.

3. **Analytics & Roadmap Embedded Header Suppression (Image 3 & Image 4)**:
   - Ensure the internal `#hdr` (`AgentsFlower - Tasks ... Overview Gantt & timeline Roadmap Built ... [sun]`) is 100% hidden when viewed inside the Studio cockpit.
   - In `.agentsflower/studio/studio.js`: On `analyticsFrame` load event, guarantee suppression by setting `contentDocument.getElementById('hdr').style.display = 'none'` (with try/catch for cross-frame safety) so even projects with existing or older dashboard files never show the duplicate header bar.
   - In `.agentsflower/dashboard/common.css`: Ensure `html[data-embedded] #hdr { display: none !important; }` and zero top margin so the Filter Bar (`.fbcard`) renders directly at the top of the analytics container.
   - The Studio Analytics toolbar (`Tasks & Overview`, `Gantt & Dependency Graph`, `Roadmap & Milestones`, `Built <ts>`, theme toggle `[sun]`, `Rebuild Analytics`, `Open Fullscreen`) remains the sole top chrome for the view.

4. **Automated Tests & Quality Gate**:
   - Update `.agentsflower/tests/test_studio.py` to reflect the removed elements (`btnQuickCreate`, `btnSynthesizeTasks`, `btnChatNew`, `btnChatRefresh`, `btnChatPlus`, `search-box`) and verify the clean DOM contract.
   - Ensure all tests in `test_studio.py` pass without regression.
   - Ensure the entire suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.css
- .agentsflower/studio/studio.js
- .agentsflower/dashboard/common.css
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.css
- .agentsflower/studio/studio.js
- .agentsflower/dashboard/common.css
- .agentsflower/tests/test_studio.py

## Do not touch

- Any files outside studio, dashboard common.css, and studio tests.

## Setup

- none

## Port

- 8888 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Topbar right actions (`activeProjectChip`, `search-box`, `btnQuickCreate`) are removed; topnav right side is clean per Image 4.
- [ ] C-02: Chat panel controls (`btnChatNew`, `btnChatRefresh`, `btnChatPlus`, `btnSynthesizeTasks`) are removed per Image 2.
- [ ] C-03: Analytics iframe duplicate header `#hdr` is completely hidden and Filter Bar aligns directly at top per Image 3 & Image 4.
- [ ] C-04: Studio operates without JavaScript console errors from removed element references.
- [ ] C-05: Unit tests in `test_studio.py` pass without regressions.
- [ ] C-06: Full test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: d72d033 on t-149-studio-ui-cleanup-and-mockup-alignment
Files:
- .agentsflower/studio/index.html - removed topnav right-side actions (`#activeProjectChip`, `.search-box`, `#globalSearchInput`, `#btnQuickCreate`) and chat/composer buttons (`#btnChatNew`, `#btnChatRefresh`, `#btnChatPlus`, `#btnSynthesizeTasks`)
- .agentsflower/studio/studio.css - suppressed removed topnav action classes (`display: none !important`)
- .agentsflower/studio/studio.js - guarded `globalSearchInput` listener and added explicit `#hdr` display suppression and `data-embedded` attribute enforcement on `analyticsFrame` load
- .agentsflower/dashboard/common.css - enforced `html[data-embedded] #hdr{display:none!important;margin:0!important}` and `margin-top:0!important` on `.app` and `.fbcard`
- .agentsflower/tests/test_studio.py - updated Studio UI contract tests to verify absence of removed controls and presence of embedded `#hdr` suppression
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (44 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (544 passed / 4 skipped / 0 failed)
Criteria:
- C-01: pass - removed `#activeProjectChip`, `.search-box`/`#globalSearchInput`, and `#btnQuickCreate` from `<header class="topnav">`; evidence: .agentsflower/studio/index.html, .agentsflower/studio/studio.css
- C-02: pass - removed `#btnChatNew`, `#btnChatRefresh`, `#btnChatPlus`, and `#btnSynthesizeTasks` so `.chat-header` holds `#inspectorTaskSelect` and `.composer-toolbar` holds `#chatModelSelector`, `.composer-spacer`, and `#btnChatSend`; evidence: .agentsflower/studio/index.html
- C-03: pass - enforced `html[data-embedded] #hdr{display:none!important;margin:0!important}` with zero top margin on `.app`/`.fbcard` and set `analyticsFrame.contentDocument.getElementById('hdr').style.display = 'none'` on frame load; evidence: .agentsflower/dashboard/common.css, .agentsflower/studio/studio.js
- C-04: pass - guarded `globalSearchInput` and removed-element listeners in `studio.js` so no null DOM reference throws at runtime; evidence: .agentsflower/studio/studio.js
- C-05: pass - all 44 tests in `test_studio.py` pass without regressions; evidence: .agentsflower/tests/test_studio.py
- C-06: pass - full test suite (`python -m unittest discover -s .agentsflower/tests`) passed 548 tests (544 passed, 4 skipped); evidence: .agentsflower/tests/test_studio.py
Found, not fixed:
- Transient `WinError 5` in `ledger.py _write_atomic` (`os.replace`) occurred once in `test_scenarios.test_scenario_bug_fix_simulated_worker` during the first full-suite run and passed on rerun (already tracked in `.agentsflower/state/known-issues.md`).
Proposed memory updates:
- none
