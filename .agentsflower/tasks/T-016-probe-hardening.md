# T-016: Make model preflight and runtime handover fail closed

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: none
Branch: t-016-probe-hardening
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-016-probe-hardening
Independent check: tester
Resume: none

## Goal

Successor of rejected T-014 at 549245f758dfa10419b119a86e2cb720b489e4c6.
Preserve its complete port with git diff of that commit against its parent, then
repair the concrete T-015 findings in one final task commit. Read T-015 Result
and its probe-edge-cases.txt evidence. Do not edit predecessors or their worktrees.
Real Linux/macOS coverage remains an external release gate, never claimed here.

## Read first

- .agentflow/tasks/T-014-model-preflight.md
- .agentflow/tasks/T-015-verify-model-preflight.md

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


Outcome: completed
Change: 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 on t-016-probe-hardening
Files:
- .agentflow/tools/run_task.py - complete T-014 port (verbatim diff of 549245f against its parent) plus the T-015 repairs: AGENTFLOW_<TOOL>_MODEL_PROBE accepts only `on` (audited built-in per tool); every other value fails closed, custom argv and the {model} placeholder were removed; account/catalog probes stay in AGENTFLOW_<TOOL>_PROBE; env-sourced account probes are recorded as source+sha256 argv hash only and never appear in diagnostics; built-in argv is recorded verbatim (file constants); toolArgs is recorded as a hash; the T-NNN.env.json plaintext handover was deleted - the worker gets the spawn environment in memory only; both probes run through a Popen-based run_capture that kills the probe's whole process tree on timeout (AGENTFLOW_PROBE_TIMEOUT/AGENTFLOW_MODEL_PROBE_TIMEOUT bounds, defaults 45/60); limitHit now requires a nonzero exit plus limit wording, so successful reports mentioning quota no longer limit the tool
- .agentflow/tools/run-task.ps1 - ported thin wrapper (unchanged)
- .agentflow/tests/test_run_task.py - ported suite plus reworked fixtures (fake_devin answers the built-in probe), new coverage: catalog/auth/custom MODEL_PROBE modes fail closed, denied selected-model inference fails closed, short bare/innocuous-flag dummy secrets never serialized, no env.json written, probe timeout kills the probe tree, successful quota prose does not set limitHit
- .agentflow/tests/test_launcher_lifecycle.py - MODEL_PROBE=on opt-in for fakes
- .agentflow/tests/test_route.py - fixture now strips all TYPESAFE_/AGENTFLOW_* exports; only the two it sets reach route.py (hermetic against real machine exports and the live registry)
- .agentflow/tests/test_launcher_args.py, test_endcheck.py, test_parallel.py, test_dispatch.py, test_conductor.py, test_tick.py, test_machine_capacity.py - ported, unchanged by the repair
- .agentflow/docs/ai-handoff-protocol.md - launcher item 6 updated: spawn-only environment handover, built-in-only model probe, hash-only probe evidence
- .agentflow/VERSION - 2.11.9 (intermediate, carried from the port)
- CHANGELOG.md - 2.11.9 entry extended with the fail-closed probe, hash-only evidence, env-file removal, limitHit fix; migration notes updated
- AGENTS.md - template block version 2.11.9 (port), outside-block text preserved
Checks:
- `python .agentflow/tools/run_task.py --help` -> pass (exit 0)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (26 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` -> pass (7 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` -> pass (5 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (151 passed / 0 failed / 0 skipped, twice in a row, ~113s each, machine's real AGENTFLOW_* exported). Honest report per AC-21: the first run of the same verbatim suite failed exactly once on a Windows transient - os.replace PermissionError (Access denied) inside machine_capacity._locked in a disposable fixture; machine_capacity.py is untouched by this task and both later runs were fully clean. test_route.py showed no failure in any run after hermetization.
Criteria without a command:
- AC-18 - MODEL_PROBE accepts only `on`; "catalog", "auth status", "--infer {model}" and "on extra" all refuse with "accepts only `on`" and no runtime file, so a catalog/auth exit 0 cannot produce modelProbe.result=ok; the {model} placeholder support was removed entirely.
- AC-19 - no T-NNN.env.json is written (asserted absent); worker env is spawn-only; env probes record source+sha256 hash; toolArgs records toolArgsHash; probe timeouts/failures print only exe + hash, never user argv or captured output; dummy secrets covered in "--token <s>", bare "hunter2" and "--config hunter2" forms; no heuristic secret guessing remains (safe_argv deleted).
- AC-20 - both probes run under env-overridable strict bounds through run_capture; on expiry kill_tree removes the probe's own session/group, proven by a fake that spawns a sleeping descendant; the 1200s worker bound and tester permissions are unchanged.
- AC-21 - test_route.py strips TYPESAFE_/AGENTFLOW_*; route.py semantics unchanged; verbatim suite green twice; Change SHA above is git rev-parse HEAD verbatim.
- AC-22 - limitHit = nonzero exit AND limit wording AND not a wall-clock timeout; genuine nonzero quota exhaustion still sets it (test_launch_exit_code_and_limit_detection); prose-only exit-0 reports do not. Heuristic limit: wording detection is regex-based, so a nonzero failure without matching wording is still not a limit.
- AC-15..AC-17 and AC-01..AC-14 - preserved from the verbatim port of 549245f; coverage notes in T-012/T-013/T-014 Results still apply. AC-15 additionally hardened per above.
Platforms tested: Windows 10 + Python 3.13 only. Real macOS/Linux coverage remains an external release gate - not performed, not claimed; POSIX-only paths (start_new_session/killpg probes, ps -o lstart=, /proc identity, symlink Setup links, .sh fakes) had zero real executions.
Parity matrix (launcher): launch/status/stop/manual/mark-finished/recheck/internal worker/dispatch grants - Python on Windows+macOS+Linux; run-task.ps1 translates old parameters and preserves exit codes on Windows only.
Permission matrix (unchanged): codex developer exec --sandbox danger-full-access (preventive) / codex tester exec --sandbox workspace-write + network (preventive); claude developer -p --dangerously-skip-permissions, claude tester -p --allowedTools Read,Grep,Glob,Bash,Edit; agy developer -p --dangerously-skip-permissions, agy tester -p --output-format stream-json; devin both -p --permission-mode dangerous (all post-execution isolation via end check). Unlisted combinations refuse to launch.
Found, not fixed:
- One transient os.replace PermissionError inside machine_capacity._locked under the verbatim suite on Windows (single occurrence in three runs; file not in Allowed files, unrelated to this change).
- (pre-existing, from T-013/T-014) tick.py still spawns workers through pwsh run-task.ps1; orchestrator.md, tool-routing.md, .agentflow/README.md, GUIDE.md, README.md and gate.py's docstring still name run-task.ps1; stray untracked `nul` in the repository root - all outside Allowed files.
Proposed memory updates:
- decisions.md (dated): "Custom AGENTFLOW_<TOOL>_MODEL_PROBE argv was removed as model evidence: a catalog/auth command exiting 0 cannot be told apart from inference. Only the audited built-in (`on`) proves the selected model; account/catalog checks remain at AGENTFLOW_<TOOL>_PROBE." and "The worker env handover file was deleted: spawn-passed environment only, so secret-bearing AGENTFLOW_* values are never serialized. Probe/toolArgs evidence is source+hash; limitHit requires nonzero exit plus limit wording."
- known-issues.md: resolve the T-014 env.json/safe_argv/custom-probe entry (fixed here); keep the real macOS/Linux coverage entry (external release gate); the test_route.py non-hermetic-fixture entry is fixed in test_route.py; optionally record the transient Windows os.replace PermissionError in machine_capacity._locked seen once under the full suite.
