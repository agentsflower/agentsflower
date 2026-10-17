# T-010: English public documentation and prepared v2.12.0 release

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-007, T-008, T-026
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


Outcome: completed
Change: 0fcd77398b7d0ce42466c35a4b24d05b8d214762 on t-010-public-release-docs
Files:
- GUIDE.ru.md - previous Russian guide preserved byte-identical
- GUIDE.md - new English guide: source + local package install, update preservation, workspace, Windows/Linux/macOS paths, MCP opt-in + --enable-orchestrator-tools, machine-resource opt-in, worker lifecycle, honest metrics/--demo, recovery, permission boundaries; conductor/autostart marked Windows-only
- README.md - badges (CI/MIT/2.12.0/Python 3.10+/MCP), value proposition, Mermaid single-writer Orchestrator -> Task File -> isolated Developer/Tester artifacts -> gate.py -> accept.py -> Deployer (accepted SHA, manual, human approval); attested Oct-2026 production figures as aggregate snapshot; dashboard screenshot; quickstart; verification-status section claiming no remote/macOS result
- .agentflow/docs/assets/dashboard.png - real T-008 capture (dashboard-real-graph.png, 2560x1440), captioned as this repo's own real development dashboard
- RELEASE_NOTES.md - release contents, evidence limits, unresolved listing links recorded explicitly, human-only push/CI/tag/Release commands incl. exact `git tag -a v2.12.0` line
- CHANGELOG.md - 2.12.0 entry with migration note (no runtime file changes)
- .agentflow/VERSION, AGENTS.md - 2.12.0 in sync
- .agentflow/README.md - tools row now names run_task.py, cli.py, mcp_server.py
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python .agentflow/tests/check_package.py` -> pass (all checks: wheel+sdist build, bundled template, no core deps, agentflow --version prints 2.12.0, install/update/provenance on spaced path)
- `python -m unittest discover -s .agentflow/tests` -> pass (204 tests, OK, 3 skipped, 148s)
Criteria without a command:
- U-01 English GUIDE - all commands verified against cli.py/run_task.py/install.py --help output and current docs; links point to existing files (README, protocol, GUIDE.ru.md)
- U-02 README diagram/badges - Mermaid shows Orchestrator single-writer, contracts, isolated Developer/Tester artifacts, gate+accept; Deployer takes accepted SHA + human approval only; no merge-flow or universal-sandbox depiction; badge row claims no green CI
- U-03 production section - attested figures with explicit aggregate-snapshot caveat; only verified link aisidebar.app used; unresolved store links recorded in RELEASE_NOTES.md instead of guessed extension IDs
- U-04 screenshot/demo attribution - real T-008 png copied; caption says real task data captured locally; quickstart is local/source install, no PyPI claim
- U-05 2.12.0 sync - VERSION/AGENTS block/CHANGELOG/RELEASE_NOTES aligned; tag command prepared, nothing pushed/published/tagged; release notes state remote CI and macOS evidence still pending
- U-06 suite/package - see Checks; real stdio integration command documented in GUIDE (`python .agentflow/tools/check_mcp.py` equivalent via tests/check_mcp.py, `agentflow mcp`)
Found, not fixed:
- Store listing URLs for Export Chat from Gemini to Word, YouTube Transcript and AI Home Design remain unverified; README deliberately omits links, RELEASE_NOTES records the gap for the maintainer
- GUIDE.md is a full English rewrite, not a line-by-line translation; Russian original kept in GUIDE.ru.md
Proposed memory updates:
- session-log: T-010 done - public release docs (English GUIDE, README, RELEASE_NOTES, dashboard.png from T-008 evidence), VERSION/AGENTS 2.12.0; checks green (204 tests, check_package ok); human push/tag/CI still pending
