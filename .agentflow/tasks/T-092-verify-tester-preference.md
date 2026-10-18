# T-092: Fast-path re-check of tester-independence preference and suite evidence

Role: tester
Tool: devin
Model: swe-2-high, effort=high
Stage: 5
Depends on: T-091
Verifies: T-091 @ 0bf4ac09fa08ef2c7cd77f6591993460511ebe07

## Goal

Fast-path independent re-check of the T-091 artifact at
0bf4ac09fa08ef2c7cd77f6591993460511ebe07 (T-085 precedent; scope narrowed
per the human's 2026-10-18 Option D decision in questions.md). The artifact
is 0ba5d37 (the T-078 scheduler/report layer) plus exactly one commit. The
routing machinery underneath was already independently deep-verified: T-075
on 5a6510c (assessment core), T-083 on fc2c37c (live backup-hold
admission), T-086 on 07fbeed (launch admission), T-088 on f6bc519 and
T-090 on 52b06aa (config alias + last-wins precedence). You do not repeat
that deep work. You confirm, in a fresh disposable checkout: the artifact
identity and scope, live proof of only the new prefer-scoped exemption
(K-02), that the recorded full-suite evidence is real, and the release
metadata. Fresh session, not the developer conversation. Same CLI per the
human's Devin preference; the Codex and Claude CLIs are reported without
resources and are excluded from assessments; observed agy holds remain
honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-091-tester-independence-preference.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-078-routing-scheduler-integration.md (the residuals this closes)
- .agentflow/tools/route.py (route()/avoid/prefer), .agentflow/docs/model-options.json (prefer/floor)
- .agentflow/tests/test_routing_core.py, test_routing_scheduler.py, test_tick.py
- The candidate diff `git diff 0ba5d37...0bf4ac09fa08ef2c7cd77f6591993460511ebe07` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-091 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040, T-074, T-076, T-082 and T-078 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (K-01) The disposable checkout HEAD is exactly 0bf4ac09fa08ef2c7cd77f6591993460511ebe07 with parent 0ba5d377f0deeae979588b23d8f29585b3a70cde; `git diff main...HEAD` stays inside T-091's Allowed files; `git diff 0ba5d37...HEAD` is only the prefer-exemption fix, the disclosed fixture repairs and the one-line CHANGELOG/metadata changes.
- [ ] V-02: (K-02) Prove live in the disposable checkout that a fresh assessment of a tester whose checked task ran on the preferred CLI can select that CLI's adequate option; that a live hold still excludes it; that the exclusion still applies to a non-preferred CLI and re-includes it when nothing else is eligible; and that adequacy still rules. Confirm the exemption is scoped to `prefer` membership, not hardcoded to devin.
- [ ] V-03: (K-03) The recorded full-suite evidence is real and belongs to this SHA (inspect the saved log tail .agentflow/tasks/.runtime/T-091.full-suite.txt: 424 tests, OK, 3 skipped); all three scoped Checks pass verbatim on the exact SHA; no live TypeSafe calls in tests.
- [ ] V-04: (K-04) VERSION/AGENTS/CHANGELOG agree at 2.15.4 with only the one-line addition; the inherited S-01..S-05 restatement is accurate (spot-check at least S-01's decide()/use_backup() gates and S-02's report fields against the code); T-040 not claimed complete.
- [ ] V-05: Map all K-01..K-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary. Evaluate whether the prefer-scoped exemption creates any hazard (e.g. a preferred CLI that is actually unusable for testers) and whether the test_approval/parallel/quota_groups fixture repairs are honest stubs rather than hidden behavior changes.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Execution bounds

15-minute cap. This is a fast-path identity/scope/delta check leaning on
prior independent verifications, not a second deep review of the routing
machinery. Run the three scoped Checks verbatim on the checked SHA, probe
the prefer-exemption eligibility paths live in disposable fixtures, verdict
by evidence. No code fixes, no gratuitous whole-suite run. Save evidence in
AGENTFLOW_EVIDENCE with basenames starting `T-092.`; put `evidence:` markers
at line end followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-05 plus `Verdict:`.

## Result
Outcome: completed
Verdict: fail

Checked artifact: 0bf4ac09fa08ef2c7cd77f6591993460511ebe07 in the launcher-provided disposable checkout (worktrees/agentflow-t-091-tester-independence-preference.t-092, detached HEAD, clean tree). Fast-path re-check per the human's Option D: deep machinery verification by T-075/T-083/T-086/T-088/T-090 is relied on, not repeated. Manual attempt (the devin CLI is unauthenticated): executed by the human-facing Devin session, not the T-091 developer conversation; evidence below.

Checks:

- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-092.evidence/T-092.check-test_tick.txt
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py` -> FAIL (10 passed / 1 failed). evidence: .agentflow/tasks/.runtime/T-092.evidence/T-092.check-test_routing_scheduler.txt
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (25 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-092.evidence/T-092.check-test_routing_core.txt

Criteria:

- V-01: pass - checkout HEAD is exactly 0bf4ac09fa08ef2c7cd77f6591993460511ebe07, parent 0ba5d377f0deeae979588b23d8f29585b3a70cde, clean tree, merge-base with main is 2a1d493 (the T-089 merge). `git diff main...HEAD` lists 16 files, all inside T-091's Allowed files; AGENTS.md delta is the version block only, _template.md delta is the Routing exception field only. `git diff 0ba5d37...HEAD` = 7 files: the prefer-exemption fix in route.py, the three disclosed fixture repairs, protocol rule 3, the CHANGELOG line. evidence: .agentflow/tasks/.runtime/T-092.evidence/T-092.v01-artifact.txt
- V-02: pass - proven live on the checkout code: for a tester whose checked task ran on devin (a configured `prefer` CLI) all adequate devin options stay eligible; a live devin:devin hold excludes every devin option ("limited until..."); a tester of a codex task still gets codex kept off, and it is re-included when it is the only catalog option; the exemption reads cfg["prefer"] membership (route.py:384-386), not a hardcoded tool name. evidence: .agentflow/tasks/.runtime/T-092.evidence/T-092.v02-prefer-exemption.txt .agentflow/tools/route.py
- V-03: fail - the recorded full-suite evidence is real ("Ran 424 tests in 406.321s / OK (skipped=3)", T-091.full-suite.txt) and no live TypeSafe calls occur in tests, BUT the scoped Checks do not pass verbatim on the exact SHA: test_routing_scheduler.py::test_a_held_backup_group_stays_scoped_and_refused fails with switched=True. Reproduction: run the file at any time after 2026-10-18T13:00Z. Root cause is in the test, not the product: it records the "live" hold at a fixed constant `AT + timedelta(hours=1)` where AT = 2026-10-18T12:00Z, so the hold is permanently expired once wall clock passes 13:00Z - the developer's own runs (before 13:00Z) passed. Verified live that machine_capacity.limit_until drops the expired hold while a real future hold makes route.backup_ok refuse correctly. This is a deterministic, permanent failure on the artifact (would break every future suite/CI run), not a flake. Fix is one line: use now()+delta instead of the fixed AT. evidence: .agentflow/tasks/.runtime/T-092.evidence/T-092.check-test_routing_scheduler.txt .agentflow/tasks/.runtime/T-092.evidence/T-092.v03-flake-repro.txt .agentflow/tasks/.runtime/T-092.evidence/T-092.v03-backup-ok-live.txt .agentflow/tests/test_routing_scheduler.py
- V-04: pass - .agentflow/VERSION, the AGENTS.md version block and CHANGELOG all read 2.15.4; the CHANGELOG delta vs 0ba5d37 is exactly the one line about the preferred-CLI independence rule landing at assessment time; the S-01/S-02 restatement spot-checks are accurate (tick.py:464 decide() calls route.assessment_problems, tick.py:555 use_backup() calls route.backup_ok, route_report.py:73-77 exposes the assessment/admission/human-exception fields); T-040 is not claimed complete. evidence: .agentflow/VERSION CHANGELOG.md AGENTS.md .agentflow/tools/tick.py .agentflow/tools/route_report.py
- V-05: pass - all K-01..K-04 mapped to the evidence above. Hazard evaluation: the prefer-scoped exemption cannot force an unusable preferred CLI - adequacy and live holds still rule (probed); if `prefer` were ever pointed at a tester-incapable CLI the same hold/adequacy gates apply. The test_approval/test_parallel/test_quota_groups repairs are honest stubs (a declared `Routing exception` fixture line and `assessment_problems` stubbed where the gate is not the unit under test); no hidden behavior changes. The real defect found is the fixed-clock constant in test_routing_scheduler.py:22 (V-03).

New defects (outside the task):

- .agentflow/tests/test_routing_scheduler.py:22 + line 242: `AT = datetime(2026, 10, 18, 12, 0, ...)` + `record_limit("devin", AT + timedelta(hours=1), "devin")` - the recorded "live" hold is already expired for any run after 13:00Z; deterministic permanent failure. Bounded fix: compute the hold from `datetime.now(timezone.utc)` (or another always-future time).

Cannot verify, needs:

- Nothing blocked; all criteria were evaluated.

Proposed memory updates:

- known-issues.md, 2026-10-18: T-092 found the test_routing_scheduler.py fixed-AT time bomb (V-03) - a scoped test wrote its "live" hold at a fixed clock time; after 13:00Z it is permanently expired and the test fails deterministically. Repair: now()-relative hold; re-verify T-091 after the fix.
- session-log.md, 2026-10-18: T-092 fast-path re-check (manual attempt; devin CLI unauthenticated) verdict FAIL on T-091 @ 0bf4ac0 - artifact identity/scope, prefer-exemption and metadata all pass; V-03 fails on the expired-hold test constant. Successor needed: one-line test fix then fast-path re-check.
