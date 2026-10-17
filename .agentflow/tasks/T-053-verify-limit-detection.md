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
