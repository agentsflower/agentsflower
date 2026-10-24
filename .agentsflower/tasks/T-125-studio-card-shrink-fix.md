# T-125: Fix task card vertical shrink and title clipping in Studio Kanban

Role: developer
Tool: devin
Stage: 7
Depends on: T-121
Branch: t-125-studio-card-shrink-fix
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-125-studio-card-shrink-fix
Independent check: tester

## Goal

Fix the flexbox shrinkage bug in `.agentsflower/studio/studio.css` where `.task-card` elements inside `.cards-container` are compressed vertically (from ~95px down to ~24px) when a column contains many tasks (e.g. 23+ tasks in "Done & Merged"). Ensure all task cards maintain full natural height, multi-line titles, visible footers, and that columns scroll smoothly.

## Read first

- `.agentsflower/studio/studio.css`
- `.agentsflower/studio/studio.js`
- `.agentsflower/studio/index.html`

## Allowed files

- `.agentsflower/studio/studio.css`
- `.agentsflower/studio/studio.js`

## Do not touch

- `.agentsflower/tools/studio.py`
- `.agentsflower/tools/install.py`

## Acceptance criteria

- [ ] C-01: `.task-card` in `studio.css` specifies `flex-shrink: 0; min-height: fit-content;` preventing flex containers from compressing cards vertically.
- [ ] C-02: `.task-card-title` renders complete multi-line titles with proper line-height and word-break without text clipping.
- [ ] C-03: `.task-card-footer` displaying role tag and tool badge is always visible on all cards across all columns regardless of task count.
- [ ] C-04: `.cards-container` handles overflow with smooth vertical scrolling when card height exceeds the column viewport.

## Checks

- `python -m unittest discover -s .agentsflower/tests -p "test_skills.py"` - regression check

## Result

Outcome: completed
Criteria:
- C-01: pass - .task-card in studio.css has flex-shrink: 0 and min-height: fit-content preventing card compression in flex columns.
- C-02: pass - .task-card-title displays full multi-line title text with proper line-height (1.4) and word-break without clipping.
- C-03: pass - .task-card-footer with role tag and tool badge is consistently visible with flex-shrink: 0 across all columns.
- C-04: pass - .cards-container has min-height: 0 and overflow-y: auto, ensuring smooth vertical scrolling when card height exceeds the column viewport.

