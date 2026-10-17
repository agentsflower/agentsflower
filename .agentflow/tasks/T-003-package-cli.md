# T-003: Build distributable template package and unified CLI

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-022, T-026
Branch: t-003-package-cli
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-003-package-cli
Independent check: tester
Resume: none

## Goal

Provide an installed agentflow CLI with an independently usable bundled template,
using Python 3.10+ stdlib at runtime. Source .agentflow remains the single source;
do not maintain a second tracked copy of template files.

## Read first

- AGENTS.md
- .agentflow/docs/agentflow-production-roadmap.txt
- .agentflow/tools/install.py
- .agentflow/tools/paths.py
- .agentflow/tools/run_task.py
- .agentflow/tasks/_template.md
- .agentflow/docs/release-validation.md

## Allowed files

- pyproject.toml
- setup.py
- MANIFEST.in
- src/agentflow/
- .agentflow/tools/cli.py
- .agentflow/tools/install.py
- .agentflow/tools/paths.py
- .agentflow/tools/upstream.py
- .agentflow/tests/test_cli.py
- .agentflow/tests/check_package.py
- .agentflow/tests/test_install.py
- .agentflow/tests/test_upstream.py
- .github/workflows/ci.yml
- .agentflow/docs/release-validation.md
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/ledger.py
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

- [ ] P-01: pyproject defines a wheel/sdist build and agentflow console entry. Use a clear local distribution name (agentflow-sdlc is acceptable); do not claim it is published on PyPI. Build dependencies are optional development tooling, core runtime Requires-Dist is empty except marked extras. Python >=3.10.
- [ ] P-02: Generate bundle data from installer-owned files at build time. Exclude actual state, task contracts, project rules/plan, runtime, .git, local output/versions, credentials and maintainer-only root instructions. Include needed install stubs/constants, entry-point generation and template tools/tests/dashboard. Wheel and sdist builds retain resources without the checkout. No copied tracked parallel template tree.
- [ ] P-03: CLI supports install (existing installer flags), run TASK --role ROLE, gate preflight TASK / verify TASK / stage N, accept TASK, ledger passthrough, dashboard --open, help/version. Role validates the task, never overrides it; Deployer is manual only. Preserve exit codes, argument boundaries and no-shell subprocess execution. No worker starts on role mismatch.
- [ ] P-04: Project operations discover the intended project root (optionally explicit --project), never write ledger/runtime into site-packages or operate accidentally on bundled memory. Install/update uses bundled template resources from any CWD after source checkout is absent. Paths with spaces work.
- [ ] P-05: check_package.py exercises a built wheel in a clean venv, invokes installed CLI outside source, installs and updates a disposable git project and checks project-owned preservation and no core third-party deps. Test wheel and sdist resource/provenance behavior. Keep ordinary unittest discover stdlib-only and offline; run build integration explicitly in its own isolated env. CI may add this integration once tooling is installed.
- [ ] P-06: Source CLI compatibility and focused tests pass, full suite passes. Increment the current intermediate 2.11 patch VERSION and synchronize AGENTS/changelog migration notes; reserve 2.12.0 for final release preparation. No public tag or push. Record packaging tradeoffs and exact commands in Result.

## Checks

- `python .agentflow/tools/cli.py --help` - source command interface.
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` - routing and refusal paths.
- `python .agentflow/tests/check_package.py` - isolated wheel/sdist install/update integration; may provision development build tools in disposable environments, never global runtime deps.
- `python -m unittest discover -s .agentflow/tests` - mandatory core suite.

## Result

