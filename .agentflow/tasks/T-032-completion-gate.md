# T-032: Evidence and completion gate - criterion IDs, artifact-bound evidence, integrated-result checks, common completion command

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-056
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

Attempt state note: attempts 1 and 2 each hit the 2400s wall-clock limit while
building this task - the worktree holds a substantial in-progress draft across
several files (git status). Your job on this attempt: commit a correct
intermediate state EARLY, then continue - do not restart the task by
re-reading everything; write the Result as soon as the artifact and checks are
green. A completed-but-unverified partial cycle is worse than a verified
smaller increment.

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
- .agentflow/tasks/t-*.md (other Task Files)
- .agentflow/tasks/.runtime/
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
Outcome: completed
Change: a4f0642a911befd8769a40fbbe13feeb579a045c on t-032-completion-gate
Files:
- .agentflow/tools/gate.py - stable criterion IDs (X-NN) with preflight refusal for missing or duplicate IDs; per-criterion outcome lines required in the Result (worse than pass only for the Tester); evidence file paths validated against the task scope and existence; verify records also bind base SHAs and per-criterion outcomes; new `done` gate runs the Checks on the artifact and on a detached trial-merge tree of the branch onto the current base, tags base-failing checks as pre-existing, reuses a still-bound PASS and emits structured reasons via --out
- .agentflow/tools/accept.py - integrated-check step between trial merge and merge; durable per-repository progress in tasks/.runtime/T-NNN.accept.json
- .agentflow/tools/ledger.py - the new object fields of a verify record are validated fail-closed; acceptance requires the recorded base to still be current (own-merge exception)
- .agentflow/tools/cli.py - `agentflow done T-NNN` routes to the completion gate
- .agentflow/tasks/_template.md - criteria written as `C-NN:` with the outcome-line contract in a comment
- .agentflow/tests/test_done_gate.py - new: 21 tests covering E-01 through E-05
- .agentflow/tests/test_accept.py, test_approval.py, test_cli.py, test_endcheck.py, test_launcher_lifecycle.py, test_parallel.py, test_run_task.py, test_workspace.py - fixtures carry ID criteria and outcome lines; test_accept mocks the integrated check and gains a failure-ordering test
- .agentflow/docs/ai-handoff-protocol.md - Terms, the preflight list and the Acceptance section document the new contract
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.14.0 with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (9 passed)
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` -> pass (3 passed)
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` -> pass (15 passed)
- `python -m unittest discover -s .agentflow/tests` -> pass (289 passed, 3 skipped)
Criteria:
- E-01: pass - stable IDs and outcome lines are enforced by .agentflow/tools/gate.py at preflight and verify; the form is documented in .agentflow/tasks/_template.md and covered by .agentflow/tests/test_done_gate.py
- E-02: pass - evidence paths are validated for scope and existence in .agentflow/tools/gate.py; the bound record in .agentflow/tools/gate.py and .agentflow/tools/ledger.py ties task, attempt, header hash, artifact SHAs and base SHAs, and moved inputs invalidate it
- E-03: pass - the trial merge uses git merge-tree plus a temporary commit, checked out detached by .agentflow/tools/gate.py, which runs the task Checks on the merged trees; .agentflow/tools/accept.py calls it before merging and persists per-repository progress
- E-04: pass - the done gate lives in .agentflow/tools/gate.py and .agentflow/tools/cli.py as agentflow done; acceptance, the launcher and a platform hook can call it, and it returns structured pass or fail reasons
- E-05: pass - checks failing on the current base are tagged pre-existing and reported separately from introduced failures in .agentflow/tools/gate.py, covered by .agentflow/tests/test_done_gate.py
- E-06: pass - the full suite passes verbatim, the version moved to the value in .agentflow/VERSION with AGENTS.md synced and CHANGELOG.md carrying migration notes
Found, not fixed:
- On Windows, ledger.py _write_atomic's os.replace occasionally loses to a transient file lock (PermissionError WinError 5) in the disposable test repos: two test_done_gate tests flaked once and passed on rerun. A pre-existing platform race, not from this change.
Proposed memory updates:
- decisions.md: 2026-10-17 - T-032 made acceptance artifact-bound and criteria-covered: required criteria carry stable X-NN IDs and the Result maps each to an outcome line with in-scope evidence; the verify record binds task, attempt, requirements hash, artifact SHA(s) and base SHA(s) - moved inputs invalidate; accept.py runs the Checks on the trial-merge result before merging and persists per-repository progress without claiming cross-repository atomicity; gate.py done / agentflow done is the single completion command, reusable while bound and tagging base-failing checks as pre-existing. Rejected: a separate evidence store (the verify record already bound attempt and artifact) and worktree-only acceptance (it missed integrated regressions).
