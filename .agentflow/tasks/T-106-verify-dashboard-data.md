# T-106: Independently verify the roadmap dashboard data layer

Role: tester
Tool: devin
Stage: 5
Depends on: T-044
Verifies: T-044 @ 1d0895089d63a51e7b5987a98c34b449090f368f

## Goal

Independently evaluate the exact T-044 artifact
(1d0895089d63a51e7b5987a98c34b449090f368f) against every P-01..P-09 criterion
in its Task File, in a disposable checkout. The artifact adds the roadmap
data layer to .agentflow/dashboard/build.py (project-plan.md parser, stage
records joined with ledger/runtime evidence, schemaVersion-1 payload,
diagnostics, expanded --demo fixture), the README data contract, 21 new
dashboard tests, and 2.15.8 release metadata. Fresh session, not the
developer conversation. Same CLI per the human's Devin preference: Codex
and Claude CLIs are statically excluded in model-options.json; the observed
agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-044-dashboard-data.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...1d0895089d63a51e7b5987a98c34b449090f368f` in the disposable checkout
- .agentflow/dashboard/README.md (the declared data contract the payload must honor)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-044 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (P-01/P-02) The plan parser handles the real docs/project-plan.md (source order, fenced code, heading boundaries, raw text preserved) and the payload carries the documented stage record fields under schemaVersion:1 - verify against the README contract and the real build output, not the developer's summary.
- [ ] V-02: (P-03/P-04) Declared status, ledger counts and criterion evidence are three independent fields; zero-task stages total:0; stale Verifies SHA flagged; diagnostics carry sources/warnings/gaps/unmappedTaskIds; a bad plan cannot hide task data.
- [ ] V-03: (P-05/P-06) Evidence-ref validation rejects traversal/absolute/symlink escapes and non-http(s) URLs; attempts/routing/verify payload fields pass only allowlisted keys (no argv/env/pid/paths/quota); malformed records degrade to null + diagnostic, not a crash.
- [ ] V-04: (P-07/P-08) The --demo fixture exercises the named diagnostics and reads no canonical memory; the golden regression fixtures prove task fields are byte-identical to the pre-change build on identical inputs.
- [ ] V-05: (P-09) Both Checks pass verbatim on the exact SHA (`test_dashboard.py`, `build.py`, `build.py --demo`); the recorded full-suite evidence is reviewed; VERSION/AGENTS block/CHANGELOG agree at 2.15.8 with migration notes.
- [ ] V-06: The artifact is exactly one commit on t-044-dashboard-data; `git diff main...1d08950` stays inside T-044's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-07: Map all P-01..P-09 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`

## Execution bounds

Run the three Checks verbatim on the checked SHA; exercise the parser and
ref-validation against adversarial inputs inside disposable fixtures; audit
the payload allowlists for leaked unsafe fields. No code fixes, no
gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE with
basenames starting `T-106.`; put `evidence:` markers at line end followed
only by intended claim paths - never quote an `evidence:` marker inside
prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-07 plus `Verdict:`.

## Result
Outcome: completed
Verdict: partial
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (30 passed / 0 failed, on 1d08950 detached+clean)
- `python .agentflow/dashboard/build.py` -> pass (89 tasks, 6 stages, 91 dependencies, 20 successors, 208 commits -> out/)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out/ [DEMO DATA])
- all outputs recorded, evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.checks.txt
Criteria:
- V-01: pass - real docs/project-plan.md parsed in source order (ids 6,1,2,3,4,5), fenced code and level-1..3 heading boundaries honored, declaredRaw/exitCriteria verbatim; every README-contract stage field present in the real payload; README authored-syntax spec exists before use, evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.real-payload.json, .agentflow/tasks/.runtime/T-106.evidence/T-106.probe.txt
- V-02: partial - independent declared/counts/coverage fields, zero-task total:0 with no percentage, stale Verifies warning (demo: T-104 deadbeef vs 9f00dc1), sources/warnings/gaps/unmappedTaskIds all present; DEFECT: read_plan catches FileNotFoundError/OSError only - a non-UTF-8 project-plan.md raises UnicodeDecodeError and crashes the whole build (repro: write b"\xff\xfe" to a plan path, call read_plan -> unhandled UnicodeDecodeError, no payload, task data hidden), violating "malformed plan" diagnostics and "bad plan cannot hide task data" for that input class, evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.probe.txt, .agentflow/tasks/.runtime/T-106.evidence/T-106.demo-payload.json
- V-03: pass - 15-case ref battery green: ../, absolute / and ~, drive-letter C:, UNC, dir-junction escape (mklink /J resolved outside ROOT), javascript:/data:/file:/ftp: all invalid, http(s) pass as unfetched references, missing file -> refExists:false; ATTEMPT/VERIFY/CHECK/ROUTE allowlists drop argv/env/pid/workdir/quotaGroup/machineLease/usage/requestId/probabilities incl. nested admitted map; malformed/absent runtime records degrade to null + diagnostic (fake .runtime probe); real T-044.json confirms pid/argv/workdir/quota present in source and absent after filtering; note: empty ref= resolves to the project root and reports refExists:true (cosmetic, no escape), evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.probe.txt, .agentflow/tasks/.runtime/T-106.evidence/T-106.probe.py
- V-04: pass - demo fixture covers six-stage plan with zero-task stages, historical closure with References, one recorded recurring cycle, pass/fail/pending external evidence, planned-vs-ledger mismatch, duplicate-id warning, unmapped T-108; demo_graph reads literals + DEMO_PLAN only (check_fs=False, no git/ledger/plan reads), sources all synthetic, deterministic across runs; regression proven independently: pre-change build.py loaded from git main and re-run on identical inputs - all pre-existing task fields byte-identical, only additive attempts/routing/verifications and stages/diagnostics/provenance/schemaVersion added, evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.regression.txt, .agentflow/tasks/.runtime/T-106.evidence/T-106.demo-payload.json
- V-05: pass - three Checks verbatim green on the exact SHA; recorded full-suite claim (453 passed / 4 skipped, one transient _write_atomic WinError-5 rerun green) corroborated by known-issues entry 2026-10-18; VERSION=2.15.8, AGENTS block line 2.15.8, CHANGELOG 2.15.8 entry with migration notes, all in the same diff, evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.checks.txt
- V-06: pass - t-044-dashboard-data is exactly 1d08950, rev-list main..branch = 1 commit; diff name-only = build.py, README.md, test_dashboard.py, VERSION, AGENTS.md (version line only), CHANGELOG.md - all inside T-044 Allowed files; T-044 Task File unmodified in main repo, evidence: .agentflow/tasks/.runtime/T-106.evidence/T-106.checks.txt
- V-07: pass - mapping: V-01->P-01/P-02, V-02->P-03/P-04, V-03->P-05/P-06, V-04->P-07/P-08, V-05->P-09, all backed by probes/payloads above; no green summary was trusted without re-execution or adversarial input
New defects (outside the task):
- none new; the _write_atomic WinError-5 flake is already tracked in known-issues (2026-10-18); same UnicodeDecodeError fragility pre-exists in LEDGER/Task File reads (predates this artifact)
Cannot verify, needs:
- POSIX symlink escape not exercised (Windows checkout; dir-junction escape verified instead - same resolve()+is_relative_to path)
Proposed memory updates:
- none (tester); the Orchestrator may want a small fix task: catch ValueError/UnicodeDecodeError in read_plan (and optionally ledger/task-file reads) so a malformed plan degrades to diagnostics instead of crashing the build
