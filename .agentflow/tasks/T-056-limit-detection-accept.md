# T-056: Recoverable handover round 2 - finalization under corrected scope declaration

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-056-limit-detection-accept
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-056-limit-detection-accept
Independent check: tester
Resume: none

## Goal

Successor of rejected T-052: the rejected task's own contract omitted the
inherited T-030 base from its Allowed files, so the verified artifact could
not pass scope verification - an Orchestrator authoring defect, not a product
defect. The artifact itself was independently verified PASS by T-053 on
5b3797bc6e483dce3b579c0f2c94f26acf466f58 (all X-01..X-05 criteria with live
evidence). Your job: branch from that preserved commit, confirm the artifact
is complete and green, and produce the Result + release metadata under this
contract whose Allowed files correctly declare the full inherited scope.
Reconcile - do not re-implement what is already verified.

## Read first

- .agentflow/tasks/T-052-limit-detection-fix.md (rejected contract; its artifact is your base)
- .agentflow/tasks/T-053-verify-limit-detection.md (the independent verification of the exact base SHA)
- .agentflow/tasks/T-031-verify-recoverable-handover.md (round-2 findings the fix answers)
- .agentflow/tools/limit_detection.py, run_task.py, quota_groups.py, machine_capacity.py, gate.py, tick.py, conductor.ps1
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)

## Allowed files

- .agentflow/tools/limit_detection.py
- .agentflow/tools/run_task.py
- .agentflow/tools/tick.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/quota_groups.py
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/gate.py
- .agentflow/docs/model-options.json
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/tests/ (any file)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

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

- [ ] F-01: The branch carries the complete verified fix: quoted report-prose does not produce limitHit at exit 0 or 1 (shows/prints/displays/writes/echoes, already-open quote spans), bare or error-prefixed provider lines still match, resource_check names the actually-blocking hold (tool-wide vs group-scoped correctly).
- [ ] F-02: If anything is missing vs the T-053-verified base, add only the delta and report it; if the base is complete, the Result records `Change:` as the inherited commit SHA on this branch plus any consolidation commit you add for release metadata.
- [ ] F-03: VERSION/AGENTS/CHANGELOG reflect the shipped fix under this task (VERSION 2.13.1 already exists on the base - keep it if nothing further lands, patch-bump only if you change product files).
- [ ] F-04: Every T-030/T-050-verified behavior stays green: quota groups, classification, takeover block, recovery capture, Resume semantics, fail-closed readers, bound acceptance, locked --stop.
- [ ] F-05: Full suite passes verbatim; CHANGELOG migration notes accurate; propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` - quote-frame and signal classes.
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` - group scoping.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - classification, takeover, draft capture.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - group-aware needs.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 5b3797bc6e483dce3b579c0f2c94f26acf466f58 on t-056-limit-detection-accept
Files:
- none new - the branch HEAD is exactly the T-053-verified commit 5b3797b (on the preserved T-030 base f6d746b); nothing was missing vs the verified base, so no delta and no consolidation commit were added. Its file set (all inside this contract's Allowed files): .agentflow/tools/limit_detection.py, run_task.py, tick.py, conductor.ps1, quota_groups.py, machine_capacity.py, gate.py, .agentflow/docs/model-options.json, .agentflow/docs/ai-handoff-protocol.md, .agentflow/tests/ (4 files), .agentflow/VERSION, AGENTS.md (version line only), CHANGELOG.md
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` -> pass (16 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (42 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (266 ran / 0 failed, 3 skipped platform-specific)
Criteria without a command:
- F-01 - confirmed by inspection and the green suite on the exact verified SHA: `_QUOTE_FRAME` carries shows/prints/displays/writes/wrote/written/echoes/echoed, `_inside_quote` skips matches inside an already-open quote span, bare and error-prefixed provider lines still match (16 detector tests green); `resource_check` names the actually-blocking hold via `scope = " group <g>"` only when the binding constraint is group-scoped - the bare `<tool>` key reads tool-wide (run_task.py:849).
- F-02 - the base is complete: branch `t-056-limit-detection-accept` is at 5b3797b (the T-053-verified SHA) on the preserved T-030 base f6d746b, worktree clean, `git diff main...HEAD` = 17 files all inside Allowed files. `Change:` records the inherited SHA; no consolidation commit was needed because the release metadata already landed in 5b3797b.
- F-03 - VERSION = 2.13.1, AGENTS.md block version line = 2.13.1 (only line changed there), CHANGELOG.md has a dated 2.13.1 entry with migration notes (`install.py --update` ships the corrected tools; recorded holds keep keys and expiry). No product file changed under this task, so no patch bump.
- F-04 - the 266-test suite exercises and passes every T-030/T-050-verified behavior on this SHA: quota-group scoping, stop classification, takeover/leftover blocking, recovery capture, Resume semantics, fail-closed readers, bound acceptance, locked --stop (same coverage T-053 verified live).
- F-05 - full suite green verbatim; CHANGELOG 2.13.1 migration notes are accurate for the shipped fix; dated decisions.md text proposed below.
Found, not fixed:
- none new under this contract; the inherited artifact's own disclosures stand (error-prefixed lines still count even when they quote a phrase - T-031-verified semantic; the unclosed-delimiter edge; the Transcript Youtube installed detector still carries the pre-fix gap - a separate project's task).
Proposed memory updates:
- decisions.md: "2026-10-17 - T-056: the T-052 artifact (2.13.1, 5b3797b) is accepted under a successor contract whose Allowed files declare the full inherited T-030+T-052 scope. T-052's rejection was an Orchestrator authoring defect - its contract omitted the inherited T-030 base files from Allowed files so the verified artifact could not pass scope verification - not a product defect: T-053 had independently verified every criterion PASS on the exact SHA. Rejected: re-implementing or amending the verified fix, and a no-op consolidation commit (release metadata already landed in 5b3797b; the branch HEAD is the recorded Change)."
- tasks ledger: when a successor task inherits an earlier unmerged branch as its base, its Allowed files must declare the whole `git diff main...HEAD` file set, not only the delta commit's files - scope verification diffs the branch, not the last commit.
