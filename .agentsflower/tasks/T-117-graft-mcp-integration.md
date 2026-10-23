# T-117: Graft MCP adapter and tooling integration

Role: developer
Tool: devin
Model: swe-2-max
Stage: 6
Depends on: T-116
Branch: t-117-graft-mcp-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-117-graft-mcp-integration
Independent check: T-118
Resume: none

## Goal

Implement Graft integration into AgentsFlower per specification from T-116:
1. Provide an optional CLI wrapper/command `agentsflower graft` (`build`, `query`, `impact`).
2. Expose Graft tools via AgentsFlower MCP server (`graft_query`, `graft_impact`, `graft_symbols`).
3. Add helper in `gate.py` / `scoper` to validate and propose `## Files` based on symbol impact graph.
4. Keep core runtime dependencies zero: Graft integration is activated when Graft / Tree-sitter is installed, or through optional extra `[graft]`.

## Read first

- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/graft-integration-spec.md

## Allowed files

- .agentflow/tools/
- .agentflow/docs/
- .agentflow/tests/test_graft.py
- pyproject.toml

## Do not touch

- Existing ledger or canonical state files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- `agentsflower graft` CLI commands work cleanly when Graft is available.
- MCP server exposes graft tools cleanly.
- Tests in `test_graft.py` pass.

## Checks

- `python -m unittest discover -s .agentflow/tests -p "test_graft.py"`

## Result

<!-- Worker writes its outcome below this block -->
