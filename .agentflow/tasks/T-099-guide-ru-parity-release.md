# T-099: Russian guide parity and public documentation finalization

Role: developer
Tool: devin
Stage: 5
Depends on: T-098
Branch: t-099-guide-ru-parity-release
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-099-guide-ru-parity-release
Independent check: tester
Resume: none

## Goal

Subtask 3 of re-scoped T-036 (improvement-plan.md section 5): bring
GUIDE.ru.md to section-by-section parity with the post-T-098 GUIDE.md,
preserve the mode/concurrency/commit guarantees across all docs, and finalize
the release metadata for the documentation-alignment train.

## Read first

- .agentflow/docs/improvement-plan.md (section 5)
- GUIDE.md, GUIDE.ru.md, README.md, RELEASE_NOTES.md, .agentflow/README.md
- .agentflow/docs/ai-handoff-protocol.md (Single/Team mode, concurrency and commit rules)
- CHANGELOG.md, .agentflow/VERSION, AGENTS.md

## Allowed files

- GUIDE.ru.md
- GUIDE.md (only edits needed for parity or factual correction)
- README.md
- RELEASE_NOTES.md
- .agentflow/README.md
- .agentflow/docs/release-validation.md (only if parity reveals a drift)
- .agentflow/roles/tool-routing.md (only the stale agy-tester claim below)
- .agentflow/VERSION
- AGENTS.md, CLAUDE.md (AgentFlow version block only)
- CHANGELOG.md
- .agentflow/tests/ (any file - test_layout.py enforces structure and may need updating)

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/commands/
- .claude/commands/
- .agentflow/docs/improvement-plan.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/project-rules.md
- .agentflow/docs/model-options.json
- .agentflow/docs/quota-policy.json
- .agentflow/docs/typesafe.md
- .agentflow/docs/engineering-rules.md
- .agentflow/roles/developer.md
- .agentflow/roles/tester.md
- .agentflow/roles/orchestrator.md
- .agentflow/roles/deployer.md
- .github/
- pyproject.toml, setup.py, MANIFEST.in
- .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] G-01: GUIDE.ru.md stays Russian and carries the same factual content as GUIDE.md (section-by-section parity, not a word-for-word translation); README/GUIDE/RELEASE_NOTES honesty rules hold (no invented results, URLs, metrics).
- [ ] G-02: Explicit Single/Team mode choice, user concurrency restrictions and commit rules are preserved in text; nothing automatically relaxes them.
- [ ] G-03: Release metadata agrees with the merged T-097/T-098 state: .agentflow/VERSION, the AGENTS.md/CLAUDE.md version blocks, and CHANGELOG.md migration notes describe the documentation-alignment train as one coherent release step, saying what an installed project must do.
- [ ] G-04: Full suite passes verbatim. Propose dated decisions.md text in the Result.
- [ ] G-05: Leftover from the T-036 re-scope (reported by the T-098 worker): `.agentflow/roles/tool-routing.md` ~line 46 still claims the Antigravity CLI Tester "stays interactive (-i) and needs a human /exit" - stale vs `run_task.py` tool_argv, which launches agy non-interactively (`-p --output-format stream-json`). Correct that line only; the IDE stays -Manual. GUIDE.ru.md carries the same stale wording - fix under G-01.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - template structure and entry-point integrity.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - install/update integrity of changed files.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
