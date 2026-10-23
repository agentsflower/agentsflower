# T-069: Independently verify evidence-gate scope fix

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-068
Verifies: T-068 @ 0193c0a

## Goal

Independently evaluate the exact T-068 artifact (2.14.1 - the evidence gate
validates only claimed evidence, not path-like prose) against every
V-01..V-04 criterion in its Task File, in a disposable checkout at the exact
SHA. Probe the claims live; report the worst criterion as the verdict.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-068-evidence-scope-fix.md (contract + Result)
- .agentflow/tasks/T-034-bounded-autonomy.md (the Result whose prose tokens were falsely flagged - your reproduction case)
- The candidate diff `git diff main...0193c0a` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-068 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] Z-01: Reproduce the T-034 scenario at the checked SHA: run the evidence validation against T-034's actual Result text (verify/done, launch.argv, init/config, decisions.md, decide/next-orchestrator/status/run tokens) and confirm zero evidence problems - in a disposable repo, with your own probe, not just the shipped tests.
- [ ] Z-02: Real evidence still binds: probe that a claimed `.agentflow/tasks/.runtime/...` path missing on disk still fails, and a claimed path outside the task's allowed scope still fails; a claimed existing in-scope file passes.
- [ ] Z-03: Schema/prose distinction holds: a Result line describing where a config lives (`.agentflow/docs/quota-policy.json`) is not treated as a claim when no evidence marker/list presents it; probe both directions - a line that DOES claim evidence still binds.
- [ ] Z-04: No over-tightening: confirm that a Result with NO evidence claims at all does not fail the evidence check (the criterion-level outcome lines remain the binding contract).
- [ ] Z-05: All claimed checks pass verbatim on the exact SHA (claimed 299/0/3-skipped); VERSION/AGENTS/CHANGELOG 2.14.1 in sync; diff inside Allowed files; the disclosed WinError-5 flake is bounded and matches the known-issues pattern.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - evidence-binding regressions.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - baseline regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` -> pass (25 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (299 passed / 0 failed, 3 skipped)
Criteria:
- Z-01: pass - evidence: .agentflow/tasks/.runtime/T-069.evidence/T-069.probe_evidence.out.txt - own probe imports the checked gate code inside a fresh disposable repo and replays the eight T-034 outcome lines verbatim: zero evidence problems; the pre-fix code flags 21 problems on the same text, so the probe is not vacuous
- Z-02: pass - evidence: .agentflow/tasks/.runtime/T-069.evidence/T-069.probe_evidence.out.txt - a claimed runtime file missing on disk fails not-found, a runtime file of another task and existing out-of-scope and parent-relative claims fail scope, while an existing own-runtime file and an existing in-scope file pass
- Z-03: pass - evidence: .agentflow/tasks/.runtime/T-069.evidence/T-069.probe_evidence.out.txt - a prose line describing where the quota policy schema lives stays a mention, the same repository path after an evidence marker or as a bare list is claimed and fails, and a bare list of an existing in-scope file passes
- Z-04: pass - evidence: .agentflow/tasks/.runtime/T-069.evidence/T-069.probe_evidence.out.txt - outcome lines with no claims at all, an empty evidence text and a single plain word all produce zero evidence problems
- Z-05: pass - evidence: .agentflow/tasks/.runtime/T-069.evidence/T-069.checks.out.txt - the three Checks pass verbatim at the SHA (25, 15 and 299 with 3 skipped); version files all read 2.14.1; the diff touches only Allowed files per the recorded stat .agentflow/tasks/.runtime/T-069.evidence/T-069.diff-stat.txt; the disclosed transient registry replace failure matches the recurring known-issues pattern and did not recur here
New defects (outside the task):
- none
Cannot verify, needs:
- nothing
Proposed memory updates:
- none
