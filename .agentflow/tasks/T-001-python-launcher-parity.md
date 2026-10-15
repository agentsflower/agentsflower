# T-001: Cross-platform Python launcher with PowerShell compatibility

Role: developer
Tool: claude
Model: opus, effort=high
Stage: 6
Depends on: none
Branch: t-001-python-launcher-parity
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-001-python-launcher-parity
Independent check: tester
Resume: none

## Goal

Port the existing launcher lifecycle to Python 3.10+ stdlib on Windows, macOS and Linux. Keep the PowerShell entry point as a thin compatible wrapper. Unsupported permission modes fail closed.

## Read first

- AGENTS.md
- .agentflow/docs/project-rules.md
- .agentflow/docs/agentflow-production-roadmap.txt
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/state/decisions.md
- .agentflow/tools/run-task.ps1
- .agentflow/tools/gate.py
- .agentflow/tools/ledger.py
- .agentflow/tools/paths.py
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/tick.py
- .agentflow/tools/conductor.ps1
- .agentflow/tests/test_launcher_lifecycle.py
- .agentflow/tests/test_launcher_args.py
- .agentflow/tests/test_endcheck.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tests/test_run_task.py
- .agentflow/tests/test_launcher_lifecycle.py
- .agentflow/tests/test_launcher_args.py
- .agentflow/tests/test_endcheck.py
- .agentflow/tests/test_parallel.py
- .agentflow/tests/test_dispatch.py
- .agentflow/tests/test_conductor.py
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/VERSION
- CHANGELOG.md
- AGENTS.md

## Do not touch

- .agentflow/tools/gate.py
- .agentflow/tools/ledger.py
- .agentflow/tools/accept.py
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/tick.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/conductor-panel.ps1
- .agentflow/state/
- .agentflow/dashboard/
- .agentflow/docs/project-rules.md
- .agentflow/docs/project-plan.md
- .agentflow/docs/agentflow-production-roadmap.txt
- README.md
- GUIDE.md
- pyproject.toml

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] AC-01: Python supports launch, status, stop, manual, mark-finished, recheck, internal worker and dispatch grants. PowerShell only translates old parameters and delegates, preserving exit codes, Unicode/space paths, interpreter overrides and existing tick/conductor callers.
- [ ] AC-02: Preserve preflight/approval, dependency and overlap checks, exclusive launch, attempts/baselines and launcher-owned ledger issuance before handoff. Duplicate/terminal launches fail; failed handoffs remain recoverable. Corrupted active runtime state fails closed.
- [ ] AC-03: Preserve worktrees, tester checkouts/isolation, setup link/copy/env, main-folder Result ownership and endcheck. Cleanup unlinks symlinks/junctions without following their targets. Preserve AGENTFLOW_TARGET and evidence environment behavior.
- [ ] AC-04: Preserve capacity/port claims, PID/start identity, grant exchange and lease activation/release. Stop handles managed descendant processes before another writer starts; uncertain ownership blocks takeover. Manual/error paths release resources correctly.
- [ ] AC-05: Preserve model/effort precedence, executable overrides, logs and limit detection. Document supported CLI/OS permission combinations and preventive versus post-execution isolation. Unsupported modes explicitly refuse execution without a permissions downgrade.
- [ ] AC-06: Before every worker start, check executable, authenticated model access, machine capacity and observed quota/access limits. Record the freshness/source of resource observations without secrets. CLI help alone is not proof of model access. Unknown quota is explicit and requires an approved bounded time/attempt policy or another checked route; no fabricated remaining percentage. Avoid paid probes unless authorized. Unsupported availability checks block unattended launch with an actionable diagnostic. Use fixtures for automated checks.
- [ ] AC-07: Core uses Python 3.10+ stdlib; Unix launch needs no PowerShell/Windows API. Checks retain PowerShell on Windows and sh on Unix. Portable tests use Python fake workers, isolated machine state and disposable repositories, never real paid model calls.
- [ ] AC-08: Tests cover launch/status/stop descendants, manual/recheck, failed handoff, concurrent launch refusal, approval/terminal states, arguments, setup-link safety, grants/capacity and model/resource preflight. Platform-specific skips explain gaps; simulations are not reported as real OS coverage.
- [ ] AC-09: Update only launcher-related protocol sections. Conductor/autostart stays Windows-only; ledger remains stateful; production approval remains human-only. Add CHANGELOG migration notes, intermediate VERSION 2.11.9 and matching AGENTS.md template block, preserving outside-block text. Reserve final 2.12.0 for release task. Propose canonical decision updates in Result for the Orchestrator.
- [ ] AC-10: Result gives parity and permission matrices, actual platforms tested and gaps. Independent T-002 must verify exact Change SHA before acceptance. If required fixes need files outside Allowed files, report blocked rather than expanding ownership.

## Checks

- `python .agentflow/tools/run_task.py --help` - portable entry point.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - lifecycle, permissions and resource checks.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` - model precedence and wrapper compatibility.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` - existing callers and issuance.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - Result ownership and isolation.
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` - shared grants compatibility.
- `python -m unittest discover -s .agentflow/tests` - mandatory regression suite before commit.

## Result

