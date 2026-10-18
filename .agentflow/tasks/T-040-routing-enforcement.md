# T-040: Mandatory assessed adequacy routing - persisted Jev assessment, floor enforcement, launch admission

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-070
Branch: t-040-routing-enforcement
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-040-routing-enforcement
Independent check: tester
Resume: none

## Goal

Implement the human routing requirement (.agentflow/tasks/.runtime/
required-routing-policy-2026-10-17.md): every worker launch needs a persisted,
requirements-bound Jev assessment that admits only a model adequate for the
task, with Devin-preferred but adequacy-first ordering. Reconcile first -
route.py already produces assessments with confidence bands and backup
selection; extend into enforced admission, do not rebuild.

## Read first

- .agentflow/tasks/.runtime/required-routing-policy-2026-10-17.md (authoritative requirements)
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (created 2026-10-17 - the live config)
- .agentflow/docs/ai-handoff-protocol.md (Launching workers, Autonomous orchestration)
- .agentflow/tools/route.py, plan_route.py, run_task.py, tick.py, ledger.py, gate.py, machine_capacity.py, quota_groups.py (lands via T-030), limit_detection.py (lands via T-030)
- .agentflow/tests/test_route.py, test_parallel.py, test_run_task.py, test_tick.py, test_launcher_lifecycle.py

## Allowed files

- .agentflow/tools/route.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/tick.py
- .agentflow/tools/ledger.py
- .agentflow/tools/gate.py
- .agentflow/tools/quota_groups.py
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/route_report.py
- .agentflow/tools/cli.py
- .agentflow/tasks/_template.md (assessment fields only if needed)
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (schema fields only, e.g. quota_group documentation)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md (docs task owns them)
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects, their machine leases and their model-options.json

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] Q-01: Every worker launch (run_task.py paths and tick.py automatic launch) requires a persisted assessment record bound to the task's requirements fingerprint (task id + header/criteria/checks hash): source, timestamp, Jev model/version/request id, confidence band, required capability/effort, project floor, eligible options, selected CLI/model/effort, exclusion/override reasons, availability source and freshness, fallback sequence, blocked reason. Missing, stale (contract changed), failed or low-confidence assessment blocks the launch with a diagnosable reason; an explicit auditable human exception path exists and is recorded as such, never presented as Jev evidence.
- [ ] Q-02: Adequacy floor: swe-2-high is the project floor and default preference; a task assessed to need more rejects swe-2-high even when it is the only free option - the launch blocks/waits with the resource reason. Devin adequate options are searched before other CLIs; CLI preference never compensates for insufficient fit. No universal made-up cross-vendor ranking: adequacy is capability/effort-based with an auditable policy.
- [ ] Q-03: At launch the resolved worker argv is rechecked after all env/CLI overrides: the selected model/effort cannot be silently lowered by AGENTFLOW_<TOOL>_ARGS or wrapper defaults (the existing remove_overridden rule is extended to the recorded assessment, not just the header line). Backups must satisfy the same requirement; a backup weaker than the requirement is ineligible.
- [ ] Q-04: Retry and recovery cannot downgrade: a re-launch, fallback tool switch or resumed attempt re-validates the recorded requirement; quota exhaustion mid-task preserves artifacts and reassesses before retry; reset/cooldown windows are respected instead of polling exhausted models; a held family does not imply the whole tool is held (quota groups from T-030).
- [ ] Q-05: Assessment metadata is persisted in .runtime per task in a documented schemaVersioned JSON (T-NNN.route.json extended or a sibling record), readable by route_report.py and by the planned dashboard data task; no credentials, raw argv, numeric quota balances or unfiltered provider output are ever written.
- [ ] Q-06: Manual (-Manual) execution follows the same admission rule: recorded assessment or the explicit human exception; the exception path is visible in the record.
- [ ] Q-07: Tests cover: missing/stale assessment blocks; swe-2-high admitted for floor-adequate tasks; stronger requirement rejects swe-2-high; adequate stronger Devin preferred over other CLIs; other CLI used only when no adequate Devin option is free; no adequate model -> blocked; env-arg downgrade rejected; low-confidence/failed Jev diagnosed; retry/fallback cannot downgrade; group-scoped quota handling; every worker role covered; changed contract hash invalidates. No live TypeSafe calls in the suite - a local stand-in only; the zero-dependency core boundary holds.
- [ ] Q-08: Documentation synchronized: protocol routing/lifecycle text, typesafe.md, model-options.json schema notes, CHANGELOG entry with migration notes for installed projects, VERSION bump and AGENTS block. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py` - assessment/admission behavior.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - launch admission integration.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - automatic-admission rules.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
