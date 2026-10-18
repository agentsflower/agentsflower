# T-075: Independently verify routing core recovery

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-074
Verifies: T-074 @ 5a6510c9b76201ccce35d1a10ce685be0d76a6e2

## Goal

Independently evaluate the exact T-074 artifact (5a6510c9b76201ccce35d1a10ce685be0d76a6e2)
against every R-01..R-05 criterion in its Task File, in a disposable checkout.
The artifact delivers the preserved T-040 routing assessment/admission core as
an API-only release; independently prove each claim rather than re-quoting
worker results. This is a fresh session, not the developer conversation. Same
CLI is necessary per the human's Devin preference: Codex worker sandbox writes
were environment-blocked on this machine; observed agy holds remain honored.
Never downgrade or invent available quota.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-074-routing-core-recovery.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-040-routing-enforcement.md (original policy)
- .agentflow/tools/route.py, .agentflow/tools/gate.py, .agentflow/tools/plan_route.py, .agentflow/tools/quota_groups.py
- .agentflow/tests/test_routing_core.py, .agentflow/tests/test_route.py
- .agentflow/docs/model-options.json, .agentflow/docs/typesafe.md, CHANGELOG.md (2.15.2 entry)
- The candidate diff `git diff main...5a6510c9b76201ccce35d1a10ce685be0d76a6e2` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-074 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040 worktree and its preserved drafts (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (R-01) The artifact is the preserved T-040 patch applied once on the stated base, at the checked SHA, in a clean tree; `git diff main...5a6510c9b76201ccce35d1a10ce685be0d76a6e2` stays inside the declared Allowed files; the T-040 worktree and original drafts are unchanged. Compare the inherited draft surface with the claimed implemented delta.
- [ ] V-02: (R-02) The persisted schema explicitly represents successful, blocked, low-confidence and failed/unavailable assessments bound to requirementsHash, and a changed requirements contract invalidates the record. Requirement-first selection holds: capability/effort adequacy filters before ordering, the configured floor then prefer ordering, adequate Devin options precede other CLIs. Probe missing/stale/low-confidence/failed as diagnosable admission blocks, not just test names.
- [ ] V-03: (R-03) The launch-side API T-076 will call exists and behaves: assessment_problems/admission/history/latest_assessment/backup_ok/log_admission. admission() evaluates the resolved model/effort identity after AGENTFLOW_<TOOL>_ARGS-style env overrides and refuses a header or env downgrade; a human routing exception is recorded distinguishably from Jev evidence; a backup below requirement or under a quota-group hold is refused. Reproduce at least the downgrade refusal and the exception-vs-Jev distinction live in the disposable checkout.
- [ ] V-04: (R-04) The draft regressions are repaired: the routing log/history directory follows the configured FLOW_ROOT per call (probe with a redirected root), and an inadequate backup is rejected where the draft once expected an inadequate Claude backup. Confirm no unit test makes real network calls (patched env/stand-ins only).
- [ ] V-05: (R-05) Both scoped Checks pass verbatim on the exact SHA; review the developer's recorded one full-suite run on this artifact (391/0/3-skipped) instead of repeating the whole suite; VERSION, the AGENTS version block and CHANGELOG agree at 2.15.2 and describe API-only delivery with launch enforcement pending T-076; T-040 is not claimed complete.
- [ ] V-06: Map all R-01..R-05 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified, never infer success from a green summary alone. Evaluate the developer's disclosure that test_plan_route.py now reads the real machine registry through eligibility->limit_until: record whether it is an environment-dependence defect and whether it passes on this machine today.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`
- `python -m unittest discover -s .agentflow/tests -p test_plan_route.py`

## Execution bounds

20-minute cap. Run scoped checks verbatim on the checked SHA, probe the
admission/exception/root-override paths live in disposable fixtures, give an
evidence-based verdict. No code fixes, no repeated broad architecture reads,
no gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`. The older
role example without colon/verdict is obsolete; do not omit explicit
per-criterion outcomes.

## Result
Outcome: completed
Verdict: partial
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (19 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_plan_route.py` -> pass (2 passed / 0 failed)
Criteria:
- V-01: pass - Disposable checkout HEAD=5a6510c9b76201ccce35d1a10ce685be0d76a6e2, clean tree. `git apply --check` of the preserved patch on the stated base b40c934 passes and applies cleanly (4 files, +515/-153). base+patch vs HEAD: gate.py, plan_route.py, quota_groups.py identical; route.py differs only by the claimed +20/-10 delta (import-time RT_DIR -> per-call _rt_dir(), accurate selectionReason + print). `git diff main...5a6510c` touches 11 files, all inside T-074 Allowed files. Developer worktree unchanged: recomputed gate baseline (HEAD sha + status) = e0ba64d7... = the launcher's recorded baseline. T-040 worktree drafts unchanged: its `git diff --stat` is identical to the patch (+515/-153) and the patch reverse-checks against it. evidence: .agentflow/tasks/.runtime/T-075.evidence/T-075.v01-patch-stat.txt .agentflow/tasks/.runtime/T-075.evidence/T-075.v01-route-delta.txt
- V-02: pass - schemaVersion 1 `assessment` events bound to requirementsHash persist ok/blocked/low-confidence/failed (route.py:376-455, T-075.v02-p6-p7-output.txt: blocked/low-confidence/failed each surface a diagnosable block; changed contract -> "the recorded assessment is stale" in T-075.v03-v04-probe-output.txt P5). Adequacy (effort ceiling via option_ceiling incl. declared `tier`, plus max_complexity cap) filters candidates before ordering; order is floor -> prefer -> Jev rank: probed ['devin-swe-2','devin-astra','codex-ultra','agy-flash'] against probabilities {codex 0.9, agy 0.7, swe-2 0.05, astra 0.3} - adequate Devin options precede other CLIs. Missing record -> diagnosable block (P6). Verified by live probe and the 19-test focused suite, not just claimed names. evidence: .agentflow/tasks/.runtime/T-075.evidence/T-075.v02-p6-p7-output.txt .agentflow/tasks/.runtime/T-075.evidence/T-075.v03-v04-probe-output.txt
- V-03: partial - The launch-side API exists and was exercised live (T-075.v03-v04-probe-output.txt): header downgrade refused ("below the recorded requirement >= high", P1a); env downgrade refused when the header names no model (AGENTFLOW_DEVIN_ARGS --model swe-2-medium, P1b); stronger env model admitted with deviation=True (P1c); a `Routing exception:` line returns source=human-exception and log_admission writes event='human-exception' carrying reason+overrode, distinct from event='admission'/source='jev' (P2); backup_ok refuses below-requirement backups including another tool's weaker model (P3). Gap: backup_ok does not check quota-group holds - under a patched machine_capacity.limit_until the adequate backup is still admitted (P3: (True, '')). Holds are honored at assessment time (held options never enter candidates, hence never the recorded backup; diagnosed via adequateHeld), but a backup whose group becomes held after assessment is not refused by the artifact's own launch-side API; only the launcher's separate resource check would catch it (T-076).
- V-04: pass - _rt_dir() resolves FLOW_ROOT per call; live redirect probe lands T-007.route.json under the relocated root and history() reads it back (P4). The obsolete inadequate-Claude-backup expectation is replaced by the adequate devin-max assertion with claude named in `inadequate` (test_route.py diff; suite green). No real network in unit tests: both suites serve a 127.0.0.1 stand-in via TYPESAFE_BASE_URL; subprocess envs strip TYPESAFE_*/AGENTFLOW_* and set a temp AGENTFLOW_MACHINE_STATE_DIR + AGENTFLOW_ROUTE_ASSUME_CLI_AVAILABLE=1.
- V-05: pass - All three scoped Checks pass verbatim on the exact SHA (outputs: .agentflow/tasks/.runtime/T-075.evidence/T-075.check-test_route.txt, T-075.check-test_routing_core.txt, T-075.check-test_plan_route.txt). The developer's one full-suite run is recorded in .agentflow/tasks/.runtime/T-074.1.log ("Full suite green: 391 tests, 3 skipped"), matching the Result. VERSION=2.15.2, AGENTS.md block=2.15.2, CHANGELOG 2.15.2 entry states "API-only: launch enforcement is still pending, T-040 is not complete".
- V-06: pass - R-01..R-05 mapped to concrete evidence above. The developer's test_plan_route.py disclosure evaluated: route.eligibility->live_reason->machine_capacity.limit_until reads the real %LOCALAPPDATA%\AgentFlow\machine\registry.json while only cli_usable is patched - a genuine environment-dependence defect (a future codex/devin hold would exclude options and fail the assertions). It passes on this machine today (2/2; the registry holds are agy + agy:agy-gemini expiring ~2026-10-21, which do not intersect the test's codex/devin options). test_plan_route.py was outside T-074's Allowed files, so non-repair in scope is consistent.
New defects (outside the task):
- backup_ok ignores live quota holds (see V-03 gap): adequate-but-held backups are admitted; holds are only excluded at assessment time and by the launcher's separate resource check. Candidates for T-076: consult machine_capacity.limit_until / live_reason for the backup's tool+quota_group.
- test_plan_route.py environment dependence via the real machine registry (latent; passes today).
Cannot verify, needs:
- none
Proposed memory updates:
- known-issues.md, 2026-10-18: backup_ok does not consult quota-group holds - an adequate backup held after assessment is admitted by the artifact's API (T-075 P3 probe); assessment-time selection and the launcher resource check are the only hold guards until T-076.
- session-log.md, 2026-10-18: T-075 verified T-074 @5a6510c with live probes; Verdict partial on the backup-hold facet of V-03; scoped checks 12/0 + 19/0 + 2/0 green; artifact confirmed = preserved patch applied once + the recorded route.py delta.
