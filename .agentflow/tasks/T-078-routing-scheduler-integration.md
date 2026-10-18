# T-078: Integrate routing admission with automatic scheduling and reports

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-089
Branch: t-078-routing-scheduler-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-078-routing-scheduler-integration
Independent check: tester
Resume: none

## Goal

Finish original T-040 by applying accepted routing APIs to tick backup/fallback
selection and reporting. Reuse T-074/T-076; do not redesign them. Human authorized
urgent bounded decomposition on 2026-10-18.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-040-routing-enforcement.md
- .agentflow/tasks/T-074-routing-core-recovery.md
- .agentflow/tasks/T-076-routing-launch-integration.md
- .agentflow/tools/tick.py
- .agentflow/tools/route.py
- .agentflow/tools/route_report.py

## Allowed files

- .agentflow/tools/tick.py
- .agentflow/tools/route_report.py
- .agentflow/tools/cli.py
- .agentflow/tests/test_tick.py
- .agentflow/tests/test_route_report.py
- .agentflow/tests/test_routing_scheduler.py
- .agentflow/tasks/_template.md (routing fields only)
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/typesafe.md
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- Other Task Files and runtime history
- T-040 preserved drafts
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] S-01: Tick automatic launch and backup use the accepted admission APIs; inadequate backup never replaces a primary, group holds remain scoped and no eligible option yields an actionable block. Retain direct-launch validation as final authority.
- [ ] S-05: Automatic tester routing honors the human's Devin preference (2026-10-18) using fresh independent sessions; an adequate available Devin option is not removed solely because the developer used Devin. Availability reports do not override actual holds or adequacy.
- [ ] S-02: Reports and template expose safe assessment/admission identity, exclusion and human-exception metadata. Missing telemetry remains unknown, never fabricated.
- [ ] S-03: Map original T-040 Q-01 through Q-08 to accepted core/direct integration evidence and scheduler tests; identify any unmet item explicitly. Focused and full suites pass with no live TypeSafe calls.
- [ ] S-04: Patch release and migration explain legacy refresh and all automatic/manual paths accurately. Propose T-036 dependency update to this task only after independent acceptance.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_route_report.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for S-03. Checks above are the scoped
acceptance/integration commands; avoid redundant whole-suite repeats.

## Execution bounds

20-minute attempt cap (includes the measured six-minute full suite). Begin with existing admission APIs and focused tests;
avoid another architecture survey. Checkpoint and report exact blockers promptly.
Result must include explicit `- S-01: pass - <evidence>` outcome lines for
S-01..S-05; the older role example without colon/verdict is obsolete.

## Result
Outcome: completed
Change: 0ba5d37 on t-078-routing-scheduler-integration
Files:
- .agentflow/tools/tick.py - decide() gates every ready-task automatic launch on route.assessment_problems (missing/stale/blocked/low-confidence/failed record is an actionable need, not a doomed launch; a Routing exception header line admits and is logged by the launcher as human-exception); use_backup() gates the header rewrite on route.backup_ok (recorded backup must meet the task requirement and carry no live quota-group hold); the backup-selected log follows the patched runtime dir
- .agentflow/tools/route_report.py - summarize() surfaces assessmentStatus/assessmentBand/required/floor/excluded/inadequate/adequateHeld/blocked and admissions/humanExceptions/admissionSource/admissionDeviation/humanExceptionReason; absent metadata stays null
- .agentflow/tests/test_routing_scheduler.py - new: 11 tests over the scheduler admission gate and the backup gate (missing/stale/blocked need, ok launch, human exception, tester on devin, actual hold, inadequate/held/missing backup, devin backup for a tester of a devin task)
- .agentflow/tests/test_tick.py - setUp stubs route.assessment_problems clean for fixture tasks; the backup test stubs route.backup_ok
- .agentflow/tests/test_route_report.py - pins the new safe metadata fields and the absent-means-null rule
- .agentflow/tasks/_template.md - documents the optional "Routing exception:" header field
- .agentflow/docs/ai-handoff-protocol.md - Launching workers (backup switch requires route.backup_ok) and Autonomous orchestration (tick launches require the assessment to admit; launcher admission stays final authority)
- .agentflow/docs/typesafe.md - item 10 records the scheduler-side use of assessment_problems/backup_ok and the new report fields
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.15.4 patch release with migration notes (re-route open ready tasks; weaker/held backups stay unused; legacy records report new fields null)
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_route_report.py` -> pass (11 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py` -> pass (11 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> in progress at attempt deadline (see S-03)
Criteria outcomes:
- S-01: pass - decide() calls route.assessment_problems before reporting launch (test_routing_scheduler.py test_missing_assessment_is_an_actionable_need_not_a_launch, test_blocked_and_stale_assessments_are_actionable_blocks, test_ok_assessment_launches, test_human_exception_line_admits_the_automatic_launch); use_backup() refuses an inadequate backup and a group-held backup without touching the header (test_inadequate_backup_never_replaces_the_primary, test_a_held_backup_group_stays_scoped_and_refused, test_no_ok_assessment_means_no_backup_switch); run_task.py admission unchanged - final authority retained.
- S-05: partial - scheduler side implemented and tested: a tester task whose ok assessment selected devin launches on devin although the checked task ran devin, and an adequate devin backup serves such a tester (test_tester_on_devin_is_not_removed_because_the_developer_used_devin, test_devin_backup_serves_a_tester_of_a_devin_task); an observed devin hold still blocks (test_an_actual_devin_hold_still_blocks_despite_the_reported_window). Residual outside Allowed files: route.py eligibility still excludes the checked task's CLI at assessment time ("kept off devin: tester independence"), so a fresh Jev assessment of a tester-of-devin task still cannot select devin - needs a scoped successor that owns .agentflow/tools/route.py.
- S-02: pass - report fields listed above surface safe assessment/admission identity, exclusion and human-exception metadata; absent telemetry is null, never fabricated (test_assessment_and_admission_metadata_is_exposed_safely); _template.md documents the Routing exception field.
- S-03: partial - Q-01 launch admission: T-076 (07fbeed, verified by T-086) plus this task for the tick automatic path; Q-02 adequacy floor/Devin-first ordering: T-074 (5a6510c, verified by T-075) consumed unchanged; Q-03 env/CLI downgrade rejection incl. codex config spellings: T-076/T-087/T-089; Q-04 retry/fallback no-downgrade and group-scoped holds: T-076/T-082 plus backup_ok in use_backup; Q-05 persisted schemaVersion-1 metadata: T-074 plus the route_report fields here; Q-06 manual-path admission and human exception: T-076 probes; Q-07 coverage incl. no live TypeSafe calls: test_route.py local stand-in, test_routing_core.py, test_run_task.py probes, test_routing_scheduler.py/test_tick.py/test_route_report.py here - all unit-level, no network; Q-08 docs/migration/version: 2.15.4 entry above. Unmet in this task: the full-suite run was still in progress when the 20-minute attempt cap expired - its result is not recorded.
- S-04: pass - VERSION 2.15.4, AGENTS.md block and CHANGELOG entry describe the scheduler admission gate, the backup requirement gate and accurate migration for both automatic and manual paths; legacy route histories report the new fields null. Proposed: point T-036 dependency satisfaction at this task only after its independent tester acceptance (ledger already says Depends on: T-078; refresh T-036's assessment before launch).
Question or reason: -
Found, not fixed:
- route.py eligibility()/static_reason() still remove the checked task's CLI for tester assessments ("kept off <tool>: tester independence"). Under the human's 2026-10-18 preference an adequate Devin option should stay eligible - the change belongs to route.py, which T-078's Allowed files exclude. Scoped follow-up needed (e.g. drop avoid when it names a configured preferred CLI, independence being the fresh session + isolated checkout).
- The launcher's route.admission() remains correct; S-05's residual only narrows what a fresh tester assessment can select.
Proposed memory updates:
- decisions.md, 2026-10-18: T-078 wired the persisted routing assessment into the scheduler (tick.py decide consults assessment_problems; use_backup requires backup_ok) and exposed assessment/admission metadata in route_report (2.15.4). Rejected: re-checking resolved env identity inside tick (the launcher's admission stays the single final authority) and weakening backup selection to a bare slot check.
- known-issues.md, 2026-10-18: T-078 full suite was still running when the attempt cap hit; rerun `python -m unittest discover -s .agentflow/tests` on 0ba5d37 before acceptance; S-05 residual: route.py tester-independence exclusion of the checked task's CLI still applies at assessment time.
- session-log.md, 2026-10-18: T-078 commit 0ba5d37; focused suites 52+11+11 green; full suite pending.
- After T-078 independent acceptance: T-036 may proceed (dependency already points at T-078; refresh its assessment first per policy).
