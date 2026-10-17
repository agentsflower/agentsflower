# T-010: English public documentation and prepared v2.12.0 release

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-007, T-008, T-009
Branch: t-010-public-release-docs
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-010-public-release-docs
Independent check: tester
Resume: none

## Goal

Prepare all local public-launch artifacts from the implemented features. Human
push and GitHub publication remain manual after final local review; no remote
CI results, published package/tag or macOS pass may be invented.

## Read first

- AGENTS.md
- .agentflow/docs/agentflow-production-roadmap.txt
- README.md
- GUIDE.md
- .agentflow/docs/release-validation.md
- pyproject.toml
- .agentflow/tools/cli.py
- .agentflow/tools/mcp_server.py
- .agentflow/tasks/T-008-dashboard-visual-review.md
- CHANGELOG.md

## Allowed files

- README.md
- GUIDE.md
- GUIDE.ru.md
- CHANGELOG.md
- RELEASE_NOTES.md
- .agentflow/VERSION
- AGENTS.md
- .agentflow/README.md
- .agentflow/roles/tool-routing.md
- .agentflow/roles/orchestrator.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/release-validation.md
- .agentflow/docs/assets/dashboard.png
- .agentflow/tests/test_layout.py
- .agentflow/tests/test_install.py
- pyproject.toml

## Do not touch

- .agentflow/state/
- .agentflow/tools/
- .agentflow/dashboard/
- .github/workflows/ci.yml
- src/agentflow/

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] U-01: Preserve current Russian guide as GUIDE.ru.md and supply comprehensive English GUIDE.md: source/package installation, update preservation, Windows/Linux/macOS paths, optional MCP/operator flag, resource opt-in, worker lifecycle, truthful metrics/demo, recovery and supported permission boundaries. Windows conductor/autostart explicitly Windows-only. Commands match implemented CLI and docs links work.
- [ ] U-02: README has clear value proposition, CI/MIT/version/Python/MCP badges without invented green results; Mermaid shows Orchestrator single-writer memory, contracts, Developer/Tester isolated artifacts, gate and acceptance. Deployer consumes accepted SHA and human approval; never depicts Deployer as developer merge flow or sandbox guarantee for all tools.
- [ ] U-03: Production section uses human-attested October 2026 product figures and direct verified product/listing URLs: NotebookLM AI Sidebar 80k, 4.7/111, Featured; Export Chat from Gemini to Word 4k, 4.8/38, Featured; YouTube Transcript 1.6k; AI Home Design production SaaS. Explain aggregate snapshot without claiming deduplicated unique people or new independently measured telemetry. Do not guess extension IDs/links; record unresolved link evidence explicitly.
- [ ] U-04: Copy actual T-008 screenshot into docs/assets/dashboard.png; sample/demo attribution visible. English quickstart and links to both guides. No unsupported PyPI publication claim; prefer verified local/source install instructions.
- [ ] U-05: Synchronize 2.12.0 VERSION, AGENTS block and package metadata. CHANGELOG/migration and RELEASE_NOTES include final behavior, known evidence limits, human-only push/CI verification/tag/release commands. Prepare exact tag command after final acceptance; do not push, publish or create a misleading verified release tag while macOS/remote evidence is pending.
- [ ] U-06: test_layout/test_install and full suite pass; package integration rebuilt against final metadata (use existing check_package.py) and real stdio integration command remains documented. Final T-011 reviews these artifacts and local release preparation; external nine-job results remain a separately explicit release gate.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - links and repository layout.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - synchronized generated entry points.
- `python .agentflow/tests/check_package.py` - final wheel metadata/resources.
- `python -m unittest discover -s .agentflow/tests` - full suite.

## Result

