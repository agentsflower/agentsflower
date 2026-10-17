# T-052: Recoverable handover round 2 - quoted-phrase false positive and group label fix

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-052-limit-detection-fix
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-052-limit-detection-fix
Independent check: tester
Resume: none

## Goal

Successor of T-030 (rejected on an independent partial review): fix the single
remaining defect class the tester found on f6d746b, keeping every verified part
of 2.13.0. The prepared worktree starts at the preserved rejected commit
f6d746bec79dc703df4b57f15c7b982b44c5fdc5 - keep that base, do not reset or
rebase it.

## Read first

- .agentflow/tasks/T-031-verify-recoverable-handover.md (the independent Result - R-01's partial entry and the New defects section are your defect list)
- .agentflow/tasks/T-030-recoverable-handover.md (original contract + Result)
- .agentflow/tools/limit_detection.py, run_task.py (resource_check), quota_groups.py
- .agentflow/tests/test_limit_detection.py, test_quota_groups.py, test_run_task.py

## Allowed files

- .agentflow/tools/limit_detection.py
- .agentflow/tools/run_task.py
- .agentflow/tools/conductor.ps1 (only if the detector interface changes)
- .agentflow/tools/tick.py (only if the detector interface changes)
- .agentflow/tests/ (any file)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)

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

- [ ] D-01: A verbatim strong provider phrase embedded inside a quote in prose (after verbs like shows/prints/displays/writes/echoes, or inside an already-quoted span) does NOT produce limitHit at exit 0 or at nonzero exit - the fix must extend the quote-frame handling so real product-log prose that quotes a provider phrase is skipped, while an actual provider stderr/stdout line containing the phrase still matches.
- [ ] D-02: The resource_check refusal under a TOOL-WIDE hold names the tool-wide hold correctly (not the session's own group); group-scoped hold messages stay group-scoped.
- [ ] D-03: Every T-030-verified behavior stays green: quota-group scoping, stop classification, takeover/leftover blocking, recovery capture, Resume semantics, plus the T-050-verified lifecycle behaviors.
- [ ] D-04: Full suite passes verbatim in the task worktree; increment VERSION (patch), sync AGENTS block and CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` - quote-frame and signal classes.
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` - group scoping.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - classification, takeover, draft capture, resource-check wording.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - group-aware needs.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 5b3797bc6e483dce3b579c0f2c94f26acf466f58 on t-052-limit-detection-fix
Files:
- .agentflow/tools/limit_detection.py - `_QUOTE_FRAME` gained the report verbs shows/prints/displays/writes/wrote/written/echoes/echoed; new `_inside_quote` treats a match inside an unclosed quote span as quoted subject matter (word-internal apostrophes are not delimiters, a closing/possessive `'` opens no span); `_quoted` consults it, so prose quoting the provider verbatim is skipped at any exit code while bare or error-prefixed provider lines still match
- .agentflow/tools/run_task.py - `resource_check` names the actually-blocking hold: the bare `<tool>` key reads `<tool> is limited until ...` even when the session has a quota group; a `<tool>:<group>`-scoped binding constraint still reads `<tool> group <group> is limited until ...`
- .agentflow/tests/test_limit_detection.py - 2 new tests: quoted report prose at exit 0 and 1, phrase after a closed quote still counts
- .agentflow/tests/test_run_task.py - 1 new test: tool-wide hold names the tool, not the session's group
- .agentflow/VERSION 2.13.1, AGENTS.md version line, CHANGELOG.md entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` -> pass (16 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (42 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (266 ran / 0 failed, 3 skipped platform-specific). Note: a first full-suite run flaked on two Windows environmental issues (a PermissionError temp-file lock in test_endcheck_violation_then_recheck and a still-running worker in test_dispatch_grant_becomes_the_worker_lease); both pass standalone and the verbatim re-run is fully green.
Criteria without a command:
- D-01: pinned by the two new tests covering every named verb (shows/prints/displays/writes/echoes) plus an already-open span at exit 0 and 1, and confirmed on the tester's exact fixtures (`the banner shows|prints "you've hit your usage limit"` now `no limit` at both exit codes); a bare `You've hit your usage limit` line and an `ERROR:`-prefixed phrase still match.
- D-02: the new test reproduces the reported mislabel (tool-wide `devin` hold + session group `dg`) and asserts `devin is limited until` and not `devin group dg is limited`; the group-scoped message stays pinned by the existing test.
- D-03: all T-030/T-050-verified behavior exercised green inside the 266-test suite (group scoping, stop classification, takeover blocking, recovery capture, Resume semantics, fail-closed readers, bound acceptance, locked --stop).
- D-04: VERSION 2.13.1, AGENTS block synced, CHANGELOG migration notes written; decisions.md text proposed below.
Found, not fixed:
- An `error:`-prefixed line still counts even when it quotes a phrase - outer error precedence is a T-031-verified semantic, left unchanged per D-01's prose-only scope.
- The audited upstream detector in the Transcript Youtube install carries the same unlisted-verb gap (this file was byte-identical to it before this fix); fixing that project is its own task.
- A rare edge: a match after an odd count of `"`/`` ` `` (a stray unclosed delimiter earlier in the line) reads as quoted - acceptable per the "inside an already-quoted span" requirement.
Proposed memory updates:
- decisions.md: "2026-10-17 - T-052 (2.13.1): the shared limit detector's quote frame now skips a verbatim provider phrase inside quoted report prose - the report-verb list gained shows/prints/displays/writes/echoes and any match inside an already-open quote span counts as quoted - while bare or error-prefixed provider lines still trip `limitHit`; resource_check names the hold that actually blocks (bare `<tool>` reads tool-wide even for a grouped session, a group-scoped binding keeps the group label). Rejected: lowering the outer error-line precedence (T-031-verified semantic); enumerating every reporting verb (unbounded - open-span detection covers the rest)."
- known-issues.md: the residual gap T-031 recorded (verbatim phrase mid-quote after an unlisted verb) is closed at 2.13.1; keep the annotation with the superseded 2026-10-03 `limitHit` entry.
