# T-042: Clickable roadmap-view mockup for human selection

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Branch: t-042-dashboard-mockup
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-042-dashboard-mockup
Independent check: none - the human's mockup selection is the UI-RULES A1.2 gate, not a tester verdict
Resume: none

## Goal

Produce a clickable offline mockup of the new Roadmap dashboard view described
in .agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md, using
synthetic fixtures only, so the human can pick a layout variant. This task
changes no product dashboard code; it produces the selection artifact plus the
agreed data-schema notes the implementation tasks will consume.

## Read first

- .agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md (authoritative spec, sections 1-4)
- .agentflow/dashboard/UI-RULES.md (A1.2 mockup rule, A3/A4 layout, B3 UX)
- .agentflow/dashboard/README.md (data contract)
- .agentflow/dashboard/build.py and out/index.html + out/graph.html (generate first if missing, then study the real layout)
- .agentflow/docs/project-plan.md and .agentflow/state/tasks.md (real stage/task shapes to mimic synthetically)

## Allowed files

- .agentflow/dashboard/mockups/ (new folder - mockup HTML, fixture JSON, README index)
- .agentflow/dashboard/versions/ (snapshot.py output only)

## Do not touch

- .agentflow/dashboard/build.py, templates, common.*, filterbar.*, README.md, UI-RULES.md, snapshot.py (read them; the mockup is a sibling artifact, not an edit)
- .agentflow/state/, .agentflow/tasks/ (other Task Files)
- everything else in the repository and other projects

## Setup

- python .agentflow/dashboard/snapshot.py save "pre-roadmap-mockup" (record the command output in the Result)
- python .agentflow/dashboard/build.py (have current real pages to compare against)

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] M-01: One self-contained clickable HTML per proposed variant (2-3 variants), stdlib/offline, inside .agentflow/dashboard/mockups/, driven by synthetic fixture data only - zero-task stages, a historical closed stage, a recurring stage with one recorded cycle, an active stage with tasks, and a failed/pending external evidence case, per the PLAN fixture list.
- [ ] M-02: Each variant shows: every declared stage independent of task filters; declared status, local task counts and exit-criteria evidence as three separate facts; a stage card with title/ID/status/counts/evidence summary/active blockers/source link; drill-down toward task cards; a diagnostics area for source freshness/mismatch. Existing Overview and Gantt navigation stays intact in the mockup chrome.
- [ ] M-03: Honest-demo fidelity: no invented values, unknown shown as unknown, a stale evidence sample labeled stale, a completed negative review shown as a negative verdict; variants differ meaningfully in information architecture (e.g., stage-first cards vs timeline-anchored stages).
- [ ] M-04: Mockups satisfy the UI-RULES constraints that apply to a mock: shared header/theme/timestamp chrome identical to the current pages, no horizontal scroll at 390/1280/1920/3840px widths, one scrolling region, filter bar shape consistent with existing pages (non-functional placeholders allowed where the variant proposes new filters).
- [ ] M-05: A short README inside mockups/ lists the variants, the open layout questions for the human, and the proposed common payload fields the implementation will build (schemaVersion, stages[], diagnostics, provenance).
- [ ] M-06: The Result names the snapshot version saved before work, the mockup paths, and which facts the human must pick. No changes outside Allowed files; no real task data embedded beyond synthetic fixtures.

## Checks

- `python .agentflow/dashboard/build.py` - current real pages still build unchanged (mockup does not alter product sources).
- `python .agentflow/dashboard/build.py --demo` - demo mode unaffected.
- Mockup files open offline in a browser without console errors (worker verifies and reports the browser used).

## Result
Outcome: completed
Change: d75d91d on t-042-dashboard-mockup
Files:
- .agentflow/dashboard/mockups/fixtures.json - synthetic payload: 6 declared stages in plan source order (Stage 6 first, as the real plan), incl. zero-task stages, historical closed Stage 3, recurring Stage 4 with one recorded cycle, declared-"planned" Stage 5 with 9 tasks (mismatch warning), Stage 6 with failed/pending external evidence; 15 tasks incl. stale Verifies link (T-957), completed negative verdict (T-956 fail), unmapped task (T-999), recorded attempts on T-951 / absent elsewhere; diagnostics + provenance blocks
- .agentflow/dashboard/mockups/chrome.css, chrome.js - shared mockup chrome: header identical to real pages plus proposed third nav "Roadmap" (Overview/Gantt links point to ../out/), MOCKUP badge, theme toggle; M namespace: three-facts renderer (declared / local counts / evidence), evidence chips and tables, mini task tables, condensed task card, diagnostics card, one filter set wired through the real createFilterBar
- .agentflow/dashboard/mockups/src/cards.src.html -> roadmap-a-cards.html - variant A: stage-first cards + roadmap rail + totals
- .agentflow/dashboard/mockups/src/journey.src.html -> roadmap-b-journey.html - variant B: vertical journey stepper with dated-record spans, expandable nodes
- .agentflow/dashboard/mockups/src/matrix.src.html -> roadmap-c-matrix.html - variant C: compact one-row-per-stage matrix, expandable rows
- .agentflow/dashboard/mockups/build.py - stdlib generator: inlines real common.css/filterbar.* + mockup chrome + fixture JSON into three self-contained offline pages
- .agentflow/dashboard/mockups/README.md - variant index, 5 open layout questions, proposed common payload fields (schemaVersion, stages[], diagnostics, provenance)
- .agentflow/dashboard/versions/v1-20261017-1441-pre-roadmap-mockup/ - snapshot.py output (git-ignored)
Checks:
- `python .agentflow/dashboard/build.py` -> pass (33 tasks, 30 dependencies, 1 successors, 122 commits; product sources untouched)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks demo fixture, unaffected)
- Mockup files open offline in a browser without console errors -> pass: Google Chrome 155.0.8059.39 headless (--headless=new) over file://; all three pages, 0 console errors and 0 window errors; no horizontal overflow at true 390px viewport (iframe harness, scrollWidth=clientWidth=380) and at 1280/1920/3840 window widths
Setup evidence:
- `python .agentflow/dashboard/snapshot.py save "pre-roadmap-mockup"` -> "saved: v1-20261017-1441-pre-roadmap-mockup"
Criteria without a command:
- M-01: three self-contained clickable variants under .agentflow/dashboard/mockups/, driven only by fixtures.json; fixture covers every PLAN case (zero-task, historical closed, recurring+one cycle, active stage, failed/pending external evidence, plus unmapped/stale/negative-verdict edge cases)
- M-02: all declared stages render independent of task filters ("Showing N of M tasks · stage list unaffected"); declared status, local counts (explicit denominator) and exit-criteria evidence are three separate labeled facts; each stage has title/ID/status/counts/evidence summary/active blockers/source link; task rows drill into a task card in the right rail; one diagnostics card holds source freshness (mtimes/fingerprints), warnings and gaps; Overview/Gantt & timeline navigation intact
- M-03: unknown/stale/pending/fail-verdict/"not recorded"/"No local tasks" all shown explicitly, nothing invented; MOCKUP badge on every page; variants differ meaningfully (stage-first cards vs journey stepper vs compact matrix)
- M-04: shared header/theme/Built chrome built from the inlined real common.css/filterbar.*; one scrolling region per layout; no h-scroll verified at 390/1280/1920/3840 (see Checks); real filter bar, all controls functional
- M-05: mockups/README.md lists variants, 5 open layout questions and the proposed payload fields
- M-06: snapshot version and mockup paths above; the human must pick: (1) variant A/B/C, (2) keep plan source order (Stage 6 first) vs sort by stage number, (3) diagnostics placement, (4) task-table depth inside a stage, (5) whether roadmap-specific filters are wanted. No changes outside Allowed files; no real task data embedded
Found, not fixed:
- The real dashboard pages overflow ~16px at a true 390px viewport (measured: out/index.html scrollWidth=396 vs clientWidth=380); the mockup topbar intentionally wraps below 1100px instead, so mockups stay clean. The implementation task may want the same fix on the real pages
- Adding mockups/ is a template change; CHANGELOG/VERSION/decisions.md are outside this task's Allowed files - release metadata stays with the Orchestrator
Proposed memory updates:
- decisions.md candidate: roadmap view keeps three facts separate (declared plan status / ledger task counts / recorded criterion evidence); Stage 6-first source order vs ordinal sorting is an open human question recorded in mockups/README.md
