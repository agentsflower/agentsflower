# T-009: Prepare multi-OS public CI

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-024
Branch: t-009-multi-os-ci
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-009-multi-os-ci
Independent check: none - repository-only CI configuration; final release Tester reviews the matrix and evidence limits
Resume: none

## Goal

Prepare the approved CI milestone now so the remaining macOS evidence can be
obtained after the human pushes. No remote trigger, push, tag or publication.
This task owns no template tool/version files and can run beside T-022.

## Read first

- AGENTS.md
- .agentflow/docs/agentflow-production-roadmap.txt
- https://github.com/actions/checkout
- https://github.com/actions/setup-python
- .agentflow/tests/test_launcher_lifecycle.py

## Allowed files

- .github/workflows/ci.yml
- .agentflow/docs/release-validation.md

## Do not touch

- .agentflow/tools/
- .agentflow/tests/
- .agentflow/state/
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md
- README.md
- GUIDE.md
- pyproject.toml

## Setup

- nothing

## Port

- nothing

## Rebuild together

<!-- No shared rebuild resources. -->

## Acceptance criteria

- [ ] C-01: Workflow runs the exact unittest discover command on ubuntu-latest, macos-latest and windows-latest crossed with quoted Python 3.10/3.11/3.12. fail-fast false; bounded job timeout; push, pull_request and manual dispatch supported. No pull_request_target, model calls, deployment or publishing.
- [ ] C-02: Use official supported actions (official current README documents checkout@v7/setup-python@v7). Read-only repository permission and persist-credentials false. Isolate machine registry in runner temp; no real AGENTFLOW credentials. Preserve expected platform-specific skips, without masking genuine failures.
- [ ] C-03: release-validation.md explains local Windows/Linux evidence versus nine remote jobs not yet run, and exact human push/dispatch/read-results steps. Never invent a green macOS run. Later package/MCP tasks may extend this workflow after ownership ends.
- [ ] C-04: Inspect matrix/trigger syntax and run current full suite. This is repository CI configuration, not a template runtime release: do not independently bump VERSION or edit shared release metadata.

## Checks

- `python -m unittest discover -s .agentflow/tests` - baseline regression compatibility.

## Result
Outcome: completed
Change: 6fe56f3 on t-009-multi-os-ci
Files:
- .github/workflows/ci.yml - new CI workflow: push/pull_request/workflow_dispatch; matrix ubuntu-latest/macos-latest/windows-latest x Python "3.10"/"3.11"/"3.12"; fail-fast false; timeout-minutes 20; permissions contents:read; checkout@v7 persist-credentials false; setup-python@v7; runs `python -m unittest discover -s .agentflow/tests` with AGENTFLOW_MACHINE_STATE_DIR in runner.temp and PYTHONUTF8=1
- .agentflow/docs/release-validation.md - new doc: local Windows/Linux evidence vs nine not-yet-run remote jobs, explicit "no green macOS result" caveat, numbered human push/dispatch/read-results steps
Checks:
- `python -m unittest discover -s .agentflow/tests` -> pass (152 passed / 0 failed)
Criteria without a command:
- C-01 - matrix/trigger syntax inspected: exact discover command on 3 OS x 3 quoted Python versions, fail-fast false, bounded timeout, push+pull_request+workflow_dispatch, no pull_request_target/model calls/deploy/publish
- C-02 - checkout@v7 and setup-python@v7 confirmed against the official current READMEs; read-only permission, persist-credentials false, registry isolated in runner.temp via AGENTFLOW_MACHINE_STATE_DIR, no credentials; existing platform skip guards preserved untouched
- C-03 - release-validation.md states evidence limits honestly and gives exact human steps; no remote run claimed
- C-04 - matrix/trigger inspected; full suite run; VERSION and shared release metadata untouched (repository CI config only)
Found, not fixed:
- none
Proposed memory updates:
- After the human pushes, the nine-job matrix run (especially macos-latest) supplies the missing remote evidence; record the run URL/result in the release task

