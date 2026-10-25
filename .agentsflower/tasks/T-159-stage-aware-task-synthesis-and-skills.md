# T-159: Stage-Aware Task Pool Synthesis and Autonomous Skills Mapping

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: T-158
Branch: t-159-stage-aware-task-synthesis-and-skills
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-159-stage-aware-task-synthesis-and-skills
Independent check: tester
Resume: none

## Goal

Enhance `/api/task/synthesize` in `studio.py` to automatically group synthesized tasks into sequential Stages and map specialized skills:

1. **Stage Topology Assignment**:
   - Analyze dependencies between decomposed discussion items.
   - Assign tasks to sequential stages (`Stage 01`, `Stage 02`...) so prerequisite tasks precede dependent tasks in lower stage numbers.
2. **Autonomous Skills Mapping**:
   - Inspect AST blast radius affected files and task goal keywords against `.agentsflower/skills/INDEX.md`:
     - CSS/HTML/UI aesthetic files -> `Skills: frontend-art-direction`
     - Chrome extension / manifest files -> `Skills: chrome-extension-mv3`
     - SEO / metadata / llms.txt -> `Skills: geo-seo-audit`
     - Performance / benchmarks -> `Skills: perf-benchmark`
   - Attach mapped skills to task metadata (`skills` array in Task Pool Card and generated Task File).
3. **Task Pool Card UI Enhancements**:
   - Render mapped skill badges alongside effort and model badges in each task item.
4. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` verifying stage grouping logic, skills matching heuristics, and payload shape.

## Read first

- .agentsflower/tools/studio.py
- .agentsflower/skills/INDEX.md
- .agentsflower/studio/studio.js
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/tools/studio.py
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/gate.py

## Setup

- none

## Port

- 8909 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: `/api/task/synthesize` returns tasks organized into ordered `stage` numbers without dependency inversions.
- [ ] C-02: AST Blast Radius and task descriptions are automatically matched against skills in `skills/INDEX.md`.
- [ ] C-03: Task Pool Card in chat displays assigned skill pills.
- [ ] C-04: Batch task ledger registration preserves assigned `Skills:` in generated Task Files.
- [ ] C-05: Unit tests in `test_studio.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Change: 142d600be8fa7af6ca356d01b6ebee839b33735b on t-159-stage-aware-task-synthesis-and-skills
Files:
- .agentsflower/tools/studio.py - added stage topology dependency analysis (`_infer_item_phase`, `_assign_stage_topology`), autonomous skills mapping against `skills/INDEX.md` (`_load_skills_catalog`, `map_task_skills`), and `Skills:` field preservation in `register_task_pool`
- .agentsflower/studio/studio.js - updated `createTaskPoolCardElement` to render formatted stage labels and `.skill-badge.skill-pill` badges alongside effort and model badges
- .agentsflower/studio/studio.css - added `.skill-badge` and `.skill-pill` pill styles in the Task Pool Card section
- .agentsflower/tests/test_studio.py - added unit tests verifying stage topology ordering without inversions, skills mapping heuristics and AST blast radius matching, `Skills:` preservation in registered Task Files, and UI skill badge markers
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (74 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (574 passed, 4 skipped / 0 failed)
Criteria:
- C-01: pass - evidence: .agentsflower/tools/studio.py .agentsflower/tests/test_studio.py
- C-02: pass - evidence: .agentsflower/tools/studio.py .agentsflower/tests/test_studio.py
- C-03: pass - evidence: .agentsflower/studio/studio.js .agentsflower/studio/studio.css .agentsflower/tests/test_studio.py
- C-04: pass - evidence: .agentsflower/tools/studio.py .agentsflower/tests/test_studio.py
- C-05: pass - evidence: .agentsflower/tests/test_studio.py
Found, not fixed:
- none
Proposed memory updates:
- none
