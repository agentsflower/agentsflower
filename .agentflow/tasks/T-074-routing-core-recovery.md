# T-074: Recover T-040 assessment and admission core

Role: developer
Tool: devin
Model: swe-2-max
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
- `python -m unittest discover -s .agentflow/tests`

## Execution bounds

15-minute attempt cap. Begin with the preserved patch and focused checks, not
another architecture survey. Checkpoint a concrete tested delta; if a check
blocks you, report its exact failure promptly. Do not repeat full suites without
a changed input or a diagnosed failure.

## Result
