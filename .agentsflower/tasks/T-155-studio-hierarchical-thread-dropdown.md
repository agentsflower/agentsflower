# T-155: Studio Hierarchical Thread Switcher UI: Researches & Implementations

Role: developer
Tool: devin
Model: swe-2-high
Routing exception: human standing policy 2026-10-21 (model-options.json + questions.md): on low confidence evaluate the Devin catalog and take the adequate higher-confidence default instead of halting; devin/swe-2-high is the mandated floor. Jev option confidence 0.97 for devin-swe-2; only the effort-tier sub-question scored 0.46 while the requirement floor is already high.
Stage: 7
Depends on: T-154
Branch: t-155-studio-hierarchical-thread-dropdown
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-155-studio-hierarchical-thread-dropdown
Independent check: tester
Resume: none

## Goal

Replace the flat select dropdown in the Studio chat header with an interactive two-section hierarchical accordion matching the user's reference mockup:

1. **Collapsible Header Sections**:
   - Section 1: `🔍 Researches` (accent header `#134e9e`, item count badge, `+` create action, collapse caret).
   - Section 2: `Implementations` (accent header `#134e9e`, task count badge, collapse caret).
2. **Nested Stages in Implementations**:
   - Inside `Implementations`, group tasks by sequential stage (`Stage 01`, `Stage 02`...).
   - Each Stage group is collapsible, showing stage title and task count.
   - Tasks display formatted identity: `T-NNN — Short Title`.
3. **Selection State & Keyboard Navigation**:
   - Clicking an item sets `state.inspectorTaskId` and closes popup.
   - Active thread highlighted with blue accent border and pill.
   - Full keyboard accessibility (Arrow keys, Enter, Esc).
4. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing DOM elements, stage grouping logic, and click handlers.

## Read first

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/run_task.py
- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8905 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Thread selector renders two distinct collapsible sections: `🔍 Researches` and `Implementations`.
- [ ] C-02: Tasks in `Implementations` are grouped under collapsible `Stage XX` subheaders.
- [ ] C-03: Visual styling matches dark theme (`#060a12`, accent `#134e9e`) with smooth accordion transitions.
- [ ] C-04: Clicking any research or task item switches active chat thread.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Change: 772f3211e65442c28dd0d5810a274ec4cbd88773 on t-155-studio-hierarchical-thread-dropdown
Files:
- .agentsflower/studio/index.html - flat <select id="inspectorTaskSelect"> replaced by .thread-selector-wrap: #threadPill button (aria-haspopup/aria-expanded) + #threadDropdown role="menu"
- .agentsflower/studio/studio.js - hierarchical switcher: researchThreadIds/threadLabel/groupTasksByStage/stageLabel (Stage NN via padStart(2,'0')), buildThreadSection/buildStageGroup/buildThreadItem, state.threadCollapsed accordion state, selectThread sets state.inspectorTaskId and closes popup, addResearchThread behind the Researches '+' action, onThreadKeydown Arrow/Enter/Escape navigation, populateInspectorTasks now re-renders the accordion; renderInspector accepts research-* thread keys
- .agentsflower/studio/studio.css - .chat-task-select block replaced by .thread-* styles: #060a12 dropdown, #134e9e accent section headers and active pill, grid-template-rows 1fr/0fr accordion transitions, caret rotation on aria-expanded
- .agentsflower/tests/test_studio.py - stale 'id="inspectorTaskSelect"' marker swapped for threadSelector/threadPill; new TestHierarchicalThreadSwitcher (6 tests) covering shell DOM, two-section accordion, stage grouping, item click/selection handlers, keyboard nav, theme CSS
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (62 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (566 passed / 0 failed, 4 skipped)
Criteria:
- C-01: pass - renderThreadDropdown builds two collapsible sections data-section="researches" (count badge, '+' addResearchThread, caret) and data-section="implementations" in .agentsflower/studio/studio.js
- C-02: pass - groupTasksByStage + buildStageGroup render collapsible thread-stage-group groups with thread-stage-header "Stage NN" + task count in .agentsflower/studio/studio.js
- C-03: pass - .thread-dropdown background #060a12, #134e9e accent borders/headers, grid-template-rows transitions in .agentsflower/studio/studio.css
- C-04: pass - .thread-item click -> selectThread(id) sets state.inspectorTaskId, closeThreadDropdown, renderInspector in .agentsflower/studio/studio.js
- C-05: pass - TestHierarchicalThreadSwitcher in .agentsflower/tests/test_studio.py; both ## Checks commands green above
Found, not fixed:
- .chat-header-controls CSS rule is orphaned in studio.css (no matching markup); pre-existing since the T-149 header cleanup, outside this task's scope
Proposed memory updates:
- none
