# T-015: Verify selected-model access and safe probe evidence

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-014
Verifies: T-014 @ 549245f758dfa10419b119a86e2cb720b489e4c6

## Goal

Independently review the delta 87de72c..549245f, especially T-014 AC-15..AC-17.
Reuse T-013 evidence for unchanged Windows behavior, but run the full suite on
the new SHA. Do not modify code or spend quota on real model probes. Other tools
are unavailable: agy alternative models exhausted, Claude unavailable, Codex
conserved by human. Fresh tester session on Devin is necessary.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-014-model-preflight.md
- .agentflow/tasks/T-013-verify-launcher-recovery.md
- .agentflow/tools/run_task.py (probe/selected_model/resource_check and safe_argv ranges)
- .agentflow/tests/test_run_task.py (new probe regression tests)

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

- [ ] R-01: T-014 AC-15 really checks the selected model. Inspect built-in and custom argv: an auth/catalog-only custom probe or omitted {model} must not silently become selected-model proof. Review tool model/effort precedence, opt-in, timeout and repository tool/write prevention. Demonstrate gaps with isolated fakes, never paid inference.
- [ ] R-02: AC-16 protects secret-bearing user probe argv and diagnostics, including flag=value, separate flag value and short bare dummy secrets. Probe output and exceptions must not leak them. Report heuristic limits honestly.
- [ ] R-03: AC-17 policy matches detached execution; new behavior preserves bounded noninteractive agy testing, no elevated Tester permissions, and human production approval.
- [ ] R-04: Record exact full-suite count/failures/skips and any repeatable test_route flakiness separately. Reviewer leaves branch/worktree/task baseline unchanged.
- [ ] R-05: Actual Linux/macOS coverage remains unverified unless backed by real host evidence. Overall verdict cannot claim cross-platform acceptance based on Windows-only tests. Distinguish local code defects from missing external evidence.
- [ ] R-06: T-014 Result names a wrong full Change SHA (same 7-character prefix). Actual branch/worktree HEAD is the Verifies SHA above. Report this evidence defect; do not silently correct the Developer Result. No code acceptance until authoritative Change is accurate.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - launcher/probe regressions.
- `python -m unittest discover -s .agentflow/tests` - exact artifact full suite.

## Result

Outcome: completed
Verdict: fail
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (24 passed / 0 failed, ~25s, twice)
- `python -m unittest discover -s .agentflow/tests` -> pass (149 passed / 0 failed / 0 skipped, 91.3s, verbatim on the Verifies SHA with the machine's real AGENTFLOW_* exported)

Checked artifact: detached HEAD 549245f758dfa10419b119a86e2cb720b489e4c6 in this worktree, clean tree, identical to t-014-model-preflight branch HEAD in the main repository.
Evidence files (AGENTFLOW_EVIDENCE): check1-test_run_task.txt, probe-edge-cases.txt, checked-sha.txt, worktree-status.txt.

Criteria:
- R-01 - partial - opt-in, fail-closed, model passing, bounds and recording verified: unset/`off` AGENTFLOW_<TOOL>_MODEL_PROBE refuses the unattended launch; account-ok+model-denied fails closed; `{model}` whole-token substitution works; builtin `on` appends the selected model flag; MODEL_PROBE_TIMEOUT=60s; probe runs in an empty temp cwd with stdin DEVNULL; builtins request no repository tools (codex --sandbox read-only, claude --allowedTools "", agy/devin -p only); resourceCheck records model/source/time/argv(sanitized)/result; no quota claim (test_selected_model_inference_probe_required_denied_and_recorded + code inspection run_task.py:587-628). Demonstrated gaps (isolated fakes, zero paid calls, probe-edge-cases.txt): (a) a custom non-inference argv is not distinguishable from an inference check - MODEL_PROBE="catalog" with Model: test-model-9 ran `exe catalog --model test-model-9`, exit 0, and was recorded `modelProbe.result=ok`; a catalog/auth-only custom probe can silently stand in as selected-model proof (the launcher appends the model flag syntactically but cannot verify the command performs inference); (b) `{model}` inside a joined token (`--model={model}`) is not substituted - only whole-argv elements match - so the literal placeholder is forwarded to the tool while the real model is appended after it; the recorded argv shows this honestly. Minor: the subprocess timeout bounds the probe process itself, not a tree.
- R-02 - fail - two confirmed leaks with a real fake launch (probe-edge-cases.txt): (1) the AGENTFLOW_* handover (run_task.py:880-883) writes every AGENTFLOW_ variable verbatim into `.agentflow/tasks/.runtime/T-NNN.env.json`; a dummy secret inside AGENTFLOW_DEVIN_PROBE / AGENTFLOW_DEVIN_MODEL_PROBE was found verbatim in T-001.env.json while T-001.json held only masked values - secret-bearing probe argv is serialized into runtime evidence, against AC-16. (2) safe_argv heuristic limits: a short bare secret (`hunter2`) and a secret value after an innocuous flag (`--config hunter2`) are recorded unmasked; secret-named flags in `--flag value` and `--flag=value` forms are masked, bare values >40 chars or containing a key word are masked, `name=value` positionals are masked, probe stdout/stderr is never serialized and LaunchError/TimeoutExpired diagnostics use safe_argv (test_probe_secrets_are_never_serialized + direct safe_argv calls).
- R-03 - pass - evidence: protocol item 2 now documents detached launcher-managed workers observed via log/--status/--stop with a launcher-enforced wall clock; the diff touches only items 2 and 6; item 3 (human-only production approval, Deployer/live-Tester in a -Manual session) and item 4 (permissions from launcher flags) are unchanged; PERMISSIONS still allows only developer/tester per tool and agy tester argv stays `-p <prompt> --output-format stream-json` - noninteractive, streaming, no elevated flags.
- R-04 - pass - evidence: full suite verbatim 149/0/0 on 549245f (check saved); test_route.py run twice in isolation: 11/11 then 11/11 - the intermittent failure the developer reported inside the suite did not reproduce this attempt; it remains a real non-hermetic-fixture risk (route.py reads the live machine registry through forwarded AGENTFLOW_* values). Branch, worktree and task baselines left unchanged (worktree-status.txt clean; no writes outside this Result).
- R-05 - unverified - only Windows 10 + Python 3.13 evidence exists here; POSIX-only paths (start_new_session, killpg tree-kill, `ps -o lstart=`/`/proc` identity, symlink Setup links, .sh fakes) had zero real executions; cross-platform acceptance cannot be claimed.
- R-06 - pass - the criterion's premise was not observed: the current T-014 Result names `Change: 549245f758dfa10419b119a86e2cb720b489e4c6`, identical to `git rev-parse t-014-model-preflight` in the main repository and to this checkout's HEAD. If an earlier draft named a wrong full SHA, it is already corrected; no evidence defect remains to report.

New defects (outside the task):
- run_task.py ~880-883: the worker env handover writes all AGENTFLOW_* variables raw into .runtime/T-NNN.env.json, re-serializing any secret inside AGENTFLOW_<TOOL>_PROBE/_MODEL_PROBE verbatim (demonstrated).
- run_task.py:606-612: a custom MODEL_PROBE that performs no inference (catalog/auth) is recorded as `modelProbe result=ok` once it exits 0; `{model}` is not expanded inside `flag=value` tokens.
- run_task.py safe_argv: bare short secrets and values after non-secret-named flags are not masked.
- (pre-existing, carried from T-013/T-014) tick.py still launches via pwsh run-task.ps1; orchestrator.md, tool-routing.md, README/GUIDE and gate.py's docstring still name run-task.ps1; stray untracked `nul` file in the repository root; resourceCheck.toolArgs records AGENTFLOW_CODEX_ARGS verbatim.

Cannot verify, needs:
- A real macOS and a real Linux machine for all POSIX-only launcher paths (unchanged since T-013).

Proposed memory updates:
- known-issues.md: add - "T-014 @ 549245f: the worker env handover (.runtime/T-NNN.env.json) serializes secret-bearing AGENTFLOW_<TOOL>_PROBE/_MODEL_PROBE values verbatim; safe_argv also misses short bare secrets and values after innocuous flags. Custom MODEL_PROBE argv that performs no inference is still recorded as model probe ok; `{model}` is not expanded inside flag=value. Fix before treating the model preflight as entitlement proof."
- known-issues.md: keep - real macOS/Linux coverage still missing (external release gate); test_route.py fixture remains non-hermetic with live AGENTFLOW_* exports (intermittent, not reproduced this attempt).

