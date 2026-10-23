# T-090: Independently verify config precedence and parsing scope repair

Role: tester
Tool: devin
Model: gpt-6-astra-high
Stage: 5
Depends on: T-089
Verifies: T-089 @ 52b06aacbd1a5b5874b82cf8ff1813d17ac65a40

## Goal

Independently evaluate the exact T-089 artifact
(52b06aacbd1a5b5874b82cf8ff1813d17ac65a40) against every G-01..G-05 criterion
in its Task File, in a disposable checkout. The artifact is the twice-rejected
T-076 line (07fbeed -> f6bc519) plus one commit repairing T-088's F-01:
repeated Codex config overrides now resolve last-wins (the value the worker
receives), and `-c`/`--config` k=v parsing is scoped to codex only. Reproduce
the F-01 bypass live and prove it now refuses; prove the admitted identity
equals the effective argv; prove no regression of the T-086 coverage. Fresh
session, not the developer conversation. Same CLI per the human's Devin
preference: Codex worker sandbox writes were environment-blocked on this
machine; observed agy holds remain honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-089-config-precedence-admission.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-088-verify-config-alias.md (F-01 verdict this repair answers)
- .agentflow/tasks/.runtime/T-088.evidence/T-088.live-probes.json + T-088.codex-precedence-sources.json (the F-01 probe shape and Codex semantics)
- .agentflow/tools/route.py (env_selected), .agentflow/tools/run_task.py (selected_model, remove_overridden, tool_argv)
- .agentflow/tests/test_routing_core.py, .agentflow/tests/test_run_task.py
- The candidate diff `git diff f6bc519...52b06aacbd1a5b5874b82cf8ff1813d17ac65a40` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-089 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040, T-074, T-082, T-076 and T-087 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (G-01) The artifact is exactly f6bc519 plus one commit; `git diff f6bc519...HEAD` touches only route.py, run_task.py, the two test files and CHANGELOG.md; `git diff main...HEAD` stays inside T-089's Allowed files; everything else is byte-identical to what T-088 reviewed.
- [ ] V-02: (G-02) Reproduce F-01 live in the disposable checkout: `--config model_reasoning_effort=high --config=model_reasoning_effort=low` and the `-c` equivalent are resolved as the FINAL value and refused against >=high before CLI/lease/spawn; the same flags at a >=low requirement admit and record low; the single adequate `--config` case still admits with the resolved identity. Confirm dedicated -m/--model flags keep precedence over `-c model=` the way Codex applies them.
- [ ] V-03: (G-03) Prove the cross-tool scoping live: `AGENTFLOW_DEVIN_ARGS` carrying `--config` tokens is not interpreted as a downgrade, is admitted at the header identity, and every token reaches the worker argv verbatim; claude/agy env args are covered at least by unit evidence; `AGENTFLOW_CODEX_ARGS` keeps the documented forms.
- [ ] V-04: (G-04) The new regression tests genuinely cover repeated-key refusal and admission through the real launch path and the cross-tool non-interpretation; an AST-extracted pre-fix env_selected still misses the case (negative control); no live TypeSafe or real Codex needed.
- [ ] V-05: (G-05) All three scoped Checks pass verbatim on the exact SHA; the recorded full suite (409 run / 0 failed / 3 skipped) is reviewed not repeated; VERSION/AGENTS/CHANGELOG consistent at 2.15.3; T-040 not claimed complete; T-078 ownership unchanged.
- [ ] V-06: Map all G-01..G-05 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary. Evaluate the disclosed boundaries (whitespace-split quoted values, non-k=v passthrough, no TOML escapes, dedicated-flag first-wins) - whether any is an in-scope identity-parity defect or a correctly bounded limitation.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`

## Execution bounds

20-minute cap. Run scoped checks verbatim on the checked SHA, reproduce the
F-01 bypass/refusal live in disposable fixtures, verdict by evidence. No code
fixes, no gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE
with basenames starting `T-090.`; put `evidence:` markers at line end
followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result

Outcome: completed
Verdict: pass

Reviewed artifact: 52b06aacbd1a5b5874b82cf8ff1813d17ac65a40 in the launcher's disposable T-090 checkout, Windows / Python 3.13.7. The repeated-config bypass and cross-tool parsing hazard are repaired for the supported forms. Product code, tests, configuration, canonical memory and the developer artifact were not changed; no commit was made. An intermittent test lifecycle timeout is disclosed below rather than omitted from the passing rerun.

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (14 passed / 0 failed, exit 0).
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> initial fail (61 passed / 1 failed, exit 1); justified verbatim rerun on the unchanged SHA -> pass (62 passed / 0 failed, exit 0). The initial failure was a 30-second wait for the fake Devin attempt to become exited, not an identity assertion. Its focused repetition also passed. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_run_task.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.devin-regression-focused.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_run_task-rerun.log`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed, exit 0).
- Additional changed-test coverage: `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (22 passed / 0 failed, exit 0).
- Independent probes: 19 passed / 0 failed. Recorded developer full-suite summary reviewed, not repeated: 409 run in 484.139s, 406 passed / 0 failed / 3 skipped. The saved full-suite file is explicitly a summary, not a complete raw transcript. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.live-probes.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.recorded-full-suite.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.developer-transcript.log`

Criteria:
- V-01: pass - G-01: exactly one commit follows f6bc519631813c07583e7c5b527df97671266f84, which is HEAD's sole parent. Only route.py, run_task.py, the two specified test files and CHANGELOG.md differ; the other 183 tracked blobs are identical. All 12 main...HEAD paths, against local main 2236ad24d31c44fa6455ac5a7f44ec16fde37560, are allowed; model-options changes policy text only and AGENTS changes only its version. Both checked and developer worktrees remain clean and their HEADs and the T-089 Task File remain unchanged. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.artifact.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.candidate.diff` `.agentflow/tasks/.runtime/T-090.evidence/T-090.release-scope.diff` `.agentflow/tasks/.runtime/T-090.evidence/T-090.integrity-final.json`
- V-02: pass - G-02: live long/mixed and short repeated high-to-low forms resolve low and refuse at >=high before every fake CLI call, registry/lease, attempt, spawn and admission event. Both forms admit at >=low and record effort/tier low; captured worker argv independently resolves to that identity. Single adequate config, unrelated x=1, header precedence, repeated model keys, and dedicated model flags before and after config keys pass. The original three single-effort and three single-model downgrade spellings still refuse. Dedicated-model precedence is corroborated by pinned Codex source. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.live-probes.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.probes.py` `.agentflow/tasks/.runtime/T-090.evidence/T-090.source-review.md` `.agentflow/tasks/.runtime/T-090.evidence/T-090.codex-core-config.rs`
- V-03: pass - G-03: a live Devin launch with two --config pairs admits the header model swe-2-high; all four env tokens are captured verbatim in the actual worker argv. Config keys are not interpreted or removed for Devin/Claude/agy in independent unit probes and the changed tests. Codex retains the three documented forms. This conclusion uses actual token capture, not only the regression test's masked-token count. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.live-probes.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.devin-probe-correction.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_routing_core.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.source-review.md`
- V-04: pass - G-04: the new regressions execute real launcher subprocesses with disposable repositories, fake CLIs and synthetic requirements-bound assessments. They cover repeated-key refusal/admission and cross-tool non-interpretation; the prior alias coverage is preserved. Independent probes additionally establish absence of CLI/lease/spawn on refusal and raw argv/identity parity on admission. AST-extracted pre-fix env_selected and its helpers from f6bc519 still resolve both high-to-low examples as high, while the candidate resolves low. No live TypeSafe or real Codex inference was used. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.candidate.diff` `.agentflow/tasks/.runtime/T-090.evidence/T-090.live-probes.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_run_task-rerun.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_routing_core.log`
- V-05: pass - G-05: all three scoped commands have passing verbatim runs on the exact unchanged SHA, with the first launcher failure explicitly retained. The recorded full-suite summary and developer narrative were reviewed without another whole-suite run. Local VERSION, AGENTS and CHANGELOG agree at 2.15.3; only one clause was added to the existing release entry. T-040 is not claimed complete; T-078 retains scheduling, backup selection and reporting integration. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_route.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_run_task-rerun.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_worker_watchdog.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.recorded-full-suite.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.source-review.md`
- V-06: pass - G-01..G-05 are mapped above using direct observations. Whitespace-split quoted values remain a support limitation; non-k=v values are preserved but rejected by downstream config parsing; the escaped-low TOML example is refused as unverifiable before launch. Dedicated repeated model flags are invalid in the inspected Codex scalar CLI definition, so inherited first-wins does not establish a valid silently weaker run. These are bounded limitations for this contract's supported forms, not a reproduced identity-parity bypass. The initial lifecycle timeout, summary-only full-suite evidence, and limits of source-based downstream checks are disclosed. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.source-review.md` `.agentflow/tasks/.runtime/T-090.evidence/T-090.live-probes.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.codex-shared-options.rs` `.agentflow/tasks/.runtime/T-090.evidence/T-090.reference-codex-config-override.rs`

New defects and observations outside the parsing repair:
- Intermittent lifecycle/test behavior: the initial test_config_keys_are_not_interpreted_for_other_tools reached an admitted, running fake-worker attempt but did not observe exited within 30 seconds. The focused repetition passed in 2.164s and the full launcher rerun passed 62/62 in 199.805s. The original fixture was already removed by teardown and its PID was absent when inspected. The cause and attribution remain unknown; this observation is not claimed repaired or dismissed as a known environment fault. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_run_task.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.devin-regression-focused.log` `.agentflow/tasks/.runtime/T-090.evidence/T-090.test_run_task-rerun.log`
- The independent probe initially used an incorrect slice offset for Devin argv. Actual captured tokens were correct; only the evidence assertion was corrected and that probe repeated. Original evidence is retained, and the final report discloses the correction. No product change was needed. evidence: `.agentflow/tasks/.runtime/T-090.evidence/T-090.live-probes-initial.json` `.agentflow/tasks/.runtime/T-090.evidence/T-090.devin-probe-correction.log`

Cannot verify, needs:
- No environment blocker prevented the assigned parsing/admission checks. Fake workers establish launcher behavior; downstream precedence and invalid-flag conclusions use saved and freshly pinned Codex source, not an installed provider inference run.
- The developer's full-suite result is reviewed evidence, not an independent full-suite replay. Duplicate dedicated flags in arbitrary other CLIs are not covered by the Codex source conclusion.
- If the lifecycle timeout recurs, preserve the failing fixture and worker logs before teardown to determine its cause.

Proposed memory updates:
- T-090 independently passes 52b06aa: F-01 now refuses high-to-low overrides before launch, admitted identities match captured supported argv, and config parsing is Codex-only. Preserve the T-086/T-088 rejection history and this verification's initial lifecycle timeout alongside its passing rerun. T-078 ownership and the remaining T-040 work are unchanged.
