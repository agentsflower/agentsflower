# T-096: Merge fixed-clock stack onto the 2.15.5 mainline

Role: developer
Tool: devin
Model: swe-2-high, effort=high
Stage: 5
Depends on: none
Branch: t-096-merge-fixed-clock-stack
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-096-merge-fixed-clock-stack
Independent check: none - merge-only resolution of three release-metadata files on a stack whose product content was independently verified by T-083/T-085/T-086/T-088/T-090/T-092; the resolution is pinned line-by-line below and the check is the recorded suite plus the scoped Checks on the merge SHA
Resume: none

## Goal

Mechanical merge-only task, no judgment calls: T-095's artifact
04773311aafce6c3f98831a5f862c8c745566da6 verified PASS but cannot merge -
its release metadata says 2.15.4 while main is at 2.15.5. Branch from the
launcher-created mainline start, `git merge t-095-fixed-clock-carrier`, and
resolve the three conflicted files exactly as pinned below; every other path
is the clean auto-merge result; change nothing else.

Resolution (pinned, no judgment calls):
- `.agentflow/VERSION` -> `2.15.5` (the higher side wins; the 2.15.4 stack's
  content lands under it and keeps its own changelog entry).
- `AGENTS.md` -> `AgentFlow version: 2.15.5` - the only conflicting line.
- `CHANGELOG.md` -> keep both entries verbatim and in version order:
  `## 2.15.5 - 2026-10-20` first, then `## 2.15.4 - 2026-10-18`.

Commit as a single merge commit `[T-096] merge: fixed-clock stack onto
2.15.5 mainline` with both parents (mainline start, then 0477331).

## Read first

- .agentflow/tasks/T-095-fixed-clock-carrier.md (the artifact and its Result section)
- CHANGELOG.md on both sides of the merge (the two entries to keep verbatim)

## Allowed files

- .agentflow/tools/tick.py
- .agentflow/tools/route_report.py
- .agentflow/tools/cli.py
- .agentflow/tools/route.py
- .agentflow/tests/ (any file)
- .agentflow/tasks/_template.md (routing fields only)
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (policy text only)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- Preserved draft worktrees and branches t-093-*, t-094-*, t-095-* (read only; t-095-fixed-clock-carrier is the merge source)
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] M-01: HEAD is a single merge commit whose two parents are the launcher-created mainline start and 04773311aafce6c3f98831a5f862c8c745566da6; exactly the three pinned files were hand-resolved (VERSION = 2.15.5; AGENTS.md version block = 2.15.5; CHANGELOG.md = the verbatim 2.15.5 entry followed by the verbatim 2.15.4 entry); every other path equals the clean auto-merge result.
- [ ] M-02: the merged tree contains both lines of work unchanged: the 2.15.5 Jev-led selection + devin-gemini-4-argon pool, and the full routing-scheduler stack including both datetime.now(timezone.utc)-relative holds in test_a_held_backup_group_stays_scoped_and_refused; `git diff main...HEAD` stays inside this contract's Allowed files.
- [ ] M-03: the three scoped Checks pass verbatim on the merge SHA; the full suite is run once on the merge SHA and recorded verbatim (the merge is a changed input: route.py, typesafe.md and test_quota_groups.py auto-merged both lines of work).
- [ ] M-04: VERSION = AGENTS.md version block = 2.15.5 with both changelog entries present verbatim; T-040 is not claimed complete.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once on the merge result
and record it verbatim for M-03 (the merged tree is new content).

## Execution bounds

20-minute cap - resolve the merge first, start the full suite early (it takes
~7.5 min), run the scoped Checks, write the Result section. Result must
include explicit `- M-01: pass - <evidence>` outcome lines for M-01..M-04;
put `evidence:` markers at line end followed only by intended claim paths
(`.runtime` evidence basenames must start `T-096.`); path names inside prose
are mentions.
