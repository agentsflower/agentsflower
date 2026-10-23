# T-053: Independently verify limit detection fix

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-052
Verifies: T-052 @ 5b3797bc6e483dce3b579c0f2c94f26acf466f58

## Goal

Independently evaluate the exact T-052 artifact (2.13.1 detector fix) against
every D-01..D-04 criterion in its Task File, in a disposable checkout. Never
repair the checked artifact; report the worst criterion as the verdict. Round
2's review (T-031) is context - re-verify on this SHA.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Task lifecycle)
- .agentflow/tasks/T-052-limit-detection-fix.md (contract + worker Result)
- .agentflow/tasks/T-031-verify-recoverable-handover.md (the partial review this answers; its R-01 evidence and New defects section)
- The candidate diff `git diff main...5b3797bc6e483dce3b579c0f2c94f26acf466f58` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-052 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] X-01: The round-2 false positive is dead at BOTH exit codes through the shipped CLI: replay T-031's exact failing fixtures (provider phrase inside quotes after shows/prints/displays/writes/echoes, phrase inside an already-open quote span) and confirm no limitHit; then prove the counter-cases still trip - bare provider phrase line, error-prefixed line, phrase AFTER a closed quote. Probe edge cases the worker did not enumerate (mixed quote styles, mid-word apostrophes like "you've", a real captured worker log that discusses quotas).
- [ ] X-02: A tool-wide hold's refusal message names the tool-wide hold even for a grouped session; group-scoped holds keep the group label. Reproduce through resource_check.
- [ ] X-03: No regression in anything T-030/T-050 verified: group-scoped holds, classification, takeover/leftover block, recovery capture, Resume semantics, fail-closed readers, bound acceptance, locked --stop - run the suite and the disposable probes.
- [ ] X-04: All claimed checks pass on the exact SHA (266 green claimed; re-run full suite); VERSION 2.13.1 / AGENTS block / CHANGELOG migration notes in sync; diff inside Allowed files; found-not-fixed items truthful and complete (the tester checks the "error:-prefixed still counts" semantic and the unclosed-delimiter edge).
- [ ] X-05: The D-01 fix does not over-skip: a provider phrase embedded in a REAL failing tool line (e.g., `ERROR: requests failed: you've hit your usage limit`) still records limitHit - prove with a fixture, not only unit tests.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` - quote-frame and signal classes.
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` - group scoping.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - classification, takeover, draft capture.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - group-aware needs.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` -> pass (16 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (42 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (266 ran / 0 failed, 3 skipped platform-specific, clean verbatim re-run; the first run flaked 265/266 on a Windows temp-file PermissionError inside ledger.py _write_atomic in test_workspace.WorkspaceTests.test_file_outside_allowed_fails_verify - green standalone and on re-run, same disclosed flake class the worker noted)
Evidence root: `.agentflow/tasks/.runtime/T-053.evidence/` (checked SHA 5b3797bc6e483dce3b579c0f2c94f26acf466f58 in a detached clean disposable checkout, worktree untouched; suite output check*.txt, fixture matrix x01-matrix-results.txt + fixtures/x01-*.log, edge probes x01-edge*.txt, live runs x02_x05_live.out.txt + x01_live2/x01_live3.out.txt + x03_*.out.txt; disposable machine registry only, never the live one)
Criteria:
- X-01 - pass - the round-2 false positive is dead at BOTH exit codes through the shipped CLI: T-031's exact failing fixtures `the banner shows|prints "you've hit your usage limit"` now read `no limit` @exit0 and @exit1, as do displays/writes/echoes and past tenses, an already-open span (`the transcript contains "...`), single quotes, backticks, nested quotes, and a real captured-worker-style quota-discussion log (x01-matrix-results.txt, fixtures/). Counter-cases still trip: bare `You've hit your usage limit`, `error: rate limit exceeded`, `ERROR: requests failed: you've hit your usage limit`, and every phrase-after-closed-quote variant without a report verb (`status 'ok';`, `log "probe done" -`, `x = "v";`, unlisted-verb `the transcript contains "ok" then ...`) -> `limit:`. Edge probes: mid-word apostrophes (don't/can't/won't/user's/O'Brien) open no span. Same through the real launcher, not only the CLI: fake workers printing quoted prose exited 0 -> completed limitHit=False, exit 1 -> implementation limitHit=False, quota-discussion log -> completed limitHit=False (x01_live*.out.txt). Reading note: X-01's "phrase AFTER a closed quote" reads as "outside any quoting/framing context" - with a report verb still scoping the line (`the banner shows "ok"; you've hit ...`) the phrase stays subject matter, the pre-existing reported-speech semantic now covering the added verbs; a provider error on its own or any later line always trips.
- X-02 - pass - live through resource_check in a disposable repo: under a bare `agy` tool-wide hold a grouped session (Model: claude-opus-4-6-thinking, group agy-claude-gpt) is refused `agy is limited until ...` - names the tool-wide hold, not the session's group, so T-031's mislabel is dead; the default gemini session reads the same. Under `agy:agy-claude-gpt` the refusal keeps the group label `agy group agy-claude-gpt is limited until ...` and the gemini launch proceeds to completion (quotaGroup=agy-gemini) (x02_x05_live.out.txt).
- X-03 - pass - no regression in anything T-030/T-050 verified: the 266-test suite covers group scoping, classification, takeover/leftover block, recovery capture, Resume, fail-closed readers, bound acceptance, locked --stop; live disposable probes on this SHA reconfirm all six stop classifications (limit/timeout/verification/completed/implementation/stopped), an orphan descendant blocks relaunch (attempt count stays 1) and --stop refuses while strays run (lock kept, dead attempt closed after), a mid-work kill records a recovery with branch/HEAD/file statuses/stopReason and no file contents, the successor gets the handover with drafts preserved and `Resume: start fresh` clears only that worktree, the recovery record is bounded at 200 + truncated (x03_*.out.txt).
- X-04 - pass - all five claimed checks pass verbatim on the exact SHA (the rerun matches the claimed 266/0-failed/3-skipped; the single first-run flake is the Windows temp-lock class the worker disclosed). VERSION=2.13.1, AGENTS block=2.13.1 (version line only), CHANGELOG 2.13.1 entry with migration notes dated 2026-10-17. The task's own diff f6d746b..5b3797b is 7 files, all inside Allowed files. Found-not-fixed items verified truthful: an error:-prefixed line still counts even when it quotes a phrase (outer precedence proven live), the unclosed-delimiter edge reproduces (`a"b you've hit your usage limit` -> skipped), and the Transcript Youtube installed detector is still the pre-fix file (byte-identical except the run-task.ps1 docstring line; none of the new verbs) so it carries the same gap.
- X-05 - pass - no over-skip: the fixture `ERROR: requests failed: you've hit your usage limit` detects `limit:` at both exit codes through the CLI, and a real fake-tool worker printing that line and exiting 1 records limitHit=True + stopReason=limit in its attempt record (x02_x05_live.out.txt).
New defects (outside the task):
- none material. Observation only, not a defect: a report verb scopes the rest of its line, so `the banner shows "ok"; you've hit your usage limit` reads as subject matter - the same framing semantic responded/said/quoted already had at 2.13.0, documented in the docstring and CHANGELOG.
Cannot verify, needs:
- the POSIX descendant-detection path (sid scan) is still Windows-untested, same as T-031 noted; the Job Object + parent-chain paths were proven live.
Proposed memory updates:
- known-issues.md: the residual quote-gap T-031 recorded is verified dead at 2.13.1 on T-031's exact fixtures (both exit codes, through the shipped CLI and real launcher attempts); the T-031 mislabel (a tool-wide hold named as the session's group) is verified fixed through resource_check.
