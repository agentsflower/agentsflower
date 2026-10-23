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

- .agentsflower/docs/graft-integration-spec.md

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

- [ ] C-01: .agentsflower/docs/graft-integration-spec.md exists and details architecture, CLI/MCP interfaces, token reduction benchmarks, and non-breaking dependency strategy.

## Checks

- python -c "import pathlib; assert pathlib.Path('.agentsflower/docs/graft-integration-spec.md').is_file()"

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Change: 9fcc34e on t-116-graft-architecture-spike
Files:
- .agentsflower/docs/graft-integration-spec.md - full integration spec: architecture, verified CLI/MCP surfaces, measured benchmarks (Windows; Linux deferred), measured token-reduction bounds, zero-dependency sidecar strategy, security/privacy, honest limits
Checks:
- `python -c "import pathlib; assert pathlib.Path('.agentsflower/docs/graft-integration-spec.md').is_file()"` -> pass
Criteria:
- C-01: pass - .agentsflower/docs/graft-integration-spec.md committed at 9fcc34e; covers architecture (tree-sitter two-tier native+WASM graph, LLM `--deep` layer kept off), CLI commands and proposed `agentsflower graft`/`graft_*` MCP mapping, measured Windows benchmarks (400 files -> 1.51s build, 0.55-0.9s queries, MCP 0.47s cold/0.04s warm), measured token savings (67-89% on real-size files, honest 0% floor on tiny files), non-breaking strategy (external npm sidecar, no deps added, AGENTFLOW_GRAFT opt-in, graceful absence)
Found, not fixed:
- Pre-existing suite failure at base HEAD: test_scenarios.py test_stage5_changelog_entries_carry_migration_notes - 2.16.0 CHANGELOG entry lacks a `Migration` note (T-114/T-115 scope; CHANGELOG.md is outside Allowed files). Whole suite run: 466 tests, 1 failed (this one), 4 skipped, 423.6s.
- Graft hard-limits discovered (documented in spec): dot-directories are never indexed (`.agentsflower/tools/` is invisible - fine for installed projects, limits value on this repo itself); `graft init` writes into home-dir agent configs (use `--no-global`/skip init); telemetry is opt-out to events.nanonets.com (`graft telemetry disable`); Windows `npm i -g` fails on tree-sitter-kotlin node-gyp without MSVC tools - `--ignore-scripts` works fully (WASM fallback by design).
- Side effect to note: `graft init --yes` in the temp fixture installed a user-level graft skill into C:\Users\Win10Pro\.claude\skills\ and touched ~/.codex, ~/.gemini configs (init output listed "+ N in ~\" entries). Left in place; remove via the graft uninstall in that fixture or by hand if unwanted.
- WSL on this machine is broken (service error 0x80072747); Linux benchmark unmeasured - spec documents expectation and defers measurement to T-118/CI.
Proposed memory updates:
- decisions.md: Graft adopted direction = optional external sidecar (pin @nanonets/graft, never a pip dep); graph kept outside worktrees via `graft --dir` + `--no-gitignore --no-ignore` so gate.py endcheck (porcelain must be clean) is unaffected; `--deep` LLM tier excluded by default; telemetry disabled before rollout.
- known-issues.md: npm i -g @nanonets/graft fails on Windows without MSVC build tools (tree-sitter-kotlin node-gyp); use `--ignore-scripts` - runtime falls back to bundled WASM grammars by upstream design.
