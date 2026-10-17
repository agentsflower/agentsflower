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
