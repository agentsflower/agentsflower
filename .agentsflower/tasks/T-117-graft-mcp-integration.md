# T-117: Graft MCP adapter and tooling integration

Role: developer
Tool: devin
Model: swe-2-max
Stage: 6
Depends on: T-116
Branch: t-117-graft-mcp-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-117-graft-mcp-integration
Independent check: tester
Resume: none
Routing exception: human authorized Graft MCP adapter and tooling integration (2026-10-23)

## Goal

Implement Graft integration into AgentsFlower per specification from T-116:
1. Provide an automated installer and CLI wrapper `agentsflower graft` (`build`, `query`, `impact`, `symbols`) with auto-install via `npm i -g @nanonets/graft --ignore-scripts` when npm is available and graceful degradation when Node.js is absent.
2. Store runtime graphs in `.agentsflower/tasks/.runtime/graft/` with `--no-gitignore --no-ignore` so git worktrees remain porcelain-clean for `gate.py`.
3. Expose Graft tools via AgentsFlower MCP server (`graft_query`, `graft_impact`, `graft_symbols`).
4. Add helper in `gate.py` / `scoper` to validate and propose `## Files` based on symbol impact graph.
5. Keep core runtime dependencies zero: Graft integration is activated when Graft / Tree-sitter is installed or auto-installed via npm sidecar.

## Read first

- .agentsflower/docs/ai-handoff-protocol.md
- .agentsflower/docs/graft-integration-spec.md

## Allowed files

- .agentsflower/tools/graft.py
- .agentsflower/tools/cli.py
- .agentsflower/tools/mcp_server.py
- .agentsflower/tools/gate.py
- .agentsflower/tests/test_graft.py
- .agentsflower/docs/graft.md
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

- [ ] C-01: Auto-installer in graft.py automatically installs @nanonets/graft with --ignore-scripts if missing and npm is available, or gracefully reports instructions if Node.js is absent.
- [ ] C-02: CLI command agentsflower graft (build, query, impact, symbols) works cleanly and places runtime graphs in .agentsflower/tasks/.runtime/graft/ leaving git worktrees porcelain-clean.
- [ ] C-03: MCP server (mcp_server.py) exposes graft_query, graft_symbols, graft_impact tools with clean JSON-RPC schema.
- [ ] C-04: Test suite in test_graft.py passes and full regression suite passes.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_graft.py"

## Result

Outcome: completed
Change: 47f33956173e430f0dff9c1eda35d34161591b29
Criteria:
- C-01: pass - auto-installer in graft.py resolves graft in PATH, npm global bin, or auto-installs via npm i -g @nanonets/graft --ignore-scripts.
- C-02: pass - CLI command agentsflower graft (build, query, impact, symbols, raw) works cleanly; runtime caches placed under .agentsflower/tasks/.runtime/graft/ keeping worktrees porcelain-clean.
- C-03: pass - MCP server mcp_server.py exposes graft_query, graft_symbols, graft_impact tools with clean JSON-RPC schema.
- C-04: pass - test suite test_graft.py (10 tests) and regression suite pass.



