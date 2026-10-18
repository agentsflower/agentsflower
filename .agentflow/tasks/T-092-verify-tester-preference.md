# T-092: Fast-path re-check of tester-independence preference and suite evidence

Role: tester
Tool: devin
Model: swe-2-high, effort=high
Stage: 5
Depends on: T-091
Verifies: T-091 @ 0bf4ac09fa08ef2c7cd77f6591993460511ebe07

## Goal

Fast-path independent re-check of the T-091 artifact at
0bf4ac09fa08ef2c7cd77f6591993460511ebe07 (T-085 precedent; scope narrowed
per the human's 2026-10-18 Option D decision in questions.md). The artifact
is 0ba5d37 (the T-078 scheduler/report layer) plus exactly one commit. The
routing machinery underneath was already independently deep-verified: T-075
on 5a6510c (assessment core), T-083 on fc2c37c (live backup-hold
admission), T-086 on 07fbeed (launch admission), T-088 on f6bc519 and
T-090 on 52b06aa (config alias + last-wins precedence). You do not repeat
that deep work. You confirm, in a fresh disposable checkout: the artifact
identity and scope, live proof of only the new prefer-scoped exemption
(K-02), that the recorded full-suite evidence is real, and the release
metadata. Fresh session, not the developer conversation. Same CLI per the
human's Devin preference; the Codex and Claude CLIs are reported without
resources and are excluded from assessments; observed agy holds remain
honored.

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

- [ ] V-01: (K-01) The disposable checkout HEAD is exactly 0bf4ac09fa08ef2c7cd77f6591993460511ebe07 with parent 0ba5d377f0deeae979588b23d8f29585b3a70cde; `git diff main...HEAD` stays inside T-091's Allowed files; `git diff 0ba5d37...HEAD` is only the prefer-exemption fix, the disclosed fixture repairs and the one-line CHANGELOG/metadata changes.
- [ ] V-02: (K-02) Prove live in the disposable checkout that a fresh assessment of a tester whose checked task ran on the preferred CLI can select that CLI's adequate option; that a live hold still excludes it; that the exclusion still applies to a non-preferred CLI and re-includes it when nothing else is eligible; and that adequacy still rules. Confirm the exemption is scoped to `prefer` membership, not hardcoded to devin.
- [ ] V-03: (K-03) The recorded full-suite evidence is real and belongs to this SHA (inspect the saved log tail .agentflow/tasks/.runtime/T-091.full-suite.txt: 424 tests, OK, 3 skipped); all three scoped Checks pass verbatim on the exact SHA; no live TypeSafe calls in tests.
- [ ] V-04: (K-04) VERSION/AGENTS/CHANGELOG agree at 2.15.4 with only the one-line addition; the inherited S-01..S-05 restatement is accurate (spot-check at least S-01's decide()/use_backup() gates and S-02's report fields against the code); T-040 not claimed complete.
- [ ] V-05: Map all K-01..K-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary. Evaluate whether the prefer-scoped exemption creates any hazard (e.g. a preferred CLI that is actually unusable for testers) and whether the test_approval/parallel/quota_groups fixture repairs are honest stubs rather than hidden behavior changes.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_tick.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_scheduler.py`
- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`

## Execution bounds

15-minute cap. This is a fast-path identity/scope/delta check leaning on
prior independent verifications, not a second deep review of the routing
machinery. Run the three scoped Checks verbatim on the checked SHA, probe
the prefer-exemption eligibility paths live in disposable fixtures, verdict
by evidence. No code fixes, no gratuitous whole-suite run. Save evidence in
AGENTFLOW_EVIDENCE with basenames starting `T-092.`; put `evidence:` markers
at line end followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-05 plus `Verdict:`.

## Result
