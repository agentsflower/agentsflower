# T-091: Finish tester-independence preference and suite evidence

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-091-tester-independence-preference
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-091-tester-independence-preference
Independent check: tester
Resume: none

## Goal

Successor of rejected T-078. The artifact at
0ba5d377f0deeae979588b23d8f29585b3a70cde is complete except two diagnosed
gaps (its own honest Result): (1) S-05 residual - `route.py`
eligibility/static_reason still removes the checked task's CLI for tester
assessments whenever another catalog option remains, so a fresh assessment
of a tester-of-devin task selects Codex although an adequate Devin option
exists and the human's 2026-10-18 policy says independence is the fresh
session + isolated checkout, not a different CLI; the independence
exclusion must not remove an adequate option on the configured preferred
CLI (the `prefer` list in model-options.json), and stays only for
non-preferred tools. (2) S-03 residual - the required full suite was never
recorded (the attempt cap hit mid-run). Branch from that preserved commit,
apply the scoped eligibility fix with focused tests, and complete the one
full-suite run. Do not re-implement what T-078 proved pass.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-078-routing-scheduler-integration.md (rejected contract + Result; its artifact is your base)
- .agentflow/tasks/T-086-verify-launch-admission.md (V-05: the Devin-exclusion finding this answers)
- .agentflow/tools/route.py (static_reason, eligibility, prefer/floor resolution)
- .agentflow/docs/model-options.json (prefer/floor config, policy text)
- .agentflow/tests/test_routing_scheduler.py, test_routing_core.py, test_route.py

## Allowed files

- .agentflow/tools/tick.py
- .agentflow/tools/route_report.py
- .agentflow/tools/cli.py
- .agentflow/tools/route.py
- .agentflow/tests/ (any file)
- .agentflow/tasks/_template.md (routing fields only)
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (policy text only; preserve catalog and holds)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- T-040 preserved drafts and other worktrees (read only)
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] K-01: Branch moved onto 0ba5d377f0deeae979588b23d8f29585b3a70cde once; the delta vs that commit is only this fix and `git diff main...HEAD` stays inside this contract's Allowed files.
- [ ] K-02: For a tester task, an adequate option on the configured preferred CLI (model-options.json `prefer`) is not removed by the independence exclusion: a fresh assessment of a tester whose checked task ran on the preferred CLI can select that CLI's adequate option; the exclusion still applies to non-preferred tools and still re-includes the avoided tool when nothing else is eligible; actual holds and adequacy still rule. Prove with focused tests covering a devin-preferred tester-of-devin case and a non-preferred-CLI case.
- [ ] K-03: The required one full-suite run on the branch HEAD is recorded verbatim (the run T-078 could not finish); all scoped Checks pass verbatim; no live TypeSafe calls in tests.
- [ ] K-04: VERSION/AGENTS/CHANGELOG consistent (the 2.15.4 entry may gain one line that the preferred-CLI independence rule landed; no second release); the S-01..S-05 evidence of the inherited artifact is accurately restated where the Result records it; T-040 is not claimed complete; T-036 dependency note per the inherited contract.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for K-03. Scoped Checks above are rerun
at acceptance/integration; do not multiply whole-suite runs without cause.

## Execution bounds

20-minute cap (the full suite takes ~7.5 min - start it early). Reset the
branch onto 0ba5d37, write the failing eligibility test first, then the
smallest change. Result must include explicit `- K-01: pass - <evidence>`
outcome lines for K-01..K-04; put `evidence:` markers at line end followed
only by intended claim paths (`.runtime` evidence basenames must start
`T-091.`); path names inside prose are mentions.

## Result
Outcome: completed
Change: 0bf4ac09fa08ef2c7cd77f6591993460511ebe07 on t-091-tester-independence-preference
Files:
- .agentflow/tools/route.py - route() clears the tester-independence `avoid` when the checked task's Tool is a configured preferred CLI (`prefer` in model-options.json), so an adequate option on that CLI stays eligible; the exclusion still applies to non-preferred tools, the nothing-else-eligible re-include is untouched, and live holds plus adequacy still rule; module docstring restates the rule
- .agentflow/tests/test_routing_core.py - RoutingRecordTests gains write_tester() and three focused tests: a devin-preferred tester-of-devin keeps and selects the adequate devin option, a live devin hold still excludes it into adequateHeld, and a tester of a non-preferred codex task is still kept off codex then re-included when codex is the only option left
- .agentflow/tests/test_approval.py, test_parallel.py, test_quota_groups.py - fixture repairs the inherited artifact owed the full suite (Routing exception header line on the approval fixture; assessment_problems stubs where tick tests drive decide/run), so the suite is green on this base
- .agentflow/docs/ai-handoff-protocol.md - recovery rule 3 allows a same-tool tester when that tool is a configured preferred CLI
- CHANGELOG.md - the 2.15.4 entry gains one line: T-091 landed the same rule at assessment time
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py` -> pass (11 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (25 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass on branch HEAD 0bf4ac0, verbatim tail "Ran 424 tests in 406.321s / OK (skipped=3)", exit 0; evidence: .agentflow/tasks/.runtime/T-091.full-suite.txt
Criteria outcomes:
- K-01: pass - the branch was moved onto 0ba5d377f0deeae979588b23d8f29585b3a70cde once and holds exactly one commit (0bf4ac0, parent 0ba5d37); `git diff main...HEAD` lists only this contract's Allowed files (VERSION, AGENTS.md, CHANGELOG.md, ai-handoff-protocol.md, typesafe.md, _template.md, tick.py, route.py, route_report.py, .agentflow/tests/).
- K-02: pass - route.py:384-386 drops `avoid` only when the checked task's Tool is in cfg["prefer"]; test_tester_of_a_preferred_cli_task_keeps_and_selects_it proves a fresh assessment of a tester whose checked task ran on devin selects the adequate devin option while the Jev pick was codex; test_a_live_hold_still_removes_the_preferred_option_for_a_tester proves an observed hold still excludes it into adequateHeld; test_tester_of_a_nonpreferred_cli_is_still_excluded_then_reincluded proves the exclusion for a non-preferred CLI plus re-inclusion when nothing else is eligible; adequacy still rules (claude-plain stays inadequate). evidence: .agentflow/tools/route.py .agentflow/tests/test_routing_core.py
- K-03: pass - the one full-suite run T-078 could not finish is recorded verbatim: "Ran 424 tests in 406.321s / OK (skipped=3)" on 0bf4ac0; all three scoped Checks above pass verbatim; tests run against the local stand-in server - no live TypeSafe calls. evidence: .agentflow/tasks/.runtime/T-091.full-suite.txt
- K-04: pass - VERSION 2.15.4 = AGENTS.md version block = CHANGELOG 2.15.4 entry, which gained one line on the preferred-CLI independence rule (no second release); the inherited artifact's S-01..S-05 evidence is restated below; T-040 is not claimed complete. evidence: .agentflow/VERSION CHANGELOG.md AGENTS.md
Inherited artifact (0ba5d37) evidence, restated per K-04:
- S-01: pass - tick.py decide() consults route.assessment_problems before reporting launch and use_backup() requires route.backup_ok; proved by test_routing_scheduler.py (11 tests: missing/stale/blocked need, ok launch, human exception, inadequate/held/missing backup) and test_tick.py stubs.
- S-02: pass - route_report.py exposes assessmentStatus/assessmentBand/required/floor/excluded/inadequate/adequateHeld/blocked and admission/human-exception metadata with absent-is-null; _template.md documents the Routing exception field (test_route_report.py).
- S-03: pass - its residual (the never-recorded full suite) is closed here by the K-03 run; the inherited evidence (launch admission T-076/T-086, floor and ordering T-074/T-075, no-downgrade T-087/T-089, group-scoped holds T-082, schemaVersion-1 records T-074, unit-level coverage with no live calls) stands unchanged.
- S-04: pass - 2.15.4 version artifacts and migration notes, unchanged by this task beyond the one CHANGELOG line.
- S-05: pass - its residual (assessment-time removal of the checked task's CLI) is closed here by the K-02 change and tests; the scheduler side (tester on devin launches on devin, adequate devin backup serves it, an observed devin hold still blocks) was already proved by test_routing_scheduler.py.
- T-036 note per the inherited contract: the ledger already records Depends on: T-078; T-036 may proceed only after T-078's independent tester acceptance, and its assessment must be refreshed before launch.
Question or reason: -
Found, not fixed:
- test_tick.py test_heartbeat_is_one_holder_at_a_time once failed with PermissionError (WinError 5) on os.replace of orchestrator.json.tmp - a transient Windows replace race already documented in machine_capacity.py; the identical rerun passed. No product change needed.
Proposed memory updates:
- decisions.md, 2026-10-18: T-091 closed the T-078 residuals on 0bf4ac0 - tester independence no longer removes an adequate option on a configured preferred CLI at assessment time (independence = fresh session + isolated checkout), and the full suite (424 tests) is green. Rejected: widening the exemption beyond `prefer`.
- known-issues.md, 2026-10-18: the T-078 full-suite gap and the S-05 route.py residual are both closed by T-091 @ 0bf4ac0; transient Windows os.replace PermissionError can flake test_tick heartbeat tests - retry, do not chase.
- session-log.md, 2026-10-18: T-091 commit 0bf4ac0 on t-091-tester-independence-preference; focused 52+11+25 green; full suite 424 green in 406s; Result written; awaits tester (Independent check: tester).
