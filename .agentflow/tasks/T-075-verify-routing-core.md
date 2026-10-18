# T-075: Independently verify routing core recovery

Role: tester
Tool: devin
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

- [ ] V-01 (R-01): The artifact is the preserved T-040 patch applied once on the stated base, at the checked SHA, in a clean tree; `git diff main...5a6510c9b76201ccce35d1a10ce685be0d76a6e2` stays inside the declared Allowed files; the T-040 worktree and original drafts are unchanged. Compare the inherited draft surface with the claimed implemented delta.
- [ ] V-02 (R-02): The persisted schema explicitly represents successful, blocked, low-confidence and failed/unavailable assessments bound to requirementsHash, and a changed requirements contract invalidates the record. Requirement-first selection holds: capability/effort adequacy filters before ordering, the configured floor then prefer ordering, adequate Devin options precede other CLIs. Probe missing/stale/low-confidence/failed as diagnosable admission blocks, not just test names.
- [ ] V-03 (R-03): The launch-side API T-076 will call exists and behaves: assessment_problems/admission/history/latest_assessment/backup_ok/log_admission. admission() evaluates the resolved model/effort identity after AGENTFLOW_<TOOL>_ARGS-style env overrides and refuses a header or env downgrade; a human routing exception is recorded distinguishably from Jev evidence; a backup below requirement or under a quota-group hold is refused. Reproduce at least the downgrade refusal and the exception-vs-Jev distinction live in the disposable checkout.
- [ ] V-04 (R-04): The draft regressions are repaired: the routing log/history directory follows the configured FLOW_ROOT per call (probe with a redirected root), and an inadequate backup is rejected where the draft once expected an inadequate Claude backup. Confirm no unit test makes real network calls (patched env/stand-ins only).
- [ ] V-05 (R-05): Both scoped Checks pass verbatim on the exact SHA; review the developer's recorded one full-suite run on this artifact (391/0/3-skipped) instead of repeating the whole suite; VERSION, the AGENTS version block and CHANGELOG agree at 2.15.2 and describe API-only delivery with launch enforcement pending T-076; T-040 is not claimed complete.
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
