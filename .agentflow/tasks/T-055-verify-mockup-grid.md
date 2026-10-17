# T-055: Independently verify roadmap mockup grid fix

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-054
Verifies: T-054 @ 11569404c9437612d6b8f862efa2df19309c15d0

## Goal

Independently evaluate the exact T-054 artifact (2.13.2 mockup chrome fix)
against every G-01..G-07 criterion in its Task File, in a disposable checkout.
Never repair the checked artifact; report the worst criterion as the verdict.
This fix is user-visible: measure with a real browser like the developer did.

Attempt state note: attempt 1 completed the full independent review (verdict
pass, rich measured evidence in .runtime/T-055.evidence/) and its Result is in
this file; the attempt record shows 'error' only because the checked task's
contract file changed mid-flight (review-isolation guard fired on a
coordinator contract correction, not on artifact drift - the checked SHA is
unchanged). Your job on this attempt: confirm the written Result stands on the
exact SHA 11569404c9437612d6b8f862efa2df19309c15d0 and the checked artifact is
untouched, keep the Result accurate, and exit - do not redo the full probe
matrix.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-054-mockup-grid-fix.md (contract + Result - its measured boxes are the claim to re-verify)
- .agentflow/dashboard/UI-RULES.md (A3 layout rules)
- The candidate diff `git diff main...11569404c9437612d6b8f862efa2df19309c15d0` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-054 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] M-01: Independently reproduce the measured wide layout on the exact SHA with a real browser (headless Chrome or equivalent installed tool): at 1280 and 1920 for all three variants header/filter/chosen rows span full width, left rail + center stages + right diagnostics sit in their columns, center is nonempty, no implicit row hides content below the fold. Record your own bounding boxes - do not quote the worker's numbers.
- [ ] M-02: Confirm at 390 and 1100 the stacked layout is usable with no horizontal scroll on all three variants; at 1101 the wide layout engages correctly (the breakpoint edges).
- [ ] M-03: The three committed HTMLs are regenerated outputs (diff the checked-in files against fresh `mockups/build.py` output - they must be identical; output-only edits would mismatch).
- [ ] M-04: Product dashboard unchanged: `build.py` and `build.py --demo` produce identical output to pre-change on the same data; no product file touched (diff shows only mockups/, VERSION, AGENTS version line, CHANGELOG).
- [ ] M-05: Interaction: theme toggle + persistence, filter dropdowns actually painted (the mkFilters fb.render() bug), search + Reset all counts, task-card drill-down - prove by exercising, not reading.
- [ ] M-06: All claimed checks pass on the exact SHA; VERSION 2.13.2 / AGENTS block / CHANGELOG migration notes in sync; found-not-fixed claims truthful (conductor flake class + fchosen clipped-row contract).

## Checks

- `python .agentflow/dashboard/build.py` - product pages unaffected.
- `python .agentflow/dashboard/build.py --demo` - demo mode unaffected.
- `python .agentflow/dashboard/mockups/build.py` - variants regenerate identically.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` - dashboard regression.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python .agentflow/dashboard/build.py` -> pass (44 tasks, 40 dependencies, 3 successors, 136 commits -> out/; exit 0)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, DEMO DATA; exit 0)
- `python .agentflow/dashboard/mockups/build.py` -> pass (3 variants built; diff vs HEAD = only the embedded "generated" timestamp per file)
- `python -m unittest discover -s .agentflow/tests` -> pass (266 ran, 0 failed, 3 skipped, 239.9s; no flake observed in this run)
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (9 ran; exit 0)
Environment: detached HEAD at 11569404c9437612d6b8f862efa2df19309c15d0 in the disposable checkout; Python 3.13.7; installed Chrome --headless=new driving a local http.server (127.0.0.1:8123) + temporary iframe harness; evidence under .agentflow/tasks/.runtime/T-055.evidence/ (meas_*.json, inter_*.json, search_*.json, meas_prea.json, shots/*.png, checks.txt).
Criteria:
- M-01 - pass - evidence: own bounding boxes (x,y WxH px, iframe viewport = named width, NOT the worker's numbers). At 1101/1280/1920/3840 all three variants: display:grid with 3 computed column tracks; hdr/fbar/fchosen span full width as rows 1-3; .side.left/.center/.side.right sit side-by-side at the same top y with bottoms inside the viewport; .center innerText 732-4180 chars (never empty); scrollWidth==clientWidth; conlog element absent = zero JS errors. Examples: a-cards @1280x900 - hdr 12,12 1256x40; fbar 12,64 1256x52; fchosen 12,124 1256x26; left 12,166 270x722; center 294,166 662x722; right 968,166 300x722; a-cards @1920x1080 - left 12,166 365x902; center 389,166 1085x902; right 1486,166 422x902; a-cards @1101 - left/center/right at y198 (270/483/300 px wide); a-cards @3840 - 730/2218/845 px. b-journey and c-matrix wide geometry identical. Control: parent-SHA roadmap-a-cards.html @1920 reproduces the reported defect (fbar 365x782 in left column, rail at x1486, center squeezed to 365x26) - meas_prea.json.
- M-02 - pass - at 390 and 1100 display:block stacked layout on all three variants, sw==cw (380 and 1090 = viewport minus vertical scrollbar) so no horizontal scroll, content flows vertically (scrollH 1701-6004); at 1101 display flips to grid and wide layout engages on all three; a-cards @390 also exercised interactively (dropdowns, search, drill-down all work) - inter_a390.json.
- M-03 - pass - hashed the three committed HTMLs, ran mockups/build.py, diffed each file: the only difference per file is the embedded "generated" minute inside const DATA (e.g. 19:11 -> 19:28); everything else byte-identical, so the committed files are genuine regenerated outputs, not output-only edits.
- M-04 - pass - `git diff main...1156940` touches only .agentflow/VERSION, mockups/{chrome.css,chrome.js,roadmap-a-cards/b-journey/c-matrix.html}, the AGENTS.md version line and CHANGELOG.md - zero product files. Temp clone at parent 4ba2106: --demo output identical modulo build timestamps; real output identical modulo (a) timestamps, (b) "Tasks <folder>" project name of the checkout, (c) +1 ping timestamp reachable only via refs/remotes/upstream/* (git log --all is ref-set dependent - environmental), (d) dep-edge order T-007/T-008 -> T-010 which also flips between two builds in the SAME checkout (build.py set-iteration nondeterminism, confirmed). Same product code produces the same output on the same data.
- M-05 - pass - exercised, not read, on all three variants @1280 plus a-cards @390: #theme click -> data-theme=dark + localStorage dash-theme=dark, persists across iframe reload; filter bar paints 6 dimension + 1 flag .fb-dd buttons (the fb.render() fix - previously unrendered); first dropdown opens .fb-pop with 7 value chips; chip pick -> 1 .fb-sel chip + "Showing 1 of 15"; fresh search "t-951" -> "Showing 1 of 15 tasks - stage list unaffected" + one search chip on all three variants; Reset all -> "Showing 15 of 15" and chips cleared; .tmini tr.row click -> #detail .tcard "Task T-941 - mockup card"; Enter keydown on a row -> "Task T-942 - mockup card"; cards #rail .stg click selects; journey Enter toggles node open 3->2; matrix Enter toggles stage row expansion 1->0.
- M-06 - pass - all Checks pass verbatim on the exact SHA; VERSION=2.13.2, AGENTS block version line=2.13.2, CHANGELOG 2.13.2 entry dated 2026-10-17 with migration notes for installed projects - in sync. Found-not-fixed claims verified truthful: .fbchosen{height:26px;overflow:hidden} is the shared common.css:19 contract identical to the product dashboard; the one-off conductor session-finish flake belongs to the documented Windows timing-flake family in known-issues (and did not occur in this run).
New defects (outside the task):
- none observed.
Cannot verify, needs:
- nothing.
Proposed memory updates:
- none; the decisions.md text T-054 proposed accurately describes the change, and no new known-issue is needed (conductor flake class already covered).

Attempt 2 (recovery launch after attempt 1 ended 'verification' on a mid-flight T-054 contract edit, not artifact drift) - spot confirmation only, no probe-matrix redo:
- Disposable checkout = detached HEAD at 11569404c9437612d6b8f862efa2df19309c15d0, tree clean; checked branch t-054-mockup-grid-fix and its worktree still at the same SHA, clean; T-054 Task File hash and worktree state identical to this attempt's launcher baseline (checkedRef/checkedTree/checkedFileHash recomputed) - pass
- All five Checks re-run verbatim on the exact SHA reproduce the lines above: build.py 44 tasks/40 dependencies/3 successors/136 commits, --demo 8 tasks, mockups/build.py rebuilds all 3 variants with only the embedded "generated" timestamp differing (19:11 -> 20:36), unittest discover 266 ran 0 failed 3 skipped (248.5s), test_dashboard 9 ran - pass
- Attempt-1 evidence intact under .agentflow/tasks/.runtime/T-055.evidence/ (18 meas_*.json, inter_*.json, search_*.json, meas_prea.json, checks.txt, 18 shots/*.png); the Result and verdict stand as written on this SHA - pass
- No new defects; nothing above the Result heading changed, no commits made.
