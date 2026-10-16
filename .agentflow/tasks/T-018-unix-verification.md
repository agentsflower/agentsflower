# T-018: Complete real Unix verification of launcher candidate

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: none
Branch: t-018-unix-verification
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-018-unix-verification
Independent check: tester
Resume: none

## Goal

Blocked successor of T-016 at 1e0bd876a4c3247416f6ccc3dd9c89970a36d695.
T-017 independently passed all local criteria and 151 Windows tests; overall
Verdict remains unverified solely for actual Linux/macOS execution. Preserve
the complete source diff of that commit into one final task commit; do not
repeat rejected older implementations. Wait for the human to choose real Unix
hosts or a CI branch for manual push. No push or publication by agents.
After the route is known, prepare the supported checks/CI and fix only
reproducible platform defects within ownership. No speculative refactoring.

## Read first

- .agentflow/tasks/T-016-probe-hardening.md
- .agentflow/tasks/T-017-verify-probe-hardening.md

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

- .github/workflows/ci.yml

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
- .agentflow/tests/test_route.py
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

- [ ] AC-23: Actual Linux and macOS worker/probe spawn, descendant termination, identity checks and Setup symlinks are executed and their evidence names exact SHA/OS/Python/commands/outcomes. No simulation-only pass. If human chooses CI, prepare the previously approved 3 OS x Python 3.10/3.11/3.12 matrix, give the exact branch/SHA for human push, and wait for actual run results. Do not push. Explain any skipped cases and block acceptance on missing mandatory evidence.

- [ ] AC-18: Remove arbitrary custom MODEL_PROBE argv as an entitlement proof. Support explicit opt-in built-in, audited inference commands for supported tool/model pairs; unknown or custom modes fail closed. Account/catalog custom probes remain account-level only. Tests demonstrate catalog/auth exit 0 cannot produce modelProbe.result=ok. Remove misleading placeholder support rather than silently accepting it.
- [ ] AC-19: Do not persist user probe/extra argv or raw AGENTFLOW_* values to any runtime file, including T-NNN.env.json. Use inherited/explicit subprocess environment in memory instead of a plaintext env handover file. Evidence records only safe metadata (source, config hash, selected model, timestamp, outcome); no heuristic secret guessing. Exception diagnostics omit user argv and captured output. Cover short positional dummy secrets and innocuous flag values, not just secret-shaped flag names. Include toolArgs in the audit; do not copy real credentials into tests.
- [ ] AC-20: Bound both account and model probes and terminate their managed child processes on timeout. Use fake spawning probes; no real paid calls in tests. Preserve the established 1200-second worker bound and isolated Tester permissions.
- [ ] AC-21: Make test_route.py fixtures hermetic to real machine AGENTFLOW_* exports and registry/leases, without changing route.py semantics. Full suite must run verbatim on the final artifact; report all failures. Runtime state and Task Result full Change SHA must match git rev-parse exactly; never invent the remainder from a short SHA.
- [ ] AC-22: A successful worker report merely mentioning quota/rate-limit test cases must not set limitHit and globally block a usable tool. Preserve detection of real provider failures. Add regression coverage for successful prose vs genuine nonzero quota exhaustion; report any heuristic limitations honestly.

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

