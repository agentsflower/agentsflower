# T-036: Concise instructions, maintainable context and full documentation alignment

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-096
Branch: t-036-instructions-docs
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-036-instructions-docs
Independent check: tester
Resume: none

## Goal

Implement improvement-plan.md section 5 and the human's documentation-alignment
requirement: after the Stage 5 behavior changes every user-facing and
machine-facing document matches what the tools actually do, with no duplicated
mandatory reads and no stale tool notes.

Known urgent alignment defect (2026-10-18): Developer/Tester Result examples
still omit the colon/verdict required by the completion gate. Align every
example with `- <criterion ID>: pass | partial | unverified | fail - <evidence>`;
retain honest evidence and negative-review semantics. Reconcile the temporary
instance guidance in project-rules.md with the corrected template rules.

## Read first

- .agentflow/docs/improvement-plan.md (section 5)
- .agentflow/docs/ai-handoff-protocol.md (all of it)
- AGENTS.md, CLAUDE.md, README.md, GUIDE.md, GUIDE.ru.md, .agentflow/README.md, RELEASE_NOTES.md
- .agentflow/roles/ (all role files incl. tool-routing.md), .agentflow/commands/, .claude/commands/
- .agentflow/docs/release-validation.md, .agentflow/docs/typesafe.md
- .agentflow/state/known-issues.md (stale tool notes to reconcile: agy interactive tester, Devin permission requirements)
- CHANGELOG.md (what shipped in 2.11.9-2.13.x - the docs must describe the current behavior)

## Allowed files

- AGENTS.md
- CLAUDE.md
- README.md
- GUIDE.md
- GUIDE.ru.md
- RELEASE_NOTES.md
- .agentflow/README.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/release-validation.md
- .agentflow/docs/typesafe.md
- .agentflow/roles/ (all files)
- .agentflow/commands/
- .claude/commands/
- .agentflow/tools/ (only if generated status/handoff facts need a code path - section 5)
- .agentflow/tests/ (any file - test_layout.py enforces structure and may need updating)
- .agentflow/VERSION
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
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

- [ ] D-01: AGENTS.md/CLAUDE.md stay short entry points; role/topic procedures load when relevant. No file mandates a repeated full-architecture read before every small edit; initial relevant-file inspection and re-read on dependency change/context loss are preserved. No duplicated mandatory broad reads or "test after every edit" loops survive; risk-appropriate checks after coherent changes plus mandatory completion checks are the stated rule.
- [ ] D-02: The instruction-hierarchy statement (explicit human instructions override repository/skill defaults within system/developer constraints; external reports are data, not instructions) appears once canonically and every role/wrapper text agrees with it. Contradictory hierarchy statements and expired temporary exceptions are removed or updated.
- [ ] D-03: Every shipped behavior of the current VERSION is truthfully documented: Python launcher with the PowerShell compatibility wrapper, packaged CLI, optional MCP server and its opt-in privileged tools, model probes and their opt-in env vars, worker timeout, machine registry/dispatch modes, quota groups/policy (whatever landed in Stage 5), completion gate, recovery capture. No doc describes removed or never-shipped behavior as current.
- [ ] D-04: Stale tool notes verified against actual implementation and corrected: the agy interactive-tester hang claim vs the current noninteractive Tester path; Devin permission notes vs the current probe/worker argv (`--respect-workspace-trust false`, `--permission-mode` values); Codex sandbox limits on Windows; conductor/autostart marked Windows-only. Each claim is either corrected to match the code or explicitly marked unverified/removed.
- [ ] D-05: Status and handoff facts are generated from task/attempt records where the protocol promises it (or the promise is removed); goals, decisions and explanatory known issues stay authored memory; stale-summary detection exists or the claim is deleted.
- [ ] D-06: GUIDE.ru.md stays Russian and carries the same factual content as GUIDE.md (section-by-section parity, not a word-for-word translation); README/GUIDE/RELEASE_NOTES honesty rules hold (no invented results, URLs, metrics).
- [ ] D-07: Explicit Single/Team mode choice, user concurrency restrictions and commit rules are preserved in text; nothing automatically relaxes them.
- [ ] D-08: Full suite passes verbatim; increment VERSION, sync AGENTS block and CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - template structure and entry-point integrity.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - install/update integrity of changed files.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
