# T-105: Re-test the T-038 full-suite criterion on a flaky host

Role: tester
Tool: devin
Stage: 5
Depends on: T-038
Verifies: T-038 @ d4c6e8daf318e943f0df098612ca58a5186b4e04
Resume: .agentflow/tasks/.runtime/T-104.evidence

## Goal

Environment re-test, not a product re-review: T-104 independently verified
T-038 @ d4c6e8d and gave `Verdict: partial` solely because the verbatim full
suite flaked twice with a nondeterministic PermissionError WinError 5 on
`os.replace` of `%TEMP%`-fixture `tasks.md` (a different victim test each run,
in files outside the diff, each passing standalone - the documented Windows
file-lock flake). Every other T-038 criterion was already `pass` in T-104.
Redo only the missing piece: a clean full-suite run on the exact SHA in a
disposable checkout. Fresh session, not the developer conversation. Same CLI
per the human's Devin preference: Codex and Claude CLIs are statically
excluded in model-options.json; the observed agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-038-evaluation-rollout.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-104-verify-evaluation-rollout.md (the partial verdict and its evidence - resume from it, do not redo it)
- .agentflow/state/known-issues.md (the documented os.replace flake entries)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-038/T-104 Task Files above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: `python -m unittest discover -s .agentflow/tests` passes verbatim (exit 0) on the exact SHA d4c6e8d in the disposable checkout. If a run fails only on a lone nondeterministic os.replace WinError-5 in a %TEMP% fixture test (the documented flake signature: different victim, outside the diff, passes standalone), rerun the same command verbatim until it passes; record every attempt. A failure with any other signature is a real verdict fail.
- [ ] R-02: Carry the T-104 evidence chain forward honestly: your Result references the earlier evidence folder for the already-verified criteria; no criterion is re-verified and none is silently dropped.

## Checks

- `python -m unittest discover -s .agentflow/tests`

## Execution bounds

Only the suite rerun - T-104 already did the review. Do not re-run
test_scenarios.py or re-audit the diff. Save evidence in AGENTFLOW_EVIDENCE
with basenames starting `T-105.`; put `evidence:` markers at line end
followed only by intended claim paths - never quote an `evidence:` marker
inside prose (the validator reads it as a claim).
Use the current gate format in Result: one `- R-01: pass - <evidence>` (or
partial/unverified/fail) line for each R-01..R-02 plus `Verdict:`.

## Result
