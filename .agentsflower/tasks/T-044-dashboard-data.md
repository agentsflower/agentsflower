# T-044: Roadmap data layer - plan parser, stage records, payload schema, diagnostics

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-038
Branch: t-044-dashboard-data
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-044-dashboard-data
Independent check: tester
Resume: 7279e3f283ddc42462dfe4b7ff27300a8f3ae8df

## Goal

Implement the data/parser layer of the roadmap dashboard per PLAN.md sections
1-3: a backward-compatible project-plan.md parser, stage records joined with
ledger/contract/runtime evidence, the shared schemaVersioned payload consumed
by all dashboard pages, and honest diagnostics. Launch additionally requires
the human's mockup selection (recorded in decisions.md) - the payload schema is
fixed by PLAN.md plus the selected mockup's README; do not start before both
exist.

## Read first

- .agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md (sections 1-3, acceptance matrix)
- .agentflow/dashboard/UI-RULES.md (A2 data honesty, B1/B2 architecture and extraction)
- .agentflow/dashboard/build.py, README.md, snapshot.py
- .agentflow/dashboard/mockups/ (selected variant README + agreed payload fields)
- .agentflow/tools/route_report.py, .agentflow/tools/ledger.py, .agentflow/tools/gate.py (existing readers)
- .agentflow/docs/project-plan.md, .agentflow/state/tasks.md, representative .agentflow/tasks/T-*.md
- .agentflow/tests/test_dashboard.py, test_layout.py

## Allowed files

- .agentflow/dashboard/build.py
- .agentflow/dashboard/README.md (data contract only)
- .agentflow/tests/test_dashboard*.py (new test module allowed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/dashboard/templates, common.*, filterbar.* (the UI task owns them; coordinate schema only via the README data contract)
- .agentflow/state/, .agentflow/tasks/ (other Task Files), .agentflow/docs/project-plan.md
- .agentflow/tools/ (reuse readers; routing-assessment schema lands via T-040)
- .github/, README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in
- other projects and their machine leases

## Setup

- python .agentflow/dashboard/snapshot.py save "pre-roadmap-data" (record output in Result)

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] P-01: The parser reads the current `### Stage N. Title` format with multiline `Status:`/`Exit criteria:` blocks, preserving raw text and source order (Stage 6 may precede Stage 1), honoring Markdown heading boundaries and fenced code blocks. Zero required project-plan migration; optional criterion-ID/evidence/recurring metadata syntax is specified in dashboard/README.md before use.
- [ ] P-02: Stage records carry: ID, source ordinal, title, raw + normalized declared status, source location, exact exit-criteria text, optional authored criterion IDs/evidence links, optional recurring kind/cycle refs, linked task IDs, task counters, coverage summary, diagnostics. Task data stays under existing fields; roadmap fields are additive under a declared schemaVersion.
- [ ] P-03: Joined facts stay independent: declared status vs local execution counts (accepted/active/review/blocked/ready/rejected/cancelled with explicit denominator) vs criterion evidence (pass/fail/unknown/stale with provenance). No zero-task stage shows 0% or 100%; no accepted-count stage-completion verdict; a completed negative Tester review displays as a negative verdict; stale Verifies SHA labels stale.
- [ ] P-04: Diagnostics cover missing/unreadable/malformed plan, unknown statuses, duplicate IDs, ledger stages absent from plan, unassigned tasks (kept visible in an Unmapped group), missing runtime/git as separately labeled gaps. Duplicate IDs never resolve silently; bad stage data never hides readable task data.
- [ ] P-05: Evidence links validate existence under the project root; traversal/symlink escapes rejected; external URLs are references, never fetched at build; all project strings escaped; javascript:/data: URL schemes rejected.
- [ ] P-06: Attempt/assessment records expose only the documented allowlist (task/attempt id, tool, requested model/effort, recorded effective identity, timestamps, exit status, timeout/limit observation, safe evidence refs) sourced from runtime and routing records - including the T-040 assessment schema when present, degrading to unknown when absent. Never raw env/argv/logs/credentials/quota balances.
- [ ] P-07: Demo fixture (--demo) covers: six-stage plan with zero-task stages, historical closure without tasks, recurring stage with one recorded cycle, accepted tasks plus failed/pending external evidence, active planned stage, duplicate-ID diagnostics. Demo reads no canonical memory and writes only out/.
- [ ] P-08: All existing pages still build and show the same task data as before (regression fixtures compare payload task fields against the pre-change build on the same inputs).
- [ ] P-09: Full suite passes verbatim; increment VERSION, sync AGENTS block, CHANGELOG with migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` - payload/parser/semantics matrix.
- `python .agentflow/dashboard/build.py` and `python .agentflow/dashboard/build.py --demo` - real and demo pages build.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 1d08950 on t-044-dashboard-data
Setup: `python .agentflow/dashboard/snapshot.py save "pre-roadmap-data"` -> `saved: v1-20261021-1640-pre-roadmap-data`

Files:
- .agentflow/dashboard/build.py - plan parser (source order, heading/fence boundaries), stage records joined with ledger/runtime/git evidence, evidence-ref validation, attempt/routing/verify allowlists, diagnostics (sources/warnings/gaps/unmappedTaskIds/freshnessNote/provenance), schemaVersion 1, expanded --demo fixture
- .agentflow/dashboard/README.md - "Roadmap data" contract: every payload field, the three independent stage facts, and the optional authored project-plan syntax
- .agentflow/tests/test_dashboard.py - 21 new tests: PlanParserTests, StageJoinTests, RuntimeAllowlistTests, RoadmapPayloadTests, TaskFieldRegressionTests (golden task fields vs the pre-change build)
- .agentflow/VERSION - 2.15.7 -> 2.15.8
- AGENTS.md - AgentFlow block version line synced to 2.15.8
- CHANGELOG.md - 2.15.8 entry with migration notes

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (30 passed / 0 failed)
- `python .agentflow/dashboard/build.py` -> pass (89 tasks, 6 stages, 91 dependencies, 20 successors, 206 commits -> out/)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out/ [DEMO DATA])
- `python -m unittest discover -s .agentflow/tests` -> pass (453 passed / 0 failed, 4 skipped). First run failed once in test_worker_watchdog (PermissionError WinError 5 on os.replace inside ledger.py _write_atomic, temp fixture) - the documented transient flake (known-issues 2026-10-18); isolated rerun of that file 14/14 green, verbatim full rerun green.

Criteria:
- P-01: pass - parse_plan in .agentflow/dashboard/build.py reads `### Stage N` headings in source order (real payload: Stage 6 record precedes Stage 1), keeps raw Status/Exit criteria text verbatim, treats fenced code and level 1-3 heading boundaries as opaque; zero plan migration needed; optional criterion/evidence/recurring syntax specified in .agentflow/dashboard/README.md before use (PlanParserTests)
- P-02: pass - stages[] records carry id, ordinal, title, declaredRaw/declared/declaredKey, source/sourceRef/sourceHref/line, exitCriteria verbatim, optional criteria[].evidence, recurring, historicalRefs, taskIds, counts{...other{},total}, coverage, per-stage diagnostics; all additive under schemaVersion:1, task fields unchanged
- P-03: pass - declared status, ledger counts (accepted/active/review/blocked/ready/rejected/cancelled + total denominator, no percentage) and criterion evidence stay independent payload fields; zero-task stages report total:0 not 0%/100%; verdict/status/result remain three separate fields; stale Verifies SHA -> stale:true + warning (StageJoinTests)
- P-04: pass - diagnostics.sources (read/missing/unreadable/absent with fingerprint), warnings (duplicate stage ids never resolved - both flagged, tasks unmapped; declared-vs-ledger mismatches; stale links; ledger stages absent from plan), gaps (missing plan, absent runtime, unstructured criteria, no git), unmappedTaskIds keeps unassigned tasks visible; task data built before the plan join so bad stage data cannot hide it
- P-05: pass - check_ref resolves file refs under ROOT (traversal, absolute and symlink escapes rejected, missing targets flagged refExists:false), only http/https URLs pass as external references never fetched, javascript:/data: rejected; payload embedded via JSON with the pre-existing `</` escape (.agentflow/dashboard/build.py StageJoinTests.test_bad_refs_rejected_and_missing_marked)
- P-06: pass - tasks[].attempts/routing/verifications filtered through ATTEMPT_KEEP/VERIFY_KEEP/CHECK_KEEP/ROUTE_*_KEEP allowlists incl. nested maps; no argv/env/pid/paths/quota; malformed or absent records degrade to null + diagnostic (RuntimeAllowlistTests)
- P-07: pass - DEMO_PLAN in build.py: six stages incl. zero-task stages (1, 2, 4), historical closures with References and no tasks, recurring stage 4 with cycle-2026-10-15, stage 6 authored evidence pass/fail/pending (one external URL, one file ref), active stage 5 declared planned vs 5 ledger tasks, stage 3 declared twice -> duplicate diagnostic, T-108 -> Unmapped; embedded attempt/routing/verify records; demo reads no canonical memory and writes only out/ (RoadmapPayloadTests, test_main_demo_writes_only_out)
- P-08: pass - TaskFieldRegressionTests pin GOLDEN_TASKS and GOLDEN_DEMO task fields/edges/commits/pings/metrics produced by the pre-roadmap build on identical inputs; new fields are setdefault-additive only
- P-09: pass - full suite verbatim OK (453, 4 skipped); VERSION 2.15.8, AGENTS block synced, CHANGELOG entry with migration notes; decisions.md text proposed below

Found, not fixed:
- ledger.py _write_atomic hit the known transient WinError 5 on os.replace once during the first full-suite run (test_worker_watchdog fixture; green standalone and on verbatim rerun) - recorded in known-issues since 2026-10-18; hardening (retry-with-backoff) belongs to the separately scoped Windows reliability task named there, not to this dashboard task.

Proposed memory updates:
- decisions.md: `2026-10-21 - T-044 (2.15.8): the roadmap dashboard data layer parses docs/project-plan.md into stage records (source order, fenced-code/heading boundaries, raw text preserved) and joins them with ledger, Task File and .runtime evidence into one schemaVersion:1 payload for both pages. Declared status, execution counts and criterion evidence stay three independent facts; no stage-completion percentage exists. Optional authored syntax (criterion ids, evidence key=value lines, Recurring/References blocks) is documented in dashboard/README.md - plain Status:/Exit criteria: plans need no migration. Pages render unchanged; the roadmap UI lands in a separate task.`
- known-issues.md: `2026-10-21 - the WinError-5 _write_atomic flake surfaced once more in test_worker_watchdog during the T-044 full suite; verbatim rerun green. Recurrence confirms the 2026-10-18 note: scope a bounded retry-hardening task rather than treating it as resolved.`
