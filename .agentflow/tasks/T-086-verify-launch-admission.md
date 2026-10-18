# T-086: Independently verify launch admission enforcement

Role: tester
Tool: devin
Model: gpt-6-astra-xhigh
Stage: 5
Depends on: T-076
Verifies: T-076 @ 07fbeed18e6a8d1a60eee491e1b81171b8090a6d

## Goal

Independently evaluate the exact T-076 artifact
(07fbeed18e6a8d1a60eee491e1b81171b8090a6d) against every I-01..I-05 criterion
in its Task File, in a disposable checkout. The artifact wires the accepted
T-074/T-084 admission API into `run_task.py cmd_launch` so every launch path
(direct, --manual, tick, retry) is refused on a missing/stale/failed/
low-confidence assessment or a resolved-identity downgrade, with an auditable
human exception path. Prove each claim with your own live probes; do not
re-quote worker results. Fresh session, not the developer conversation. Same
CLI per the human's Devin preference: Codex worker sandbox writes were
environment-blocked on this machine; observed agy holds remain honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-076-routing-launch-integration.md (contract + Result, not the checkout copy)
- .agentflow/tools/run_task.py (cmd_launch integration), .agentflow/tools/route.py (admission/identity_problems/log_admission)
- .agentflow/tests/test_run_task.py (RoutingAdmissionTests), .agentflow/tests/test_route.py, .agentflow/tests/test_endcheck.py
- .agentflow/docs/model-options.json, .agentflow/docs/typesafe.md, CHANGELOG.md (2.15.3 entry)
- The candidate diff `git diff main...07fbeed18e6a8d1a60eee491e1b81171b8090a6d` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-076 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040, T-074 and T-082 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (I-01) In the disposable checkout, `cmd_launch` calls `route.admission` after preflight/budget and before any probe/lease/spawn; the resolved identity uses header Model with AGENTFLOW_<TOOL>_ARGS filtered the same way the real argv is built. Prove with your own live probe that a missing, stale, failed or low-confidence assessment refuses a direct and a --manual launch before spawn, and that a `Routing exception:` header admits and is recorded distinguishably from Jev evidence.
- [ ] V-02: (I-02) Prove an env-flag downgrade (`AGENTFLOW_<TOOL>_ARGS --model <weaker>`) is refused on launch and on retry, an adequate resolved identity is admitted with a persisted admission event (safe metadata only), and process/lease/hold safety is preserved (nothing leased or spawned on refusal).
- [ ] V-03: (I-03) The new RoutingAdmissionTests really exercise disposable launches (not just mocks of the gate), and the T-072 watchdog regressions still pass; confirm no test makes live TypeSafe calls.
- [ ] V-04: (I-04) All three scoped Checks pass verbatim on the exact SHA; the recorded full suite (398/0/3 skipped) is reviewed not repeated; VERSION/AGENTS/CHANGELOG agree at 2.15.3 and accurately describe direct-launch enforcement with automatic backup/report integration left to T-078.
- [ ] V-05: (I-05) The model-options.json policy text implements the human's 2026-10-18 Devin preference for development, fresh independent testing and orchestration without lowering adequacy, inventing measured quota or touching observed holds; the tester-role and developer-role Devin-ordering tests exist and pass; no generic other-CLI preference remains.
- [ ] V-06: Map all I-01..I-05 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer success from a green summary. Evaluate the disclosure that tick.use_backup still ignores route.backup_ok at selection time - whether that is in-scope defect or correctly deferred to T-078.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`

## Execution bounds

20-minute cap. Run scoped checks verbatim on the checked SHA, probe the
admission/exception/downgrade paths live in disposable fixtures, verdict by
evidence. No code fixes, no gratuitous whole-suite run. Save evidence in
AGENTFLOW_EVIDENCE with basenames starting `T-086.`; put `evidence:` markers
at line end followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result

Outcome: completed
Verdict: fail

Reviewed artifact: 07fbeed18e6a8d1a60eee491e1b81171b8090a6d in the launcher's isolated checkout, Windows / Python 3.13.7. Product files and the developer worktree were not changed; no commit was made.

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (14 passed / 0 failed, exit 0).
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (53 passed / 0 failed, exit 0).
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed, exit 0).
- Recorded full suite reviewed, not repeated: the saved developer log says 398 tests run, OK (3 skipped), in 395.006s; this is 395 passed plus 3 skipped, rather than 398 passed plus 3 skipped.

Criteria:
- V-01: fail - I-01: admission is correctly after preflight/budget and before probes/lease/spawn; independent direct/manual probes refuse missing, stale, failed, low-confidence and blocked records without creating attempts or calling the CLI. Both human-exception paths are distinguishably audited. However D-01 admits a Codex low-effort env override while recording tier high, so admitted identity does not match outgoing arguments. evidence: `.agentflow/tasks/.runtime/T-086.evidence/T-086.live-probes.json` `.agentflow/tasks/.runtime/T-086.evidence/T-086.codex-alias.json` `.agentflow/tasks/.runtime/T-086.evidence/T-086.source-review.txt`
- V-02: fail - I-02: normal --model swe-2-medium downgrades refuse initial launch, repeated launch and an actual retry after a completed adequate attempt, preserving prior attempts and CLI-call count. Adequate launch records safe metadata and releases its lease; a correctly encoded active group hold blocks before probes/spawn. D-01 nevertheless bypasses the required effort through --config and starts a worker. evidence: `.agentflow/tasks/.runtime/T-086.evidence/T-086.live-probes.json` `.agentflow/tasks/.runtime/T-086.evidence/T-086.hold-recheck.json` `.agentflow/tasks/.runtime/T-086.evidence/T-086.codex-alias.json`
- V-03: pass - I-03: RoutingAdmissionTests use real launcher subprocesses, disposable Git repositories, synthetic persisted assessments and fake CLI executables, not a mocked admission gate. All 53 launcher and 14 watchdog tests pass. TypeSafe tests use a loopback stand-in and dummy key; launcher admission reads local records and performs no Jev call. evidence: `.agentflow/tasks/.runtime/T-086.evidence/T-086.test_run_task.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.test_worker_watchdog.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.source-review.txt`
- V-04: partial - I-04: all three scoped Checks pass on the exact SHA; the actual saved full-suite output was reviewed without rerunning it. VERSION/AGENTS/CHANGELOG agree at 2.15.3 and include migration instructions and the T-078 backup/report deferral. The universal env-override enforcement description is stronger than actual behavior because of D-01. evidence: `.agentflow/tasks/.runtime/T-086.evidence/T-086.test_route.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.test_run_task.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.test_worker_watchdog.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.recorded-full-suite.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.review.md`
- V-05: partial - I-05: the policy-text portion passes: Devin preference, fresh independent sessions, adequacy, qualitative until-2026-11-01 availability and observed holds are accurately stated; only policy text changed, and both new role-ordering tests pass. The broader no-generic-other-CLI-preference claim remains incomplete: a tester checking a Devin developer still has every Devin option excluded and selects Codex. Those tests only check developers on another CLI. This remaining behavior is explicitly assigned to T-078 S-05, so it is disclosed rather than treated as a request to broaden T-076. evidence: `.agentflow/tasks/.runtime/T-086.evidence/T-086.live-probes.json` `.agentflow/tasks/.runtime/T-086.evidence/T-086.candidate.diff` `.agentflow/tasks/.runtime/T-086.evidence/T-086.test_route.log` `.agentflow/tasks/.runtime/T-086.evidence/T-086.review.md`
- V-06: pass - I-01/I-02 fail, I-03 passes, I-04/I-05 are partial for the specific reasons above. tick.use_backup does not call route.backup_ok before changing the header, but automatic backup selection/reporting is explicitly excluded by T-076's Goal and owned by T-078 S-01; that omission is correctly deferred. D-01 concerns final launch admission and cannot be deferred under that exception. evidence: `.agentflow/tasks/.runtime/T-086.evidence/T-086.review.md` `.agentflow/tasks/.runtime/T-086.evidence/T-086.source-review.txt`

New defects and remaining gaps:
- D-01 (high, I-01/I-02): in a disposable task with Model gpt-6.1-sol, no header effort, and a matching ok assessment requiring high effort, set AGENTFLOW_CODEX_ARGS to `--config model_reasoning_effort=low` and launch through run_task.py. Expected: refusal before CLI/lease/spawn. Actual: exit 0, worker attempt 1 starts and completes, the outgoing argv retains the low setting, while the admission event says effort null / tier high. The otherwise equivalent `-c model_reasoning_effort=low` correctly refuses. The installed Codex help confirms --config is a supported alias. route.env_selected recognizes only -c; the launcher passes the long alias unchanged. The inherited parser limitation is exposed by the new integrated guarantee.
- The fresh-tester Devin exclusion remains a real behavior gap, already owned by T-078 S-05. Policy text alone does not remove route.py's static exclusion. The detailed review distinguishes the policy-text and effective-behavior readings of V-05.
- The first independent hold probe used an ISO string where the registry requires an epoch number. Its preserved TypeError is a fixture error, not a product defect. Only that diagnosed check was repeated with the correct schema and passed; both records remain in evidence.

Cannot verify, needs:
- No environment blocker prevented the assigned checks. Fake workers prove admission/argv/process/lease behavior without real provider inference; the TypeSafe stand-in is loopback only.
- The full-suite evidence is the developer's saved run, not an independent full-suite replay. Its narrative mentions an output-capture rerun, so the Result's "run once" wording is not corroborated.
- D-01 needs a developer correction and independent re-test before the launch-enforcement claim can be accepted.

Proposed memory updates:
- Record that T-086 checked 07fbeed independently with all 81 scoped tests green but Verdict fail because the supported Codex --config effort override bypasses admission. Preserve T-078 ownership of backup selection/reporting and the same-CLI tester-routing gap.
