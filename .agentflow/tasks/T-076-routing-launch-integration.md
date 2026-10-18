# T-076: Integrate assessed routing into direct worker launch

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-074
Branch: t-076-routing-launch-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-076-routing-launch-integration
Independent check: tester
Resume: none

## Goal

Wire the independently accepted T-074 core into direct and manual launch and
retry. Preserve the urgent T-072 deadline watchdog. Automatic scheduling,
backup selection and final reporting are owned by dependent T-078. Human
authorized urgent bounded decomposition on 2026-10-18.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-040-routing-enforcement.md (original Q-01 through Q-08)
- .agentflow/tasks/T-074-routing-core-recovery.md (accepted API and evidence)
- .agentflow/tools/route.py
- .agentflow/tools/run_task.py
- .agentflow/tests/test_route.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/tick.py
- .agentflow/tools/route.py (only integration defects with regression tests)
- .agentflow/tests/
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (policy text/preference only; preserve model catalog and actual holds)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- Other Task Files, runtime history, original T-040 worktree
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] I-01: Direct and manual launches call T-074 admission API after effective argv resolution; missing/stale/failed/low-confidence assessments refuse before spawning. Auditable explicit human exceptions remain possible.
- [ ] I-02: Retry uses the same admission check, cannot downgrade via environment flags, and retains process/lease/hold safety. Persist safe admission metadata, never secrets.
- [ ] I-03: Live disposable probes cover a refused missing assessment, refused override downgrade, accepted adequate selection and explicit human exception. Preserve T-072 watchdog regressions.
- [ ] I-04: Focused/full regressions pass; patch release, protocol and migration accurately describe direct launch enforcement. Automatic backup/report integration remains pending T-078. No live TypeSafe calls in tests.
- [ ] I-05: Align the instance routing policy with the human's 2026-10-18 Devin preference for development, fresh independent testing and orchestration. Remove any generic other-CLI preference that contradicts it, without lowering adequacy, fabricating measured quota or bypassing actual holds; the reported unlimited window ends 2026-11-01 with no exact cutoff supplied. Test tester-role selection as well as developer-role selection.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for I-04. Checks above are the scoped
acceptance/integration commands; avoid redundant whole-suite repeats.

## Execution bounds

20-minute attempt cap (includes the measured six-minute full suite). Reuse the accepted API instead of redesigning it. Run
focused checks after coherent changes, then one required full suite. If blocked,
checkpoint and report the exact failing criterion without an hours-long retry.
Result must include explicit `- I-01: pass - <evidence>` outcome lines for
I-01..I-05; the older role example without colon/verdict is obsolete.

## Result
