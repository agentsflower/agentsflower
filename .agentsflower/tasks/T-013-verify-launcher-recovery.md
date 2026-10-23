# T-013: Independent verification of bounded launcher recovery

Role: tester
Tool: devin
Model: swe-2-high
Stage: 6
Depends on: T-012
Verifies: T-012 @ 87de72c4d71992c53fd7d34d6f5c1278580c8a78

## Goal

Independently evaluate the exact T-012 artifact, especially the demonstrated agy
interactive hang, bounded execution and honest resource/identity guarantees.
Same tool as Developer is necessary: agy Opus/Sonnet/GPT-OSS inference probes all
returned RESOURCE_EXHAUSTED; Claude unavailable and Codex is conserved by human.
Use a fresh session, make no fixes. Focused reads, not entire large files at once.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/tasks/T-012-launcher-recovery.md
- .agentflow/tools/run_task.py
- .agentflow/tests/test_run_task.py

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/
- .agentflow/tests/
- .agentflow/state/
- .agentflow/docs/
- AGENTS.md
- CHANGELOG.md

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Evaluate every T-012 criterion AC-01 through AC-14 separately with evidence. Overall verdict is worst criterion. Do not equate successful tests with meeting a stronger contractual guarantee.
- [ ] R-02: agy Tester argv is noninteractive, streams logs and has no newly elevated permissions. No real paid/quota probes or external project writes in automated checks.
- [ ] R-03: Parent wall-clock timeout terminates managed descendants, records an error and releases leases. Inspect behavior with absent/mismatched process identity, streaming-reader failures and tool timeout ignored.
- [ ] R-04: Selected-model access, unknown quotas and bounded policy are represented honestly. Catalog/auth checks must not be claimed as proof of inference entitlement; report any gap against AC-06.
- [ ] R-05: Full suite runs verbatim on the checked artifact; report exact count, failures and skips. Windows-only evidence does not establish real macOS/Linux behavior. Mark real Unix coverage unverified where required rather than inventing proof.
- [ ] R-06: Reviewed branch, developer worktree and task header/Result remain unchanged. Save evidence under AGENTFLOW_EVIDENCE and fill only this task's Result.

## Checks

- `python .agentflow/tools/run_task.py --help` - portable entry point and documented runtime controls.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - bounded execution and recovery regressions.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` - argv and wrapper compatibility.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on exact artifact.

## Result

Outcome: completed
Verdict: unverified
Checks:
- `python .agentflow/tools/run_task.py --help` -> pass (exit 0; portable entry point, all subcommands and documented runtime controls)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (22 passed / 0 failed, 19.5s)
- `python -m unittest discover -s .agentflow/tests -p test_launcher_args.py` -> pass (7 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (147 passed / 0 failed / 0 skipped, 79.2s, verbatim with the machine's real AGENTFLOW_* env exported)

Evidence files (AGENTFLOW_EVIDENCE): check1-help.txt, check2-test_run_task.txt, check3-test_launcher_args.txt, check4-full-suite.txt, agy-help.txt

Per-criterion evaluation of T-012 at 87de72c4d71992c53fd7d34d6f5c1278580c8a78 (detached checkout, clean):
- AC-01 - pass - evidence: every subcommand exercised in test_run_task.py + full suite; run-task.ps1 is a thin delegating wrapper preserving the exit code (test_wrapper_delegates_and_preserves_the_exit_code); existing tick/conductor callers unchanged on Windows (they still call run-task.ps1, which delegates). Unicode/space paths not explicitly exercised, but argv is built natively without shell quoting (low risk).
- AC-02 - pass - evidence: tests cover approval/terminal refusals, launch.lock + stale-lock removal, duplicate-launch refusal, corrupted runtime state failing closed, failed handoff leaving a recoverable error attempt with the lease returned and ledger at in progress; per-attempt baseline observed in this session's T-013.json.
- AC-03 - pass - evidence: test_tester_checkout_removed_and_link_target_untouched (detached checkout of the checked SHA, junction unlinked without following its target, checkout removed); worker_env forces AGENTFLOW_TARGET from the task and sets AGENTFLOW_EVIDENCE for testers; endcheck compares header hash, checked ref, worktree state and checked-file hash. Windows junction path verified; the POSIX symlink variant is inspected-only (p.is_symlink()->unlink cannot follow the target by construction).
- AC-04 - unverified - Windows fully verified: --stop kills the worker and its spawned grandchild, lease registry ends empty, wrong-start identity makes alive() report not-ours, unmeasurable identity refuses the kill. The Unix mechanism (start_new_session + killpg SIGTERM/SIGKILL) never executed - no Linux/macOS machine exists here; a real Unix run is required.
- AC-05 - pass - evidence: model/effort precedence tests (ArgvParityTests, LauncherArgsTests) incl. the duplicate --model regression; the tool x role permission matrix with preventive vs post-execution isolation is documented in the run_task.py docstring; unlisted role/tool combinations refuse the launch rather than downgrading; limit detection preserved (log-tail regex; documented heuristic).
- AC-06 - pass - evidence: resource_check covers executable, free authenticated-access probe, observed limits and machine capacity; probe=off or a failing probe refuses the unattended launch with an actionable diagnostic (test evidence); resourceCheck records at/exe/probe/probeSource, no percentages, no secrets in defaults. Gap against the criterion: the probe proves account-level access only - it does not check that the task's selected model is entitled for inference. The artifact does not claim otherwise (docstring "exit 0 = access"; developer Result calls `agy models` a catalog probe, access evidence only). Unknown quota stays unknown; the bound is the launcher-enforced wall clock (WORKER_TIMEOUT 1200s), an approved bounded time policy, not a fabricated quota.
- AC-07 - pass - evidence: all imports are Python 3.10+ stdlib plus local machine_capacity/paths; every Windows-API call sits under an os.name == "nt" guard; no PowerShell is invoked on the non-nt path (killpg/setsid/symlink/`ps` only); gate.py's shell() (pwsh on Windows, sh on Unix) is untouched by the diff; the suite uses only Python fake workers, isolated machine state and disposable repos - no real model calls.
- AC-08 - pass - evidence: the listed coverage exists (launch/status/stop-descendants, manual/recheck, failed handoff, concurrent refusal, approval/terminal refusals, argv, setup-link safety, grants/capacity, resource preflight). Full suite reported 0 skips; the two conditional skips (missing pwsh for the wrapper test, unmeasurable pid_start) explain their gap inline. Simulations are honestly labeled fakes.
- AC-09 - pass - evidence: the protocol diff is confined to launcher-related sections (file inventory, runtime state, launching workers); VERSION is 2.11.9 and 2.12.0 stays reserved; the AGENTS.md change is only the template block version line, outside-block text preserved; CHANGELOG 2.11.9 entry includes migration notes; decision updates were proposed in the Result, not written to canonical memory.
- AC-10 - pass - evidence: the developer Result contains the parity and permission matrices, actual platforms tested (Windows 10 + Python 3.13) and the honest Unix gap; this Tester verified the exact Change SHA (detached HEAD = 87de72c4d71992c53fd7d34d6f5c1278580c8a78, matching the Verifies header of this task).
- AC-11 - pass - evidence: tool_argv for (agy, tester) returns `-p <prompt> --output-format stream-json` with no permission flags (old launcher used `-i`, see parent run-task.ps1); the installed agy.exe --help confirms -p/--print is the noninteractive print mode and --output-format stream-json exists (read-only run, agy-help.txt); stdin is DEVNULL in run_logged, so no input channel exists; unsupported combinations still refuse.
- AC-12 - pass - evidence: test_wall_clock_timeout_kills_the_tree_and_records_an_error runs a Python fake that ignores any CLI timeout (sleeps 300s under a 5s bound): the tree died, the attempt recorded a "wall-clock timeout ... (AGENTFLOW_WORKER_TIMEOUT)" error, the lease registry ended empty, and EARLY-STREAMED appeared in the log while the attempt was still running. Enforcement lives in the launcher (p.wait(timeout) -> kill_tree), not the tool; a regression test asserts the agy tester argv contains no -i; probes are bounded by PROBE_TIMEOUT=45s and are recorded as access evidence, not entitlement proof.
- AC-13 - unverified - honesty requirements verified: docstring and protocol item 6 state observed limits are records, not an enforceable budget; unknown quota stays unknown. Unsafe-takeover refusal verified on Windows: wrong recorded start => not ours; unmeasurable identity => alive() false and --stop warns instead of killing a possibly reused pid. The macOS fix itself (`ps -o lstart=` parsed as "%a %b %d %H:%M:%S %Y" -> ticks) cannot execute or be faithfully simulated on Windows, and the Linux /proc path is likewise unexecuted here. It fails closed (None => refuse) if measurement fails, which bounds the risk.
- AC-14 - pass - evidence: verbatim `python -m unittest discover -s .agentflow/tests` = 147 tests, 0 failures, 0 skips, with this machine's real AGENTFLOW_* exported (AGENTFLOW_CODEX, AGENTFLOW_CODEX_ARGS, AGENTFLOW_DEVIN_ARGS, AGENTFLOW_MACHINE_CODEX_MAX, AGENTFLOW_TARGET=local, AGENTFLOW_TYPESAFE_KEY_FILE); fixtures strip machine AGENTFLOW_* variables (verified in test_parallel/test_tick/test_machine_capacity/test_dispatch/test_conductor). No remaining machine-environment failure.

Task criteria:
- R-01 - unverified - every criterion AC-01..AC-14 evaluated separately above; AC-04 and AC-13 cannot be established without a real Unix/macOS machine, so they are not equated with the passing Windows tests.
- R-02 - pass - evidence: agy tester argv is `-p <prompt> --output-format stream-json` (noninteractive, streams, no permission flags - no elevation vs the previous `-i`); automated checks use only Python fakes in temp dirs - no real paid/quota probes, no external project writes; agy --help exercised read-only.
- R-03 - pass - evidence: timeout test demonstrates tree-kill + timeout error + lease release with a CLI-timeout-ignoring fake; absent identity (pidStart None or unmeasurable) makes --stop warn and close the attempt as error without signalling a possibly reused pid; mismatched start identity is not ours (tested). Streaming-reader failure inspected: the pump is a daemon thread joined with a 10s bound, p.wait(timeout) is independent of it - a dead or stuck reader cannot unbound the process or hang completion.
- R-04 - pass - evidence: selected-model access is represented honestly (account-level probe recorded with source and time, no entitlement claim); unknown quotas stay unknown with the wall clock as the bounded policy; catalog/auth responses are not claimed as inference entitlement. Gap against AC-06 reported in the AC-06 line above: no per-model entitlement check exists before launch.
- R-05 - unverified - evidence: the verbatim suite ran 147/0/0 on Windows with the real machine environment; every POSIX-only path (.sh fake workers, start_new_session, killpg, symlink links, `ps -o lstart=`, /proc identity) executed zero times - Windows evidence cannot establish real macOS/Linux behavior.
- R-06 - pass - evidence: baseline verified mid-attempt - checkedRef = 87de72c4d71992c53fd7d34d6f5c1278580c8a78 (unchanged), checkedTree hash matches a clean developer worktree at that SHA, T-012 file hash and this task's header hash match the attempt baseline; evidence saved under AGENTFLOW_EVIDENCE; only this Result section was written.

New defects (outside the task):
- (inside the artifact, already disclosed by the developer) ai-handoff-protocol.md "Launching workers" item 2 still says "Visible windows only"; the Python worker spawns with CREATE_NO_WINDOW / no console. Observation is via log + --status + --stop. Rule and implementation now disagree.
- (pre-existing, disclosed) tick.py still spawns workers through pwsh run-task.ps1; on Unix a tick launch needs run_task.py invoked directly. roles/orchestrator.md, tool-routing.md, .agentflow/README.md, GUIDE.md, README.md and gate.py's docstring still say run-task.ps1.
- (minor) resourceCheck stores the env-provided probe argv verbatim; an operator who puts a secret inside AGENTFLOW_<TOOL>_PROBE would write it into tasks/.runtime/T-NNN.json. Built-in probes contain none.
- (pre-existing hygiene) a stray empty file named `nul` sits untracked in the repository root (dated 2026-10-14, predates this attempt) - a `> nul` redirect under Git Bash creates a real file.

Cannot verify, needs:
- A real macOS and a real Linux machine: worker spawn (start_new_session), killpg descendant kill, `ps -o lstart=` and /proc start identity, symlink Setup links, .sh fake workers. All POSIX-only code paths had zero executions here.

Proposed memory updates:
- known-issues.md: add - "2.11.9 launcher: POSIX-only paths (start_new_session/killpg tree-kill, `ps -o lstart=`/`/proc` pid identity, symlink Setup links) are implemented and statically reviewed but were never executed on a real macOS/Linux machine; verify on the first Unix install. Windows 10 + Python 3.13 verified (147 tests)."
- known-issues.md: keep the limitHit heuristic entry; add that machine AGENTFLOW_* exports no longer break the verbatim suite (fixtures isolate env).
- session-log.md: T-013 - independent verification of T-012 @ 87de72c on Windows: all 4 Checks verbatim green (147 tests, 0 skips), agy tester argv and wall-clock recovery confirmed, baseline untouched; verdict unverified solely for real macOS/Linux coverage.
