# T-044: Roadmap data layer - plan parser, stage records, payload schema, diagnostics

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-038
Branch: t-044-dashboard-data
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-044-dashboard-data
Independent check: tester
Resume: none

## Goal

Implement the data/parser layer of the roadmap dashboard per PLAN.md sections
1-3: a backward-compatible project-plan.md parser, stage records joined with
ledger/contract/runtime evidence, the shared schemaVersioned payload consumed
by all dashboard pages, and honest diagnostics. Launch additionally requires
the human's mockup selection (recorded in decisions.md) - the payload schema is
fixed by PLAN.md plus the selected mockup's README; do not start before both
exist.

## Read first

- .agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md (sections 1-3, acceptance matrix)
- .agentflow/dashboard/UI-RULES.md (A2 data honesty, B1/B2 architecture and extraction)
- .agentflow/dashboard/build.py, README.md, snapshot.py
- .agentflow/dashboard/mockups/ (selected variant README + agreed payload fields)
- .agentflow/tools/route_report.py, .agentflow/tools/ledger.py, .agentflow/tools/gate.py (existing readers)
- .agentflow/docs/project-plan.md, .agentflow/state/tasks.md, representative .agentflow/tasks/T-*.md
- .agentflow/tests/test_dashboard.py, test_layout.py

## Allowed files

- .agentflow/dashboard/build.py
- .agentflow/dashboard/README.md (data contract only)
- .agentflow/tests/test_dashboard*.py (new test module allowed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/dashboard/templates, common.*, filterbar.* (the UI task owns them; coordinate schema only via the README data contract)
- .agentflow/state/, .agentflow/tasks/ (other Task Files), .agentflow/docs/project-plan.md
- .agentflow/tools/ (reuse readers; routing-assessment schema lands via T-040)
- .github/, README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in
- other projects and their machine leases

## Setup

- python .agentflow/dashboard/snapshot.py save "pre-roadmap-data" (record output in Result)

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] P-01: The parser reads the current `### Stage N. Title` format with multiline `Status:`/`Exit criteria:` blocks, preserving raw text and source order (Stage 6 may precede Stage 1), honoring Markdown heading boundaries and fenced code blocks. Zero required project-plan migration; optional criterion-ID/evidence/recurring metadata syntax is specified in dashboard/README.md before use.
- [ ] P-02: Stage records carry: ID, source ordinal, title, raw + normalized declared status, source location, exact exit-criteria text, optional authored criterion IDs/evidence links, optional recurring kind/cycle refs, linked task IDs, task counters, coverage summary, diagnostics. Task data stays under existing fields; roadmap fields are additive under a declared schemaVersion.
- [ ] P-03: Joined facts stay independent: declared status vs local execution counts (accepted/active/review/blocked/ready/rejected/cancelled with explicit denominator) vs criterion evidence (pass/fail/unknown/stale with provenance). No zero-task stage shows 0% or 100%; no accepted-count stage-completion verdict; a completed negative Tester review displays as a negative verdict; stale Verifies SHA labels stale.
- [ ] P-04: Diagnostics cover missing/unreadable/malformed plan, unknown statuses, duplicate IDs, ledger stages absent from plan, unassigned tasks (kept visible in an Unmapped group), missing runtime/git as separately labeled gaps. Duplicate IDs never resolve silently; bad stage data never hides readable task data.
- [ ] P-05: Evidence links validate existence under the project root; traversal/symlink escapes rejected; external URLs are references, never fetched at build; all project strings escaped; javascript:/data: URL schemes rejected.
- [ ] P-06: Attempt/assessment records expose only the documented allowlist (task/attempt id, tool, requested model/effort, recorded effective identity, timestamps, exit status, timeout/limit observation, safe evidence refs) sourced from runtime and routing records - including the T-040 assessment schema when present, degrading to unknown when absent. Never raw env/argv/logs/credentials/quota balances.
- [ ] P-07: Demo fixture (--demo) covers: six-stage plan with zero-task stages, historical closure without tasks, recurring stage with one recorded cycle, accepted tasks plus failed/pending external evidence, active planned stage, duplicate-ID diagnostics. Demo reads no canonical memory and writes only out/.
- [ ] P-08: All existing pages still build and show the same task data as before (regression fixtures compare payload task fields against the pre-change build on the same inputs).
- [ ] P-09: Full suite passes verbatim; increment VERSION, sync AGENTS block, CHANGELOG with migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` - payload/parser/semantics matrix.
- `python .agentflow/dashboard/build.py` and `python .agentflow/dashboard/build.py --demo` - real and demo pages build.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
