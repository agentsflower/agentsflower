# T-038: Evaluation scenarios, open-task migration safety and Stage 5 release metadata

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-099
Branch: t-038-evaluation-rollout
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-038-evaluation-rollout
Independent check: tester
Resume: a7142bf93038b23ca94490b8211f241953ee5a30

## Goal

Implement improvement-plan.md section 6: a reproducible scenario set that
exercises the new lifecycle/recovery/evidence machinery, proof that migrations
preserve open tasks, and the consolidated release record for the Stage 5 work.
This is the last Stage 5 implementation task.

## Read first

- .agentflow/docs/improvement-plan.md (section 6, exit criteria of all sections)
- .agentflow/docs/ai-handoff-protocol.md (Installing or updating AgentFlow)
- .agentflow/docs/release-validation.md
- .agentflow/tools/install.py, .agentflow/tools/ledger.py, .agentflow/tools/gate.py
- .agentflow/tests/test_install.py, test_launcher_lifecycle.py, check_package.py
- CHANGELOG.md (the Stage 5 entries this release consolidates)

## Allowed files

- .agentflow/tests/ (any file, including a new scenarios module)
- .agentflow/tools/ (only if a scenario needs a small test hook that is genuinely missing)
- .agentflow/docs/release-validation.md
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- .agentflow/roles/, .agentflow/commands/, .claude/commands/
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects and their machine leases (repository-only scope since 2026-10-17: no external rollout exists; all installer/migration validation happens in disposable AgentFlow fixtures)

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Reproducible scenario fixtures cover the plan's named cases with disposable repositories only: a bug-fix task, a contract-change task, a quota/limit recovery (simulated), and an interrupted-merge recovery. Simulated-process tests are labeled as such in their names/docstrings; anything that needs a real platform is skipped with a stated reason, never faked.
- [ ] V-02: A migration test proves `install.py --update` onto a project with open tasks preserves ledger statuses, open Task Files, project-owned docs and settings, and applies the template-side migration notes recorded in the Stage 5 CHANGELOG entries.
- [ ] V-03: release-validation.md reflects the Stage 5 reality: what is locally verified, what needs remote CI, what is simulation-only. The prior remote-CI failure (run 39026298541: windows-latest and macos-latest test jobs fail while ubuntu passes) is recorded as a known evidence gap, not silently dropped.
- [ ] V-04: CHANGELOG consolidates the Stage 5 releases with honest migration notes for installed projects; VERSION is the final Stage 5 version; AGENTS.md block matches. The release claims no external rollout: repository-only scope since 2026-10-17 means none exists, and unmet external criteria are recorded as out of scope, never fabricated as done.
- [ ] V-05: Full suite passes verbatim plus the new scenario tests. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite including new scenarios.
- `python .agentflow/tests/check_package.py` - packaged-template integrity after all Stage 5 changes.

## Result
Outcome: completed
Change: d4c6e8d on t-038-evaluation-rollout
Files:
- .agentflow/tests/test_scenarios.py - new: disposable-repo fixture driving the real run_task.py/gate.py/accept.py/tick.py/ledger.py; four simulated cases (bug-fix, contract-change with moved-artifact/moved-base re-verify, quota-limit recovery, interrupted-merge resume), an opt-in real-platform variant, an install.py --update open-task migration proof, and a Stage 5 CHANGELOG migration-note check
- .agentflow/docs/release-validation.md - new "Stage 5 evaluation evidence" section: locally verified vs simulation-only vs still-needs-remote-CI; run 39026298541 windows/macos failure kept as an open gap
- .agentflow/VERSION - 2.15.6 -> 2.15.7
- AGENTS.md - AgentFlow block version line 2.15.6 -> 2.15.7
- CHANGELOG.md - 2.15.7 consolidation entry over the Stage 5 releases with migration notes and scope honesty
Checks:
- `python -m unittest discover -s .agentflow/tests` -> pass (432 passed / 0 failed, 4 skipped: platform and real-platform opt-ins)
- `python .agentflow/tests/check_package.py` -> pass (all checks passed)
Criteria:
- V-01: pass - evidence: .agentflow/tests/test_scenarios.py; all four named cases run in disposable git repositories only; simulated workers carry `_simulated` in test names and docstrings; the real-platform variant is skipped unless AGENTFLOW_REAL_PLATFORM=1 (1 of the 4 suite skips), never faked
- V-02: pass - evidence: .agentflow/tests/test_scenarios.py (OpenTaskMigrationTests): --update preserves ledger statuses, open Task Files, project-owned docs and settings and runbook byte-for-byte, delivers current template files, and the preserved task still reads under the new ledger and gate tools; test_stage5_changelog_entries_carry_migration_notes checks every entry >= 2.12.1 records a migration note
- V-03: pass - evidence: .agentflow/docs/release-validation.md lines 47-73; run 39026298541 recorded as an open evidence gap
- V-04: pass - evidence: CHANGELOG.md (2.15.7 entry), .agentflow/VERSION, AGENTS.md; no external rollout claimed, unmet external criteria recorded as out of scope
- V-05: pass - full suite green verbatim including the new module; dated decisions.md text proposed below
Found, not fixed:
- none new; the remote-CI windows/macos gap and the unrelated known-issues entries stand as recorded
Proposed memory updates:
- decisions.md: `- 2026-10-21 - T-038 closed Stage 5 at 2.15.7: a reproducible scenario suite (test_scenarios.py) covers the plan's named lifecycle/recovery cases in disposable repositories with simulated workers only, and install.py --update is proven to preserve open tasks and project-owned files. Rejected: claiming any external rollout or remote-CI parity - the project is repository-only since 2026-10-17 and the run-39026298541 windows/macos failure remains an open evidence gap.`
- known-issues.md: the run-39026298541 entry remains accurate; nothing new to add
