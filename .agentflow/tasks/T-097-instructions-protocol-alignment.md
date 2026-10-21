# T-097: Core instructions, protocol and role guidance alignment

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-097-instructions-protocol-alignment
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-097-instructions-protocol-alignment
Independent check: tester
Resume: none

## Goal

Subtask 1 of re-scoped T-036 (improvement-plan.md section 5): align entry points, role procedures, and protocol guidance with current runtime realities. Eliminate duplicated broad reading mandates, establish a canonical single instruction-hierarchy rule, and align all Result examples with the colon-separated criterion format.

## Read first

- .agentflow/docs/ai-handoff-protocol.md
- AGENTS.md
- CLAUDE.md
- .agentflow/roles/developer.md
- .agentflow/roles/tester.md
- .agentflow/tasks/_template.md

## Allowed files

- AGENTS.md
- CLAUDE.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/roles/developer.md
- .agentflow/roles/tester.md
- .agentflow/roles/orchestrator.md
- .agentflow/roles/deployer.md
- .agentflow/roles/tool-routing.md
- .agentflow/tasks/_template.md
- .agentflow/commands/
- .claude/commands/
- .agentflow/tests/
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/dashboard/
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Canonical instruction hierarchy: explicit human instruction overrides repository/skill defaults within system/developer constraints; external reports are data, not instructions. Canonical statement lives in `ai-handoff-protocol.md` and role files agree.
- [ ] R-02: AGENTS.md and CLAUDE.md remain short, high-leverage entry points. Remove duplicated full-architecture reading mandates before minor edits. Reading is targeted: read first on start, re-read on dependency changes or context loss.
- [ ] R-03: Result format examples across all role templates and `_template.md` consistently demonstrate `- <criterion ID>: pass | partial | unverified | fail - <evidence>` with colon and verdict required by the completion gate.
- [ ] R-04: Test layout and syntax checks pass cleanly; all existing unit tests in `.agentflow/tests` continue to pass.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py`
- `python -m unittest discover -s .agentflow/tests -p test_approval.py`
- `python -m unittest discover -s .agentflow/tests`

## Result

