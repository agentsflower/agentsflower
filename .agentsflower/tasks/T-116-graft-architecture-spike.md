# T-116: Research and evaluate Graft codebase knowledge graph engine

Role: developer
Tool: devin
Model: swe-2-max
Stage: 6
Depends on: none
Branch: t-116-graft-architecture-spike
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-116-graft-architecture-spike
Independent check: none - research spike
Resume: none
Routing exception: human authorized research spike for Graft codebase knowledge graph integration (2026-10-23)

## Goal

Conduct an architectural spike on integrating Graft (codebase knowledge graph engine using Tree-sitter AST and local symbol mapping, e.g. `@nanonets/graft` / `trailhq/Graft` / `tree-sitter` bindings) into AgentsFlower:
1. Evaluate local deterministic AST parsing across major languages (Python, TypeScript, JS, Go, Rust) without third-party cloud LLM requirements.
2. Determine how Graft can run as an MCP server or CLI command (`agentsflower graft impact <path-or-symbol>`) to provide:
   - Orchestrator blast-radius and file dependency scoping for Task File `## Files` section.
   - Developer/Tester symbol queries (`callers`, `definitions`, `signatures`) inside isolated worktrees, reducing exploratory token usage by 60-80%.
3. Document concrete CLI commands, performance benchmarks on Windows/Linux, and package dependency implications (preserving AgentsFlower core's zero third-party runtime dependency rule by making Graft an optional extra or standalone tool).

Produce `.agentflow/docs/graft-integration-spec.md`. Do not touch product code in this task.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/engineering-rules.md

## Allowed files

- .agentflow/docs/graft-integration-spec.md

## Do not touch

- Product code, existing tools, ledger, canonical state files (propose updates in Result).
- Existing test suites and configuration files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- `.agentflow/docs/graft-integration-spec.md` exists and details architecture, CLI/MCP interfaces, token reduction benchmarks, and non-breaking dependency strategy.

## Checks

- `python -c "import pathlib; assert pathlib.Path('.agentflow/docs/graft-integration-spec.md').is_file()"`

## Result

<!-- Worker writes its outcome below this block -->
