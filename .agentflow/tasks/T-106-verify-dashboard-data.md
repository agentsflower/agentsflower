# T-106: Independently verify the roadmap dashboard data layer

Role: tester
Tool: devin
Stage: 5
Depends on: T-044
Verifies: T-044 @ 1d0895089d63a51e7b5987a98c34b449090f368f

## Goal

Independently evaluate the exact T-044 artifact
(1d0895089d63a51e7b5987a98c34b449090f368f) against every P-01..P-09 criterion
in its Task File, in a disposable checkout. The artifact adds the roadmap
data layer to .agentflow/dashboard/build.py (project-plan.md parser, stage
records joined with ledger/runtime evidence, schemaVersion-1 payload,
diagnostics, expanded --demo fixture), the README data contract, 21 new
dashboard tests, and 2.15.8 release metadata. Fresh session, not the
developer conversation. Same CLI per the human's Devin preference: Codex
and Claude CLIs are statically excluded in model-options.json; the observed
agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-044-dashboard-data.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...1d0895089d63a51e7b5987a98c34b449090f368f` in the disposable checkout
- .agentflow/dashboard/README.md (the declared data contract the payload must honor)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-044 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (P-01/P-02) The plan parser handles the real docs/project-plan.md (source order, fenced code, heading boundaries, raw text preserved) and the payload carries the documented stage record fields under schemaVersion:1 - verify against the README contract and the real build output, not the developer's summary.
- [ ] V-02: (P-03/P-04) Declared status, ledger counts and criterion evidence are three independent fields; zero-task stages total:0; stale Verifies SHA flagged; diagnostics carry sources/warnings/gaps/unmappedTaskIds; a bad plan cannot hide task data.
- [ ] V-03: (P-05/P-06) Evidence-ref validation rejects traversal/absolute/symlink escapes and non-http(s) URLs; attempts/routing/verify payload fields pass only allowlisted keys (no argv/env/pid/paths/quota); malformed records degrade to null + diagnostic, not a crash.
- [ ] V-04: (P-07/P-08) The --demo fixture exercises the named diagnostics and reads no canonical memory; the golden regression fixtures prove task fields are byte-identical to the pre-change build on identical inputs.
- [ ] V-05: (P-09) Both Checks pass verbatim on the exact SHA (`test_dashboard.py`, `build.py`, `build.py --demo`); the recorded full-suite evidence is reviewed; VERSION/AGENTS block/CHANGELOG agree at 2.15.8 with migration notes.
- [ ] V-06: The artifact is exactly one commit on t-044-dashboard-data; `git diff main...1d08950` stays inside T-044's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-07: Map all P-01..P-09 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`

## Execution bounds

Run the three Checks verbatim on the checked SHA; exercise the parser and
ref-validation against adversarial inputs inside disposable fixtures; audit
the payload allowlists for leaked unsafe fields. No code fixes, no
gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE with
basenames starting `T-106.`; put `evidence:` markers at line end followed
only by intended claim paths - never quote an `evidence:` marker inside
prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-07 plus `Verdict:`.

## Result
