# T-107: Repair read_plan malformed-input crash on the verified data-layer artifact

Role: developer
Tool: devin
Stage: 5
Depends on: none
Branch: t-107-plan-decode-repair
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-107-plan-decode-repair
Independent check: tester
Resume: none

## Goal

T-044 was rejected solely on the T-106 tester's V-02 finding: `read_plan` in
.agentflow/dashboard/build.py catches `FileNotFoundError`/`OSError` but not
`UnicodeDecodeError` (a `ValueError` subclass), so a non-UTF-8
`project-plan.md` crashes the whole build - no payload, task data hidden -
violating the P-04 "malformed plan degrades to diagnostics" contract
(repro: write `b"\xff\xfe"` as the plan, call read_plan). The rest of the
artifact was independently verified on the exact SHA.

Move this task's new branch onto the preserved artifact commit
1d0895089d63a51e7b5987a98c34b449090f368f (git reset --hard from the
launcher-created start, clean tree), then repair: treat undecodable or
otherwise `ValueError`-raising plan input the same way a missing plan is
treated - a diagnostics entry (plan source `unreadable`), never a crash -
and prove it with a regression test. The same fragility pre-exists in the
ledger/Task-File readers but those predate the artifact and are NOT in this
task's scope (recorded in known-issues).

## Read first

- .agentflow/tasks/T-044-dashboard-data.md (contract + Result section)
- .agentflow/tasks/T-106-verify-dashboard-data.md (the V-02 finding and repro)
- .agentflow/dashboard/build.py (read_plan and the plan-source diagnostics path)
- .agentflow/tests/test_dashboard.py (PlanParserTests - extend it)

## Allowed files

- .agentflow/dashboard/build.py
- .agentflow/dashboard/README.md
- .agentflow/tests/test_dashboard.py
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/tools/
- .github/
- .agentflow/dashboard/out/ and versions/ (generated/local)
- other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: A non-UTF-8 or otherwise undecodable `project-plan.md` no longer crashes the build: read_plan treats it like the missing/absent case - plan source `unreadable` (or equivalent diagnostics state), stages empty/degraded, task data still emitted, exit 0. Proven by the T-106 repro (`b"\xff\xfe"` bytes) as a regression test in test_dashboard.py.
- [ ] R-02: Malformed-but-decodable input keeps its existing behavior (the diagnostics paths T-044 built stay intact); no other reader behavior changes.
- [ ] R-03: The 2.15.8 CHANGELOG entry (unreleased) gains one honest line about the malformed-plan hardening; VERSION stays 2.15.8.
- [ ] R-04: All three of T-044's Checks plus the full suite pass verbatim on the new SHA.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`
- `python -m unittest discover -s .agentflow/tests`

## Result
Outcome: completed
Change: 096040e on t-107-plan-decode-repair
Files:
- .agentflow/dashboard/build.py - read_plan catches (OSError, ValueError) so UnicodeDecodeError degrades to the `unreadable` diagnostic; real_graph marks the plan sources entry `unreadable` (keeping fingerprint, detail "not decodable as UTF-8 text") when bytes were readable but undecodable
- .agentflow/tests/test_dashboard.py - PlanParserTests.test_undecodable_plan_is_a_diagnostic_not_a_crash: b"\xff\xfe" plan and a generic ValueError both return None with an `unreadable` diagnostic, no exception
- CHANGELOG.md - one hardening line added to the unreleased 2.15.8 entry
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (31 passed / 0 failed)
- `python .agentflow/dashboard/build.py` -> pass (89 tasks, 6 stages, 91 dependencies, 20 successors, 209 commits -> out/)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out/ [DEMO DATA])
- `python -m unittest discover -s .agentflow/tests` -> pass (450 passed / 4 skipped)
Criteria:
- R-01: pass - live repro verified on the artifact base: worktree project-plan.md replaced with b"\xff\xfe", `python .agentflow/dashboard/build.py` exited 0 with 89 tasks and 0 stages emitted; payload shows plan source status "unreadable" (fingerprint kept, detail "not decodable as UTF-8 text"), warning "is unreadable ('utf-8' codec can't decode byte 0xff...)" and gap "project plan ... unavailable - stage data absent"; the b"\xff\xfe" repro is a regression test in test_dashboard.py
- R-02: pass - decodable-malformed behavior untouched: parse_plan/join_stages unchanged, all 30 pre-existing dashboard tests still pass; the sources-status flip only fires when bytes read but text undecodable (missing->missing and OSError->unreadable paths unchanged)
- R-03: pass - CHANGELOG 2.15.8 gained the "- Hardening (T-107)..." line; VERSION still 2.15.8, AGENTS block untouched
- R-04: pass - all three T-044 Checks plus the full suite ran verbatim and green on 096040e
Found, not fixed:
- same UnicodeDecodeError fragility pre-exists in the ledger/Task File readers (LEDGER.read_text and Task File reads in real_graph) - predates the artifact, explicitly out of this task's scope (recorded in known-issues)
Proposed memory updates:
- none
