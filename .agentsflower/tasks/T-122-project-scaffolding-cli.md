# T-122: Project Scaffolding CLI & Template Engine

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-120
Branch: t-122-project-cli
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-122-project-cli
Independent check: tester
Resume: none
Routing exception: human authorized via AgentsFlower Studio (2026-10-24)

## Goal

Provide a dedicated CLI interface for workspace and project management in AgentsFlower:
1. Implement `agentsflower project list` to list all discovered and attached workspaces with version and task metrics.
2. Implement `agentsflower project attach <path>` to register any existing local folder into the Studio registry.
3. Implement `agentsflower project new <path> [--name <name>]` to scaffold a fresh project from the current AgentsFlower template.
4. Implement `agentsflower project update <path>` to upgrade a target project to the latest AgentsFlower version.
5. Provide unit tests in `.agentsflower/tests/test_project_cli.py`.

## Read first

- .agentsflower/docs/ai-handoff-protocol.md
- .agentsflower/tools/install.py
- .agentsflower/tools/cli.py

## Allowed files

- .agentsflower/tools/cli.py
- .agentsflower/tools/install.py
- .agentsflower/tests/test_project_cli.py
- .agentsflower/state/tasks.md
- .agentsflower/state/current-step.md

## Do not touch

- All other files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] C-01: `agentsflower project list` displays registered workspaces and their template version in terminal table.
- [ ] C-02: `agentsflower project attach <path>` validates folder and saves to attached registry.
- [ ] C-03: `agentsflower project new <path>` scaffolds a complete AgentsFlower project using template-owned files.
- [ ] C-04: `agentsflower project update <path>` invokes installer update safely.
- [ ] C-05: Unit tests in `test_project_cli.py` pass cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_project_cli.py"

## Result

<!-- Worker writes its outcome below this block -->
