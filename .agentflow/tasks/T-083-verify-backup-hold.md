# T-083: Independently verify backup hold admission repair

Role: tester
Tool: devin
Model: gpt-6-astra-xhigh
Stage: 5
Depends on: T-082
Verifies: T-082 @ fc2c37cc7144d7a5788ac6ee797f4b1020d34025

## Goal

Independently evaluate the exact T-082 artifact
(fc2c37cc7144d7a5788ac6ee797f4b1020d34025) against every S-01..S-04 criterion
in its Task File, in a disposable checkout. The artifact is the preserved
T-074 routing core at 5a6510c plus one commit repairing `backup_ok` to
consult the live machine-registry quota-group hold at call time. Prove each
claim independently; do not re-quote worker results. This is a fresh session,
not the developer conversation. Same CLI per the human's Devin preference
(T-075 precedent): Codex worker sandbox writes were environment-blocked on
this machine; observed agy holds remain honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-082-backup-hold-admission.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-075-verify-routing-core.md (the partial verdict this repair answers)
- .agentflow/tasks/.runtime/T-075.evidence/T-075.v03-v04-probe-output.txt (the original gap probe)
- .agentflow/tools/route.py, .agentflow/tools/machine_capacity.py, .agentflow/tools/quota_groups.py
- .agentflow/tests/test_routing_core.py, .agentflow/tests/test_route.py
- The candidate diff `git diff 5a6510c...fc2c37cc7144d7a5788ac6ee797f4b1020d34025` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-082 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040 and T-074 worktrees and their preserved drafts (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (S-01) The artifact is exactly 5a6510c plus one commit: in the disposable checkout at fc2c37c, `git diff 5a6510c...HEAD` touches only route.py and test_routing_core.py inside T-082's Allowed files; everything else is byte-identical to what T-075 verified at 5a6510c.
- [ ] V-02: (S-02) `backup_ok` consults the live machine-registry hold at call time for the backup's tool+quota_group: reproduce live in the disposable checkout that a post-assessment group hold is refused with a diagnosable reason, a tool-wide hold is refused, an unrelated group/tool hold does not block, an unheld adequate backup is admitted, and a below-requirement backup is still refused. No new network calls.
- [ ] V-03: (S-03) The regression test actually exercises the post-assessment ordering (hold created after the ok assessment record) against a disposable registry, and the pre-existing backup test is pinned away from the real machine registry - confirm neither test can silently pass against this machine's live registry.
- [ ] V-04: (S-04) Both scoped Checks pass verbatim on the exact SHA; the recorded full-suite run (392/1 transient WinError-5 flake/3 skipped, isolated rerun green) is reviewed rather than repeated; VERSION/AGENTS/CHANGELOG agree at 2.15.2 and still describe API-only delivery with launch enforcement pending T-076; T-040 is not claimed complete.
- [ ] V-05: Map all S-01..S-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer success from a green summary. Evaluate the developer's "Found, not fixed" disclosures (test_approval WinError 5 flake; test_plan_route.py real-registry dependence): record whether either is a defect of this artifact and whether it reproduces today.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`
- `python -m unittest discover -s .agentflow/tests -p test_route.py`

## Execution bounds

20-minute cap. Run scoped checks verbatim on the checked SHA, probe the
call-time hold paths live in disposable fixtures (temp
AGENTFLOW_MACHINE_STATE_DIR), give an evidence-based verdict. No code fixes,
no repeated broad architecture reads, no gratuitous whole-suite run. Save
evidence in AGENTFLOW_EVIDENCE with basenames starting `T-083.`; put
`evidence:` markers at line end followed only by intended claim paths - path
names inside prose are mentions, not claims.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-05 plus `Verdict:`. The older
role example without colon/verdict is obsolete; do not omit explicit
per-criterion outcomes.

## Result

Outcome: completed
Verdict: pass

Checked artifact: fc2c37cc7144d7a5788ac6ee797f4b1020d34025 in the launcher-provided disposable checkout, independently of the developer session.

Checks:

- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (20 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.check-test_routing_core.txt
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (12 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.check-test_route.txt
- Additional targeted disclosure check: `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (5 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.check-test_approval.txt
- Independent probe -> pass: 11 backup cases, both backup tests instrumented for fixture isolation, regression negative control, and current-hold/controlled-hold planning comparisons. The negative control and controlled planning failures are expected evidence, not failures of the repair. evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.verify.py

Criteria:

- V-01: pass - S-01: HEAD is the exact requested SHA, its direct parent is 5a6510c9b76201ccce35d1a10ce685be0d76a6e2, and the range contains exactly one commit. The clean checkout differs only in route.py and test_routing_core.py, both allowed. Git tree comparison proves the other 183 of 185 entries have identical modes/types/blob IDs. The product delta adds only the local hold lookup after adequacy validation. evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.v01-artifact.txt .agentflow/tasks/.runtime/T-083.evidence/T-083.candidate.diff
- V-02: pass - S-02: persisted an ok assessment before any registry existed, then changed only the disposable registry between calls. A fresh matching group hold and a tool-wide hold both refuse with the option name and expiry; another group on the same tool, the same group name on another tool, and an unrelated tool-wide hold permit admission. Unheld/expired/removed holds admit the adequate backup; below-requirement remains refused. Env-selected group lookup and explicit-model precedence also pass. The assessment bytes remain unchanged throughout; network guards observe zero calls. evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.v02-live-probe.txt
- V-03: pass - S-03: instrumented both actual backup tests with a poisoned ambient registry and a guard that rejects every state-directory access outside each test's own temporary fixture. Both pass; the new test records ok before the first registry lookup, which sees the newly created devin:devin hold. Neither test accesses the ambient/live registry or network. Running the exact 5a6510c backup_ok function in memory makes the new regression fail at its post-assessment refusal assertion, proving it detects the original gap. Product files were not changed for this control. evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.v03-isolation.txt
- V-04: pass - S-04: both scoped Checks pass verbatim at the exact SHA. Reviewed the canonical T-082 Result and launcher recording of the single broad run: 392 run / 1 failure / 3 skipped, followed by an isolated 5/5 approval rerun. These are narrative recordings, not raw unittest stdout; the broad run is not claimed green and was not repeated. S-04 requires that run to be recorded, alongside green scoped Checks. Local VERSION, AGENTS and CHANGELOG agree at 2.15.2; the release explicitly remains API-only, launch enforcement awaits T-076, and T-040 is not complete. evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.v04-recorded-suite-and-release.txt .agentflow/tasks/.runtime/T-083.evidence/T-083.check-test_routing_core.txt .agentflow/tasks/.runtime/T-083.evidence/T-083.check-test_route.txt
- V-05: pass - S-01..S-04 map to V-01..V-04 above with independent behavioral and artifact evidence. Evaluated both disclosures: test_plan_route retains a real test-isolation defect in this artifact, inherited unchanged from the base. It passes 2/2 against a disposable snapshot of today's machine holds (agy and agy:agy-gemini); adding a disposable codex hold reproduces one assertion failure and one NoDecision error. The live registry was read only. The reported approval WinError 5 did not reproduce today (5/5); ledger.py and test_approval.py are also unchanged from the base, and ledger's unguarded os.replace retains the reported failure mode. Neither disclosure is introduced by T-082 or contradicts this scoped repair. evidence: .agentflow/tasks/.runtime/T-083.evidence/T-083.v05-disclosures.txt .agentflow/tasks/.runtime/T-083.evidence/T-083.check-test_approval.txt

New defects (outside the task):

- None newly discovered. Confirmed the previously disclosed planning-test dependence; retain it for a separate fix.
- Retain the reported intermittent ledger replacement failure as an inherited robustness issue. Today's passing rerun does not establish that it is eliminated.

Cannot verify, needs:

- No requested criterion is blocked. The original full-suite traceback and the intermittent Windows failure's underlying cause were not independently available/reproduced; the review above distinguishes the recorded report from today's observations.

Proposed memory updates:

- Record T-083 pass for T-082 at fc2c37c: the post-assessment backup-hold gap is independently verified repaired, with 20/20 and 12/12 scoped checks.
- Keep launch integration pending T-076 and T-040 incomplete. Preserve the planning-test isolation issue and intermittent ledger replacement issue as separate follow-up items.
