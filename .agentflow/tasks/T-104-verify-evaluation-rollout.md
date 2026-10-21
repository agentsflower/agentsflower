# T-104: Fast-path re-check of evaluation scenarios and Stage 5 release metadata

Role: tester
Tool: devin
Stage: 5
Depends on: T-038
Verifies: T-038 @ d4c6e8daf318e943f0df098612ca58a5186b4e04

## Goal

Fast-path re-check of the exact T-038 artifact
(d4c6e8daf318e943f0df098612ca58a5186b4e04) in a disposable checkout. Re-scoped
after two low-confidence Jev assessments (complexity ~1.92, effort conf ~0.36)
- the T-085/T-092 precedent: a narrower contract that still proves the
artifact on its own evidence rather than a deep critical review of every
assertion. The artifact adds test_scenarios.py (four disposable-repo
lifecycle/recovery scenarios through the real tools + a migration proof + an
opt-in real-platform case), the Stage 5 evidence map, and 2.15.7 release
metadata. Fresh session, not the developer conversation. Same CLI per the
human's Devin preference: Codex and Claude CLIs are statically excluded in
model-options.json; the observed agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-038-evaluation-rollout.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...d4c6e8daf318e943f0df098612ca58a5186b4e04` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-038 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] W-01: Scope and integrity: the artifact is exactly one commit on t-038-evaluation-rollout; `git diff main...d4c6e8d` stays inside T-038's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] W-02: The scenario module is not vacuous: it drives the real run_task.py/gate.py/accept.py/ledger.py against disposable git repositories (read the fixture code - no product fakes standing in for the machinery under test); simulated workers are honestly labeled; the real-platform case is opt-in (`AGENTFLOW_REAL_PLATFORM`) and never faked; at least two scenario tests assert on concrete lifecycle state, not just "no exception".
- [ ] W-03: (V-02) The migration test builds an old-version fixture, runs the real install.py --update, and asserts open-task state (ledger rows, Task Files, project-owned files) survives - verify the assertions exist and ran.
- [ ] W-04: (V-03/V-04) Spot-check honesty of the release metadata: VERSION and the AGENTS version block read 2.15.7; the CHANGELOG 2.15.7 entry exists with migration notes; release-validation.md keeps the run-39026298541 windows/macos gap (it did not get quietly closed).
- [ ] W-05: (V-05) T-038's Checks pass verbatim on the exact SHA, plus `python -m unittest discover -s .agentflow/tests -p test_scenarios.py` in isolation.
- [ ] W-06: Map the above to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary. If a deeper concern surfaces that this narrow contract can't settle, report it as `unverified` with the reason instead of stretching the review.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_scenarios.py`
- `python -m unittest discover -s .agentflow/tests -p test_install.py`
- `python .agentflow/tests/check_package.py`

## Execution bounds

Run the scoped checks verbatim on the checked SHA; read the scenario
fixture enough to prove it is not vacuous - this is a bounded re-check, not
a line-by-line audit of 700 lines of test code. No code fixes, no gratuitous
whole-suite run. Save evidence in AGENTFLOW_EVIDENCE with basenames starting
`T-104.`; put `evidence:` markers at line end followed only by intended
claim paths - never quote an `evidence:` marker inside prose (the validator
reads it as a claim).
Use the current gate format in Result: one `- W-01: pass - <evidence>` (or
partial/unverified/fail) line for each W-01..W-06 plus `Verdict:`.

## Result
