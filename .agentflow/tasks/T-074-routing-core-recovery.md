# T-074: Recover T-040 assessment and admission core

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-080
Branch: t-074-routing-core-recovery
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-074-routing-core-recovery
Independent check: tester
Resume: none

## Goal

Finish the reusable routing assessment/admission API from the preserved T-040
draft, with focused tests. This is the first bounded delivery of T-040; launch
integration is a separate dependent task T-076. Do not reimplement the draft.
Human authorized urgent decomposition and forward progress on 2026-10-18.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-040-routing-enforcement.md (original policy and full scope)
- E:\Projects\AgentFlow\code\.agentflow\tasks\.runtime\T-040-preserved-draft.patch
- .agentflow/tools/route.py
- .agentflow/tools/gate.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/quota_groups.py
- .agentflow/tests/test_route.py

## Allowed files

- .agentflow/tools/route.py
- .agentflow/tools/gate.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/quota_groups.py
- .agentflow/tests/test_route.py
- .agentflow/tests/test_routing_core.py
- .agentflow/docs/model-options.json (schema only; no account/quota changes)
- .agentflow/docs/typesafe.md
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/tools/run_task.py, tick.py, conductor.ps1
- .agentflow/state/
- Other Task Files and runtime history
- T-040 worktree (read only; preserve original drafts)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Apply the preserved patch to this new checkout once (git apply --check first); resolve only genuine base changes. Keep original T-040 drafts unchanged. Record inherited files and actual implemented delta.
- [ ] R-02: A requirements-bound persisted schema represents successful, low-confidence, failed and unavailable assessments explicitly. Selection respects task capability, effort and project floor before availability; adequate Devin options precede other CLIs. Missing/stale/low-confidence requirements are diagnosable blocks.
- [ ] R-03: Export tested assessment/admission APIs for T-076 to call after effective argv resolution. An explicit human routing exception is distinguishable from Jev evidence; backups/retries cannot lower requirements or bypass quota groups.
- [ ] R-04: Repair the known draft regressions: route log destination follows the configured FLOW_ROOT, and inadequate Claude backup is rejected rather than preserving an obsolete test expectation. No network calls in unit tests.
- [ ] R-05: Focused and full suites pass, patch release and migration describe API-only delivery (launch enforcement is still pending T-076). Do not claim T-040 complete yet.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for R-05. Scoped Checks above are rerun
at acceptance/integration; do not multiply whole-suite runs without cause.

## Execution bounds

20-minute attempt cap (includes the measured six-minute full suite). Begin with the preserved patch and focused checks, not
another architecture survey. Checkpoint a concrete tested delta; if a check
blocks you, report its exact failure promptly. Do not repeat full suites without
a changed input or a diagnosed failure.
Result must include explicit `- R-01: pass - <evidence>` outcome lines for
R-01..R-05; the older role example without colon/verdict is obsolete.

## Result
Outcome: completed
Change: 5a6510c on t-074-routing-core-recovery
Files:
- .agentflow/tools/route.py - persisted schemaVersion-1 assessment events (ok/blocked/low-confidence/failed) bound to requirementsHash; requirement-first selection (_required floor lift, adequate_reason, admission_order, resolve_requirement); launch-side API history/latest_assessment/assessment_problems/admission/log_admission/backup_ok/env_selected/identity_problems; log dir resolved from FLOW_ROOT per call (_rt_dir); selectionReason distinguishes inadequate vs held vs deprioritized
- .agentflow/tools/gate.py - ROUTING_FIELDS, requirements_hash(), parse() exposes requirementsHash + routingException
- .agentflow/tools/quota_groups.py - option_for() (tool+model -> option); group_for() kept
- .agentflow/tools/plan_route.py - recommend() moved onto eligibility/adequate_reason/admission_order/resolve_requirement
- .agentflow/tests/test_route.py - backup expectation now the adequate devin-max (inadequate claude rejected); independence test pinned against host CLI/registry
- .agentflow/tests/test_routing_core.py - new: 19 focused tests for the record schema, ordering, blocks, resolved-identity admission, human exception, backup gate
- .agentflow/docs/model-options.json - schema keys only: "floor": {"option": "devin-swe-2", "effort": "high"}, "prefer": ["devin"]
- .agentflow/docs/typesafe.md - tier/quota_group fields; requirement-first ordering; assessment record + admission API
- .agentflow/VERSION, AGENTS.md (version block), CHANGELOG.md - 2.15.2 patch release + migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (19 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (391 passed / 0 failed / 3 skipped) - required pre-commit run after the coherent change
- R-01: pass - `git apply --check` clean, then applied the preserved patch once with no base conflicts; T-040 worktree untouched. Inherited files: route.py, gate.py, plan_route.py, quota_groups.py (patch stat +515/-153). Implemented delta beyond the draft: _rt_dir() FLOW_ROOT fix, accurate selectionReason + print, test_route.py expectation fixes, new test_routing_core.py, floor/prefer config keys, typesafe.md sync, 2.15.2 metadata.
- R-02: pass - four statuses persisted explicitly bound to requirementsHash (test_ok_assessment_persists_the_binding_schema, test_nothing_adequate_is_a_blocked_record_not_a_pick, test_low_confidence_and_failed_are_persisted_not_silent); adequacy (effort ceiling/complexity cap incl. declared tier) filters before ordering, floor then prefer then Jev rank (test_adequacy_is_capability_and_effort_based, test_admission_order_floor_then_preferred_then_rest, test_floor_beats_a_higher_ranked_other_cli); missing/stale/low-confidence/failed are diagnosable (test_missing_stale_failed_and_low_confidence_are_diagnosable_blocks, test_stale_contract_makes_the_record_refuse_admission).
- R-03: pass - assessment_problems/admission/backup_ok/log_admission/history/latest_assessment exported for T-076 after effective argv resolution; admission() re-checks the resolved model/effort after AGENTFLOW_<TOOL>_ARGS (test_admission_checks_the_resolved_identity_after_env, test_header_or_env_downgrade_is_refused, test_env_selected_parses_documented_flag_forms); Routing exception is recorded as a human-exception event, never Jev evidence (test_human_exception_is_distinguishable_not_jev_evidence); backups/retries must meet the same requirement (test_backup_must_meet_the_same_requirement) and group holds stay honored (test_a_held_adequate_option_is_diagnosed_not_used).
- R-04: pass - _rt_dir() resolves FLOW_ROOT per call, proven by test_log_and_history_follow_the_configured_flow_root plus the unchanged atomic-log test in test_route.py; the obsolete below-requirement Claude backup expectation is replaced by the adequate devin-max assertion; no network in unit tests (local stand-in/patched env only).
- R-05: pass - focused and full suites green as recorded above; VERSION 2.15.2, AGENTS.md block and CHANGELOG entry state API-only delivery with launch enforcement pending T-076; T-040 is not claimed complete.
Question or reason: -
Found, not fixed:
- test_plan_route.py (not in Allowed files) now depends on the real machine registry through eligibility->limit_until; green today because no codex/devin/claude hold is recorded, but a future tool-wide hold could make it environment-dependent.
Proposed memory updates:
- decisions.md, 2026-10-18: T-074 delivered the T-040 routing core as API-only release 2.15.2 - persisted schemaVersion-1 assessments bound to requirementsHash (statuses ok/blocked/low-confidence/failed), requirement-first selection with floor=devin-swe-2@high and prefer=[devin] now configured in model-options.json, and the launch-side API (assessment_problems/admission/backup_ok/log_admission) for T-076 to wire into run_task.py/tick.py. Rejected: gating launches inside this task (deferred by the approved decomposition) and letting CLI preference rank inadequate options (preference applies only within adequate candidates).
- session-log.md, 2026-10-18: T-074 done at 5a6510c; focused suites 12+19 green, full suite 391 green; next step is T-076 launch enforcement.
