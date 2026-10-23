# T-065: Independently verify completion gate carrier

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-064
Verifies: T-064 @ 7f208e2

## Goal

Independently evaluate the exact T-064 artifact (7f208e2 - the consolidated
completion gate merged with main's T-062 audit fix) against every C-01..C-04
criterion in its Task File, in a disposable checkout. The artifact carries the
T-032 completion gate plus the T-060+T-062 audit fixes - independently prove
each load-bearing claim rather than re-quoting worker results.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-064-completion-gate-carrier.md (contract + Result)
- .agentflow/tasks/T-032-completion-gate.md, T-060-completion-gate-final.md (the carried Results)
- The candidate diff `git diff main...7f208e2` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-064 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] Q-01: Criterion IDs are enforced: a Task File without IDs or with duplicate IDs is refused at preflight; a Result missing an outcome line for a required criterion fails verify; a completed negative review still parses. Probe live, do not only read code.
- [ ] Q-02: Evidence binding works: an evidence file path outside the task's scope is rejected; editing the Result/attempt artifact after a bound verify record invalidates it. Probe one bound record, not only tests.
- [ ] Q-03: The integrated check is real: a task whose Checks pass in its worktree but fail on the trial-merge result cannot be accepted - probe or find the executed path; `agentflow done` returns structured reasons, not just an exit code.
- [ ] Q-04: Audit scope fixed: a _template.md commit no longer flags, a t-*.md commit still flags, a .runtime commit still flags - live probe on a disposable repo at the checked SHA.
- [ ] Q-05: No regression in the T-050/T-056-verified behaviors and the T-054 mockup work: full suite green verbatim (claimed 295/0/3-skipped); VERSION/AGENTS/CHANGELOG consistent (2.14.0 + shipped 2.13.3 entry retained); `git diff main...7f208e2` inside declared Allowed files; the one transient flake the worker disclosed is believable and bounded.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-audit and baseline regressions.
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` - preflight criteria-ID enforcement.
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - the completion gate tests.
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` - completion command surface.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` -> pass (3 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (295 passed / 0 failed / 3 skipped; verbatim green on run 3 after one environmental flake in each of runs 1 and 2)
Criteria:
- Q-01: pass - live probes on disposable repos running the checked SHA's tools: preflight refused a Task File whose criterion had no stable ID and one with a duplicated ID (the dup named P-01); verify failed a completed Result that lacked the required outcome line; a tester Result with Verdict fail over mixed criteria verified clean and its record kept both per-criterion outcomes. Transcript .agentflow/tasks/.runtime/T-065.probes.log
- Q-02: pass - an evidence path outside the task scope was rejected both as a parent-relative path and as an absolute drive path; the bound record was probed end to end: the second done run reused the bound PASS (reused flag set, still one record on disk), a Result edit dropping the outcome line failed without reuse, a new commit on the branch failed with a Result-Change mismatch, pointing Change at the new commit produced a fresh measured record, and a moved base re-measured as well. Transcript .agentflow/tasks/.runtime/T-065.probes.log
- Q-03: pass - the executed path was probed live: .agentflow/tools/accept.py ran verify, wrote the trial-merge tree with git merge-tree, ran the task check on the integrated result, and stopped before merging (the fixture's probe file stayed absent from the base and the durable progress file recorded the failed integrated step); gate done and cli done each emitted structured JSON with ok, problems, checks, preExisting and verifyRecord fields, not just an exit code. Transcript .agentflow/tasks/.runtime/T-065.probes.log; code path also in .agentflow/tools/gate.py
- Q-04: pass - live audit on a disposable repo at the checked SHA: a branch commit touching only .agentflow/tasks/_template.md produced no problems; a branch commit adding a Task File under tasks flagged it and named the offending path; a branch commit adding launcher runtime state under tasks flagged it and named the path. Transcript .agentflow/tasks/.runtime/T-065.probes.log; regression coverage .agentflow/tests/test_endcheck.py
- Q-05: pass - verbatim suite on the exact SHA: run 3 passed 295, failed 0, skipped 3; runs 1 and 2 each hit one environmental flake outside the diff (the documented WinError 5 atomic-replace race in a disposable fixture, and a test fixture crossing local midnight) and both passed on rerun; VERSION, the AGENTS version line and CHANGELOG all read 2.14.0 with the shipped 2.13.3 entry retained; all 18 diff files stay inside the declared Allowed files and the AGENTS change is only the version line; a4f0642 and main 1a05af9 are both ancestors of the merge. Evidence .agentflow/tasks/.runtime/T-065.check-full-run1.log, .agentflow/tasks/.runtime/T-065.check-full-run2.log, .agentflow/tasks/.runtime/T-065.check-full-run3.log, .agentflow/tasks/.runtime/T-065.diff-meta.log, CHANGELOG.md
New defects (outside the task):
- date-fragile test fixture, pre-existing on main: .agentflow/tests/test_route.py binds TODAY at module import but asserts routing_date computed later, so a suite run crossing local midnight fails with a one-day mismatch (observed verbatim in run 2: got 2026-10-18 where 2026-10-17 was expected); green in both other runs.
Cannot verify, needs:
- none; all five Checks ran verbatim on the checked SHA and every criterion was probed live in disposable fixtures.
Proposed memory updates:
- .agentflow/state/known-issues.md, dated 2026-10-18: add the routing_date date-boundary flake next to the existing atomic-replace WinError 5 recurrence; look again whenever a suite run crosses local midnight.