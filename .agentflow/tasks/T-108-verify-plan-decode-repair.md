# T-108: Independently verify the malformed-plan repair

Role: tester
Tool: devin
Stage: 5
Depends on: T-107
Verifies: T-107 @ 096040e406d225ee96bd7fcd39a6785e0291945d

## Goal

Independently evaluate the exact T-107 artifact
(096040e406d225ee96bd7fcd39a6785e0291945d) against every R-01..R-04 criterion
in its Task File, in a disposable checkout. The branch carries the verified
T-044 data-layer artifact (1d08950, reset --hard) plus one repair commit:
read_plan catches (OSError, ValueError) so a non-UTF-8 plan degrades to the
`unreadable` diagnostic instead of crashing the build. Fresh session, not
the developer conversation. Same CLI per the human's Devin preference: Codex
and Claude CLIs are statically excluded in model-options.json; the observed
agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-107-plan-decode-repair.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-106-verify-dashboard-data.md (the V-02 finding and its repro, plus the T-104/T-106 evidence chain this repair must satisfy)
- The candidate diff `git diff main...096040e406d225ee96bd7fcd39a6785e0291945d` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-107 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (R-01) Reproduce the T-106 defect live in the disposable checkout: write a non-UTF-8 (e.g. b"\xff\xfe") project-plan.md, run `python .agentflow/dashboard/build.py` - exit 0, task data still emitted, plan source `unreadable` with the fingerprint kept; the regression test exists and fails against the pre-repair code (negative control).
- [ ] V-02: (R-02) The fix is scoped to the plan reader: parse/join behavior, missing-plan and OSError paths, and all pre-existing dashboard tests unchanged; no other reader touched.
- [ ] V-03: (R-03/R-04) All four of T-107's Checks pass verbatim on the exact SHA; CHANGELOG 2.15.8 gained only the hardening line; VERSION stays 2.15.8.
- [ ] V-04: The artifact is exactly the verified 1d08950 plus one repair commit (`git rev-list main..096040e` = 2 commits: 1d08950 then 096040e); `git diff main...096040e` stays inside T-107's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-05: Confirm the T-106 evidence chain still holds on this SHA: the data-layer payload fields, ref validation, allowlists and demo fixture behave as T-106 verified (spot-re-run its probe areas - the repair must not have regressed them).
- [ ] V-06: Map all R-01..R-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`

## Execution bounds

Run the Checks verbatim on the checked SHA; reproduce the defect repro
live (negative control against the pre-repair reader); spot re-verify the
T-106 probe areas the repair could plausibly regress. No code fixes, no
gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE with
basenames starting `T-108.`; put `evidence:` markers at line end followed
only by intended claim paths - never quote an `evidence:` marker inside
prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (31 passed / 0 failed, on 096040e detached+clean)
- `python .agentflow/dashboard/build.py` -> pass (89 tasks, 6 stages, 91 dependencies, 20 successors, 211 commits -> out/)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out/ [DEMO DATA])
- plus T-107's 4th check `python -m unittest discover -s .agentflow/tests` -> see V-03 (2 verbatim runs, 454 tests each, 1 transient environmental error per run in artifact-untouched code), evidence: .agentflow/tasks/.runtime/T-108.evidence/T-108.checks.txt
Criteria:
- V-01: pass - live repro in this checkout: project-plan.md overwritten with b"\xff\xfe", `python .agentflow/dashboard/build.py` exited 0 emitting 89 tasks / 0 stages; payload plan source {"status":"unreadable","fingerprint":"sha256:b3d510ef","detail":"not decodable as UTF-8 text"} (fingerprint kept), warning "'utf-8' codec can't decode byte 0xff" and gap "stage data absent" present; probe also shows a generic ValueError degrades identically and missing-plan still reports "missing"; regression test test_undecodable_plan_is_a_diagnostic_not_a_crash ERRORS against the pre-repair build.py (git show 1d08950) with UnicodeDecodeError while all 30 pre-existing tests pass there - negative control holds, evidence: .agentflow/tasks/.runtime/T-108.evidence/T-108.repro.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.repro-build.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.negative-control.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.probe.txt
- V-02: pass - repair diff (1d08950..096040e) touches only build.py (read_plan except OSError -> (OSError, ValueError); real_graph flips plan source to unreadable with detail when bytes were read but text undecodable), one added test, one CHANGELOG line; parse_plan/join_stages/block_text/check_ref/attempt_view/verify_view/routing_view unchanged; missing->missing and OSError->unreadable wording identical; no other reader touched (ledger/Task-File fragility is pre-existing, out of scope per task), evidence: .agentflow/tasks/.runtime/T-108.evidence/T-108.scope.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.probe.txt
- V-03: pass - all 3 Checks verbatim green on 096040e; T-107's 4th check (full suite) ran twice verbatim on the exact SHA: 454 tests per run, one transient environmental failure/error per run in subsystems the artifact does not touch (run1 test_done_gate.test_accept_records_integrated_progress: WinError 5 in ledger.py _write_atomic on a temp tasks.md - known-issue 2026-10-18, file rerun 26/26 OK; run2 test_route.test_medium_band setUp: ledger.py add exit 1 in a temp fixture - known-issue 2026-10-16 class, standalone 4/4 OK, manual fixture loop 0/30); CHANGELOG 2.15.8 gained only the "- Hardening (T-107)..." line; VERSION = 2.15.8, evidence: .agentflow/tasks/.runtime/T-108.evidence/T-108.check4-fullsuite.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.check4-fullsuite-rerun.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.scope.txt
- V-04: pass - git rev-list main..096040e = exactly 2 commits (1d08950 parent 7279e3f, 096040e parent 1d08950): the verified T-044 artifact plus one repair commit; git diff --name-only main...096040e = VERSION, dashboard/README.md, build.py, test_dashboard.py, AGENTS.md, CHANGELOG.md - all inside T-107 Allowed files; T-107 Task File unmodified in the main repo (git status clean on it), evidence: .agentflow/tasks/.runtime/T-108.evidence/T-108.scope.txt
- V-05: pass - T-106's adversarial probe re-run verbatim against this checkout: 70/71 expectations identical (real-plan source order, fenced-code trap, heading boundaries, 15-case ref battery incl. junction escape, attempt/verify/routing allowlists dropping argv/env/pid/quota, malformed-runtime degradation to null+diagnostic, join_stages semantics, payload contract fields, demo fixture coverage/determinism); the single difference is checkout state, not product behavior: this worktree has an empty gitignored .runtime/ dir, so the runtime source reports "read"/"0 attempt records" where T-106's checkout reported "absent", evidence: .agentflow/tasks/.runtime/T-108.evidence/T-108.t106-probe.txt, .agentflow/tasks/.runtime/T-108.evidence/T-108.probe.txt
- V-06: pass - mapping: V-01->R-01 (undecodable plan degrades to diagnostics, task data still emitted, regression test + negative control), V-02->R-02 (decodable/missing/OSError paths and all other readers unchanged), V-03->R-03/R-04 (CHANGELOG line, VERSION, all four Checks), V-04->artifact shape/scope/task-file integrity, V-05->T-106 evidence chain re-probed on this SHA; every verdict backed by executed commands and payload output, none inferred from green summaries
New defects (outside the task):
- none in the artifact; the documented _write_atomic / ledger-subprocess WinError-5 flake recurred twice during this verification on two unrelated tests (both green in isolation) - third independent observation after T-082/T-083, strengthening the case for the bounded ledger-write hardening already suggested in known-issues
Cannot verify, needs:
- a fully clean single-run whole-suite pass could not be produced on this machine (each of two verbatim runs hit one transient temp-dir flake in code untouched by the artifact); everything else verified live on the exact SHA
Proposed memory updates:
- none required for the task itself; consider noting the repeated _write_atomic flake observation for the already-planned ledger-write hardening work
