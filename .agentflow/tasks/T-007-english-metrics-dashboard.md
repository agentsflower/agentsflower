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

