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
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (5 passed / 0 failed)
Criteria:
- V-01: pass - the documented feature claims match the code on the checked SHA: the agentflow subcommand list (install/run/gate/done/accept/ledger/mcp/hooks/dashboard) equals cli.py:167-192 and gate verbs equal gate.py:975-983; AGENTFLOW_<TOOL>/_ARGS/_PROBE (`off` refuses unattended), _MODEL_PROBE=on opt-in builtin, AGENTFLOW_WORKER_TIMEOUT 1200, the four autonomy budgets, watchdog, nested-launch delegate rule, power_guard, gate done + trial merge + bound-PASS reuse, dispatchShadow/off-shadow-active modes, quota-group holds and the declared quota-policy/quota-samples keys all match run_task.py/tick.py/dispatch.py/machine_capacity.py/quota_groups.py line-for-line (references in the audit file); the corrected stale items (2.12.0 badge, nine-jobs-never-ran, old gate-verb list, bare-flag run_task argv) are gone and nothing in the diff describes removed/never-shipped behavior as current. One disclosure: the model probe is called "opt-in" and the doc leaves implicit that unset refuses an unattended launch - the launcher's own docstring uses the same "explicit opt-in" framing and the refusal is the documented check-failure path, so this is consistent, not a defect. evidence: .agentflow/tasks/.runtime/T-101.evidence/T-101.doc-audit.txt .agentflow/tasks/.runtime/T-101.evidence/T-101.candidate-diff.txt
- V-02: pass - tool notes match tool_argv()/MODEL_PROBE_ARGS exactly: agy tester `-p --output-format stream-json` non-interactive (developer adds --dangerously-skip-permissions, run_task.py:351-353); Devin `-p --permission-mode dangerous --respect-workspace-trust false` both roles (:355) with the opt-in probe on `--permission-mode auto` (:174-175) - identical to this attempt's recorded launch.argv and modelProbe.argv; Codex dev danger-full-access / tester workspace-write+network (:339-345); claude --dangerously-skip-permissions / --allowedTools (:348-350); the Codex Windows-sandbox write-denial limitation and the conductor/autostart Windows-only notes are stated in GUIDE.md, README.md and .agentflow/README.md where they belong. evidence: .agentflow/tasks/.runtime/T-101.evidence/T-101.doc-audit.txt
- V-03: pass - no changed doc promises generated handoffs: GUIDE.md:200 states status derives from records and handoff.md stays an authored note. release-validation.md matches ci.yml exactly (9 matrix + 2 package + 2 mcp = thirteen jobs, 20/30-min bounds, push/PR/workflow_dispatch, contents:read + persist-credentials:false, mcp `needs: tests` skip) and records run 39026298541 (main@50adf65) identically to known-issues.md including the local Win10/Py3.13 204-test green reproduction; typesafe.md audited against route.py - schemaVersion 1 bound to requirementsHash, ok/blocked/low-confidence/failed, floor/recommended/quota_group/model_by_effort, assessment_problems/admission/backup_ok/log_admission, AGENTFLOW_BACKUP_ROUTING, key-file vars all present as documented - the claimed "no correction needed" stands. evidence: .agentflow/tasks/.runtime/T-101.evidence/T-101.doc-audit.txt
- V-04: pass - all three of T-098's Checks pass verbatim on the exact SHA in this disposable checkout: the two scoped files above plus `python -m unittest discover -s .agentflow/tests` -> Ran 424 tests in 343.341s, OK (skipped=3), reproducing the recorded 424/0/3 evidence rather than trusting it. VERSION reads 2.15.6, the AGENTS.md version block reads 2.15.6, and the CHANGELOG `## 2.15.6 - 2026-10-21` entry agrees; its Migration paragraph tells an installed project to run install.py --update with no configuration, workflow or contract change. evidence: .agentflow/tasks/.runtime/T-101.evidence/T-101.check-test_layout.txt .agentflow/tasks/.runtime/T-101.evidence/T-101.check-test_install.txt .agentflow/tasks/.runtime/T-101.evidence/T-101.check-full-suite.txt
- V-05: pass - `git log main..38f94f6` lists exactly one commit ([T-098] docs: align shipped-features documentation with 2.15.x behavior); branch t-098-shipped-features-docs tip = 38f94f6482e1fb97ad4991cee8ba99203d2b5f65 = the checked SHA; the diff touches only 8 files, all inside T-098's Allowed files (README, GUIDE, RELEASE_NOTES, .agentflow/README, release-validation, VERSION, AGENTS, CHANGELOG; typesafe.md unchanged as claimed); this Task File's header sha256 equals the launch baseline taskHash 63e8cd0e..., the checked T-098 file's sha256 equals baseline checkedFileHash 2c22a4b2..., and the developer worktree is clean at 38f94f6. evidence: .agentflow/tasks/.runtime/T-101.evidence/T-101.doc-audit.txt .agentflow/tasks/.runtime/T-101.evidence/T-101.candidate-diff.txt
- V-06: pass - S-01 maps to V-01, S-02 to V-02, S-03/S-04 to V-03, S-05 to V-04; every verdict above rests on direct code reads, verbatim command output and hash comparisons saved under the evidence folder - nothing was inferred from the developer's green summary.
New defects (outside the task):
- none observed in the checked artifact; the stale copies the developer disclosed (tool-routing.md ~line 46 agy interactive-tester claim, GUIDE.ru.md -Manual wording, the 2026-10-03 Antigravity known-issues entry) sit outside T-098's Allowed files and were already reported under "Found, not fixed".
Cannot verify, needs:
- nothing.
Proposed memory updates:
- none.
