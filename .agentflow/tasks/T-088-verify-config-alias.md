# T-088: Independently verify codex --config alias admission repair

Role: tester
Tool: devin
Model: gpt-6-astra-high
Stage: 5
Depends on: T-087
Verifies: T-087 @ f6bc519631813c07583e7c5b527df97671266f84

## Goal

Independently evaluate the exact T-087 artifact
(f6bc519631813c07583e7c5b527df97671266f84) against every D-01..D-04 criterion
in its Task File, in a disposable checkout. The artifact is the T-086-failed
T-076 launch-admission artifact at 07fbeed plus one commit repairing the
D-01 bypass (env effort/model override through Codex's `--config` spellings
was admitted unseen). Reproduce the original bypass live and prove it now
refuses; prove the rest of the artifact did not regress. Fresh session, not
the developer conversation. Same CLI per the human's Devin preference: Codex
worker sandbox writes were environment-blocked on this machine; observed agy
holds remain honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-087-codex-config-alias-admission.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-086-verify-launch-admission.md (the fail verdict this repair answers: D-01)
- .agentflow/tasks/.runtime/T-086.evidence/T-086.codex-alias.json + T-086.live-probes.json (the original bypass shape)
- .agentflow/tools/route.py (env_selected, _config_kv/_config_value), .agentflow/tools/run_task.py (selected_model, remove_overridden, config_kv)
- .agentflow/tests/test_routing_core.py, .agentflow/tests/test_run_task.py
- The candidate diff `git diff 07fbeed...f6bc519631813c07583e7c5b527df97671266f84` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-087 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040, T-074, T-082 and T-076 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (D-01) The artifact is exactly 07fbeed plus one commit; `git diff 07fbeed...HEAD` touches only route.py, run_task.py, the two test files and CHANGELOG.md; `git diff main...HEAD` stays inside T-087's Allowed files; everything else is byte-identical to what T-086 reviewed.
- [ ] V-02: (D-02) Reproduce the T-086 bypass live in the disposable checkout: `AGENTFLOW_CODEX_ARGS` carrying `--config model_reasoning_effort=low`, `--config=model_reasoning_effort=low` and `-c model_reasoning_effort=low` are all refused against a >=high requirement before CLI/lease/spawn; an adequate `--config` value is admitted with the resolved identity recorded; a `--config model=` downgrade is refused; unrelated `--config` keys do not corrupt parsing or the outgoing argv. Also confirm the admitted argv matches the admitted identity (no divergence between what admission saw and what the worker would run).
- [ ] V-03: (D-03) The new regression tests genuinely cover each spelling against the live launch path or admission call (disposable launcher, fake codex, synthetic records); a negative control shows the pre-fix env_selected would have missed the alias; no live TypeSafe calls or real Codex needed.
- [ ] V-04: (D-04) All three scoped Checks pass verbatim on the exact SHA; the recorded full suite (403 run / 0 failed / 3 skipped) is reviewed not repeated; VERSION/AGENTS/CHANGELOG consistent at 2.15.3 with only the alias line added; T-040 not claimed complete; T-078 ownership of backup/report integration unchanged.
- [ ] V-05: Map all D-01..D-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary. Note whether the fix introduces any new parsing hazard (e.g. `--config` values that are not k=v, quoting, other tools' args).

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`

## Execution bounds

20-minute cap. Run scoped checks verbatim on the checked SHA, reproduce the
bypass/refusal live in disposable fixtures, verdict by evidence. No code
fixes, no gratuitous whole-suite run. Save evidence in AGENTFLOW_EVIDENCE
with basenames starting `T-088.`; put `evidence:` markers at line end
followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-05 plus `Verdict:`.

## Result

Outcome: completed
Verdict: fail

Reviewed artifact: f6bc519631813c07583e7c5b527df97671266f84 in the launcher's isolated checkout, Windows / Python 3.13.7. The original single-override bypass is repaired, but repeated supported config overrides still admit an identity different from the worker's effective configuration. Product code, tests, configuration, canonical memory and the developer artifact were not changed; no commit was made.

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (14 passed / 0 failed, exit 0).
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (58 passed / 0 failed, exit 0).
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed, exit 0).
- Additional focused check of the changed routing-core tests: `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (20 passed / 0 failed, exit 0).
- Recorded full suite reviewed, not repeated: 403 run in 453.628s, OK (3 skipped), meaning 400 passed / 0 failed / 3 skipped. Independent probes: 12 pass, 1 fail. evidence: `.agentflow/tasks/.runtime/T-088.evidence/T-088.check-results.md` `.agentflow/tasks/.runtime/T-088.evidence/T-088.scoped-checks.log` `.agentflow/tasks/.runtime/T-088.evidence/T-088.test_routing_core.log` `.agentflow/tasks/.runtime/T-088.evidence/T-088.recorded-full-suite.log`

Criteria:
- V-01: pass - D-01: HEAD has exactly one parent, 07fbeed18e6a8d1a60eee491e1b81171b8090a6d, and is exactly one commit ahead. Only route.py, run_task.py, test_routing_core.py, test_run_task.py and CHANGELOG.md differ; the other 183 tracked blobs are identical. The main...HEAD paths, against main at 2236ad24d31c44fa6455ac5a7f44ec16fde37560, are all within T-087's Allowed files. Both checked and developer worktrees remained clean and their HEADs and the T-087 Task File hash stayed unchanged. evidence: `.agentflow/tasks/.runtime/T-088.evidence/T-088.artifact.json` `.agentflow/tasks/.runtime/T-088.evidence/T-088.candidate.diff` `.agentflow/tasks/.runtime/T-088.evidence/T-088.integrity-before.json` `.agentflow/tasks/.runtime/T-088.evidence/T-088.integrity-after-probes.json`
- V-02: fail - D-02: the three isolated effort downgrades and three model-key downgrades all refuse before any fake CLI call, registry/lease, attempt or admission event. Adequate long/equals aliases, model overrides, unrelated x=1 and header precedence pass, with captured worker argv matching construction. However F-01 below permits high followed by low, records high and starts a worker carrying both overrides; Codex applies the last value. The required admitted-identity/argv parity therefore fails. evidence: `.agentflow/tasks/.runtime/T-088.evidence/T-088.live-probes.json` `.agentflow/tasks/.runtime/T-088.evidence/T-088.probes.py` `.agentflow/tasks/.runtime/T-088.evidence/T-088.codex-overrides.rs` `.agentflow/tasks/.runtime/T-088.evidence/T-088.codex-precedence-sources.json`
- V-03: pass - D-03: the new tests run real launcher subprocesses in disposable Git repositories, use synthetic requirements-bound assessment records and fake Codex executables, and cover all three required spellings. Independent probes additionally capture every fake CLI invocation and the real worker argv. An AST-extracted env_selected from 07fbeed misses both long effort aliases and the model alias while the current function resolves them; the short-effort control resolves low in both versions. The 58 launcher and 20 routing-core tests pass. No real Codex inference or live TypeSafe endpoint is required or used; HTTP tests use a local stand-in. The regression tests do not cover repeated-key precedence, which explains their green result despite F-01. evidence: `.agentflow/tasks/.runtime/T-088.evidence/T-088.source-review.txt` `.agentflow/tasks/.runtime/T-088.evidence/T-088.live-probes.json` `.agentflow/tasks/.runtime/T-088.evidence/T-088.check-results.md`
- V-04: pass - D-04: all three scoped Checks pass verbatim on the exact SHA. The saved full-suite output and T-087 attempt-2 narrative were reviewed without another full run. VERSION, AGENTS and the existing CHANGELOG entry agree at 2.15.3; only the alias sentence was added by this repair, with no second release. T-040 is not claimed complete and T-078 retains automatic scheduling, backup/report integration and the previously disclosed tester-routing gap. This passes the stated validation/release criterion; the broader alias guarantee remains limited by D-02/F-01. evidence: `.agentflow/tasks/.runtime/T-088.evidence/T-088.check-results.md` `.agentflow/tasks/.runtime/T-088.evidence/T-088.recorded-full-suite.log` `.agentflow/tasks/.runtime/T-088.evidence/T-088.source-review.txt` `.agentflow/tasks/.runtime/T-088.evidence/T-088.candidate.diff`
- V-05: pass - D-01 pass, D-02 fail, D-03 pass, D-04 pass, with the narrow versus universal alias reading made explicit. Parsing review distinguishes the inherited first-value precedence and whitespace-splitting limitations from the newly broadened cross-tool config interpretation. Malformed non-k=v arguments are preserved, simple quoted low is refused, and quote stripping does not implement TOML escapes. These observations and the concrete remaining bypass are reported below rather than inferred from green tests. evidence: `.agentflow/tasks/.runtime/T-088.evidence/T-088.parsing-attribution.json` `.agentflow/tasks/.runtime/T-088.evidence/T-088.live-probes.json` `.agentflow/tasks/.runtime/T-088.evidence/T-088.source-review.txt`

Defects and parsing observations:
- F-01 (high, D-02 / V-02): use a disposable Codex task with Model gpt-6.1-sol, no header effort, and a matching ok assessment requiring at least high. Set AGENTFLOW_CODEX_ARGS to `--config model_reasoning_effort=high --config=model_reasoning_effort=low` and launch. Expected: resolve the final low override and refuse before CLI/lease/spawn. Actual: exit 0, admission records effort/tier high with deviation false, an attempt and lease are created, and the fake worker receives both overrides in that order. route.env_selected only assigns effort while it is None; tool_argv preserves both when the header has no effort. The saved Codex source at openai/codex@8c076942cb70fba8e5c4732c23f1faabc4aed484 applies overrides in sequence and replaces an existing scalar, so the final effort is low. This is a remaining inherited precedence defect, not a claim that T-087 first introduced it: the old short-form parser also kept the first of repeated -c values. It directly violates this task's explicit identity-parity criterion.
- Newly introduced parsing hazard: the Codex config helpers are used for every tool. For example, AGENTFLOW_DEVIN_ARGS=`--config model=gpt-6.1-mini` now changes env_selected/selected_model and is removed when a header model exists; the base left it uninterpreted and preserved it. The equivalent long effort key also affects Claude args. This is a demonstrated cross-tool parsing change, not proof that either real CLI supports those arguments.
- Inherited limitations: splitting on whitespace breaks an unrelated quoted value such as `--config note="hello world"` into two argv tokens. Non-k=v values are ignored for identity but retained for the downstream CLI, so this layer is not a config-syntax validator. New quote stripping handles `"low"` but does not decode TOML escapes: `"\u006cow"` remains a literal escape sequence in the parsed identity rather than low. These boundaries are recorded without claiming a live provider run.

Cannot verify, needs:
- No environment blocker prevented the assigned checks. Fake workers prove launcher admission, argument delivery and lease/process behavior; actual provider inference was intentionally unnecessary.
- The full-suite result is reviewed developer evidence, not an independent replay. The additional Codex source snapshots establish config precedence; they are not a claim about an executed installed Codex binary.
- F-01 needs a developer correction and an independent re-test before accepting the complete alias/identity guarantee. Preserve T-078's existing scope rather than treating its deferred work as repaired here.

Proposed memory updates:
- T-088 independently verified f6bc519: all 86 required scoped tests and 20 additional routing-core tests pass, and the original single-alias bypass is repaired. Verdict remains fail because repeated config values can pass admission as high while the worker receives a final low override. Keep this evidence and the original T-086 failure history.
