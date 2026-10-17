# T-057: Independently verify limit detection finalization

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-056
Verifies: T-056 @ 5b3797bc6e483dce3b579c0f2c94f26acf466f58

## Goal

Fast-path independent check: T-053 already deep-verified this exact SHA
(all criteria pass, live evidence). Re-verify the two load-bearing claims on
this SHA in a disposable checkout - the false-positive fix and the hold-label
fix - plus the scope/metadata checks T-053 ran. Do not re-run the full probe
matrix T-053 already produced unless something fails.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-056-limit-detection-accept.md (contract + Result)
- .agentflow/tasks/T-053-verify-limit-detection.md (the deep verification of this exact SHA - confirm, don't redo)
- The candidate diff `git diff main...5b3797bc6e483dce3b579c0f2c94f26acf466f58` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-056 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] Y-01: The branch diff `main...5b3797b` touches only declared Allowed files (the inherited T-030 set + the T-052 fix set + release metadata) - confirm the scope check passes.
- [ ] X-01 replay: T-031's failing fixtures (`the banner shows|prints "you've hit your usage limit"`) read `no limit` at both exit codes through the shipped CLI; `ERROR: requests failed: you've hit your usage limit` still detects `limit:`.
- [ ] X-02 replay: a bare tool-wide `agy` hold refuses a grouped session with `agy is limited until` (tool name, not the session group); a group-scoped hold keeps the group label.
- [ ] Y-04: The five check commands pass on the exact SHA; VERSION/AGENTS/CHANGELOG 2.13.1 in sync; diff inside declared Allowed files.
- [ ] Y-05: Verdict consistency: confirm the Result's claimed SHA is the branch HEAD and the criteria statuses are truthful.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` - quote-frame and signal classes.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - resource-check wording + regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` -> pass (16 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (42 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (266 ran / 0 failed, 3 skipped platform-specific)
Evidence root: `.agentflow/tasks/.runtime/T-057.evidence/` (detached disposable checkout at 5b3797bc6e483dce3b579c0f2c94f26acf466f58, worktree of t-056 untouched, checkout clean at end; check*.txt suite output, y01-diff-files.txt + y01-agents-diff.txt scope, x01-fixture-*.log + x01-replay-results.txt detector probes, x02_replay.py + x02_replay.out.txt live resource_check probe in a disposable repo with a disposable machine registry, y05-branch-head.txt SHA consistency).
Criteria:
- Y-01 - pass - `git diff main...5b3797b` lists 17 files, every one inside T-056's declared Allowed files (7 tools + model-options.json + protocol + 5 test files + VERSION + AGENTS.md + CHANGELOG.md); the AGENTS.md hunk is the AgentFlow block version line only (y01-diff-files.txt, y01-agents-diff.txt).
- X-01 replay - pass - through the shipped CLI `limit_detection.py`: fixtures `the banner shows "you've hit your usage limit"` and `the banner prints "you've hit your usage limit"` read `no limit` at exit 0, exit 1 and unset exit code; `ERROR: requests failed: you've hit your usage limit` still detects `limit:` at all three (x01-replay-results.txt).
- X-02 replay - pass - live through run_task resource_check in a disposable repo at the checked SHA: a bare `agy` tool-wide hold refuses a grouped claude session (and the default gemini session) with `agy is limited until ...` - tool name, not the session group; an `agy:agy-claude-gpt` hold refuses the claude session with `agy group agy-claude-gpt is limited until ...` while the gemini session launches and completes (quotaGroup=agy-gemini, stopReason=completed) (x02_replay.out.txt).
- Y-04 - pass - all three check commands pass verbatim on the exact SHA (16/0, 42/0, 266/0-failed/3-skipped; check*.txt); VERSION=2.13.1, AGENTS.md block=2.13.1, CHANGELOG.md has the dated `## 2.13.1 - 2026-10-17` entry whose migration notes accurately describe the shipped fix (`install.py --update` ships the corrected tools; recorded holds keep keys and expiry).
- Y-05 - pass - the Result's claimed `Change:` SHA 5b3797bc6e483dce3b579c0f2c94f26acf466f58 is the branch HEAD of `t-056-limit-detection-accept` (git rev-parse, y05-branch-head.txt); claimed check counts (16/21/42/23/266) are truthful - 16, 42 and the 266/3-skipped totals re-verified verbatim, the 21 quota_groups and 23 tick counts are inside the green full-suite run; the claimed 17-file scope matches my independent diff.
New defects (outside the task):
- none
Cannot verify, needs:
- nothing - the two load-bearing claims and the scope/metadata checks all re-verified on the exact SHA; the deeper probe matrix (edge quotes, stop classifications, recovery capture, POSIX paths) stands on T-053's live evidence for this same SHA and was not re-run per the task's fast-path mandate.
Proposed memory updates:
- none - T-053's proposed known-issues update already covers the verified fix state; this task adds only that the T-056 acceptance artifact passed its fast-path re-verification.
