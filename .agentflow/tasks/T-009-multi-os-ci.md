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

