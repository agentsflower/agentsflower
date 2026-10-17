# T-032: Evidence and completion gate - criterion IDs, artifact-bound evidence, integrated-result checks, common completion command

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-030
Branch: t-032-completion-gate
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-032-completion-gate
Independent check: tester
Resume: none

## Goal

Implement improvement-plan.md section 3: acceptance becomes an
artifact-bound, criteria-covered gate instead of "Outcome completed plus
verbatim checks on the task worktree". Reconcile first - task contracts already
carry ID-style criteria and verify records bind attempt/SHA; extend, do not
rebuild.

## Read first

- .agentflow/docs/improvement-plan.md (section 3)
- .agentflow/docs/ai-handoff-protocol.md (Acceptance, Task lifecycle, Release order)
- .agentflow/tools/gate.py, .agentflow/tools/accept.py, .agentflow/tools/ledger.py, .agentflow/tools/run_task.py, .agentflow/tools/cli.py
- .agentflow/tasks/_template.md and a completed contract with ID criteria (.agentflow/tasks/T-010-public-release-docs.md)
- .agentflow/tests/test_endcheck.py, test_parallel.py, test_cli.py, test_install.py

## Allowed files

- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/ledger.py
- .agentflow/tools/run_task.py
- .agentflow/tools/cli.py
- .agentflow/tasks/_template.md
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/docs/project-rules.md is project-owned - never in a task branch
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] E-01: Required acceptance criteria carry stable IDs (the `X-NN:` form already used in recent contracts). Preflight refuses a Task File whose `Acceptance criteria` have no IDs or duplicate IDs; the Result maps every required ID to an outcome line (`- <id>: <verdict> - <evidence>`), and verify fails when a required criterion has no outcome line or a worse-than-pass one it ignores. A completed negative review remains representable.
- [ ] E-02: Evidence declared in criteria/Result as file paths is validated: referenced paths inside the allowed scope must exist; evidence outside the task scope is rejected. Evidence is bound to the task's artifact SHA(s) and the base SHA it was produced against; changed inputs (new attempt, moved SHA, edited header) invalidate the bound evidence record.
- [ ] E-03: Acceptance checks the integrated result, not only the task worktree: before merge, accept.py (or a gate step it calls) runs the task's Checks against the trial-merge result onto the current base (per repository for workspaces), persisting progress so an interrupted multi-repository merge resumes without claiming cross-repository atomicity. A task that conflicts or fails checks on the integrated tree cannot be accepted.
- [ ] E-04: A single completion-check command exists (e.g., `python .agentflow/tools/cli.py done T-NNN` or gate subcommand) that acceptance, the launcher and an optional platform hook can all call to evaluate "done" per the protocol definition: requested changes complete, applicable required checks pass on the current artifact, introduced regressions fixed, required review/integration conditions satisfied. It returns structured pass/fail reasons, not just an exit code.
- [ ] E-05: Pre-existing unrelated defects are reported separately and do not authorize scope expansion - the completion command distinguishes "failed by this change" from "failing before this change" where the check output allows it.
- [ ] E-06: Full suite passes verbatim; increment VERSION, sync AGENTS block and CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - baseline/integrity regressions.
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` - preflight criteria-ID enforcement.
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` - completion command surface.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
