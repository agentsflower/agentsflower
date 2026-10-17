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
