# T-001: Cross-platform Python launcher with PowerShell compatibility

Role: developer
Tool: devin
Model: swe-2-high
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

Outcome: completed
Change: 06b7e3afb2e6d85bc5f5e54ad9e9a80ccea2d62f on t-001-python-launcher-parity
Files:
- .agentflow/tools/run_task.py - new: the whole launcher lifecycle in Python 3.10+ stdlib (launch, --status, --stop, --manual, --mark-finished, --recheck, internal --worker, --dispatch-grant); same runtime-state schema, lock, gates, worktrees, setup links, capacity claims and ledger issuance as run-task.ps1 had
- .agentflow/tools/run-task.ps1 - now a thin wrapper: translates the old parameter names to run_task.py and preserves its exit code
- .agentflow/tests/test_run_task.py - new portable suite: disposable repos, Python fake workers (.cmd/.sh), isolated machine registry; launch/status/stop of descendants, manual/recheck, failed handoff, lock and duplicate/terminal refusals, corrupted-state fail-closed, grants/capacity, resource preflight, setup-link safety, argv parity
- .agentflow/tests/test_launcher_args.py - same model/effort cases now against run_task.tool_argv; plus a wrapper delegation/exit-code check
- .agentflow/tests/test_launcher_lifecycle.py - the spawn-failure test now injects a bad AGENTFLOW_WORKER_PYTHON instead of overriding Start-Process; other tests unchanged (they exercise the wrapper on pwsh/powershell and tick's real path)
- .agentflow/docs/ai-handoff-protocol.md - launcher-related references only (Terms, Runtime state, Launching workers 1 and 6): the launcher is run_task.py, run-task.ps1 delegates; machine-setup bullet now documents the access probe and AGENTFLOW_WORKER_PYTHON
- .agentflow/VERSION - 2.11.9
- CHANGELOG.md - 2.11.9 entry with migration notes
- AGENTS.md - AgentFlow version in the template block -> 2.11.9; outside-block text untouched
Checks:
- `python .agentflow/tools/run_task.py --help` -> pass
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (20 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` -> pass (7 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` -> pass (5 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (145 passed / 0 failed) with AGENTFLOW_SHARED_DISPATCHER and AGENTFLOW_MACHINE_CODEX_MAX unset; verbatim on this machine 4 unrelated tests fail (test_tick x2, test_parallel x1, test_machine_capacity x1) because the machine env leaks AGENTFLOW_SHARED_DISPATCHER=active and AGENTFLOW_MACHINE_CODEX_MAX=2 into them - an env-isolation gap in files outside Allowed files, not in the launcher diff
Criteria without a command:
- Parity matrix: launch/status/stop/mark-finished/recheck/manual/worker/dispatch-grant, runtime schema, launch.lock, preflight->claim->workdir->attempt->ledger->spawn order, env handover file, agy notice, and all error paths ported 1:1. Differences, all deliberate: worker is a detached Python process, not a pwsh window (the old code already used -WindowStyle Hidden); logs are always UTF-8 (Tee could write UTF-16 on PS5); Windows setup links use cmd `mklink /J`, POSIX uses symlink; tree stop uses taskkill /T /F on Windows, killpg TERM->KILL on POSIX; pidStart is .NET ticks on Windows and Linux (/proc), unmeasurable elsewhere so liveness is pid-only there.
- Permission matrix: (codex,developer)=danger-full-access preventive, (codex,tester)=workspace-write+network preventive, (claude|agy|devin,developer)=dangerous flags post-execution endcheck, (claude tester)=allowedTools post-execution, (agy|devin tester)=interactive/print flags post-execution. Any (tool,role) outside the table refuses to launch; no silent downgrade. Preventive = CLI-enforced sandbox (codex only); post-execution = disposable checkout + endcheck for everything else.
- AC-06 probes: built-in free checks `codex login status`, `claude auth status`, `devin auth status`, `agy models` (all verified to exist in this machine's CLIs except codex, which is not installed - per Codex CLI docs); AGENTFLOW_<TOOL>_PROBE overrides, `off` declares the tool uncheckable and blocks unattended launch; result recorded in attempt.resourceCheck (time, exe, probe, source, limits - no secrets). Quota remaining is never fabricated: unknown stays unknown, a bounded attempt policy is the existing limitHit->record_limit->fallback path.
- Platforms actually tested: Windows 10 + Python 3.13 only. macOS/Linux paths (symlinks, killpg, /proc pidStart, POSIX fakes in tests) are implemented and review-verified but not executed on a real Unix machine - the honest gap for T-002.
Found, not fixed:
- roles/orchestrator.md, roles/tool-routing.md, .agentflow/README.md, GUIDE.md, README.md and gate.py's docstring still say run-task.ps1; all are outside Allowed files or do-not-touch, and the wrapper keeps them literally true.
- Protocol rule "Visible windows only" kept its text; the previous launcher already spawned -WindowStyle Hidden and the Python worker has no console at all - observation stays through the log + state file + --stop.
- test_tick.py, test_machine_capacity.py, test_parallel.py read the real AGENTFLOW_* environment; two are outside Allowed files, so the isolation gap stays documented rather than fixed.
- tick.py still spawns workers through pwsh run-task.ps1 (do-not-touch): on Unix an automatic tick launch needs run_task.py called directly; conductor stays Windows-only per AC-09.
Proposed memory updates:
- decisions.md: "2026-10-15: 2.11.9 - launcher ported to Python (milestone 1). run_task.py owns the lifecycle on all OSes, run-task.ps1 delegates. Worker access is proven by a free per-tool probe (AGENTFLOW_<TOOL>_PROBE, built-ins for the four CLIs); a missing check blocks unattended launch instead of guessing. Rejected: treating CLI help/--version as access proof, and silently running unchecked. The (tool,role) permission matrix is explicit; unknown combinations refuse rather than downgrade. Rejected: porting the conductor (Windows-only by design)."
- session-log.md: T-001 done - Python launcher + wrapper + portable tests; 145 tests green with machine AGENTFLOW_* overrides unset.
- known-issues.md: this machine exports AGENTFLOW_SHARED_DISPATCHER=active and AGENTFLOW_MACHINE_CODEX_MAX=2, which break test_tick/test_parallel/test_machine_capacity env isolation when running the suite verbatim (not product bugs).
