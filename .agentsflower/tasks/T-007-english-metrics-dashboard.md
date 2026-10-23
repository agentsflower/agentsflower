# T-007: Honest telemetry and English dashboard

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-005
Branch: t-007-english-metrics-dashboard
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-007-english-metrics-dashboard
Independent check: tester
Resume: none

## Goal

Extend existing route_report evidence into useful metrics and translate the
entire existing dashboard to English. Preserve the established layout; no
unsolicited redesign. Use a clearly marked demo dataset without touching memory.

## Read first

- AGENTS.md
- .agentflow/docs/agentflow-production-roadmap.txt
- .agentflow/tools/route_report.py
- .agentflow/tools/ledger.py
- .agentflow/dashboard/README.md
- .agentflow/dashboard/UI-RULES.md
- .agentflow/dashboard/build.py
- .agentflow/docs/ai-handoff-protocol.md (Dashboard section)

## Allowed files

- .agentflow/tools/route_report.py
- .agentflow/tools/ledger.py
- .agentflow/dashboard/
- .agentflow/tests/test_route_report.py
- .agentflow/tests/test_dashboard.py
- .agentflow/tests/test_layout.py
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/
- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- pyproject.toml
- README.md
- GUIDE.md
- .agentflow/docs/assets/dashboard.png

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] D-01: Reuse route_report as the metrics provider; do not duplicate computation in ledger/dashboard. First-pass gate rate is explicitly defined (first recorded verify per task, denominator only tasks with that evidence), grouped by recorded role/tool with counts. Distinguish valid negative Tester report from positive verdict. No cherry-picking later PASS as first pass.
- [ ] D-02: Attempts, routing outcomes and lead-time source/definition are explicit. Missing start/acceptance history, runtime, costs or token/context telemetry is unknown/N/A, not zero or invented savings. No causal model-quality/efficiency claim from outcomes. Fresh clone reports absence honestly.
- [ ] D-03: All human dashboard labels, filters, roles, Gantt, timeline and metrics default to English. Machine states and status/outcome/verdict remain separate. Tester links use Verifies and checked SHA, not a title regex. Update data contract, protocol and UI rules to reflect human-approved English default; preserve Russian project communication.
- [ ] D-04: Save a source snapshot before noticeable changes. Add an explicit --demo or equivalent isolated demo mode with clear DEMO DATA label, deterministic fixture data, no canonical-memory writes and no fabricated real project evidence. Keep existing layout recognizable; demonstrate filters/task cards/metrics and safe text rendering.
- [ ] D-05: Focused metrics tests cover fail-then-pass, absent evidence, denominators, stale checker links and separate verdict semantics. Build real and demo outputs. Tester T-008 will capture a real high-resolution screenshot as evidence; do not fabricate an image. Increment intermediate 2.11 version and synchronize release metadata.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route_report.py` - evidence-based metrics.
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` - labels, links and demo safety.
- `python .agentflow/dashboard/build.py` - real local view.
- `python .agentflow/dashboard/build.py --demo` - deterministic visibly marked demo.
- `python -m unittest discover -s .agentflow/tests` - full regression suite.

## Result

Outcome: completed
Change: f282ab7 on t-007-english-metrics-dashboard
Files:
- .agentflow/tools/route_report.py - new metrics() provider: first-pass gate rate from the first .runtime/T-NNN.verify.json record per task (denominator = tasks with evidence), lead time from attempt timestamps, tester verdict counts, explicit definitions, N/A for missing/cost telemetry; included in CLI output
- .agentflow/dashboard/build.py - English display labels with machine keys (statusKey/roleKey) kept separate, check edges and checkedBy from the Verifies field + SHA with stale-link flagging, route_report.metrics() in the payload, deterministic --demo fixture
- .agentflow/dashboard/{template,graph_template}.html, common.js/css, filterbar.js, snapshot.py - translated to English; DEMO DATA badge; metrics panel in the summary view; layout preserved
- .agentflow/dashboard/README.md, UI-RULES.md, .agentflow/docs/ai-handoff-protocol.md - data contract, UI rules and Dashboard section updated to the human-approved English default
- .agentflow/tests/test_dashboard.py (new), test_route_report.py, test_layout.py - Verifies links, stale links, verdict separation, first-record semantics, denominators, absent evidence, demo isolation
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.11.14 release metadata
Checks:
- python -m unittest discover -s .agentflow/tests -p test_route_report.py -> pass (10 passed / 0 failed)
- python -m unittest discover -s .agentflow/tests -p test_dashboard.py -> pass (9 passed / 0 failed)
- python .agentflow/dashboard/build.py -> pass (25 tasks, real local view)
- python .agentflow/dashboard/build.py --demo -> pass (8 tasks, deterministic, DEMO DATA marked)
- python -m unittest discover -s .agentflow/tests -> pass (204 passed / 0 failed, 3 skipped)
Criteria without a command:
- D-01: route_report.metrics() is the single provider; dashboard embeds it; first recorded verify only, grouped by recorded role/tool; fail verdict shown as a valid negative report in testerVerdicts and the check field
- D-02: every metric has a definitions entry; missing history/runtime/cost is N/A or excluded, never zero; no causal claims (descriptive note in output)
- D-03: English labels everywhere; Russian kept only in data-matching regexes that read Russian ledger/task text (project communication unchanged); machine keys separate
- D-04: snapshot v1 saved before changes; --demo is deterministic (two builds byte-identical, asserted in tests), DEMO DATA badge in the header, writes only out/
- D-05: no screenshot fabricated - left for tester T-008
Found, not fixed:
- .agentflow/state/decisions.md needs a dated entry per project rules but is in the task's Do not touch - proposed below
- ledger.py (Allowed files) needed no change; route_report is the only metrics provider
Proposed memory updates:
- decisions.md, 2026-10-17: dashboard interface switched to English default (human-approved via T-007); tester links use Verifies + SHA with stale flagging; metrics only from recorded evidence, N/A for missing telemetry
