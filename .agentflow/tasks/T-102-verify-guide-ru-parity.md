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
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (5 passed / 0 failed)
Criteria:
- V-01: pass - (G-01) GUIDE.ru.md is Russian and mirrors GUIDE.md section-by-section: identical 20-heading sequence at identical line numbers, both files 236 lines; every pure-ASCII line in the Russian file exists verbatim in GUIDE.md (Compare-Object: 0 RU-only ASCII lines, so no invented commands/URLs/identifiers; 74 EN-only lines are translated prose). Section-by-section read found the same facts: install/update/migrate/package/MCP/machine-resources surface, launch checks and worker bounds, fixed per-tool argv, recovery semantics. Three small RU-only sentences exist, each verified true (detached background workers - protocol; English dashboard UI - build.py/RELEASE_NOTES; gitignore negation tip); no Russian-only sections remain; no invented results, URLs or metrics - evidence: .agentflow/tasks/.runtime/T-102.evidence/T-102.parity.txt
- V-02: pass - (G-02) all four guarantees survive in the Russian text: the roles table keeps the explicit Single Mode vs role-team split (GUIDE.ru.md:160-166); one task per fresh session (:165); one commit per task (:173); deployer always --manual with a human start (:168); no push/merge/deploy - merges belong to accept.py, deployment starts only after the human's explicit yes (:230). Nothing in the file relaxes them - evidence: .agentflow/tasks/.runtime/T-102.evidence/T-102.parity.txt
- V-03: pass - (G-03) .agentflow/VERSION = 2.15.6, the AGENTS.md version block = 2.15.6, and the top CHANGELOG entry "## 2.15.6 - 2026-10-21" all agree; the changelog describes T-097+T-098+T-099 as one coherent documentation-alignment step. Migration notes verified against install.py itself: OWNED ships roles/ recursively (so tool-routing.md), typesafe.md, README.md and the version blocks via --update, and GUIDE.ru.md is not in OWNED - "template-side, not installed" is accurate. RELEASE_NOTES.md was retargeted to the pending 2.15.6 and keeps honest limits (no tag, no PyPI, no green macOS) - evidence: .agentflow/tasks/.runtime/T-102.evidence/T-102.version-routing.txt
- V-04: pass - (G-05) tool-routing.md:46 now matches run_task.py tool_argv() exactly: agy developer `-p --dangerously-skip-permissions --output-format stream-json`, tester `-p --output-format stream-json`, both non-interactive ("print mode" is the file's established term for -p). The stale interactive -i / /exit tester claim is gone; a scoped search found no other stale interactive-tester claim in the diff; the IDE line still says -Manual - evidence: .agentflow/tasks/.runtime/T-102.evidence/T-102.version-routing.txt
- V-05: pass - (G-04) all three Checks above pass verbatim on 4519a63 (6/0, 15/0, 5/0). T-099's third check `python -m unittest discover -s .agentflow/tests` was also run once on the exact SHA for completeness: 424 passed / 0 failed / 3 skipped - evidence: .agentflow/tasks/.runtime/T-102.evidence/T-102.checks.txt
- V-06: pass - the artifact is exactly one commit on t-099-guide-ru-parity-release (`git rev-list --count main..4519a63` = 1; branch points at 4519a63; the disposable checkout is clean). `git diff main...4519a63` touches only GUIDE.ru.md, CHANGELOG.md, RELEASE_NOTES.md and .agentflow/roles/tool-routing.md - all inside T-099's Allowed files. The T-099 Task File is committed and unmodified in the main repository, and T-099's last launcher attempt is recorded exited/completed, meaning its endcheck (Task File above Result unchanged) passed - evidence: .agentflow/tasks/.runtime/T-102.evidence/T-102.diff-scope.txt
- V-07: pass - every G-01..G-05 maps to a V-criterion above with measured evidence; nothing was inferred from the developer's green summary - each claim was re-verified against sources (install.py OWNED list, run_task.py tool_argv(), git state, verbatim unittest output)
New defects (outside the task):
- install.py:269's refusal message points readers to GUIDE.md "Migration from the root layout", but the guide's actual section is "C. Migrate the old layout" - a pre-existing wording mismatch (both files unchanged by this artifact)
Cannot verify, needs:
- nothing
Proposed memory updates:
- none new; the T-099 developer's two proposals (dated decisions.md entry for the 2.15.6 train; known-issues.md annotation of the 2026-10-03 Antigravity entry) are accurate and remain worth applying
