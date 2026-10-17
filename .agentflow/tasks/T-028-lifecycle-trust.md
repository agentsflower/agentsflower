# T-028: Trustworthy task lifecycle - state enforcement, atomic runtime, PS 5.1 --live, merge-history audit

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-028-lifecycle-trust
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-028-lifecycle-trust
Independent check: tester
Resume: none

## Goal

Implement improvement-plan.md section 1 in the template: a task can only be
claimed, attempted and transitioned through verified state; malformed runtime
state blocks rather than silently passes; the known launcher defects are closed.
Reconcile first - part of this exists since 2.11.3/2.11.11; do not duplicate.

## Read first

- .agentflow/docs/improvement-plan.md (section 1, exit criteria)
- .agentflow/docs/ai-handoff-protocol.md (Task lifecycle, Launching workers, Runtime state)
- .agentflow/docs/project-rules.md
- .agentflow/state/known-issues.md
- .agentflow/tools/run_task.py, .agentflow/tools/run-task.ps1, .agentflow/tools/gate.py, .agentflow/tools/ledger.py, .agentflow/tools/tick.py, .agentflow/tools/accept.py
- .agentflow/tests/test_run_task.py, test_launcher_lifecycle.py, test_endcheck.py, test_parallel.py, test_tick.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/gate.py
- .agentflow/tools/ledger.py
- .agentflow/tools/tick.py
- .agentflow/tools/accept.py
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files; branch may not commit under it)
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

- [ ] L-01: Launch-state enforcement is verified end to end, including paths that do not go through preflight: `ledger.py set --status in progress` on an awaiting-approval task is refused (the approval gate cannot be bypassed by a direct CLI call), and terminal tasks (done/rejected/cancelled) cannot acquire a new attempt. Retry states that the protocol allows keep working. Prove both the refused and the allowed directions in tests.
- [ ] L-02: The empty `--live` argument defect on Windows PowerShell 5.1 is reproduced and fixed (locate it: gate.py preflight `--live` parsing, run_task.py argv construction, or run-task.ps1 delegation). The supported shells (powershell 5.1, pwsh 7, sh) each get a regression test or a documented static check where a live PS 5.1 host is unavailable.
- [ ] L-03: Merge-history false positives in gate.py are reproduced and fixed: a developer branch whose merge commits are legitimately empty of Task File changes passes `worktree_copy_problems`, while an actual worker commit under .agentflow/tasks/ is still rejected. Cover octopus-merge audit failure path and ordinary merges in disposable-repo tests.
- [ ] L-04: Runtime writes are atomic (attempt JSON, verify JSON, tick.json, tool-limits.json, conductor-side runtime records this task owns): write-temp-then-os.replace, and a malformed or truncated runtime file fails closed with a diagnosable error, never reads as "no active work" or "no evidence". Schema validation rejects structurally invalid attempt/verify records at read time.
- [ ] L-05: Every result and verification record binds task ID, attempt number, requirements hash (Task File header hash) and full artifact SHA(s) - extend the existing records where a field is missing; legacy verify/attempt records and open tasks keep working (define and test the migration path).
- [ ] L-06: Process-identity checks (pid + pidStart) are used consistently wherever a process is claimed dead or alive; a reused pid cannot impersonate a live worker.
- [ ] L-07: Full suite passes verbatim in the task worktree; increment VERSION (next patch), sync the AGENTS.md block version line and CHANGELOG entry with migration notes. Propose dated decisions.md text in the Result - do not write canonical memory.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - launcher lifecycle and state binding.
- `python -m unittest discover -s .agentflow/tests -p test_launcher_lifecycle.py` - launch/state/preflight regressions.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-history and baseline audits.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - runtime state handling.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
