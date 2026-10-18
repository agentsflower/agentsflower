# T-076: Integrate assessed routing into direct worker launch

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-084
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
Outcome: completed
Change: 07fbeed18e6a8d1a60eee491e1b81171b8090a6d on t-076-routing-launch-integration
Files:
- .agentflow/tools/run_task.py - cmd_launch calls route.admission() after preflight and the launch budgets, before probes/lease/spawn; route.log_admission() appends the admission/human-exception event; launcher docstring names the gate; import route
- .agentflow/tests/test_run_task.py - RoutingAdmissionTests: live disposable launches with a fake devin CLI (missing/stale/failed assessment refused, AGENTFLOW_DEVIN_ARGS downgrade refused on launch and retry, adequate selection admitted and recorded, human exception admitted and recorded); tester fixture gains the exception line; fake task dict gains "file"
- .agentflow/tests/test_route.py - I-05 instance-policy test (floor/prefer/policy text, developer+tester adequacy ordering) and end-to-end routing test (developer and tester land on the Devin option over a higher Jev rank)
- .agentflow/tests/test_endcheck.py - disposable fixture task gains 'Routing exception: disposable test fixture' so legacy launches keep passing the new gate
- .agentflow/docs/ai-handoff-protocol.md - section 7 describes admission on the persisted assessment for every launch path incl. retry, and the auditable 'Routing exception:' human override
- .agentflow/docs/typesafe.md - launch-side API now wired into the launcher
- .agentflow/docs/model-options.json - policy encodes the human's 2026-10-18 Devin preference for development, fresh independent testing and orchestration; 2026-11-01 window marked qualitative; catalog and holds unchanged
- .agentflow/VERSION, AGENTS.md - 2.15.3
- CHANGELOG.md - 2.15.3 entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (53 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (398 passed / 0 failed, 3 skipped) - required full suite, run once after the coherent change
- I-01: pass - run_task.py cmd_launch invokes route.admission(t, tool, rt_dir=RT_DIR) after gate preflight and budget_stop, before any probe, lease or spawn; identity_problems resolves header Model plus AGENTFLOW_<TOOL>_ARGS (header wins, same precedence as env_args). Live probes in RoutingAdmissionTests.test_missing_stale_and_failed_assessments_refuse_before_anything refuse missing/failed/stale records for direct (T-001 devin) and --manual launches with no runtime file created; 'Routing exception:' header admits and is audited (test_human_exception_admits_and_is_recorded_as_a_human_decision)
- I-02: pass - retries and re-launches re-enter cmd_launch under launch.lock, so the identical admission applies; test_env_override_downgrade_is_refused_on_launch_and_retry refuses AGENTFLOW_DEVIN_ARGS '--model swe-2-medium' twice against an effort>=high record and nothing is leased; an adequate '--model swe-2-high' retry passes; log_admission persists only resolved identity/source/requirementsHash (no secrets, no quota figures)
- I-03: pass - RoutingAdmissionTests (test_run_task.py) run live disposable probes: refused missing/failed/stale assessments, refused env-override downgrade incl. retry, admitted adequate selection with recorded admission event, admitted human exception recorded as human-exception with 'overrode'; test_worker_watchdog.py passes 14/14 (T-072 watchdog preserved)
- I-04: pass - focused checks 14+53+14 pass, full suite 398 pass/3 skipped; VERSION 2.15.3 with AGENTS.md block, CHANGELOG entry and migration notes, protocol section 7 and typesafe.md describe direct-launch enforcement; automatic backup/report integration left to T-078; no live TypeSafe calls (tests write assessment records directly / patch the client)
- I-05: pass - model-options.json policy implements the 2026-10-18 preference (Devin for development, fresh independent testing and orchestration; other CLI only when no adequate Devin option is usable; tester independence = fresh session on isolated checkout, not a different CLI); no generic other-CLI preference remains, adequacy/floor unchanged, no fabricated measured quota (2026-11-01 window labeled qualitative), observed holds untouched; test_route.py covers tester-role and developer-role selection
Question or reason:
Found, not fixed:
- tick.use_backup still does not consult route.backup_ok at selection time; launch-side admission in cmd_launch still refuses a weaker backup. Backup selection/reporting integration is T-078 scope per this task's Goal.
Proposed memory updates:
- decisions.md, 2026-10-18: T-076 released 2.15.3 - launch admission enforced in run_task.py cmd_launch for direct/manual/tick/retry paths (missing/stale/blocked/low-confidence/failed assessment refuses before spawn; env downgrade refused; 'Routing exception:' header is the audited human override). Instance routing policy set to the human's 2026-10-18 Devin preference for development, fresh independent testing and orchestration; Devin reported unlimited through 2026-11-01 (qualitative, actual holds still apply). Automatic scheduling/backup/reporting integration deferred to T-078.
