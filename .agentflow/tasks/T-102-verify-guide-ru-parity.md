# T-102: Independently verify Russian guide parity and release finalization

Role: tester
Tool: devin
Stage: 5
Depends on: T-099
Verifies: T-099 @ 4519a63c17ff05b5962cb9452dedcaabaec0ced4

## Goal

Independently evaluate the exact T-099 artifact
(4519a63c17ff05b5962cb9452dedcaabaec0ced4) against every G-01..G-05 criterion
in its Task File, in a disposable checkout. The artifact rewrites GUIDE.ru.md
to section-by-section parity with the post-T-098 GUIDE.md, corrects the stale
agy-tester claim in tool-routing.md, and folds the documentation-alignment
train into one 2.15.6 release record (CHANGELOG + RELEASE_NOTES). Fresh
session, not the developer conversation. Same CLI per the human's Devin
preference: Codex and Claude CLIs are statically excluded in
model-options.json; the observed agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-099-guide-ru-parity-release.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...4519a63c17ff05b5962cb9452dedcaabaec0ced4` in the disposable checkout
- GUIDE.md next to GUIDE.ru.md in the checkout (the parity pair)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-099 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (G-01) GUIDE.ru.md is Russian and section-by-section parallel to GUIDE.md on the checked SHA (same heading sequence, same facts); no invented results, URLs or metrics; no Russian-only sections left that the English guide does not carry.
- [ ] V-02: (G-02) The Single/Team mode choice, one-task-per-fresh-session concurrency, one-commit rule and deployer --manual/human-approval rules survive in the Russian text - nothing relaxes them.
- [ ] V-03: (G-03) VERSION, AGENTS.md version block and CHANGELOG agree at 2.15.6; the changelog describes the T-097+T-098+T-099 train as one coherent step and migration notes match what install.py --update actually ships (verify GUIDE.ru.md's install status against install.py, don't trust the claim).
- [ ] V-04: (G-05) tool-routing.md's agy line now matches `run_task.py` tool_argv() exactly; no other stale interactive-tester claim remains in the diff scope.
- [ ] V-05: (G-04) All three of T-099's Checks pass verbatim on the exact SHA.
- [ ] V-06: The artifact is exactly one commit on t-099-guide-ru-parity-release; `git diff main...4519a63` stays inside T-099's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-07: Map all G-01..G-05 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py`
- `python -m unittest discover -s .agentflow/tests -p test_install.py`
- `python -m unittest discover -s .agentflow/tests -p test_approval.py`

## Execution bounds

Run the scoped checks verbatim on the checked SHA; compare the two guides
side by side and verify version/changelog facts against install.py and the
version blocks - this is an accuracy review, not a translation-quality
critique. No code fixes, no gratuitous whole-suite run. Save evidence in
AGENTFLOW_EVIDENCE with basenames starting `T-102.`; put `evidence:` markers
at line end followed only by intended claim paths - never quote an
`evidence:` marker inside prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-07 plus `Verdict:`.

## Result
