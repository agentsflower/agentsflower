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

## Result
Outcome: completed
Change: 67549594f049f1df2293acd9f9902c7090ddcf8a on t-096-merge-fixed-clock-stack
Files:
- .agentflow/VERSION - hand-resolved to 2.15.5 (the file was a single-line conflict)
- AGENTS.md - hand-resolved: version block line kept at 2.15.5 (the only conflicted line)
- CHANGELOG.md - hand-resolved: kept both entries verbatim in version order (2.15.5 entry first, then 2.15.4)
- .agentflow/docs/ai-handoff-protocol.md, .agentflow/docs/typesafe.md, .agentflow/tasks/_template.md, .agentflow/tests/test_approval.py, .agentflow/tests/test_parallel.py, .agentflow/tests/test_quota_groups.py, .agentflow/tests/test_route_report.py, .agentflow/tests/test_routing_core.py, .agentflow/tests/test_routing_scheduler.py (new), .agentflow/tests/test_tick.py, .agentflow/tools/route.py, .agentflow/tools/route_report.py, .agentflow/tools/tick.py - clean auto-merge of both lines, no manual edits
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py` -> pass (11 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (25 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` (required pre-commit check, run once on the merge SHA) -> pass (424 passed / 0 failed / 3 skipped; verbatim tail `Ran 424 tests in 339.692s` / `OK (skipped=3)`) evidence: .agentflow/tasks/.runtime/T-096.full-suite.txt
- M-01: pass - HEAD is the single merge commit 6754959; `git log -1 --format=%P` shows parents 478fa110b74075617141d1f5aea2266d017a9194 (launcher-created mainline start) then 04773311aafce6c3f98831a5f862c8c745566da6. `git merge-tree --write-tree 478fa11 0477331` reproduced exactly the three pinned conflicts, and `git diff --name-only <auto-merge tree de00b49d> HEAD` lists only .agentflow/VERSION, AGENTS.md, CHANGELOG.md - so every other path equals the clean auto-merge result. Resolutions verified: VERSION = 2.15.5; AGENTS.md version block = 2.15.5; CHANGELOG.md = verbatim `## 2.15.5 - 2026-10-20` entry (line 5) followed by the verbatim `## 2.15.4 - 2026-10-18` entry (line 43).
- M-02: pass - merged tree contains both lines of work unchanged: `recommended` map and `devin-gemini-4-argon` pool entry present in .agentflow/docs/model-options.json (2.15.5 line), and both datetime.now(timezone.utc)+timedelta(hours=1) holds present in test_a_held_backup_group_stays_scoped_and_refused in .agentflow/tests/test_routing_scheduler.py; `git diff --name-only main...HEAD` lists 14 paths, all inside Allowed files (_template.md delta is only the `Routing exception:` routing field; the merge adds no model-options.json delta vs main).
- M-03: pass - the three scoped Checks above pass verbatim on merge SHA 6754959; the full suite ran once on the merge SHA: `Ran 424 tests in 339.692s` / `OK (skipped=3)` evidence: .agentflow/tasks/.runtime/T-096.full-suite.txt
- M-04: pass - .agentflow/VERSION = 2.15.5, AGENTS.md version block = 2.15.5, both changelog entries present verbatim; T-040 is not claimed complete.
Found, not fixed:
- none
Proposed memory updates:
- none (merge-only resolution; T-095 Result and the 2.15.5 changelog entry already carry the context)
