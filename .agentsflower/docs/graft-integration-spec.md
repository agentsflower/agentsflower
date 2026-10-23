# Graft integration specification

Architectural spike T-116: evaluating Graft (codebase knowledge graph) as an optional
context layer for AgentsFlower. All commands below were run and measured on
2026-10-23 against `@nanonets/graft` 0.24.1 on Windows 10, Node v22.16.0; source
inspections cite `dist/` files of that release.

## Verdict

Integrate as an **optional external sidecar**, never a bundled dependency. The
structural tier (tree-sitter wiring graph) is fully deterministic — no model, no
API key, no network — and covers every AgentsFlower need: blast-radius scoping
for `## Files`, symbol queries for workers inside worktrees, and MCP tools.
`--deep` (LLM summaries) exists but stays off; AgentsFlower does not require it.

## What Graft is

Graft was renamed **Trail-code** (trailhq) in 0.22.0; the same build ships as
`@nanonets/graft` (`graft` command) and `@trailhq/trail-code` (`trail` command).
Both are maintained; pin `@nanonets/graft` 0.24.x (MIT). Repository:
github.com/trailhq/Trail-Code (formerly nanonets/graft, redirects).

`graft build` parses the repo with tree-sitter into a **wiring graph**: per-file
cards (`graft/<path>.md`, signatures + spans) plus `.graph/wiring.json`
(nodes = file/function/method/class/struct, edges = calls/references). It is a
local, regenerable cache — like `node_modules`, not a committed artifact.

### Two parsing tiers (dist/graph/native.js, generic.js)

- **Depth tier**: native grammar addons (tree-sitter per-language packages).
  Loaded lazily per language; a missing binary is remembered, never fatal.
- **Breadth tier**: WASM grammars (`tree-sitter-wasm` via `web-tree-sitter`).
  Any language whose native addon fails falls back here automatically.

24 languages are claimed; the WASM set observed in `generic.js` covers rust, java,
c, cpp, ruby, c_sharp, scala, elixir, solidity, ocaml, zig, dart, vue plus the
native set (python, typescript/tsx, javascript, go, php, kotlin, r, swift).

### LLM tier (`--deep`, off by default)

`graft build --deep` adds concept nodes and per-symbol summaries via an LLM
(`GRAFT_API_KEY`, `GRAFT_PROVIDER` = openai|anthropic|litellm|orcarouter).
Without a key it warns and falls back to the structural build — verified.
AgentsFlower uses the structural tier only; `--deep` sends code to a third-party
endpoint and needs an explicit human decision before any use.

## Verified behavior (this spike, measured)

| Check | Result |
|---|---|
| `graft build`, 49 files, 5 languages (py, ts, js, go, rs) | 0.81s, 233 nodes / 310 edges, all 5 languages indexed |
| `graft build`, 400 Python files | 1.51s cold (~265 files/s), 3,600 nodes / 7,150 edges, `graft/` = 5.5 MB (~14 KB/file) |
| `graft callers <sym>` / `map` / `grep` / `skeleton` | 0.55–0.9s per call on a 3,600-node graph, freshness-checked + auto-refresh on edit |
| `callers` on missing symbol | exit 1 with `✗ no symbol` (machine-detectable) |
| `--json` on `callers` | clean `{query, matches:[{symbol:{id,name,kind,path,span}, hits:[{relation…}]}]}` |
| `graft blast` (working tree vs HEAD) | seeds changed symbols, walks `--depth N|all` incoming edges; markdown/mermaid/json formats; CI-oriented |
| Cross-file and transitive edges | verified (`pipeline` in m8.py → `f5_k0` in m5.py; `--depth all` closure) |
| Incremental refresh | automatic before each query; 1 changed file ≈ +0.5s inside query time |
| **Git worktree** (`.git` file, not dir) | build + queries work unchanged — the critical AgentsFlower case |
| `graft mcp` (stdio, newline-delimited JSON-RPC 2.0) | init 0.47s cold; 6 tools; `tools/call` 0.04s warm |
| MCP tool names | `graft_find_code`, `graft_file_api`, `graft_check_freshness`, `graft_trace_calls`, `graft_find_all`, `graft_repo_map` |
| `--deep` without API key | graceful fallback to structural build with warning — exit 0 |
| External graph dir | `graft --dir <outside-path>` + `--no-gitignore --no-ignore` → worktree stays `git status`-clean |
| `graft build --check` | CI drift gate: fails when `graft/` is stale vs code |
| Linux | not measurable here (WSL service down, 0x80072747); WASM tier is platform-independent, expect parity — verify in T-118/CI |

## CLI surface (0.24.1)

```
graft build [--deep] [--only-dir p] [--include-dir d] [--no-reuse] [--lsp]
            [--no-gitignore] [--no-ignore] [--check] [--json]
graft ask "<question>" [--source] [--full] [-n N] [--in path] [--json]
graft callers <symbol> [--direction in|out] [--depth N|all] [--json]
graft blast [--base ref] [--depth N|all] [--format text|markdown|mermaid|json]
graft grep <regex> [--fixed] [-i] [--in path] [--json]
graft skeleton <file>
graft map [--max-dirs N]
graft check                    # freshness
graft mcp [dir]                # stdio MCP server, 6 tools
graft init|uninstall|telemetry|version|upgrade
```

Notable: every query self-refreshes the graph first (uncommitted edits included),
so workers never run `build` by hand. `--depth all` on `callers` is the full
transitive blast radius — this is what T-117 must expose as `impact`.

### Indexing rules (dist/ingest/fs.js)

- Files enumerated via `git ls-files --cached --others --exclude-standard`
  (tracked + untracked-not-ignored); filesystem walk is the non-git fallback.
- `SKIP_DIRS` = node_modules, dist, build, _build, out, target, vendor,
  coverage, __pycache__, venv — overridable per repo with `--include-dir`.
- Files > 1 MB are skipped (generated/vendored heuristic).
- **Dot-directories are skipped wholesale and can never be re-included**
  (documented KNOWN LIMITATION in source). `.agentsflower/tools/*.py` is
  invisible to Graft — see "Fit to AgentsFlower" below.
- `--only-dir <path>` restricts indexing to subtrees — useful for scoping a
  graph to the task's repo/area.

## Proposed AgentsFlower interface (for T-117)

### `agentsflower graft` CLI passthrough (cli.py pattern)

`cli.py` already dispatches argument-list subprocesses. Add a `graft` subcommand
that resolves the binary once (`shutil.which("graft")`, else
`npx --no-install graft`, else a clear "not installed" diagnostic) and forwards
arguments verbatim. Composite conveniences on top:

| AgentsFlower command | Maps to |
|---|---|
| `agentsflower graft build` | `graft --dir <runtime-dir> build --no-gitignore --no-ignore` |
| `agentsflower graft query <q>` | `graft --dir <runtime-dir> ask "<q>" --source` |
| `agentsflower graft impact <symbol>` | `graft --dir <runtime-dir> callers <symbol> --depth all --json` |
| `agentsflower graft impact <path>` | `graft --dir <runtime-dir> blast --format json` (diff-based) |
| `agentsflower graft symbols <file>` | `graft --dir <runtime-dir> skeleton <file>` |

`<runtime-dir>` default: `<project>/.agentsflower/tasks/.runtime/graft/<repo-hash>` —
outside tracked files by convention (`.runtime/` is already non-product), so
**the worktree stays clean and `gate.py` endcheck (`git status --porcelain`
must be empty, gate.py:812) is unaffected**. This is the key integration
decision: never write `graft/` into a worktree, never touch `.gitignore`.

### MCP tools (mcp_server.py)

Mirror the existing `agentflow_*` tools: stdlib subprocess wrappers around the
CLI (not a proxy to `graft mcp` — keeps one server surface, zero new deps,
same `_err`/`_clip` conventions). Read-only annotations.

| Tool | Wraps | Purpose |
|---|---|---|
| `graft_query(question, path_scope?)` | `graft ask --source [--in]` | locate + understand code |
| `graft_impact(symbol_or_path)` | `callers --depth all` / `blast` | blast radius → `## Files` |
| `graft_symbols(file)` | `skeleton` / `file_api` | API surface without bodies |

### Orchestrator use: `## Files` scoping

`graft impact <symbols of the task>` or `graft blast` on the diff yields the
dependency closure with `file:line`; a `gate.py`/`scoper` helper (T-117)
proposes/validates `Allowed files` against it. Human stays the authority — the
graph proposes, it does not widen silently.

### Worker use: token-lean exploration

Role-file doctrine (add to developer/tester "Read first" guidance): one
`graft map` or `graft ask` for orientation, `graft symbols` before editing,
`graft callers --depth 2` before touching a signature, `graft grep` for
exhaustive finds. Graft's own SKILL.md codifies the one-call-per-need doctrine;
the role file should reference it rather than duplicate it.

### Launcher use: pre-built graph

`run_task.py init_workdir` (run_task.py:897) is where a conditional
`graft --dir <runtime> build --no-gitignore --no-ignore` belongs — after the
worktree exists, before worker handoff, gated on `AGENTFLOW_GRAFT=1` and a
resolved binary; a failure is a log line, never a LaunchError. Workers without
the flag see zero behavior change. Alternatively the worker's first query builds
lazily (every graft command self-builds); pre-build just moves ~1-2s off the
critical path.

## Benchmarks

Measured (Windows 10, Node 22.16, `--ignore-scripts` install i.e. WASM parsers):

| Operation | 49 files / 5 langs | 400 files / 3.6k nodes |
|---|---|---|
| `build` cold | 0.81 s | 1.51 s |
| `build` incremental (1 file) | inside query, +~0.5 s | inside query, +~0.5 s |
| `callers` / `map` / `grep` | 0.55–0.6 s | 0.58–0.88 s |
| MCP `initialize` | — | 0.47 s |
| MCP `tools/call` warm | — | 0.04 s |

Linux: unmeasured (WSL unavailable). The WASM tier has no platform-specific code
path; expect ≤ Windows times on equivalent hardware. Confirm on a real Linux
host in T-118 before quoting numbers outward.

## Token reduction (measured, chars÷4 ≈ tokens; graft's own footer estimates agree)

| Scenario | Graft | Naive | Saved |
|---|---|---|---|
| File API surface, 4.5 KB module | `skeleton` ≈ 379 tok | read 1,140 tok | **67%** |
| Callers of one symbol | `callers` ≈ 123 tok | read ≥1 file + grep spread | **89%** vs single file; more vs real exploration |
| Diff blast radius | `callers --depth all` ≈ 200 tok | grep + read 3 files ≈ 409 tok | **51%** (tiny synthetic files — floor, not ceiling) |
| Repo orientation, 400 files | `map` ≈ 670 tok | read-all ≈ 52,250 tok | **99%** (upper bound; real workers read 5–15 files, not all) |
| Tiny file (<500 B) | any query ≈ file size | read file | **0–negative** — graft adds header overhead |

Honest bound: the 60–80% reduction claim holds when exploration would otherwise
read multiple real-size files — exactly the worker-onboarding pattern
(grep → open → follow import → repeat). For single tiny files graft is neutral.
Track real per-task savings via graft's `[graft] tokens saved ≈ N` footer —
it is designed to be summed per session (route_report-compatible telemetry).

## Dependency strategy (non-breaking)

AgentsFlower core stays **stdlib-only, `dependencies = []`** — unchanged.

1. Graft is a **Node package, not pip**: it cannot enter `pyproject.toml`
   dependencies at all. It is discovered at runtime like `git` itself.
2. Detection: `shutil.which("graft")` → `npx --no-install graft` → absent.
   Absent graft: `agentsflower graft *` prints the install hint and exits 1;
   MCP `graft_*` tools return `{ok:false,error:"graft not installed"}`;
   the launcher skips the pre-build. Nothing else changes.
3. Install paths (documented in spec + `--help`):
   - `npm install -g @nanonets/graft` (needs Node ≥20; on Windows may fail at
     `tree-sitter-kotlin`'s node-gyp step without MSVC build tools — observed
     on this machine)
   - `npm install -g @nanonets/graft --ignore-scripts` — verified fully
     functional: missing native grammars fall back to bundled WASM parsers;
     upstream designed for this (npm ≥11 skips dep scripts by default anyway)
   - pin: `npm install -g @nanonets/graft@0.24` — record the tested version in
     project-rules once adopted
4. Install footprint: package 29 MB; full node_modules tree 289 MB
   (grammars + openai/anthropic SDKs used only by `--deep`/learn features).
5. Version bumps are deliberate: `graft upgrade` or `npm i -g @nanonets/graft@N`;
   `graft version` self-checks npm (degrades to "unreachable" offline — verified).
6. No Python-side optional extra is needed; if a discoverability hint is wanted,
   an `extras` entry like `graft = []` is impossible (npm ≠ pip) — document
   instead. T-117 may add an empty marker extra only if tooling requires one.

## Security, privacy, supply chain

- **Telemetry: ON by default, opt-out** — anonymous aggregates
  (app_version, os/arch/node, repo uuid hash, file-count buckets, durations)
  to `events.nanonets.com`; no code/paths/queries (TELEMETRY.md; queue file
  inspected). `graft telemetry disable` once per machine (`~/.graft/telemetry.json`
  → `enabled:false`). AgentsFlower integration docs must call this out; the
  launcher may set it non-interactively via `graft telemetry disable`.
- **`graft init` writes outside the repo**: agent wiring into `~/.claude/`,
  `~/.codex/`, `~/.gemini/` etc. (observed: it installed a user-level graft
  skill on this machine). AgentsFlower wires tools itself — recommend
  `init --agents <id> --no-global --no-hooks` or skip `init` entirely and use
  `build`/`mcp` directly.
- **`--deep` and `init --connect` send code/metadata to third parties**
  (LLM provider; team.trailhq.com). Keep both out of every AgentsFlower path.
- MCP server is stdio-local; exposure follows whatever client embeds it —
  same trust model as the existing `mcp_server.py`.
- Supply chain: 17 direct npm deps incl. `openai`, `@anthropic-ai/sdk`,
  `tree-sitter-*` grammars. Mitigate by pinning a version ≥7 days old
  (0.24.1 released 2026-10-22 — **do not** auto-track `latest`; wait or pin
  0.23.x for the first rollout), `--ignore-scripts`, and the fact that graft
  never enters the product's runtime path — a bad release degrades one
  optional tool, not AgentsFlower.

## Fit to AgentsFlower — honest limits

1. **Dot-dir exclusion hits this repo itself**: AgentsFlower's own product code
   lives in `.agentsflower/tools/` — invisible to Graft forever (hardcoded).
   On the template repo graft sees only `src/` + `setup.py` (3 files). The
   value is for **projects that install AgentsFlower** (their product code is
   in normal dirs) — and for those, excluding `.agentsflower/` is *correct*:
   workers query product source, not workflow internals. If AgentsFlower's own
   development wants graph queries, only `src/agentsflower/` benefits; that is
   a real but bounded limitation, no workaround exists upstream.
2. AST edges are name-based, not compiler-resolved (except opt-in `--lsp`,
   which needs a per-language server). Dynamic dispatch, reflection, and
   string-built call sites are missed — `impact` output is a strong lower
   bound on blast radius, not a proof. `gate.py` must treat it as advisory.
3. `blast` measures a **diff** (working tree vs HEAD, or `--base`); for
   pre-edit scoping use `callers --depth all` on the task's symbols.
4. Grep/map/callers auto-refresh but the markdown **cards** under `graft/` lag
   until rebuild — query tools, don't read cards, after editing (upstream
   SKILL.md says the same).
5. No Windows global install without either MSVC tools or `--ignore-scripts`;
   the latter is the documented fast path.
6. Node ≥20 is a new runtime prerequisite for an otherwise Python-only tool —
   acceptable because optional, but the launcher must degrade silently.

## Recommendation

Proceed to T-117 with: CLI passthrough + three MCP tools + runtime-dir graph
(outside worktrees) behind `AGENTFLOW_GRAFT`; orchestrator `impact`→`Allowed files`
advisory scoper in `gate.py`; telemetry-off and `--no-gitignore --no-ignore`
defaults; version pinned in project-rules after T-118 verifies on Linux.
