# T-109: Independently verify the roadmap view UI

Role: tester
Tool: devin
Stage: 5
Depends on: T-046
Verifies: T-046 @ 822c3ecff773e40427197d16098d8531703f0d95

## Goal

Independently evaluate the exact T-046 artifact
(822c3ecff773e40427197d16098d8531703f0d95) against every U-01..U-09 criterion
in its Task File, in a disposable checkout. The artifact emits
out/roadmap.html (three persisted layouts - Cards, Journey, Matrix - with
separate declared-status / local-task-counts / criterion-evidence facts,
drill-down into the shared task card, unmapped group, diagnostics card) and
adds the shared nav link; VERSION is 2.15.9. Fresh session, not the
developer conversation. Same CLI per the human's Devin preference: Codex
and Claude CLIs are statically excluded in model-options.json; the observed
agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-046-dashboard-ui.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...822c3ecff773e40427197d16098d8531703f0d95` in the disposable checkout
- .agentflow/dashboard/UI-RULES.md and the approved mockups (roadmap-a-cards.html, roadmap-b-journey.html, roadmap-c-matrix.html)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-046 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- Real render check: open the built out/roadmap.html (real and demo) at the UI-RULES widths the task names (at minimum 390 and a wide width) with whatever rendering tool is available on this host (headless Chrome/Edge if present; else a JS DOM stub like the developer used). Report what was actually rendered, not inferred.

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (U-01/U-02/U-03) The built page carries the shared nav/theme; every view shows stage cards with all three facts labeled separately (declared status, local task counts, exit-criteria evidence - never merged into one number); zero-task stages, recurring cycles, stale links and the unmapped group all render distinctly.
- [ ] V-02: (U-04/U-05) Drill-down shows allowlisted attempts/routing/gate records only (no argv/env/pid/paths/quota leaks in the rendered DOM or payload); diagnostics card is labeled a build snapshot with source freshness.
- [ ] V-03: (U-06/U-07) UI-RULES conformance at the named widths (single scroller, no horizontal overflow, filterbar doesn't slice the stage list) AND zero regression on the other pages (build out/ and confirm index/graph unchanged in structure, nav added everywhere).
- [ ] V-04: (U-08/U-09) No external fetch/dependency in the built page (offline self-contained); all Checks pass verbatim on the exact SHA; VERSION/AGENTS block/CHANGELOG agree at 2.15.9.
- [ ] V-05: Scope and integrity: exactly one commit on t-046-dashboard-ui; `git diff main...822c3ec` stays inside T-046's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-06: Map all U-01..U-09 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`

## Execution bounds

Run the Checks verbatim on the checked SHA; render/inspect the built pages
at the named widths (the task's Port allows a real browser if one exists);
grep the embedded payload/DOM for unsafe field leaks. No code fixes, no
gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE with
basenames starting `T-109.`; put `evidence:` markers at line end followed
only by intended claim paths - never quote an `evidence:` marker inside
prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result
