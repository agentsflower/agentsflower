# T-101: Independently verify shipped-features docs alignment

Role: tester
Tool: devin
Stage: 5
Depends on: T-098
Verifies: T-098 @ 38f94f6482e1fb97ad4991cee8ba99203d2b5f65

## Goal

Independently evaluate the exact T-098 artifact (commit `38f94f6482e1fb97ad4991cee8ba99203d2b5f65` on
`t-098-shipped-features-docs`) against every S-01..S-05 criterion in its Task
File, in a disposable checkout. The artifact rewrites the user-facing feature
docs to describe shipped 2.15.x behavior (probes, worker bounds, dispatch,
quota, gate done, recovery capture), corrects stale tool notes, records the
real remote CI run, and bumps VERSION/AGENTS block/CHANGELOG to 2.15.6.
Fresh session, not the developer conversation. Same CLI per the human's Devin
preference: Codex and Claude CLIs are statically excluded in
model-options.json; the observed agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-098-shipped-features-docs.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...38f94f6482e1fb97ad4991cee8ba99203d2b5f65` in the disposable checkout
- .agentflow/tools/run_task.py (tool_argv, MODEL_PROBE_ARGS, worker timeout) and .agentflow/tools/cli.py (the real subcommand list) - the code the docs must match

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-098 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (S-01) Spot-check the documented feature claims against code: the `agentflow` CLI subcommand list matches `cli.py`; probe env vars, `AGENTFLOW_WORKER_TIMEOUT`, dispatch modes, quota policy keys, and per-tool worker argv match `run_task.py`/related tools; no doc describes removed or never-shipped behavior as current.
- [ ] V-02: (S-02) The corrected tool notes are accurate: agy workers run `-p --output-format stream-json` per `run_task.py` tool_argv; Devin worker argv is `--permission-mode dangerous --respect-workspace-trust false`; Codex Windows-sandbox and conductor Windows-only notes are stated where the docs can carry them.
- [ ] V-03: (S-03/S-04) No allowed doc promises generated handoffs (status derives from records, handoff stays authored); release-validation.md matches `.github/workflows/ci.yml` and typesafe.md matches `route.py`.
- [ ] V-04: (S-05) All three of T-098's Checks pass verbatim on the exact SHA; VERSION 2.15.6, AGENTS version block, and the CHANGELOG 2.15.6 entry agree, and migration notes say what an installed project must do.
- [ ] V-05: The artifact is exactly one commit on t-098-shipped-features-docs; `git diff main...38f94f6482e1fb97ad4991cee8ba99203d2b5f65` stays inside T-098's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-06: Map all S-01..S-05 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py`
- `python -m unittest discover -s .agentflow/tests -p test_install.py`
- `python -m unittest discover -s .agentflow/tests -p test_approval.py`

## Execution bounds

Run the scoped checks verbatim on the checked SHA; verify doc claims against
the named code paths - this is a docs-accuracy review, not a line-by-line
proofread. No code fixes, no gratuitous whole-suite run. Save evidence in
AGENTFLOW_EVIDENCE with basenames starting `T-101.`; put `evidence:` markers
at line end followed only by intended claim paths - never quote an
`evidence:` marker inside prose (the validator reads it as a claim).
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result
