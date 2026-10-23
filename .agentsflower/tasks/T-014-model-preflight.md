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

Outcome: completed
Change: 549245f758dfa10419b119a86e2cb720b489e4c6 on t-014-model-preflight
Files:
- .agentflow/tools/run_task.py - ported artifact (T-012 @ 87de72c) plus: opt-in selected-model inference probe (AGENTFLOW_<TOOL>_MODEL_PROBE=on|custom argv with {model}, MODEL_PROBE_TIMEOUT=60s, empty temp cwd, stdin DEVNULL, no repository tools/writes); selected_model() resolves the effective model (task Model line, else AGENTFLOW_<TOOL>_ARGS); safe_argv() masks secret-shaped probe argv in evidence/diagnostics; run_capture gained cwd + closed stdin; resourceCheck now stores sanitized probe argv and a modelProbe record {at, model, source, argv, timeout, result}; unset/off model probe refuses unattended launches; account-access success with model inference denied fails closed; no remaining-quota figure is ever claimed
- .agentflow/tools/run-task.ps1 - thin compatibility wrapper delegating to run_task.py (port, unchanged semantics)
- .agentflow/tests/test_run_task.py - full ported lifecycle suite + 2 new regression tests: inference probe required/denied/recorded (incl. auth-ok + model-denied, builtin opt-in, {model} substitution) and dummy-secret masking in evidence and diagnostics
- .agentflow/tests/test_launcher_lifecycle.py - fixture opts the fake devin into the inference probe (AGENTFLOW_DEVIN_MODEL_PROBE=auth)
- .agentflow/tests/test_launcher_args.py, test_endcheck.py, test_parallel.py, test_dispatch.py, test_conductor.py, test_tick.py, test_machine_capacity.py - ported fixture/env isolation, unchanged
- .agentflow/docs/ai-handoff-protocol.md - item 2 rewritten: detached launcher-managed workers observed via log/--status/--stop with guaranteed wall clock (was "Visible windows only"); item 6 documents the model-inference probe, sanitization and no-quota-claims; launcher sections only
- .agentflow/VERSION - 2.11.9 (intermediate; 2.12.0 reserved for release)
- CHANGELOG.md - 2.11.9 entry extended: model-inference preflight, probe sanitization, visible-window rule fix; migration notes require AGENTFLOW_<TOOL>_MODEL_PROBE or -Manual for unattended launches
- AGENTS.md - template block version line 2.11.9 only; outside-block text preserved
Checks:
- `python .agentflow/tools/run_task.py --help` -> pass (exit 0; portable entry point)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (24 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` -> pass (7 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_dispatch.py` -> pass (5 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass on the final run (149 passed / 0 failed / 0 skipped, ~90s, machine's real AGENTFLOW_* exported). Honest report per AC-14: two earlier runs of the same verbatim suite each failed exactly one test in test_route.py (test_medium_band... 1 != 4, then test_low_band_is_no_decision 1 != 3). test_route.py is not in Allowed files, so it was not modified. The fixture passes this machine's real AGENTFLOW_* (AGENTFLOW_CODEX exe, AGENTFLOW_CODEX_ARGS, AGENTFLOW_MACHINE_CODEX_MAX=2) into route.py, which consults the real machine-capacity registry; exit 1 vs 3/4 is consistent with live codex slot/lease state on this machine, not with any T-014 change - the failure appeared on different tests across runs and the file passed in isolation (11/11) and inside the final verbatim run.
Criteria without a command:
- AC-15 - implemented as described above; covered by test_selected_model_inference_probe_required_denied_and_recorded (unset/off refused, auth-ok+model-denied refused, {model} substitution, builtin opt-in, recorded model/source/time/outcome). Probes use fakes only; no real paid calls were made. A probe success is recorded as point-in-time model access, never remaining quota.
- AC-16 - safe_argv masks flag values for secret-named flags (key|token|secret|passw|bearer|credential|cookie|header|signat|auth), name=value pairs and long bare values; probe stdout/stderr is never serialized; covered by test_probe_secrets_are_never_serialized with a dummy secret in both probes, asserted absent from runtime JSON and output.
- AC-17 - protocol item 2 now documents detached workers observed via log/--status/--stop plus the launcher-enforced wall clock; production approval (item 3/11) and permissions unchanged.
- AC-01..AC-14 - preserved by the verbatim port of 87de72c plus the additions above; all coverage notes from T-012's Result and T-013's evaluation still apply.
Platforms tested: Windows 10 + Python 3.13 (this machine). macOS/Linux execution evidence remains an external release gate - not performed here, not claimed; the POSIX-only paths (start_new_session, killpg, ps -o lstart=, /proc identity, symlink Setup links, .sh fakes) had zero real executions.
Parity matrix (launcher): launch/status/stop/manual/mark-finished/recheck/internal worker/dispatch grants - Python on Windows+macOS+Linux; run-task.ps1 translates old parameters and preserves exit codes on Windows only.
Permission matrix (unchanged): codex developer exec --sandbox danger-full-access (preventive) / codex tester exec --sandbox workspace-write + network (preventive); claude developer -p --dangerously-skip-permissions, claude tester -p --allowedTools Read,Grep,Glob,Bash,Edit, agy developer -p --dangerously-skip-permissions, agy tester -p --output-format stream-json, devin both -p --permission-mode dangerous (all post-execution isolation via end check). Unlisted combinations refuse to launch.
Found, not fixed:
- test_route.py intermittent failure inside the verbatim suite on this machine (see Checks note): its fixture forwards real AGENTFLOW_* exports to route.py, which reads the live machine-capacity registry; making it hermetic needs test_route.py, outside this task's Allowed files.
- (pre-existing, from T-013) tick.py still spawns workers through pwsh run-task.ps1 on Windows; roles/orchestrator.md, tool-routing.md, .agentflow/README.md, GUIDE.md, README.md and gate.py's docstring still reference run-task.ps1 - all outside Allowed files.
- stray untracked file `nul` in the repository root (pre-existing, predates this task).
- resourceCheck.toolArgs still records AGENTFLOW_CODEX_ARGS verbatim for codex attempts (pre-existing shape; a secret put there by an operator would be recorded - out of AC-16's probe scope, flagged for a successor).
Proposed memory updates:
- decisions.md (dated): "Unattended launches now require an explicit opt-in selected-model inference probe (AGENTFLOW_<TOOL>_MODEL_PROBE); the account-access probe alone was rejected as entitlement proof. Rejected alternative: running the built-in inference probe by default - it would perform surprise paid calls." and "Workers are documented as detached processes observed via log/--status/--stop with a launcher-enforced wall clock; the 'visible windows only' rule was retired because it no longer matched the implementation."
- known-issues.md: add - "test_route.py is intermittently non-hermetic inside the full suite on machines exporting AGENTFLOW_* (route.py reads the live machine registry); isolate the fixture in a follow-up." and keep the T-013 Unix-coverage entry: POSIX-only launcher paths still unverified on real macOS/Linux - external release gate.
