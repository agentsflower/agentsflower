# T-078: Integrate routing admission with automatic scheduling and reports

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-076
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
