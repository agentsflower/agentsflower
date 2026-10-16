# T-017: Verify fail-closed probes and secret-free handover

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-016
Verifies: T-016 @ 1e0bd876a4c3247416f6ccc3dd9c89970a36d695

## Goal

Independently replay the concrete T-015 findings against the repaired artifact.
Review the delta 549245f..1e0bd87 and T-016 AC-18..AC-22; reuse T-013/T-015
evidence only for unchanged behavior. Same tool is necessary: agy alternatives
are exhausted, Claude unavailable, Codex conserved. No real inference probes.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-016-probe-hardening.md
- .agentflow/tasks/T-015-verify-model-preflight.md
- .agentflow/tools/run_task.py (probe, evidence, env handover, limitHit ranges)
- .agentflow/tests/test_run_task.py (new regressions)
- .agentflow/tests/test_route.py (fixture isolation)

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/
- .agentflow/tests/
- .agentflow/state/
- .agentflow/docs/

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Catalog/auth/custom MODEL_PROBE values fail closed; only explicit audited built-ins run inference for the same concrete model selected by worker argv. Unknown/default model selection cannot silently prove a different model. Check opt-in and timeout without paid requests.
- [ ] R-02: Replay T-015 short-secret/innocuous-flag cases and fake launch. No raw probe/extra argv or AGENTFLOW_* values in any runtime file, including env handover. Evidence/diagnostics must not depend on heuristic secret guessing. Review spawned worker environment behavior after removing env JSON.
- [ ] R-03: Probe timeout kills managed descendants; worker timeout and agy Tester noninteractive argv remain intact. Successful quota prose does not set limitHit; real nonzero quota failures still do. Report limitations explicitly.
- [ ] R-04: Run full suite verbatim, save output/count/skips. Test_route fixture cannot reach live machine limits/leases through inherited env. Exact branch/worktree SHA and task baselines remain unchanged.
- [ ] R-05: Actual Linux/macOS execution remains unverified until real host evidence exists. Record this explicitly and do not issue an overall cross-platform pass on Windows tests alone. Separate any remaining local defect from this external gate.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - probes, secret safety, bounds and limit regression.
- `python -m unittest discover -s .agentflow/tests -p test_route.py` - isolated routing fixture.
- `python -m unittest discover -s .agentflow/tests` - full artifact suite.

## Result

Outcome: completed
Verdict: unverified
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (26 passed / 0 failed, ~34s)
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (11 passed / 0 failed, ~3s)
- `python -m unittest discover -s .agentflow/tests` -> pass (151 passed / 0 failed / 0 skipped, ~106s, verbatim on the Verifies SHA with the machine's real AGENTFLOW_* exported)

Checked artifact: detached HEAD 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 in this worktree, clean tree before and after; reviewed delta 549245f..1e0bd87 (6 files, +223/-138). No real inference probes run; fakes only.
Evidence files (AGENTFLOW_EVIDENCE): check1-test_run_task.txt, check2-test_route.txt, check3-full-suite.txt, probe-replay.txt, checked-sha.txt, worktree-status.txt.

Criteria:
- R-01 - pass - evidence: probe-replay.txt + test_selected_model_inference_probe_required_denied_and_recorded. Independent replay with a fake CLI (isolated machine-state dir): MODEL_PROBE="catalog", "auth status", "--infer {model}", "on extra", unset and "off" all fail closed with LaunchError before any attempt file exists; a catalog/auth exit 0 cannot reach modelProbe. Only `on` runs the audited built-in, which appends the task's concrete selected model via the tool's model flag (recorded argv ends "--model test-model-9"), so a default/unknown selection proves nothing about a different model. MODEL_PROBE="on" with inference denied (exit 4) fails closed with an actionable diagnostic. Opt-in and timeout confirmed without paid requests (AGENTFLOW_MODEL_PROBE_TIMEOUT, default 60).
- R-02 - pass - evidence: test_probe_secrets_are_never_serialized + diff/code inspection + probe-replay.txt. Short bare dummy secret ("hunter2"), secret after an innocuous flag ("--config hunter2") and flag-value secrets are never serialized: operator probe argv is recorded as probeHash only (probe=null, source=env), diagnostics show "exe <custom probe sha256:...>", no heuristic masking remains (safe_argv deleted, replaced by argv_hash). T-NNN.env.json and apply_env_file are deleted; the worker receives AGENTFLOW_* only through the Popen spawn env (os.environ minus TARGET/EVIDENCE), and cmd_worker rebuilds the tool env in memory via worker_env(t) - functionally the handover survives without any runtime file. toolArgs replaced by toolArgsHash for all tools. Probe stdout/stderr still never serialized.
- R-03 - pass - evidence: test_probe_timeouts_kill_the_probe_tree + code inspection. run_capture is Popen-based: on TimeoutExpired it calls kill_tree on the probe's own process group/session (CREATE_NEW_PROCESS_GROUP on Windows, start_new_session on POSIX); the test proves a spawned sleeping descendant dies. Worker bound unchanged (AGENTFLOW_WORKER_TIMEOUT default 1200, kill_tree + lease release); agy tester argv unchanged ("-p <prompt> --output-format stream-json", noninteractive, no elevation). limitHit now requires nonzero exit AND limit wording AND not timed_out: exit-0 quota prose does not limit (new regression), genuine nonzero quota failures still do (test_launch_exit_code_and_limit_detection). Honest limitation carried over: a nonzero failure without matching wording is still not flagged - wording regex remains heuristic.
- R-04 - pass - evidence: check3-full-suite.txt. Full suite verbatim on the exact Verifies SHA: 151 passed / 0 failed / 0 skipped; the T-016 one-time transient os.replace PermissionError did not reproduce. test_route.py now strips all TYPESAFE_/AGENTFLOW_* exports and sets only the two it needs (machine-state dir + assume-CLI), so the fixture cannot reach the live registry/leases through inherited env. Branch, worktree and task baselines unchanged (worktree-status.txt clean; no writes outside this Result).
- R-05 - unverified - Windows 10 + Python 3.13 evidence only. POSIX-only paths (start_new_session/killpg in run_capture and the worker spawn, ps/proc identity, symlink Setup links, .sh fakes) had zero real executions. No overall cross-platform pass is claimed; this is an external host-evidence gate, not a local defect.

New defects (outside the task):
- .agentflow/tools/conductor.ps1 ~185: Start-Orchestrator still serializes every AGENTFLOW_* variable verbatim into conductor.env.json - the same secret-handover class T-016 removed from run_task.py. The file was Do not touch for T-016; pre-existing, Windows-only orchestrator autostart path.
- (pre-existing, carried) tick.py still launches via pwsh run-task.ps1; orchestrator.md, tool-routing.md, README/GUIDE and gate.py's docstring still name run-task.ps1; stray untracked `nul` in the repository root.

Cannot verify, needs:
- A real macOS and a real Linux machine for all POSIX-only launcher paths (unchanged since T-013/T-015).

Proposed memory updates:
- known-issues.md: resolve the T-014 env.json/safe_argv/custom-probe entry (verified fixed at 1e0bd87); keep the real macOS/Linux coverage entry (still an external release gate); add that conductor.ps1 still writes AGENTFLOW_* verbatim to conductor.env.json.

