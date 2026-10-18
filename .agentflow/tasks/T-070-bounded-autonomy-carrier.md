# T-070: Bounded autonomy carrier - T-034 artifact under corrected evidence gate

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-068
Branch: t-070-bounded-autonomy-carrier
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-070-bounded-autonomy-carrier
Independent check: tester
Resume: none

## Goal

Successor of rejected T-034: its artifact
(ccd74ba1fd0b046a952f4a42fec8ade70b1cb7d1, the complete B-01..B-08 bounded
autonomy feature set, 346 tests green in its own run) is fully implemented but
was rejected because the then-current evidence gate flagged path-like prose in
its Result as undeclared evidence - a machinery defect now fixed on main by
T-068 (2.14.1). The prepared worktree sits on the preserved commit ccd74ba -
keep that base, merge current main (2.14.1 evidence fix + everything up to it),
confirm every T-034 criterion is green under the corrected gate, consolidate
release metadata, write the Result. Reconcile - do not re-implement verified work.

## Read first

- .agentflow/tasks/T-034-bounded-autonomy.md (rejected contract + Result - the artifact you inherit)
- .agentflow/tasks/T-068-evidence-scope-fix.md + T-069-verify-evidence-scope.md (the gate fix now on main)
- .agentflow/tools/run_task.py, tick.py, gate.py, plan_route.py, hooks.py, cli.py on the branch

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/tick.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/route.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/route_report.py
- .agentflow/tools/gate.py
- .agentflow/tools/cli.py
- .agentflow/tools/hooks.py
- .agentflow/tools/install.py (only if the adapter file must ship to installed projects)
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/docs/model-options.json (inherited T-034 base carries it)
- .agentflow/docs/quota-policy.json (schema the policy mechanism documents - may be added if the artifact needs it)
- .agentflow/docs/quota-samples.json (same)
- .agentflow/docs/release-validation.md
- .agentflow/docs/typesafe.md
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/t-*.md (other Task Files)
- .agentflow/tasks/.runtime/
- .agentflow/docs/project-rules.md
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- .agentflow/roles/, .agentflow/commands/, .claude/commands/
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] H-01: Every T-034 criterion (B-01..B-08) holds on this branch: recorded model identity fields, declared quota policy, launch budgets (attempts/duration/identical failures/tool switches), nested-launch delegate rule, Codex Stop-hook adapter, checksHash-bound verify reuse, plan_route kind - all present and green.
- [ ] H-02: The branch merges cleanly with current main (which carries 2.14.1's evidence fix); the Result's prose tokens no longer trip the evidence gate - verify the fixed gate accepts the inherited Result text.
- [ ] H-03: All T-050/T-056/T-064-verified behaviors stay green (fail-closed readers, bound acceptance, locked --stop, group scoping, classification, recovery, criterion IDs, integrated checks, agentflow done).
- [ ] H-04: Full suite passes verbatim; VERSION/AGENTS/CHANGELOG consistent (the artifact claims 2.15.0 - keep it if it remains the highest version after merging main); propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - identity and budget regressions.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - quota policy regressions.
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - check-reuse binding.
- `python -m unittest discover -s .agentflow/tests -p test_hooks.py` - hook adapter regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
