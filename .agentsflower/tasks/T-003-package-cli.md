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
Outcome: completed
Change: 1849b2bfd292f2d1fb3e19054f4029c5f42049e7 on t-003-package-cli
Files:
- pyproject.toml - setuptools build, dist name agentflow-sdlc (local, no PyPI claim), `agentflow` console entry, Python >=3.10, empty runtime deps, optional `build` extra
- setup.py - custom build_py/sdist: generates agentflow/template/ at build time from install.OWNED (no tracked copy); sdist embeds it so a wheel built from the sdist reuses it; version from .agentflow/VERSION; removes egg-info residue after the build
- MANIFEST.in - excludes maintainer root instructions (AGENTS.md/CLAUDE.md) and caches from the sdist
- src/agentflow/__init__.py, src/agentflow/cli.py - package __version__ from bundled template/VERSION; console entry loads the bundled tools/cli.py so installed and source CLI share one implementation
- .agentflow/tools/cli.py - the CLI: install passthrough to sibling or bundled install.py; run validates Task File Role/Tool (mismatch = exit 1, nothing started; deployer always --manual); gate/accept/ledger passthrough; dashboard [--open]; --version; --project. Project root = nearest .agentflow with protocol file + template-source.json or state/; no-shell subprocess, exit codes preserved
- .agentflow/tests/test_cli.py - 14 tests: discovery, refusal paths, argv/exit-code passthrough
- .agentflow/tests/check_package.py - explicit build integration (no test_ prefix): builds wheel+sdist, installs each in clean venvs, runs CLI outside source on a spaced path, checks bundle contents, provenance, project-file preservation, zero runtime deps
- .github/workflows/ci.yml - added `package` job (ubuntu+windows, py3.12) running check_package.py
- .agentflow/docs/release-validation.md - records the package job
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.11.12 bump, entry-block sync, changelog with migration notes; 2.12.0 left for release prep; no tag/push
Checks:
- `python .agentflow/tools/cli.py --help` -> pass (prints usage + all subcommands)
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` -> pass (14 passed / 0 failed)
- `python .agentflow/tests/check_package.py` -> pass (17 checks: wheel+sdist build, clean-venv installs, install/update on spaced disposable project, provenance, freeze = agentflow-sdlc only)
- `python -m unittest discover -s .agentflow/tests` -> pass (172 passed / 0 failed)
Criteria without a command:
- P-01..P-04 - covered by the check_package/test_cli evidence above: build deps optional-only, bundle generated from install.OWNED with state/tasks/rules/plan excluded (asserted on wheel and sdist contents), run refuses on role mismatch before any subprocess, deployer forced --manual, project discovery refuses bundled memory and bare .agentflow
- Packaging tradeoffs recorded: build-time code generation into build_lib + sdist file list (not package_data) keeps a single template source; the agentflow-sdlc name is local - publication would need a real index name
- Exact build/integration commands: `python -m build --outdir <dir>` (needs `pip install build` in a disposable env), `pip install <wheel|sdist>`, `python .agentflow/tests/check_package.py`
Found, not fixed:
- `gate verify T-003` at this point correctly reported FAIL before the commit/Result existed (attempt/Outcome/Change pending); left for the acceptance run
- `python -m build` prints a setuptools license-metadata deprecation warning (license = {text = "MIT"}); cosmetic, slated upstream change by 2027
Proposed memory updates:
- decisions.md (dated): T-003 chose setuptools + build-time bundle generation (sdist embeds the tree; wheel-from-sdist reuses it) so .agentflow stays the single source; dist name agentflow-sdlc is local-only; project-root marker = protocol file + (template-source.json or state/), which excludes bundled memory; run keeps --role as a match check because run_task.py derives the role from the Task File anyway
- release-validation / CI note: package job runs check_package.py on ubuntu+windows; macOS package evidence still unobserved (same gap as unit tests)

