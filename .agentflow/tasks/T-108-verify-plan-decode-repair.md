# T-108: Independently verify the malformed-plan repair

Role: tester
Tool: devin
Stage: 5
Depends on: T-107
Verifies: T-107 @ 096040e406d225ee96bd7fcd39a6785e0291945d

## Goal

Independently evaluate the exact T-107 artifact
(096040e406d225ee96bd7fcd39a6785e0291945d) against every R-01..R-04 criterion
in its Task File, in a disposable checkout. The branch carries the verified
T-044 data-layer artifact (1d08950, reset --hard) plus one repair commit:
read_plan catches (OSError, ValueError) so a non-UTF-8 plan degrades to the
`unreadable` diagnostic instead of crashing the build. Fresh session, not
the developer conversation. Same CLI per the human's Devin preference: Codex
and Claude CLIs are statically excluded in model-options.json; the observed
agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-107-plan-decode-repair.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-106-verify-dashboard-data.md (the V-02 finding and its repro, plus the T-104/T-106 evidence chain this repair must satisfy)
- The candidate diff `git diff main...096040e406d225ee96bd7fcd39a6785e0291945d` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-107 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (R-01) Reproduce the T-106 defect live in the disposable checkout: write a non-UTF-8 (e.g. b"\xff\xfe") project-plan.md, run `python .agentflow/dashboard/build.py` - exit 0, task data still emitted, plan source `unreadable` with the fingerprint kept; the regression test exists and fails against the pre-repair code (negative control).
- [ ] V-02: (R-02) The fix is scoped to the plan reader: parse/join behavior, missing-plan and OSError paths, and all pre-existing dashboard tests unchanged; no other reader touched.
- [ ] V-03: (R-03/R-04) All four of T-107's Checks pass verbatim on the exact SHA; CHANGELOG 2.15.8 gained only the hardening line; VERSION stays 2.15.8.
- [ ] V-04: The artifact is exactly the verified 1d08950 plus one repair commit (`git rev-list main..096040e` = 2 commits: 1d08950 then 096040e); `git diff main...096040e` stays inside T-107's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-05: Confirm the T-106 evidence chain still holds on this SHA: the data-layer payload fields, ref validation, allowlists and demo fixture behave as T-106 verified (spot-re-run its probe areas - the repair must not have regressed them).
- [ ] V-06: Map all R-01..R-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`

## Execution bounds

Run the Checks verbatim on the checked SHA; reproduce the defect repro
live (negative control against the pre-repair reader); spot re-verify the
T-106 probe areas the repair could plausibly regress. No code fixes, no
gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE with
basenames starting `T-108.`; put `evidence:` markers at line end followed
only by intended claim paths - never quote an `evidence:` marker inside
prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result
