# T-115: Verify full rebranding to agentsflower

Role: tester
Tool: codex
Model: gpt-6.1-sol
Stage: 6
Depends on: T-114
Branch: main
Worktree: none
Independent check: none
Resume: none

## Goal

Independently verify full rebranding across all entry points, tests, and CLI:
1. Run `python -m unittest discover -s .agentsflower/tests`.
2. Verify `README.md`, `GUIDE.md`, `AGENTS.md` and `pyproject.toml`.
3. Verify `install.py` installs cleanly into a throwaway repository.

## Read first

- .agentsflower/tasks/T-114-rebrand-agentsflower-core.md

## Allowed files

- none (read-only verification)

## Acceptance criteria

- All unit tests pass on `.agentsflower/tests`.
- Verdict is pass.

## Checks

- `python -m unittest discover -s .agentsflower/tests`

## Result

<!-- Worker writes its outcome below this block -->
