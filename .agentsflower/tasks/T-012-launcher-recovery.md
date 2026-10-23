# T-012: Recover Python launcher and bounded agy review

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: none
Branch: t-012-launcher-recovery
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-012-launcher-recovery
Independent check: tester
Resume: start fresh

## Goal

Current recovery: agy Opus failed with RESOURCE_EXHAUSTED after reading sources;
Sonnet and GPT-OSS probes also failed with the same reset window. All executors
have exited. Continue preserved draft on Devin medium to avoid the long high
reasoning stall. Focus on the concrete -i hang and regression/timeout repair;
read targeted function ranges rather than entire large files. Earlier recovery
notes below are historical, not instructions to select agy again.

Recovery attempt: prior Devin attempt was stopped after over ten minutes with no
log/Result and no repair changes. The staged original port is preserved in this
task's worktree; inspect it and continue, do not discard it. No prior repair
commit exists. Selected-model inference access for agy Opus was checked before
handover. This header update is after the previous attempt fully stopped.

Main baseline suite during handover: 124 tests, one transient WinError 5 replacing
a disposable registry file in test_dispatch. Immediate narrow rerun passed 5/5.
Report recurrence honestly; do not modify machine_capacity.py outside ownership.

Successor of rejected T-001. Preserve the unmerged Python port at
06b7e3afb2e6d85bc5f5e54ad9e9a80ccea2d62f while fixing the demonstrated agy
interactive Tester hang. The prior commit/worktree is read-only source material.
Apply its diff into this task branch without creating an extra commit, then make
the repairs; final branch has one task commit. Do not edit T-001 or T-002.
Use `git diff 06b7e3a^ 06b7e3a` as source, never merge an unaccepted task.

Port the existing launcher lifecycle to Python 3.10+ stdlib on Windows, macOS and Linux. Keep the PowerShell entry point as a thin compatible wrapper. Unsupported permission modes fail closed.

## Read first

- .agentflow/tasks/T-001-python-launcher-parity.md
- .agentflow/tasks/T-002-verify-python-launcher-parity.md

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

Outcome: completed
Change: 87de72c on t-012-launcher-recovery
Files:
- .agentflow/tools/run_task.py - preserved T-001 port (full launcher lifecycle, Python 3.10+ stdlib); repaired: agy Tester now runs `-p --output-format stream-json` (noninteractive print mode, no dangerous flags); `run_logged` got a launcher-enforced wall-clock limit (`AGENTFLOW_WORKER_TIMEOUT`, default 1200s, 0/non-number disables) that kills the managed process tree on expiry; `cmd_worker` records the timeout error (exitCode 124 if needed, state `error`) and releases the lease; `pid_start` gained a macOS/other-Unix fallback via `ps -o lstart=`; `alive`/`--stop` refuse to signal a pid whose recorded start identity cannot be confirmed
- .agentflow/tools/run-task.ps1 - thin wrapper delegating to run_task.py (from the preserved port, unchanged by the repair)
- .agentflow/tests/test_run_task.py - updated agy tester argv expectation (+regression: no `-i`, no dangerous flags); new `test_wall_clock_timeout_kills_the_tree_and_records_an_error` (Python fake sleeping past a 5s limit: streamed log line seen while running, tree killed, timeout note, lease released); new `test_recorded_pid_identity_is_verified_before_any_kill`
- .agentflow/tests/test_parallel.py, test_tick.py, test_machine_capacity.py, test_dispatch.py, test_conductor.py - fixtures now clear machine `AGENTFLOW_*` variables instead of only overriding a few, so the verbatim suite no longer depends on the machine environment
- .agentflow/tests/test_launcher_args.py, test_launcher_lifecycle.py, test_endcheck.py - as staged from the preserved port (wrapper delegation, spawn-failure via AGENTFLOW_WORKER_PYTHON, endcheck coverage)
- .agentflow/docs/ai-handoff-protocol.md - launcher-related sections only: Python launcher ownership, access probe, and item 6 now states that observed limits are records, not an enforceable budget, and that every non-manual worker runs under the launcher-enforced wall clock
- .agentflow/VERSION - 2.11.9 (kept; 2.12.0 reserved for release)
- CHANGELOG.md - 2.11.9 entry extended with the repair bullets and migration notes
- AGENTS.md - template block version 2.11.9, outside-block text untouched
Checks:
- `python .agentflow/tools/run_task.py --help` -> pass (exit 0)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (22 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` -> pass (7 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` -> pass (5 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (147 passed / 0 failed), run verbatim with this machine's real environment exported (AGENTFLOW_CODEX, AGENTFLOW_CODEX_ARGS, AGENTFLOW_DEVIN_ARGS, AGENTFLOW_MACHINE_CODEX_MAX=2, AGENTFLOW_TARGET=local, AGENTFLOW_TYPESAFE_KEY_FILE). No remaining machine-environment failure.
Criteria without a command:
- AC-11: agy tester argv is `agy -p <prompt> --output-format stream-json`, verified against the installed agy CLI help (agy.exe at C:\Users\Win10Pro\AppData\Local\agy\bin\agy.exe lists `-p/--print` noninteractive mode and `--output-format stream-json`); read-only only, no writes. No skip-permissions flags for Tester; disposable-checkout + endcheck isolation preserved; unlisted (tool,role) combinations still refuse to launch.
- AC-12: timeout is enforced by the launcher process itself (`p.wait(timeout=...)` -> `kill_tree`), not delegated to the tool's own CLI timeout; tested with a Python fake that ignores any CLI limit and sleeps 300s - the tree died, the attempt recorded `wall-clock timeout ... (AGENTFLOW_WORKER_TIMEOUT)` and the lease registry ended empty. Output streams to the attempt log while running (asserted before exit). Built-in probes are bounded by PROBE_TIMEOUT=45s; `agy models` is a model catalog probe, reported as access evidence only, not a quota measurement.
- AC-13: docstring and protocol say explicitly that observed quota/access limits are records, not an enforceable time/attempt budget; unknown quota stays unknown. macOS start identity now measured via `ps -o lstart=`; when a recorded identity cannot be re-confirmed, `alive` reports not-ours and `--stop` warns and skips the kill instead of signalling a possibly reused pid.
- Parity matrix (unchanged from the preserved port): launch/status/stop/mark-finished/recheck/manual/worker/dispatch-grant, runtime schema, launch.lock, preflight->claim->workdir->attempt->ledger->spawn order, env handover file, all error paths. Deliberate differences: detached Python worker instead of a pwsh window; UTF-8 logs; `mklink /J` vs symlink; taskkill /T /F vs killpg; pidStart .NET ticks on Windows, /proc on Linux, `ps lstart` elsewhere.
- Permission matrix: (codex,developer) danger-full-access preventive; (codex,tester) workspace-write+network preventive; (claude|agy|devin,developer) dangerous flags post-execution; (claude,tester) allowedTools post-execution; (agy,tester) `-p --output-format stream-json` post-execution; (devin,tester) permission-mode dangerous post-execution. Anything else refuses; no silent downgrade.
- Platforms actually tested: Windows 10 + Python 3.13, 147 tests. macOS/Linux paths (`ps lstart`, killpg, symlinks, POSIX fakes) are implemented and unit-covered where simulatable but not executed on a real Unix machine - honest gap for the independent Tester.
Found, not fixed:
- roles/orchestrator.md, roles/tool-routing.md, .agentflow/README.md, GUIDE.md, README.md and gate.py's docstring still say run-task.ps1; outside Allowed files or do-not-touch (wrapper keeps them literally true).
- tick.py still spawns workers through pwsh run-task.ps1 (do-not-touch): on Unix a tick launch needs run_task.py invoked directly; conductor stays Windows-only.
- Protocol rule "Visible windows only" unchanged; the Python worker has no console - observation is via log + runtime state + --stop, as under the previous -WindowStyle Hidden spawn.
- agy CLI also offers `--print-timeout`; deliberately not used because AC-12 requires parent-enforced bounds that hold even when a tool ignores its own timeout.
Proposed memory updates:
- decisions.md: "2026-10-16: 2.11.9 - launcher ported to Python (run_task.py owns the lifecycle; run-task.ps1 delegates) and hardened after the agy Tester hang: all tools run noninteractive, the launcher enforces AGENTFLOW_WORKER_TIMEOUT (default 20 min) by killing the managed tree, and macOS pid identity uses `ps -o lstart=` so --stop refuses unconfirmed/reused pids. Rejected: interactive -i testers (hangs), tool-side --print-timeout (tool can ignore it), treating observed limits as an enforceable budget, killing by pid when identity is unmeasurable."
- known-issues.md: resolve the 2026-10-03 entry about limitHit heuristics? No - keep it; add: machine AGENTFLOW_* exports no longer break the verbatim test suite (fixtures isolate env). Note agy -i interactive mode hung a Tester attempt (T-002) - fixed by -p + launcher wall clock.
- session-log.md: T-012 - recovered the staged Python port, repaired agy Tester interactivity, added launcher-enforced wall clock, macOS pid-start identity, env-isolated fixtures; 147 tests green verbatim.

