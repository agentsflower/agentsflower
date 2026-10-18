# T-082: Repair backup_ok quota-group hold admission

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-075
Branch: t-082-backup-hold-admission
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-082-backup-hold-admission
Independent check: tester
Resume: none

## Goal

Successor of rejected T-074. The artifact at
5a6510c9b76201ccce35d1a10ce685be0d76a6e2 is complete except one diagnosed gap
(independent tester T-075, V-03 partial): `backup_ok` admits an adequate
backup whose quota group is under a live machine-registry hold - holds are
excluded at assessment time only, so a backup whose group becomes held after
assessment is still admitted by the artifact's own launch-side API. Branch
from that preserved commit, repair `backup_ok` to consult the live hold
(`machine_capacity.limit_until` / `live_reason` for the backup's
tool+quota_group) at call time, and add focused regression tests. Do not
re-implement or re-verify the rest of the artifact.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-074-routing-core-recovery.md (contract + Result; its artifact is your base)
- .agentflow/tasks/T-075-verify-routing-core.md (Result: V-03 gap, P3 probe)
- .agentflow/tasks/.runtime/T-075.evidence/T-075.v03-v04-probe-output.txt (the live probe that found the gap)
- .agentflow/tools/route.py (assessment/admission API incl. `backup_ok`, on your branch)
- .agentflow/tools/machine_capacity.py, .agentflow/tools/quota_groups.py (read only: hold lookup + group mapping)
- .agentflow/tests/test_routing_core.py, .agentflow/tests/test_route.py

## Allowed files

- .agentflow/tools/route.py
- .agentflow/tests/test_routing_core.py
- .agentflow/tests/test_route.py (only if a backup expectation needs adjusting)
- CHANGELOG.md (only if the 2.15.2 entry's wording claims what did not exist)

## Do not touch

- .agentflow/tools/run_task.py, tick.py, conductor.ps1, gate.py, plan_route.py, quota_groups.py, machine_capacity.py (read only)
- .agentflow/tests/test_plan_route.py (known latent environment-dependence; separate scope, do not repair here)
- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- T-040 and T-074 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] S-01: Branch `t-082-backup-hold-admission` moved onto 5a6510c9b76201ccce35d1a10ce685be0d76a6e2 once; `git diff 5a6510c...HEAD` (or equivalent) is only this fix and stays inside Allowed files. No product change beyond the hold gap; the inherited artifact is otherwise byte-identical to what T-075 verified.
- [ ] S-02: `backup_ok` consults the live machine-registry hold at call time for the backup's tool and quota group (`machine_capacity.limit_until`/`live_reason` or the equivalent existing helper): an adequate backup under a fresh post-assessment hold is refused with a diagnosable reason, an adequate unheld backup is still admitted, a below-requirement backup is still refused, a hold on an unrelated group does not block. No new network calls.
- [ ] S-03: Focused regression tests prove the call-time refusal under a hold appearing after the assessment, the unheld admission, and the below-requirement refusal (patched registry/stand-ins only, no real machine state or network).
- [ ] S-04: Both scoped Checks pass verbatim; one full-suite run after the coherent change is recorded per project rules (no repeated whole-suite runs); VERSION stays 2.15.2 and the CHANGELOG 2.15.2 entry remains accurate (API-only, launch enforcement pending T-076); T-040 is not claimed complete.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`
- `python -m unittest discover -s .agentflow/tests -p test_route.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for S-04. Scoped Checks above are rerun
at acceptance/integration; do not multiply whole-suite runs without cause.

## Execution bounds

20-minute attempt cap (includes the measured six-minute full suite). Begin by
moving the branch onto 5a6510c, then the focused tests and the smallest fix,
not another architecture survey. Result must include explicit
`- S-01: pass - <evidence>` outcome lines for S-01..S-04; the older role
example without colon/verdict is obsolete. Put `evidence:` markers at line
end, followed only by intended claim paths (`.runtime` evidence basenames
must start `T-082.`); path names inside prose are mentions.

## Result
Outcome: completed
Change: fc2c37cc7144d7a5788ac6ee797f4b1020d34025 on t-082-backup-hold-admission
Files:
- .agentflow/tools/route.py - backup_ok consults the live machine-registry hold at call time: after the recorded-requirement check it resolves the backup's option on the same model identity identity_problems verified (header model or env-selected) via quota_groups.option_for and refuses with "<option> is limited until <iso>" when machine_capacity.limit_until(tool, quota_group) reports an end - covers both the '<tool>:<group>' hold and the bare tool-wide hold through _limit_end
- .agentflow/tests/test_routing_core.py - new test_backup_ok_consults_the_live_hold_at_call_time (disposable registry under a temp AGENTFLOW_MACHINE_STATE_DIR written after the ok record: post-assessment group hold refused, tool-wide hold refused, unrelated group/tool hold admitted, unheld admitted, below-requirement still refused); test_backup_must_meet_the_same_requirement pinned to a temp AGENTFLOW_MACHINE_STATE_DIR so the real registry can no longer leak into backup_ok
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (20 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> 392 ran / 1 failed / 3 skipped - the required one full-suite run after the coherent change; the single failure is test_approval.test_planned_task_waits_until_approved, a transient WinError 5 on os.replace in its temp ledger fixture, unrelated to this change (isolated rerun: 5/5 pass - see Found, not fixed)
- S-01: pass - branch moved onto 5a6510c9b76201ccce35d1a10ce685be0d76a6e2 once (git reset --hard from 52a946d on a clean tree); `git diff 5a6510c..HEAD` is the single commit fc2c37c touching only route.py and test_routing_core.py, both Allowed files; everything else of the T-074 artifact is byte-identical to what T-075 verified
- S-02: pass - backup_ok now consults the live hold at call time for the backup's tool+quota_group: post-assessment 'devin:devin' hold refused with "devin-swe-2 is limited until ...", tool-wide 'devin' hold refused, 'agy:agy-gemini'+'codex' holds do not block a devin backup, unheld adequate admitted, below-requirement still refused; no new network calls (local registry file only)
- S-03: pass - the new regression test creates the hold after the ok assessment is recorded and asserts each outcome against a disposable registry.json under a temp state dir; patched stand-ins only, no real machine state or network
- S-04: pass - both scoped Checks pass verbatim as recorded above; one full-suite run recorded after the coherent change (no repeats); VERSION stays 2.15.2 and the CHANGELOG 2.15.2 entry's "backups and retries ... cannot bypass quota groups" is now accurate of the artifact - still API-only, launch enforcement pending T-076; T-040 is not claimed complete
Question or reason: -
Found, not fixed:
- test_approval.test_planned_task_waits_until_approved flaked once inside the full suite: ledger.py _write_atomic's os.replace hit WinError 5 replacing the temp fixture's tasks.md - the transient Windows replace failure machine_capacity._replace_retry already guards against elsewhere; the file passes alone (5/5). Latent, outside Allowed files.
- test_plan_route.py still reads the real machine registry through eligibility->limit_until (the T-075 V-06 disclosure); explicitly out of scope here.
Proposed memory updates:
- known-issues.md, 2026-10-18: resolved - the backup_ok quota-hold gap found by T-075 (P3 probe) is repaired at fc2c37c: backup_ok consults machine_capacity.limit_until for the backup's tool+quota_group at call time. New latent note: ledger.py _write_atomic can hit transient WinError 5 on os.replace (seen once in test_approval during the T-082 full suite; reruns green).
- session-log.md, 2026-10-18: T-082 done at fc2c37c on t-082-backup-hold-admission (base 5a6510c); scoped checks 20/0 + 12/0, full suite 392 ran with one unrelated transient WinError 5 in test_approval (isolated rerun green); next step is T-076 launch enforcement.
