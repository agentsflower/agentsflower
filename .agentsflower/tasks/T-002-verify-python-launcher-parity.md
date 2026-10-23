# T-002: Independent verification of cross-platform Python launcher

Role: tester
Tool: agy
Model: claude-opus-4-6-thinking
Stage: 6
Depends on: T-001
Verifies: T-001 @ 06b7e3afb2e6d85bc5f5e54ad9e9a80ccea2d62f

## Goal

Independently verify the cross-platform Python launcher implementation (run_task.py, run-task.ps1 backward-compatible delegation, and portable test suite) against the acceptance criteria of T-001.

## Read first

- AGENTS.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/tasks/T-001-python-launcher-parity.md
- .agentflow/roles/tester.md

## Allowed files

- nothing

## Do not touch

- .agentflow/
- tests/
- AGENTS.md
- CHANGELOG.md

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] AC-01: Portable entry point `python .agentflow/tools/run_task.py --help` runs without error and documents supported commands.
- [ ] AC-02: Unit test suites for run_task, launcher args, launcher lifecycle, endcheck and dispatch pass cleanly.
- [ ] AC-03: Full regression test suite passes cleanly with machine environment isolated.
- [ ] AC-04: Review isolation held: checked commit, branch, and worktree unchanged.
- [ ] AC-05: Evaluate every T-001 acceptance criterion AC-01 through AC-10 against code and evidence, not only test exits. Explicitly assess model/resource probes, enforceable time/attempt bounds, permission claims and macOS process identity. Report missing real OS coverage as unverified, not pass.

## Checks

- `python .agentflow/tools/run_task.py --help` - CLI help check
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - portable launcher test suite
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` - argument and delegation test suite
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` - lifecycle and backward compatibility
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - end-of-attempt check
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` - dispatch grants
- `python -m unittest discover -s .agentflow/tests` - full regression suite verbatim; report machine-environment failures separately from an isolated-environment diagnostic run

## Result

