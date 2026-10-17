# T-026: Integrate CI after runtime baseline repair

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-022
Branch: t-026-ci-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-026-ci-integration
Independent check: none - CI-only successor; matrix already inspected, final release Tester verifies artifacts
Resume: none

## Goal

Successor of T-009: its two CI files are correct, but acceptance full suite failed
on the existing intermittent test_route exit-code case. Wait for accepted T-022
runtime repair, then make a merge-only integration from current main of preserved
CI commit 6fe56f3418ac0d8e3b7a1c8e715ae9b37d56fc35. Do not rewrite CI behavior or
change product tools. One task integration commit, exact full SHA. No push.

## Read first

- AGENTS.md
- .agentflow/tasks/T-009-multi-os-ci.md
- .agentflow/tasks/T-022-runtime-reliability.md
- .agentflow/docs/ai-handoff-protocol.md (Successors and re-tests)

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
- pyproject.toml
- README.md
- GUIDE.md

## Setup

- nothing

## Port

- nothing

## Rebuild together

<!-- No shared rebuild resources. -->

## Acceptance criteria

- [ ] C-01: Preserved CI files integrated onto repaired main, no unrelated files or edits. Same 3 OS x quoted Python 3.10/3.11/3.12 matrix, read-only permissions, no persisted checkout credentials, bounded timeout, push/PR/manual triggers, no publishing/model calls.
- [ ] C-02: Exact full suite passes on integrated artifact. If the baseline still fails, report actual error and stop; never skip/soften the test to obtain acceptance.
- [ ] C-03: Validation doc still distinguishes prepared remote jobs from actual execution. No fake macOS result, tag, push or release. Preserve runtime VERSION; this is repository CI config only.

## Checks

- `python -m unittest discover -s .agentflow/tests` - repaired-baseline CI compatibility.

## Result

