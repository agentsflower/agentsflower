# T-084: Backup-hold admission carrier - T-082 artifact under corrected scope declaration

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-083
Branch: t-084-backup-hold-carrier
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-084-backup-hold-carrier
Independent check: tester
Resume: none

## Goal

Successor of rejected T-082 (itself successor of rejected T-074): the rejected
contract's Allowed files omitted the inherited T-074 base the branch carries,
so the verified artifact could not pass scope verification - an Orchestrator
authoring defect, not a product defect. The artifact itself was independently
verified PASS by T-083 on fc2c37cc7144d7a5788ac6ee797f4b1020d34025 (all
V-01..V-05 with live probes and a negative control). Your job: move this
task's new branch onto that preserved commit, confirm the artifact is
complete and green, and produce the Result under this contract whose Allowed
files correctly declare the full inherited scope. Reconcile - do not
re-implement what is already verified.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-082-backup-hold-admission.md (rejected contract; its artifact is your base)
- .agentflow/tasks/T-083-verify-backup-hold.md (the independent PASS on the exact base SHA)
- .agentflow/tasks/T-074-routing-core-recovery.md + T-075-verify-routing-core.md (inherited artifact + the gap the repair answers)
- .agentflow/tools/route.py, machine_capacity.py, quota_groups.py on the branch
- .agentflow/tests/test_routing_core.py, test_route.py

## Allowed files

- .agentflow/tools/route.py
- .agentflow/tools/gate.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/quota_groups.py
- .agentflow/tests/test_route.py
- .agentflow/tests/test_routing_core.py
- .agentflow/docs/model-options.json
- .agentflow/docs/typesafe.md
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/tools/run_task.py, tick.py, conductor.ps1, machine_capacity.py (read only)
- .agentflow/tests/test_plan_route.py (known latent environment-dependence; separate scope)
- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- T-040, T-074 and T-082 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] F-01: The branch HEAD is exactly the T-083-verified commit fc2c37cc7144d7a5788ac6ee797f4b1020d34025 (base 5a6510c); `git diff main...HEAD` file set stays inside this contract's Allowed files. Add a consolidation commit ONLY if something verified is actually missing - none is expected, since release metadata already landed in fc2c37c.
- [ ] F-02: The inherited artifact is complete: the whole T-074 routing core plus the T-082 hold repair - backup_ok consults the live machine-registry hold for the backup's tool+quota_group at call time - nothing re-implemented, nothing dropped.
- [ ] F-03: VERSION = 2.15.2, the AGENTS.md version block agrees, and the CHANGELOG 2.15.2 entry accurately describes the combined artifact (API-only; launch enforcement pending T-076); T-040 is not claimed complete.
- [ ] F-04: Both scoped Checks pass verbatim on the branch HEAD; the already-recorded full-suite evidence (T-082: 392 ran / 1 transient test_approval WinError 5 flake / 3 skipped, isolated rerun 5/5; T-075: 391/0/3 on the base) is reported honestly, not re-run without a changed input.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`
- `python -m unittest discover -s .agentflow/tests -p test_route.py`

## Execution bounds

20-minute cap. This is a carrier: reset the branch onto fc2c37c, verify
completeness and metadata, run the scoped Checks, write the Result. No new
full suite without a changed input; no product edits unless a verified gap
is actually found. Result must include explicit `- F-01: pass - <evidence>`
outcome lines for F-01..F-04; put `evidence:` markers at line end followed
only by intended claim paths (`.runtime` evidence basenames must start
`T-084.`); path names inside prose are mentions.

## Result
Outcome: completed
Change: fc2c37cc7144d7a5788ac6ee797f4b1020d34025 on t-084-backup-hold-carrier
Files:
- none edited by this carrier task: the branch was moved onto the T-083-verified commit by `git reset --hard` from 52a946d on a clean tree; no consolidation commit was needed because nothing verified was missing
- the carried delta vs main is the combined T-074+T-082 artifact touching only .agentflow/tools/route.py, .agentflow/tools/gate.py, .agentflow/tools/plan_route.py, .agentflow/tools/quota_groups.py, .agentflow/tests/test_route.py, .agentflow/tests/test_routing_core.py, .agentflow/docs/model-options.json, .agentflow/docs/typesafe.md, .agentflow/VERSION, AGENTS.md (version block only), CHANGELOG.md - all inside this contract's Allowed files
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (20 passed / 0 failed). evidence: .agentflow/tasks/.runtime/T-084.evidence/T-084.check-test_routing_core.txt
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (12 passed / 0 failed). evidence: .agentflow/tasks/.runtime/T-084.evidence/T-084.check-test_route.txt
- F-01: pass - HEAD is exactly fc2c37cc7144d7a5788ac6ee797f4b1020d34025 (git rev-parse), direct parent 5a6510c whose parent b40c934 is the merge-base with main; `git diff main...HEAD` touches the 11 files listed above, all inside Allowed files (the AGENTS.md delta is the version-block line only: 2.15.1 -> 2.15.2); no consolidation commit added. evidence: .agentflow/tasks/.runtime/T-084.evidence/T-084.artifact-state.txt
- F-02: pass - the inherited artifact is complete: the T-074 routing core is present (requirementsHash-bound schemaVersion-1 assessment events; assessment_problems/admission/log_admission/history/latest_assessment/env_selected/identity_problems; floor/prefer ordering in model-options.json) plus the T-082 repair - backup_ok resolves the backup option via quota_groups.option_for and refuses when machine_capacity.limit_until(tool, quota_group) reports an end (route.py:710-725); nothing re-implemented, nothing dropped
- F-03: pass - .agentflow/VERSION reads 2.15.2, the AGENTS.md version block reads "AgentFlow version: 2.15.2", and the CHANGELOG 2.15.2 entry (2026-10-18) describes the combined artifact: requirement-first selection, the launch-side API including backup_ok, and "backups and retries ... cannot bypass quota groups" - now accurate of the artifact; explicitly API-only, launch enforcement pending T-076, "T-040 is not complete"
- F-04: pass - both scoped Checks pass verbatim on fc2c37c as recorded above; the recorded full-suite evidence is reported honestly, not re-run: T-082 logged 392 ran / 1 failed / 3 skipped where the failure is the transient test_approval WinError 5 on ledger._write_atomic os.replace (isolated rerun 5/5), and T-075 recorded 391/0/3 on base 5a6510c; no changed input since, so no new whole-suite run
Question or reason: -
Found, not fixed:
- test_plan_route.py retains the environment-dependence disclosed by T-075 V-06 and confirmed by T-083 V-05 (real machine registry via eligibility->limit_until); separate scope, unchanged
- ledger.py _write_atomic's unguarded os.replace retains the transient WinError 5 mode seen once in T-082's full suite; T-083's isolated rerun was 5/5 green; latent, unchanged
Proposed memory updates:
- session-log.md, 2026-10-18: T-084 carried the verified artifact onto t-084-backup-hold-carrier at fc2c37c (reset from 52a946d); the corrected scope declaration now covers the full inherited T-074+T-082 file set; scoped checks 20/0 + 12/0 green; next step is T-076 launch enforcement.
- known-issues.md, 2026-10-18: the T-082->T-084 authoring-defect pattern is answered by this contract - a carrier task's Allowed files must declare the carried base's full file set, not only the new commit's delta.
