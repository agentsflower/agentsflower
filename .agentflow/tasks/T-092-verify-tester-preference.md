# T-092: Independently verify tester-independence preference and suite evidence

Role: tester
Tool: devin
Model: gpt-6-astra-xhigh
Stage: 5
Depends on: T-091
Verifies: T-091 @ 0bf4ac09fa08ef2c7cd77f6591993460511ebe07

## Goal

Independently evaluate the exact T-091 artifact
(0bf4ac09fa08ef2c7cd77f6591993460511ebe07) against every K-01..K-04 criterion
in its Task File, in a disposable checkout. The artifact carries the whole
T-078 scheduler/report artifact (0ba5d37, rejected on two residuals) plus one
commit closing them: the assessment-time tester-independence exclusion no
longer removes an adequate option on the configured preferred CLI, and the
required full suite is recorded. Prove each claim; do not re-quote worker
results. Fresh session, not the developer conversation. Same CLI per the
human's Devin preference: Codex worker sandbox writes were
environment-blocked on this machine; observed agy holds remain honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-091-tester-independence-preference.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-078-routing-scheduler-integration.md (the residuals this closes)
- .agentflow/tools/route.py (route()/avoid/prefer), .agentflow/docs/model-options.json (prefer/floor)
- .agentflow/tests/test_routing_core.py, test_routing_scheduler.py, test_tick.py
- The candidate diff `git diff 0ba5d37...0bf4ac09fa08ef2c7cd77f6591993460511ebe07` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-091 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040, T-074, T-076, T-082 and T-078 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (K-01) The artifact is exactly 0ba5d37 plus one commit; `git diff 0ba5d37...HEAD` and `git diff main...HEAD` stay inside T-091's Allowed files; everything else is byte-identical to what T-078 produced.
- [ ] V-02: (K-02) Prove live in the disposable checkout that a fresh assessment of a tester whose checked task ran on the preferred CLI can select that CLI's adequate option; that a live hold still excludes it; that the exclusion still applies to a non-preferred CLI and re-includes it when nothing else is eligible; and that adequacy still rules. Confirm the exemption is scoped to `prefer` membership, not hardcoded to devin.
- [ ] V-03: (K-03) The recorded full-suite evidence is real and belongs to this SHA (inspect the saved log tail: 424 tests, OK, 3 skipped); all three scoped Checks pass verbatim on the exact SHA; no live TypeSafe calls in tests.
- [ ] V-04: (K-04) VERSION/AGENTS/CHANGELOG agree at 2.15.4 with only the one-line addition; the inherited S-01..S-05 restatement is accurate (spot-check at least S-01's decide()/use_backup() gates and S-02's report fields against the code); T-040 not claimed complete.
- [ ] V-05: Map all K-01..K-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary. Evaluate whether the prefer-scoped exemption creates any hazard (e.g. a preferred CLI that is actually unusable for testers) and whether the test_approval/parallel/quota_groups fixture repairs are honest stubs rather than hidden behavior changes.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Execution bounds

20-minute cap. Run scoped checks verbatim on the checked SHA, probe the
eligibility paths live in disposable fixtures, verdict by evidence. No code
fixes, no gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE
with basenames starting `T-092.`; put `evidence:` markers at line end
followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-05 plus `Verdict:`.

## Result
