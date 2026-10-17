# T-004: Independently verify distributable package and unified CLI

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-003
Verifies: T-003 @ 1849b2bfd292f2d1fb3e19054f4029c5f42049e7

## Goal

Verify the agentflow-sdlc wheel/sdist and installed CLI independently of the
developer's own run. Same tool is necessary under the human's resource policy
(agy and claude limited, codex conserved); use a fresh isolated session. No
product changes; all installs go to disposable venvs and disposable projects.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-003-package-cli.md
- pyproject.toml, setup.py, MANIFEST.in
- src/agentflow/__init__.py, src/agentflow/cli.py
- .agentflow/tools/cli.py
- .agentflow/tests/test_cli.py
- .agentflow/tests/check_package.py
- .github/workflows/ci.yml (package job)
- CHANGELOG.md (2.11.12 entry)

## Allowed files

- nothing

## Do not touch

- pyproject.toml, setup.py, MANIFEST.in, src/
- .agentflow/tools/, .agentflow/tests/, .agentflow/dashboard/
- .agentflow/state/
- global Python environments, real PyPI or any index, credentials

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Build provenance is honest: the bundled template is generated at build time from install.py's owned list, no second tracked template tree exists in the checkout, and wheel+sdist exclude state, task files, project rules/plan, runtime, .git, dashboard output/versions and maintainer root instructions while including entry points, tools, tests and dashboard sources.
- [ ] V-02: Installed CLI behaves: from a clean venv outside the source checkout (path with spaces), install and update a disposable git project with bundled resources, preserve project-owned files, and project operations resolve the intended root via --project/discovery — never writing into site-packages or bundled memory. `run` refuses on role mismatch before starting anything; deployer is forced manual; argv/exit codes pass through shell-free.
- [ ] V-03: Distribution metadata is honest: Requires-Dist empty outside extras, build tooling optional only, Python >=3.10, no PyPI publication claim, local dist name agentflow-sdlc, version matches .agentflow/VERSION (2.11.12) with changelog and AGENTS block in sync.
- [ ] V-04: All four verbatim checks pass on the verified commit; report real failures, skips and environment causes. Source branch/worktree/Task File baselines unchanged; macOS package evidence remains a declared gap, not a pass.

## Checks

- `python .agentflow/tools/cli.py --help` - source command interface.
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` - routing and refusal paths.
- `python .agentflow/tests/check_package.py` - isolated wheel/sdist install/update integration; disposable environments only.
- `python -m unittest discover -s .agentflow/tests` - full regression suite.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python .agentflow/tools/cli.py --help` -> pass (exit 0; lists install/run/gate/accept/ledger/dashboard, --version, --project) - evidence: .agentflow/tasks/.runtime/T-004.evidence/check1-cli-help.txt
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` -> pass (14 passed / 0 failed) - evidence: T-004.evidence/check2-test-cli.txt
- `python .agentflow/tests/check_package.py` -> pass (all 20 printed checks ok, exit 0; disposable venvs under %TEMP%\af pkg check *, project path "disposable proj") - evidence: T-004.evidence/check3-check-package.txt
- `python -m unittest discover -s .agentflow/tests` -> pass (172 tests, OK, 127.7s) - evidence: T-004.evidence/check4-unittest.txt
Criteria:
- V-01 provenance and content - pass - evidence: `git ls-files` shows no tracked `agentflow/template/` tree (0 files; src/ holds only __init__.py and cli.py); bundle is generated at build time from install.py `owned_files()` (OWNED list install.py:46-49, SKIP excludes __pycache__/out/versions/.runtime; tasks limited to tasks/_template.md, docs to protocol+typesafe, no state/, no project-rules/plan, no template-source.json); check_package output "wheel carries the generated template bundle", "wheel bundle has no project memory (state/tasks/rules/plan)", "wheel carries template tests and dashboard", "sdist embeds the generated template tree", "sdist carries no checkout state"; MANIFEST.in excludes AGENTS.md/CLAUDE.md; .git never enters the OWNED list.
- V-02 installed CLI behaviour - pass - evidence: check_package ran `agentflow` from a clean venv at an unrelated CWD, installed + updated + dry-run-updated a git project on a path with spaces, template-source.json pointed into the venv's site-packages not the checkout, project-owned AGENTS.md preserved, `--project <proj> ledger show` worked; root discovery requires protocol file plus state/ or template-source.json (cli.py:52-56) so bundled memory is never a project; refusal paths covered by test_cli.py (`test_role_mismatch_starts_nothing`, `test_deployer_is_manual_only`, `test_passthrough_without_project_fails_closed`, `test_gate_passthrough_argv_and_exit_code`); subprocesses are list-argv `subprocess.call`, no shell (cli.py:87,94,124,140).
- V-03 metadata honesty - pass - evidence: T-004.evidence/v03-metadata.txt - Name agentflow-sdlc, Version 2.11.12 (matches .agentflow/VERSION), Requires-Python >=3.10, Requires-Dist only under `extra == "build"` (build, setuptools); pyproject comment states the name is not published on PyPI; CHANGELOG 2.11.12 entry dated 2026-10-17 and AGENTS.md block `AgentFlow version: 2.11.12` in sync.
- V-04 checks and baselines - pass - all four verbatim checks pass on 1849b2bfd292f2d1fb3e19054f4029c5f42049e7 in a detached disposable checkout; no skips or environment failures; developer worktree `agentflow-t-003-package-cli` still clean on t-003-package-cli @1849b2b, this checkout unchanged (`git status` clean, same SHA), task file hash unchanged (SHA256 f3eb4542...ed7ea); macOS remains a declared gap: release-validation.md says no green macOS result and the CI package job matrix is ubuntu-latest + windows-latest only.
New defects (outside the task):
- none
Cannot verify, needs:
- macOS behaviour of the package (declared gap; needs a GitHub macos-latest run of the package job)
Proposed memory updates:
- none

