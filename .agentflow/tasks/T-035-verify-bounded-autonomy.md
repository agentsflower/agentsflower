# T-035: Independently verify bounded autonomy

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-070
Verifies: T-070 @ 52250de

## Goal

Independently evaluate the exact T-070 artifact - the T-034 bounded-autonomy
feature set (recorded model identity, declared quota policy, launch budgets,
delegate rule, Codex Stop-hook prototype, bound check reuse) carried onto
current main by merge commit 52250de - against every H-01..H-04 criterion in
its Task File and the B-01..B-08 requirements it carries, in a disposable
checkout. Probe the load-bearing claims live; report the worst criterion as
the verdict.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-070-bounded-autonomy-carrier.md (contract + Result)
- .agentflow/tasks/T-034-bounded-autonomy.md (carried contract + Result)
- The candidate diff `git diff main...52250de` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-034 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] W-01: Attempt records carry requested Model:/effort AND the tool-reported effective identity (probe a real attempt record or the recorded fake-tool path); unreported identity is `unknown`, not guessed; pre-field records still parse.
- [ ] W-02: Launch budgets are enforced live: a 9th attempt is refused with records intact; a task exceeding the duration cap refuses; 3 identical failures stop relaunching; a 4th tool switch is refused; a nested launch is refused without `- delegate: on`.
- [ ] W-03: The quota policy mechanism works: quota-policy.json + a stale/missing reading yields `unknown` and never blocks; a policy reading below threshold shows up in tick decide/conductor output - probe through tick.py in a disposable state dir, not only tests.
- [ ] W-04: The Stop-hook adapter is honest: `agentflow hooks` without a valid codex install refuses without writing; the written hook is project-local only; codex-stop inside a managed session is inert. Probe what is safely probeable; do not install anything.
- [ ] W-05: checksHash binding is real: a verify PASS reused only when artifact+requirements+base+checksHash match; a changed check input forces re-measurement - probe with a disposable task.
- [ ] W-06: All claimed checks pass verbatim on the exact SHA (claimed 350/0/3-skipped); VERSION/AGENTS/CHANGELOG 2.15.0 in sync; diff inside Allowed files; safe-form masking actually masks (no prompt/env leakage in the recorded argv).

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - identity and budget regressions.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - quota policy regressions.
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - check-reuse binding.
- `python -m unittest discover -s .agentflow/tests -p test_hooks.py` - hook adapter regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (49 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` -> pass (26 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_hooks.py` -> pass (13 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (350 passed / 0 failed, 3 skipped - test_mcp_server ServerSurfaceTests: optional mcp SDK not installed in this interpreter)
Criteria:
- W-01: pass - evidence: .agentflow/tasks/.runtime/T-035.evidence/T-035.probe.log - a real `run_task.py T-001 devin` launch against a fake CLI in a disposable fixture recorded requestedModel test-model-x and requestedEffort high, toolVersion "fake-devin 9.9.9", and effectiveModel plus effectiveEffort parsed from the session log; a second launch whose tool reported nothing left toolVersion, effectiveModel and effectiveEffort as unknown (never guessed, requestedModel unchanged); the genuine pre-field T-070 attempt record in this repository's runtime state, written by the 2.14.1 launcher without any of the new fields, still parses under this artifact's --status
- W-02: pass - evidence: .agentflow/tasks/.runtime/T-035.evidence/T-035.probe.log + .agentflow/tasks/.runtime/T-035.evidence/T-035.probe2.log - live refusals on default caps through the real cmd_launch path: a 9th attempt refused with "attempt budget exhausted ... AGENTFLOW_MAX_ATTEMPTS=8" and the runtime file byte-identical afterwards; attempt 1 seeded 5h back refused on "task duration budget exhausted ... 14400s"; three same-signature failures refused on "identical failures budget exhausted"; a 4th distinct platform refused on "platform switch budget exhausted" while a repeat codex launch passed the budget (records intact throughout); AGENTFLOW_ATTEMPT + AGENTFLOW_ATTEMPT_ROOT nesting refused before any runtime file exists, and the same launch proceeded under a project `- delegate: on` Preflight rule
- W-03: pass - evidence: .agentflow/tasks/.runtime/T-035.evidence/T-035.probe.log - probed through the tick tool's status and `run --dry-run --json` in a disposable state dir: a missing quota-samples file and a stale reading both yield 'unknown' and the ready task stays would-launch (never blocks); a fresh 5% reading against a 20% threshold reports 'below' in tick status and the quotaPolicy report, with action pause -> task waits, switch -> task becomes a need, report -> informed but still launchable; an 80% reading reports 'ok'; a malformed quota-policy file exits 1 with a StateError (fails closed)
- W-04: pass - evidence: .agentflow/tasks/.runtime/T-035.evidence/T-035.probe.log + .agentflow/tasks/.runtime/T-035.evidence/T-035.probe2.log - `hooks.py enable codex` and the `agentflow hooks` passthrough refuse a missing executable and a codex-cli 0.100.0 runtime with exit 1 and write nothing; a 0.130.0 runtime advertising 'hooks stable true' prints manual steps without --write (still nothing written) and --write creates only the project-local codex hooks file (the real user-level codex hooks file stayed byte-identical); codex-stop under AGENTFLOW_ATTEMPT prints "managed AgentFlow session ... stays inert" and creates no verify record; a foreign cwd gets the normal-path advisory
- W-05: pass - evidence: .agentflow/tasks/.runtime/T-035.evidence/T-035.probe.log - `gate.py done` on a disposable completed developer task wrote a bound record carrying checksHash and gate:done; a second done reported reused=1 without adding a record; tampering the stored checksHash forced re-measurement (records 1 -> 2); records stripped of the field like legacy evidence were never reused (records -> 3)
- W-06: pass - evidence: .agentflow/tasks/.runtime/T-035.evidence/T-035.check1-run_task.txt + .agentflow/tasks/.runtime/T-035.evidence/T-035.check2-tick.txt + .agentflow/tasks/.runtime/T-035.evidence/T-035.check3-done_gate.txt + .agentflow/tasks/.runtime/T-035.evidence/T-035.check4-hooks.txt + .agentflow/tasks/.runtime/T-035.evidence/T-035.check5-full.txt + .agentflow/tasks/.runtime/T-035.evidence/T-035.diff-stat.txt + .agentflow/tasks/.runtime/T-035.evidence/T-035.merge-parents.txt - all five Checks pass verbatim at 52250de (49, 52, 26, 13, then 350 with 3 env-dependent skips); VERSION reads 2.15.0, the only AGENTS.md change in the diff is the 2.15.0 block line, CHANGELOG holds the 2.15.0 entry with migration notes above 2.14.1; `git diff main...52250de` touches 16 files all inside T-070's Allowed files; 52250de's parents are ccd74ba + b865709 with b865709 an ancestor (clean carrier merge); the recorded launch argv masks the prompt and every AGENTFLOW_DEVIN_ARGS token - neither 's3cr3t' nor 'machine-default' appears anywhere in the attempt record
Notes:
- H-01..H-04 map onto the probes above: B-01=W-01, B-02=W-03, B-03=W-02 budgets, B-04=W-02 nested/delegate plus the green machine-capacity tests, B-05=W-04, B-06=W-05, B-07 (plan_route --kind reaches Jev state and result) is covered inside the verbatim 350-test suite rather than a live Jev call, B-08=W-06
- H-02's second half was probed directly (probe3.log): the eight inherited T-034 Result outcome lines replay through this artifact's corrected evidence_problems with 0 problems, while fabricated claims (another task's .runtime file, a nonexistent in-scope path) still bind - the gate is fixed, not inert
- The quota-policy.json/quota-samples.json pair is absent from the tree by design (operator-authored config per protocol 3e; T-070 listed them as may-be-added); the mechanism was verified by writing both in the disposable fixture
New defects (outside the task):
- none
Cannot verify, needs:
- a live TypeSafe (Jev) call for plan_route --kind was not spent; its recording path is covered by test_plan_route inside the green suite
Proposed memory updates:
- none
