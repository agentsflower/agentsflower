# Graft codebase knowledge graph integration

AgentsFlower provides native integration with [Graft](https://github.com/trailhq/Trail-Code) (`@nanonets/graft`), a local, deterministic AST knowledge graph engine powered by Tree-sitter.

## Highlights

- **Zero Core Python Dependencies**: Graft runs as an optional external sidecar. AgentsFlower core maintains standard-library-only runtime requirements.
- **Auto-Installation**: When `graft` is missing, AgentsFlower automatically installs `@nanonets/graft` using `npm i -g @nanonets/graft --ignore-scripts` upon first use when npm is present.
- **Git Isolation**: Graphs are built and stored under `.agentsflower/tasks/.runtime/graft/<repo-hash>` with flags `--no-gitignore --no-ignore`, keeping git worktrees clean and compliant with `gate.py` porcelain checks.
- **Privacy by Default**: Third-party telemetry is automatically disabled (`graft telemetry disable`). LLM passes (`--deep`) are never invoked by default.

## CLI Commands

```bash
# Build or refresh the AST graph in runtime cache
agentsflower graft build

# Natural language and symbol query across the graph
agentsflower graft query "Where is role routing implemented?"
agentsflower graft query "How does verification work?" --in .agentsflower/tools

# Impact / blast radius analysis
agentsflower graft impact <symbol-name>     # callers closure (--depth all)
agentsflower graft impact <file-path>       # git diff blast radius

# Symbol API signatures of a file
agentsflower graft symbols src/index.py

# Raw passthrough to underlying graft binary
agentsflower graft raw map
agentsflower graft raw check
```

## MCP Tools

The AgentsFlower MCP server (`agentsflower mcp --enable-graft-tools` or `AGENTFLOW_GRAFT=1`) exposes:

1. `graft_query(question, path_scope?)`: Query the codebase knowledge graph for relevant files and line spans.
2. `graft_impact(symbol_or_path)`: Compute blast-radius impact for a symbol or file.
3. `graft_symbols(file)`: Retrieve API skeleton and function/class signatures without file bodies.

## Advisory Scoper for Task Files

During task specification, Orchestrators and Developers can run:
```bash
agentsflower graft impact <symbol>
```
to identify dependent files and properly populate the `## Allowed files` section of the Task File.
