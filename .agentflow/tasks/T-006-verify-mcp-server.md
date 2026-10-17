# T-006: Independently verify optional MCP server and installer configuration

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-005
Verifies: T-005 @ 1665318db8c99b2a893ce367a843dfd740a76b5d

## Goal

Verify the optional official-SDK MCP server, the `agentflow mcp` passthrough
and the installer `--mcp`/`--mcp-client` configuration independently of the
developer's own run. Same tool is necessary under the human's resource policy
(agy and claude limited, codex conserved); use a fresh isolated session. No
product changes; all SDK installs go to disposable venvs and disposable
projects.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-005-mcp-server.md
- .agentflow/tools/mcp_server.py
- .agentflow/tools/cli.py (`mcp` passthrough)
- .agentflow/tools/install.py (`--mcp`, `--mcp-client`)
- .agentflow/tests/test_mcp_server.py
- .agentflow/tests/check_mcp.py
- .agentflow/tests/test_install.py
- pyproject.toml (mcp extra)
- .github/workflows/ci.yml (mcp job)
- .agentflow/docs/release-validation.md
- CHANGELOG.md (2.11.13 entry)

## Allowed files

- nothing

## Do not touch

- pyproject.toml, src/
- .agentflow/tools/, .agentflow/tests/, .agentflow/dashboard/
- .agentflow/state/, .agentflow/tasks/
- global Python environments, real PyPI credentials, real client .mcp.json files

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: The mcp extra is optional and bounded: `mcp>=2.3,<3` declared only under extras, core CLI and full suite work without the SDK installed, and a missing SDK yields a clear install-extra diagnostic (exit 2, stderr) rather than a traceback or silent fallback. No custom JSON-RPC implementation; the released official SDK is used.
- [ ] V-02: Stdio tool surface is honest: agentflow_status, agentflow_get_task, agentflow_run_gate, agentflow_query_ledger validate task IDs, enums, bounds and project root; read-only tools create no project memory and expose no arbitrary paths; run_gate invokes real gate.py with structured outcomes, exit status and bounded output and is not annotated read-only. agentflow_accept_task is absent by default and appears only with --enable-orchestrator-tools, documented as operator control not caller-role proof; no shell interpolation, stdout carries protocol only.
- [ ] V-03: Installer `--mcp` merge is safe: writes the agentflow entry into the correct per-client project config (`.mcp.json` for claude, `.cursor/mcp.json` for cursor), preserves unrelated keys and foreign servers, refuses malformed JSON and conflicting unmanaged agentflow entries atomically, handles spaced paths, targets the installed server with privileged tools off, persists no credentials, and dry-run writes nothing. The `.cursor/mcp.json` path choice is verified against current Cursor docs, not assumed.
- [ ] V-04: The four verbatim checks pass on the verified commit in a disposable checkout; check_mcp.py really provisions an isolated SDK env and proves a genuine stdio handshake, not a mock; report real failures, skips and environment causes. Developer worktree/branch/Task File baselines unchanged. Version 2.11.13, CHANGELOG and AGENTS block in sync; CI mcp job present and consistent with release-validation.md.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_mcp_server.py` - SDK-independent adapter/config safeguards.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - MCP config preservation.
- `python .agentflow/tests/check_mcp.py` - isolated real SDK stdio integration.
- `python -m unittest discover -s .agentflow/tests` - full regression suite.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_mcp_server.py` -> pass (13 ran / 0 failed, 3 SDK-gated skips; evidence check1-test_mcp_server.txt)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 ran / 0 failed; evidence check2-test_install.txt)
- `python .agentflow/tests/check_mcp.py` -> pass (all checks; real mcp 2.3.0 provisioned in disposable venv, genuine stdio handshake/list-tools/tool calls, opt-in surface, packaged `agentflow mcp` entry; evidence check3-check_mcp.txt)
- `python -m unittest discover -s .agentflow/tests` -> pass (189 ran / 0 failed, 3 skipped; evidence check4-fullsuite.txt)
Criteria:
- V-01 - pass - pyproject.toml declares `dependencies = []` and `mcp = ["mcp>=2.3,<3"]` only under optional-dependencies; full suite runs 189 tests stdlib-only; check_mcp proved missing SDK yields exit 2 with an install-extra diagnostic on stderr (`agentflow mcp: the optional MCP SDK is not installed...`); the same run installed released mcp 2.3.0 and imported `mcp.server.MCPServer`/`mcp_types.ToolAnnotations` - official SDK, no JSON-RPC fallback in mcp_server.py.
- V-02 - pass - real stdio session listed exactly agentflow_get_task/query_ledger/run_gate/status by default with run_gate not read-only; `limit=0` and `task_id="x; rm -rf /"` returned structured errors. Code review of mcp_server.py: task-id regex T-\d{1,4} fullmatch, check_type enum (verify/preflight/endcheck/task), role enum, limit 1..200, project root fixed by script location, get_task only globs .agentflow/tasks, run_gate shells out to the real gate.py via argv-list subprocess (no shell) with 20000-char bounded log and parsed --out evidence; read-only tools write nothing. accept_task absent by default, registered only under --enable-orchestrator-tools, docstring/help state it is operator control not caller-role proof; stdout is `server.run("stdio")` only, diagnostics stderr.
- V-03 - pass - install.py MCP_CONFIGS = {claude: .mcp.json, cursor: .cursor/mcp.json}; plan_mcp_config refuses malformed JSON and a conflicting unmanaged `agentflow` entry with SystemExit before any plan.write, merges preserving unrelated keys/servers, is idempotent; entry = {command: sys.executable (absolute), args: [<target>/.agentflow/tools/mcp_server.py]} - argv array, spaced paths safe, no --enable-orchestrator-tools, no env/credentials; dry-run writes nothing (test_mcp_cursor_path_and_dry_run). Cursor project path verified against live cursor.com/docs/context/mcp: "Create `.cursor/mcp.json` in your project for project-specific tools" - matches the installer's choice and its docstring note that project .mcp.json is Claude Code's location, not auto-discovered by Cursor.
- V-04 - pass - all four verbatim checks ran on a disposable worktree checkout of the verified commit (HEAD 1665318db8c99b2a893ce367a843dfd740a76b5d, `git status` clean; developer worktree/branch and Task Files untouched). check_mcp.py is genuine integration: builds the wheel, provisions two disposable venvs, pip-installs released mcp 2.3.0, performs a real MCP Client stdio handshake with no mocks. VERSION=2.11.13 matches AGENTS.md block and the CHANGELOG 2.11.13 entry with migration notes; ci.yml `mcp` job (needs: tests, ubuntu+windows, runs check_mcp.py) matches release-validation.md. No real failures, skips are the 3 documented SDK-gated unit tests in the stdlib interpreter.
New defects (outside the task):
- none
Cannot verify, needs:
- Remote CI run of the new `mcp` job (workflow present and consistent, but no GitHub Actions run observed - same caveat release-validation.md already records).
Proposed memory updates:
- none (developer already proposed the decisions.md entry for 2.11.13; tester adds nothing)

Evidence files: E:\Projects\AgentFlow\code\.agentflow\tasks\.runtime\T-006.evidence\{check1-test_mcp_server.txt,check2-test_install.txt,check3-check_mcp.txt,check4-fullsuite.txt}
