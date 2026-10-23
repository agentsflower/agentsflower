# T-114: Rebrand core template from agentflow to agentsflower

Role: developer
Tool: antigravity
Model: main
Stage: 6
Depends on: none
Branch: main
Worktree: none
Independent check: T-115
Resume: none
Routing exception: human authorized full rebranding to agentsflower (2026-10-23)

## Goal

Execute the full rebranding of the project from AgentFlow to AgentsFlower:
1. Rename folder `.agentflow/` -> `.agentsflower/`.
2. Rename package in `src/agentflow/` -> `src/agentsflower/` and update `pyproject.toml` (`name = "agentsflower-sdlc"`, CLI scripts: `agentsflower = "agentsflower.cli:main"` with backwards-compatible alias `agentflow = "agentsflower.cli:main"`).
3. Update `setup.py` to bundle from `.agentsflower/`.
4. Update `AGENTS.md`, `CLAUDE.md`, `.claude/commands/`, `README.md`, `GUIDE.md`, `GUIDE.ru.md` to reference `.agentsflower/` and `AgentsFlower`.
5. Update `paths.py` and all tools to point to `.agentsflower/` (with fallback to `.agentflow/` for legacy installed projects).
6. Update all tests in `tests/` to run against `.agentsflower/`.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/docs/ai-handoff-protocol.md

## Allowed files

- .agentflow/
- .agentsflower/
- src/
- pyproject.toml
- setup.py
- AGENTS.md
- CLAUDE.md
- README.md
- GUIDE.md
- GUIDE.ru.md
- .claude/commands/

## Do not touch

- External repositories.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- dashboard

## Acceptance criteria

- Folder `.agentsflower/` contains all workflow files.
- Python tests run and pass against `.agentsflower/`.
- Entry points reference `.agentsflower/`.

## Checks

- `python -m unittest discover -s .agentsflower/tests`

## Result

<!-- Worker writes its outcome below this block -->
