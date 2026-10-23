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

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (36 passed / 0 failed, on 822c3ec detached+clean)
- `python .agentflow/dashboard/build.py` -> pass (92 tasks, 6 stages, 93 dependencies, 21 successors, 215 commits -> out/)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out/ [DEMO DATA])
Criteria:
- V-01: pass - real render via chrome-headless-shell (Chromium 153): all three views (cards/journey/matrix) render every declared stage; per-stage facts carry separate labels "Declared status" / "Local tasks" / "Exit-criteria evidence" (7x3 fact labels counted); shared nav [Overview, Gantt & timeline, Roadmap], Built stamp, DEMO badge, theme toggle works; demo DOM shows "No local tasks" x13, recurring cycle block, stalemark x3, "not tracked per criterion" x7, Unmapped group rendered in all views, duplicate stage id rendered as two flagged cards, "declared status disagrees with the ledger" warnings, ext-marked external refs; stage expansion exposes full exit-criteria text + evidence table + task rows drilling into the shared task card evidence: .agentflow/tasks/.runtime/T-109.evidence/T-109.render-demo-390.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-demo-1280.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.dom-demo.html, .agentflow/tasks/.runtime/T-109.evidence/T-109.dom-real.html, .agentflow/tasks/.runtime/T-109.evidence/T-109.filter-demo.json
- V-02: pass - drill-down renders allowlisted records only: demo T-103 shows 2 attempts (requested->effective incl. unknown identity), routing assessment/floor/selection/availability + admission event; T-102 shows gate record reduced to cmd+exit; real T-046 (with .runtime copied into this disposable checkout) shows 3 real attempts with stopReason/timeout and 3 jev assessments, "GATE EVIDENCE not recorded"; payload scan of the real build found 222 non-null runtime sections with zero banned keys/substrings (argv/env/pid/pidStart/quota/quotaGroup/machineLease/workdir/toolArgsHash/probeHash/prompt/launch/log/requestId/usage/candidates/backup internals/absolute paths); diagnostics card titled "Diagnostics - build snapshot" carries source mtime+fingerprint table, freshnessNote, warnings, gaps, unmapped list evidence: .agentflow/tasks/.runtime/T-109.evidence/T-109.drill-demo.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.drill-real.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.payload-allowlist-scan.txt
- V-03: pass - zero page-level horizontal overflow in every view at 390/1280/1920/3840 (scrollWidth==clientWidth on demo and on real at >=1280; the one 390px real-page overflow of 43px is the shared .topbar h1 fed by the 34-char disposable-checkout folder name - identical on the untouched index/graph pages and absent when project name is short, i.e. pre-existing common.css behavior, not this artifact's layout); live filter probe: search "t-103" -> "Showing 1 of 8 tasks - stage list unaffected", all 8 stage cards retained, 1 chip, Reset restores; index/graph render unchanged structure with the new nav and zero console errors; single central scroller .stagecol, side rails reuse the existing pages' .side convention evidence: .agentflow/tasks/.runtime/T-109.evidence/T-109.render-real-390.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-real-1280.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-real-1920.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-real-3840.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-demo-1280.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-demo-1920.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.render-demo-3840.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.overflow-real-390.json, .agentflow/tasks/.runtime/T-109.evidence/T-109.scroll-out-real-1600.json
- V-04: pass - all built pages (real+demo, all three) contain zero external references (no src=/href= http, fetch, XMLHttpRequest, import(), link, script src, @import, CDN hosts); the only http(s) strings are payload data values rendered as <code> text per the contract; all three Checks pass verbatim on the exact SHA 822c3ec; VERSION=2.15.9, AGENTS block=2.15.9, CHANGELOG has a dated 2.15.9 entry with migration notes - all in the same diff evidence: .agentflow/tasks/.runtime/T-109.evidence/T-109.check1-test_dashboard.txt, .agentflow/tasks/.runtime/T-109.evidence/T-109.check2-build.txt, .agentflow/tasks/.runtime/T-109.evidence/T-109.check3-build-demo.txt, .agentflow/tasks/.runtime/T-109.evidence/out-demo/T-109.out-demo-roadmap.html, .agentflow/tasks/.runtime/T-109.evidence/out-real/T-109.out-real-roadmap.html
- V-05: pass - git rev-list main..t-046-dashboard-ui = exactly 1 commit (822c3ec, equal to the Verifies SHA and the branch tip); diff name-only = VERSION, dashboard/README.md, build.py, common.js, roadmap.css, roadmap.js, roadmap_template.html, test_dashboard.py, AGENTS.md (AgentFlow-block version line only), CHANGELOG.md - all inside T-046 Allowed files; integrity recomputed per gate.py baseline: T-109 header taskHash 98b617a8 == baseline, checkedRef t-046-dashboard-ui == 822c3ec, checkedTree bfa67986 == baseline (developer worktree clean at the SHA), T-046 checkedFileHash d5b01e79 == baseline
- V-06: pass - mapping U-01/U-02/U-03 -> V-01 (nav/chrome, per-stage three-fact labels, all distinct render states exercised live), U-04/U-05 -> V-02 (allowlisted attempts/routing/gate in drill-down on real + demo records; build-snapshot diagnostics), U-06/U-07 -> V-03 (widths, single scroller, filter isolation, no regression on other pages, themes, keyboard handlers present in code), U-08/U-09 -> V-04 (self-contained offline build, Checks verbatim, version trio), V-05 -> scope/integrity; every verdict backed by executed probes on the real artifact in this disposable checkout, none inferred from the developer's green summary
New defects (outside the task):
- pre-existing, not introduced by T-046: .topbar h1{white-space:nowrap} (common.css, unchanged) overflows the page by ~43px at 390px when the project folder name is long (this worktree name is 34 chars); index.html and graph.html built from unchanged code show the identical overflow; with a short project name no element overflows. Candidate fix: min-width:0 + ellipsis on .topbar h1.
- confirmed, already disclosed by the developer and documented in the 2.15.9 migration notes: snapshot.py versions only the pre-existing source set; roadmap_template.html/roadmap.css/roadmap.js are not covered by save/restore.
- cosmetic, consistent with the existing pages: the roadmap side rails can scroll independently when content exceeds rail height (.side{overflow:auto} - the same rule the Overview/Gantt pages already apply), so "exactly one central block scrolls" holds for the center region but side overflow is shared established behavior.
Cannot verify, needs:
- real keyboard focus traversal (Tab order) was not simulated in headless shell; keyboard support is evidenced at code level (tabindex, role=button, Enter/Space handlers, :focus-visible outlines).
- production/staging rendering n/a (local target; offline pages only).
Proposed memory updates:
- consider a bounded follow-up: snapshot.py should cover the new roadmap_* sources (already flagged in the 2.15.9 CHANGELOG); the h1 nowrap overflow at narrow widths is worth the same small fix.
