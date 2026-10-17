# T-005: Optional official-SDK MCP server and safe installer configuration

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-003
Branch: t-005-mcp-server
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-005-mcp-server
Independent check: tester
Resume: none

## Goal

Expose deterministic project operations through an optional official MCP SDK.
Core remains stdlib-only. No custom JSON-RPC fallback. Use the published SDK,
not unreleased main: PyPI mcp 2.3.0 (2026-10-02) declares Python >=3.10 and
MCPServer; current GitHub main has moved to >=3.11. Verify installed metadata/API
in an isolated env and bound the supported major dependency range.

## Read first

- AGENTS.md
- .agentflow/docs/agentflow-production-roadmap.txt
- .agentflow/tools/cli.py
- .agentflow/tools/install.py
- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/ledger.py
- pyproject.toml
- https://pypi.org/project/mcp/
- https://github.com/modelcontextprotocol/python-sdk/tree/v2.3.0
- https://code.claude.com/docs/en/mcp
- https://cursor.com/docs/context/mcp

## Allowed files

- .agentflow/tools/mcp_server.py
- .agentflow/tools/cli.py
- .agentflow/tools/install.py
- .agentflow/tools/ledger.py
- .agentflow/tests/test_mcp_server.py
- .agentflow/tests/check_mcp.py
- .agentflow/tests/test_install.py
- pyproject.toml
- src/agentflow/
- .github/workflows/ci.yml
- .agentflow/docs/release-validation.md
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/run_task.py
- .agentflow/dashboard/
- README.md
- GUIDE.md

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] M-01: Optional mcp extra uses the official released SDK with a bounded compatible major range. Core CLI and project tests work without it; startup gives a clear install-extra diagnostic when missing. No hidden package installation, no homegrown protocol fallback.
- [ ] M-02: Stdio tools: agentflow_status, agentflow_get_task(task_id), agentflow_run_gate(task_id, check_type), agentflow_query_ledger(limit, filter_role). Validate IDs, enums, bounds and project root. Status/get/query do not create project memory or expose arbitrary paths. Gate calls existing gate.py, preserving structured outcomes, exit status and bounded logs/evidence; do not label gate execution read-only.
- [ ] M-03: agentflow_accept_task exists only with explicit --enable-orchestrator-tools; absent by default. It invokes existing accept.py without bypasses. Document startup opt-in is operator control, not proof of caller role/identity. No shell interpolation, stdout protocol-only, diagnostics stderr.
- [ ] M-04: Installer explicit optional MCP flag merges .mcp.json preserving unrelated keys/servers. Refuse malformed JSON and conflicting unmanaged AgentFlow entries atomically; never overwrite another server or persist credentials. Generated command/args handle spaced paths and use the target's installed tool, default privileged tools off. Dry-run writes nothing.
- [ ] M-04b: Verify current client config paths in official docs. Support or explicitly document Cursor's project-specific config location instead of claiming root .mcp.json is auto-discovered by both clients. If installer exposes a client/config-path option, constrain writes to the intended project and test foreign-entry preservation for both paths.
- [ ] M-05: Unit tests cover missing SDK, input rejection, mutating opt-in, foreign MCP config preservation and existing gates. check_mcp.py provisions an isolated optional-SDK env and proves a real stdio handshake/list-tools/read-only tool call plus disabled privileged tool. Exercise packaged resources too; no LLM API calls. CI may add optional-SDK integration after core tests.
- [ ] M-06: Core full suite and SDK integration pass. Increment intermediate 2.11 patch version, AGENTS/changelog migration notes synchronized. Propose canonical decision in Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_mcp_server.py` - SDK-independent adapter/config safeguards.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - MCP config preservation.
- `python .agentflow/tests/check_mcp.py` - isolated real SDK stdio integration.
- `python -m unittest discover -s .agentflow/tests` - core regression suite.

## Result
Outcome: completed
Change: 1665318 on t-005-mcp-server
Files:
- .agentflow/tools/mcp_server.py - new optional stdio MCP server on the official `mcp` SDK: agentflow_status/get_task/query_ledger (read-only hints), agentflow_run_gate (real gate.py, not read-only), agentflow_accept_task only behind --enable-orchestrator-tools; strict task-id/check-type/role/limit validation; no-shell subprocesses; missing SDK -> exit 2 with install-extra diagnostic on stderr
- .agentflow/tools/cli.py - new `agentflow mcp` passthrough to the project's mcp_server.py; install help mentions --mcp/--mcp-client
- .agentflow/tools/install.py - `--mcp`/`--mcp-client` (claude -> .mcp.json, cursor -> .cursor/mcp.json): merges the agentflow entry into the client's project config preserving foreign keys/servers, refuses malformed JSON and conflicting unmanaged agentflow entries before writing, targets the installed server with privileged tools off and no credentials; dry-run writes nothing
- .agentflow/tests/test_mcp_server.py - SDK-independent tests: input rejection, missing-SDK diagnostic, real gate subprocess, opt-in surface/annotations (SDK-gated)
- .agentflow/tests/check_mcp.py - explicit integration: disposable venvs provision released `mcp>=2.3,<3` + packaged wheel; proves the missing-SDK diagnostic, a real stdio handshake/list-tools/read-only calls, rejected inputs, accept absent by default/present with the flag, and `agentflow --project <dir> mcp` through packaged resources
- .agentflow/tests/test_install.py - MCP merge preservation, idempotency, malformed/conflicting refusals, cursor path, opt-in and dry-run coverage
- pyproject.toml - `mcp` extra `mcp>=2.3,<3` (released 2.x line, Python >=3.10)
- .github/workflows/ci.yml - new `mcp` job (needs: tests) running check_mcp.py on ubuntu/windows
- .agentflow/docs/release-validation.md - records the new CI job
- .agentflow/VERSION, AGENTS.md - 2.11.13
- CHANGELOG.md - 2.11.13 entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_mcp_server.py` -> pass (13 passed / 0 failed; 3 SDK-gated skips in this stdlib interpreter)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python .agentflow/tests/check_mcp.py` -> pass (all checks; real mcp 2.3.0 handshake, list-tools, tool calls, opt-in surface, packaged CLI entry)
- `python -m unittest discover -s .agentflow/tests` -> pass (189 passed / 0 failed, 3 skipped)
Criteria without a command:
- M-04b: Claude Code project config is `.mcp.json`, Cursor's is `.cursor/mcp.json` (verified against current vendor docs; installer docstring states `.mcp.json` is not auto-discovered by Cursor). `--mcp-client` selects the path; foreign-entry preservation tested for both.
- M-06: version bumped to 2.11.13, AGENTS.md/CHANGELOG migration notes synchronized; decisions.md entry proposed below (state/ is outside Allowed files).
Found, not fixed:
- Tool results are returned as JSON TextContent (the SDK does not emit structuredContent for bare `dict` returns by default); acceptable and asserted by check_mcp.
Proposed memory updates:
- decisions.md (2026-10-17): MCP support ships as an optional extra on the released official SDK (`mcp>=2.3,<3`) instead of a custom JSON-RPC fallback or unreleased main; privileged accept stays behind an explicit startup flag documented as operator control, not caller-role proof; client config written only on explicit `--mcp`, per-client paths (.mcp.json / .cursor/mcp.json), refusing to overwrite unmanaged entries.

