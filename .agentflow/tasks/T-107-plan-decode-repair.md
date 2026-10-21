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
