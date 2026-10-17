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

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route_report.py` -> pass (10 passed / 0 failed) - evidence: .agentflow/tasks/.runtime/T-008.evidence/check1-route-report.txt
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (9 passed / 0 failed) - evidence: T-008.evidence/check2-dashboard.txt (test_layout.py additionally run: 6 passed, check2b-layout.txt)
- `python .agentflow/dashboard/build.py` -> pass (25 tasks, 23 dependencies, 1 successors, 110 commits -> out/) - evidence: T-008.evidence/check3-build-real.txt and check3b-build-real-rerun.txt
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, ... -> out/ [DEMO DATA]) - evidence: T-008.evidence/check4-build-demo.txt
- `python -m unittest discover -s .agentflow/tests` -> pass (204 tests, OK, 3 skipped, 151s) - evidence: T-008.evidence/check5-full-suite.txt
Criteria:
- V-01 first-pass gate rate honesty - pass - route_report.py metrics() reads the first record of T-NNN.verify.json only (`records[0].get("ok")`, route_report.py:158-163); denominator is tasks with verify records, others counted in tasksWithoutEvidence; tester fail verdict is a valid report (`testerVerdicts` counts it separately, DEFINITIONS route_report.py:128-141); leadSeconds/cost are None not zero; tests covering fail-then-pass, denominator, no-evidence and fresh clone: test_first_pass_uses_first_verify_record_not_a_later_pass, test_tasks_without_evidence_are_not_failures, test_denominator_groups_by_recorded_role_and_tool, test_fail_verdict_is_a_valid_negative_report_not_a_failure, test_lead_time_is_none_without_attempt_history, test_fresh_clone_reports_absence_honestly - evidence: T-008.evidence/test-names.txt, check1-route-report.txt
- V-02 English default complete and safe - pass - built pages render every label/filter/role/Gantt/timeline/metrics in English, confirmed on real screenshots T-008.evidence/dashboard-real-index.png and dashboard-real-graph.png (2560x1440, served from out/ on PORT=8398); machine keys travel untranslated as statusKey/roleKey/verdict in the payload (build.py:307-316); tester links come from the `Verifies:` header field + SHA with stale flag (verifies_of/link_checks, build.py:172-181,334-348), no title regex; Russian text regexes for ledger/task data retained (OWN_RE and successor regexes, build.py:156,207-211) and Cyrillic appears only inside those data regexes in the built pages, never as UI labels; tests: test_check_edge_uses_verifies_not_title, test_stale_checker_link_is_flagged, test_verdict_stays_separate_from_status_and_outcome, test_machine_key_kept_next_to_display_status, test_english_labels_in_both_pages, test_metrics_present_in_payload
- V-03 demo isolation and honesty - pass - demo_graph() builds a fixed fixture (base timestamp 2026-10-10, fixed generated/now, graph["demo"]=true) reading no ledger, Task Files, runtime or git; build writes only to out/ (test_main_demo_writes_only_out, test_demo_graph_is_deterministic_marked_and_isolated); header shows a visible DEMO DATA badge, confirmed on T-008.evidence/dashboard-demo-index.png and dashboard-demo-graph.png; real rebuild after --demo contains zero "DEMO" markers (count=0)
- V-04 checks on the verified commit, baselines, metadata - pass - all five verbatim checks above ran in this disposable checkout at f282ab7a7414c7fc17d7eb216a6d83ee95b1281c (detached HEAD, `git status` clean after builds because out/ is git-ignored); developer worktree E:\Projects\AgentFlow\worktrees\agentflow-t-007-english-metrics-dashboard unchanged: branch t-007-english-metrics-dashboard @ f282ab7, clean; VERSION=2.11.14, AGENTS.md block `AgentFlow version: 2.11.14`, CHANGELOG `## 2.11.14 - 2026-10-17` in sync
New defects (outside the task):
- none
- observation inside the checked change (not criterion-blocking): the demo fixture stores outcome words ("done"/"completed") in the `verdict` field for rows T-101/T-102, so demo shows "Tester assigned" where a real pass verdict would show "Tester: pass"; data is clearly marked DEMO DATA and no real-evidence claim is made
Cannot verify, needs:
- interactive browser behavior (clicks, console cleanliness) - headless Chrome screenshots verify rendering only; UI-RULES B4.21 asks for a real-browser pass but no playwright/browser harness is installed here; markup, data and both pages render correctly in the attached screenshots
Proposed memory updates:
- session-log: T-008 done - independent verification of T-007 @ f282ab7 passed (verdict pass); 204 tests green; real+demo screenshots captured to .agentflow/tasks/.runtime/T-008.evidence/ via headless Chrome on PORT=8398
