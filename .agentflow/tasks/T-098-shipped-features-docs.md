# T-098: Shipped features documentation and tool notes alignment

Role: developer
Tool: devin
Stage: 5
Depends on: T-097
Branch: t-098-shipped-features-docs
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-098-shipped-features-docs
Independent check: tester
Resume: none

## Goal

Subtask 2 of re-scoped T-036 (improvement-plan.md section 5): align the
user-facing feature documentation with what the current VERSION actually
ships, and correct stale tool notes against the implementation. Core
instructions, protocol and role guidance are T-097's scope; the Russian guide
and release metadata finalization are T-099's scope.

## Read first

- .agentflow/docs/improvement-plan.md (section 5)
- .agentflow/docs/ai-handoff-protocol.md
- README.md, GUIDE.md, RELEASE_NOTES.md, .agentflow/README.md
- .agentflow/docs/release-validation.md, .agentflow/docs/typesafe.md
- .agentflow/state/known-issues.md (stale tool notes to reconcile: agy interactive tester, Devin permission requirements)
- CHANGELOG.md (what shipped in 2.11.9-2.15.x - the docs must describe the current behavior)

## Allowed files

- README.md
- GUIDE.md
- RELEASE_NOTES.md
- .agentflow/README.md
- .agentflow/docs/release-validation.md
- .agentflow/docs/typesafe.md
- .agentflow/tools/ (only if generated status/handoff facts need a code path - section 5)
- .agentflow/tests/ (any file - test_layout.py enforces structure and may need updating)
- .agentflow/VERSION
- AGENTS.md, CLAUDE.md (AgentFlow version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/roles/, .agentflow/commands/, .claude/commands/ (T-097 scope)
- GUIDE.ru.md (T-099 scope)
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

- [ ] S-01: Every shipped behavior of the current VERSION is truthfully documented: Python launcher with the PowerShell compatibility wrapper, packaged CLI, optional MCP server and its opt-in privileged tools, model probes and their opt-in env vars, worker timeout, machine registry/dispatch modes, quota groups/policy, completion gate, recovery capture. No doc describes removed or never-shipped behavior as current.
- [ ] S-02: Stale tool notes verified against actual implementation and corrected: the agy interactive-tester hang claim vs the current noninteractive Tester path; Devin permission notes vs the current probe/worker argv (`--respect-workspace-trust false`, `--permission-mode` values); Codex sandbox limits on Windows; conductor/autostart marked Windows-only. Each claim is either corrected to match the code or explicitly marked unverified/removed.
- [ ] S-03: Status and handoff facts are generated from task/attempt records where the protocol promises it (or the promise is removed); goals, decisions and explanatory known issues stay authored memory; stale-summary detection exists or the claim is deleted.
- [ ] S-04: release-validation.md and typesafe.md match the shipped tools and current routing/admission behavior.
- [ ] S-05: Full suite passes verbatim; if template-owned files changed, VERSION incremented, AGENTS version block synced, CHANGELOG migration notes say what an installed project must do. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - template structure and entry-point integrity.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - install/update integrity of changed files.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
