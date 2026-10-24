# T-133: Verify Studio pixel-perfect mockup alignment

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-132 @ 14dcc0f52b93bf3fd46a1b86cb60798e08615869
Branch: t-133-verify-studio-pixel-perfect-mockup
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-133-verify-studio-pixel-perfect-mockup
Independent check: none
Resume: none

## Goal

Independently verify T-132 (Studio UI pixel-perfect implementation from the visual mockup contract):
1. Run `test_studio.py` and the full test suite.
2. Verify the rendered shell markup against the canonical mockup contract in `.agentsflower/mockups/README.md` (sections 1-4): horizontal topnav with `Explorer`/`Task Board (N)` pills + 5 sub-links, `ACTIVE WORKSPACE` sidebar with `+ Attach`/`+ New` and project accordion, Explorer dual-pane (line-numbered code viewer on `#111625` + Task Inception chat cockpit), Task Board stage pills + metrics row + 4 Kanban columns.
3. Verify the task payload exposes the `branch`, `worktree`, `model` fields parsed from task-file headers.
4. Where feasible, compare served pages against `.agentsflower/mockups/mockup-explorer.png` and `mockup-taskboard.png` (read them in the main checkout `E:\Projects\AgentFlow\code`; they are not part of the verified commit).
5. Record verdict in ## Result.

## Read first

- .agentsflower/tasks/T-132-studio-pixel-perfect-mockup-alignment.md
- .agentsflower/mockups/README.md (in the main checkout E:\Projects\AgentFlow\code)
- .agentsflower/roles/tester.md

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes.
- [ ] V-02: Full regression test suite passes without regressions (the developer reported two test_run_task.py environment flakes - orphaned fixture process - that pass in isolation; re-run and judge whether they are pre-existing environment noise or a T-132 regression).
- [ ] V-03: Served shell markup carries every contract element of mockups/README.md sections 1-4 (topnav pills/sub-links, sidebar accordion markers, explorer dual-pane markers, kanban pills/metrics/columns).
- [ ] V-04: The Studio tasks API payload includes `branch`, `worktree`, `model` for a task that declares them.
- [ ] V-05: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
