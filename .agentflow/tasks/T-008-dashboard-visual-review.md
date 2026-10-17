# T-008: Independently verify honest telemetry and English dashboard

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-007
Verifies: T-007 @ f282ab7a7414c7fc17d7eb216a6d83ee95b1281c

## Goal

Verify the evidence-based metrics provider and the English dashboard
independently of the developer's own run, on the verified commit. Same tool is
necessary under the human's resource policy (agy and claude limited, codex
conserved); use a fresh isolated session. Capture the real high-resolution
screenshot D-05 left for the tester. No product changes.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-007-english-metrics-dashboard.md
- .agentflow/tools/route_report.py (metrics)
- .agentflow/dashboard/README.md (data contract)
- .agentflow/dashboard/UI-RULES.md
- .agentflow/dashboard/build.py
- .agentflow/tests/test_dashboard.py
- .agentflow/tests/test_route_report.py
- .agentflow/tests/test_layout.py
- .agentflow/docs/ai-handoff-protocol.md (Dashboard section)
- .agentflow/VERSION, CHANGELOG.md, AGENTS.md (2.11.14 metadata)

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/, .agentflow/tests/, .agentflow/dashboard/
- .agentflow/state/, .agentflow/tasks/
- developer worktree/branch, pyproject.toml, README.md, GUIDE.md
- .agentflow/docs/assets/dashboard.png (the captured screenshot goes to the
  task's .runtime evidence directory, referenced from Result)

## Setup

- nothing

## Port

- PORT=8398 (serve .agentflow/dashboard/out locally for the screenshot if a
  server is needed; tests read it from the environment)

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: First-pass gate rate is honest: only the first recorded verify per
  task counts, the denominator is tasks with that evidence, a fail-then-pass
  task is a first-pass failure, and a valid negative Tester report is not
  folded into a positive verdict. Missing runtime/cost/history is N/A, never
  zero or invented savings; a fresh clone reports absence honestly.
- [ ] V-02: English default is complete and safe: every human-facing label,
  filter, role, Gantt, timeline and metrics panel renders in English;
  status/outcome/verdict stay three separate machine keys; tester links come
  from Verifies + SHA (stale links flagged), not a title regex; Russian project
  communication in ledger/task text still matches its data regexes.
- [ ] V-03: Demo mode is isolated and honest: --demo is deterministic with a
  visible DEMO DATA label, writes only to out/, touches no canonical memory and
  fabricates no real project evidence; the real build reflects the real ledger.
- [ ] V-04: The five verbatim checks pass on the verified commit in a
  disposable checkout; developer worktree/branch/Task File baselines
  unchanged; VERSION 2.11.14, AGENTS block and CHANGELOG entry in sync. Attach
  the real high-resolution screenshot of the built dashboard as evidence.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route_report.py` - evidence-based metrics.
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` - labels, links and demo safety.
- `python .agentflow/dashboard/build.py` - real local view.
- `python .agentflow/dashboard/build.py --demo` - deterministic visibly marked demo.
- `python -m unittest discover -s .agentflow/tests` - full regression suite.

## Result
