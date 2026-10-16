# T-014: Close selected-model preflight and probe evidence gaps

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: none
Branch: t-014-model-preflight
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-014-model-preflight
Independent check: tester
Resume: none

## Goal

Successor of T-012
at 87de72c4d71992c53fd7d34d6f5c1278580c8a78. Read T-013 Result. Preserve the
complete tested port by applying `git diff 87de72c^ 87de72c` into this new branch,
without adding a second commit. Do not use the older 06b7e3a as the final source.
Close selected-model inference access and safe probe-evidence recording gaps;
align launcher visibility policy with the documented detached worker behavior.
Real Linux/macOS execution evidence remains an explicit external release gate;
do not claim it was performed or weaken that requirement.

Do not edit any predecessor branch, worktree or task. Read targeted function
ranges, not entire large files at once. Source artifact already passed 147 tests
in independent Windows review. This is a new task with one final commit.

## Read first

- .agentflow/tasks/T-012-launcher-recovery.md
- .agentflow/tasks/T-013-verify-launcher-recovery.md

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
- .agentflow/tests/test_tick.py
- .agentflow/tests/test_machine_capacity.py
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

- [ ] AC-15: Before an unattended worker starts, prove access to the selected concrete model with a bounded provider-supported inference check, or fail closed with an actionable diagnostic. Account auth/model catalog alone is insufficient. Any inference probe is explicit opt-in (no surprise paid calls), passes the actual selected model, runs without repository tools/writes and has a strict timeout. Record model identity, observation source/time and outcome; never claim exact remaining quota from inference success. Tests use fakes and cover auth success with model inference denied.
- [ ] AC-16: Never serialize secret-bearing user probe argv/output into runtime evidence or exceptions. Preserve useful sanitized diagnostics. Add regression fixtures with dummy secret values; do not read real credentials.
- [ ] AC-17: Update the launcher-related visible-window rule to reflect detached Python workers observed through logs/status/stop and guaranteed wall clock. Document current behavior, not a claim of a visible console. Keep production approval and permissions unchanged.

- [ ] AC-11: agy Tester uses noninteractive print mode with streaming logs and an explicit 20-minute default wall-clock limit. Do not add dangerous/skip-permissions flags to Tester. Preserve existing post-execution isolation guarantees and fail closed on unsupported configuration. Exercise actual installed CLI read-only behavior if available; no production or external project writes.
- [ ] AC-12: Parent runner independently enforces timeout and kills the managed process tree, records a timeout error and releases lease. Test with a Python fake that ignores CLI timeout. Captured output appears while running, not only at exit; regression tests fail for interactive -i mode. Bound any access probe separately; a model catalog/auth response is not proof of selected-model inference entitlement.
- [ ] AC-13: Do not call observed limit detection an enforceable time/attempt budget. Document unknown quotas honestly. Fix macOS unknown process-start identity so stop/recovery does not kill a potentially reused PID; refuse unsafe takeover when identity cannot be established.
- [ ] AC-14: With verbatim full suite, isolate any machine AGENTFLOW_* contamination in owned test fixtures, including test_parallel.py if needed. Report any remaining failure rather than claiming cleaned-environment success satisfies the verbatim check.

- [ ] AC-01: Python supports launch, status, stop, manual, mark-finished, recheck, internal worker and dispatch grants. PowerShell only translates old parameters and delegates, preserving exit codes, Unicode/space paths, interpreter overrides and existing tick/conductor callers.
- [ ] AC-02: Preserve preflight/approval, dependency and overlap checks, exclusive launch, attempts/baselines and launcher-owned ledger issuance before handoff. Duplicate/terminal launches fail; failed handoffs remain recoverable. Corrupted active runtime state fails closed.
- [ ] AC-03: Preserve worktrees, tester checkouts/isolation, setup link/copy/env, main-folder Result ownership and endcheck. Cleanup unlinks symlinks/junctions without following their targets. Preserve AGENTFLOW_TARGET and evidence environment behavior.
- [ ] AC-04: Preserve capacity/port claims, PID/start identity, grant exchange and lease activation/release. Stop handles managed descendant processes before another writer starts; uncertain ownership blocks takeover. Manual/error paths release resources correctly.
- [ ] AC-05: Preserve model/effort precedence, executable overrides, logs and limit detection. Document supported CLI/OS permission combinations and preventive versus post-execution isolation. Unsupported modes explicitly refuse execution without a permissions downgrade.
- [ ] AC-06: Before every worker start, check executable, authenticated model access, machine capacity and observed quota/access limits. Record the freshness/source of resource observations without secrets. CLI help alone is not proof of model access. Unknown quota is explicit and requires an approved bounded time/attempt policy or another checked route; no fabricated remaining percentage. Avoid paid probes unless authorized. Unsupported availability checks block unattended launch with an actionable diagnostic. Use fixtures for automated checks.
- [ ] AC-07: Core uses Python 3.10+ stdlib; Unix launch needs no PowerShell/Windows API. Checks retain PowerShell on Windows and sh on Unix. Portable tests use Python fake workers, isolated machine state and disposable repositories, never real paid model calls.
- [ ] AC-08: Tests cover launch/status/stop descendants, manual/recheck, failed handoff, concurrent launch refusal, approval/terminal states, arguments, setup-link safety, grants/capacity and model/resource preflight. Platform-specific skips explain gaps; simulations are not reported as real OS coverage.
- [ ] AC-09: Update only launcher-related protocol sections. Conductor/autostart stays Windows-only; ledger remains stateful; production approval remains human-only. Add CHANGELOG migration notes, intermediate VERSION 2.11.9 and matching AGENTS.md template block, preserving outside-block text. Reserve final 2.12.0 for release task. Propose canonical decision updates in Result for the Orchestrator.
- [ ] AC-10: Result gives parity and permission matrices, actual platforms tested and gaps. Independent successor Tester must verify exact Change SHA before acceptance. If required fixes need files outside Allowed files, report blocked rather than expanding ownership.

## Checks

- `python .agentflow/tools/run_task.py --help` - portable entry point.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - lifecycle, permissions and resource checks.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` - model precedence and wrapper compatibility.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` - existing callers and issuance.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - Result ownership and isolation.
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` - shared grants compatibility.
- `python -m unittest discover -s .agentflow/tests` - mandatory regression suite before commit.

## Result

