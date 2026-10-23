# T-089: Repair repeated-config precedence and cross-tool parsing scope

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-088
Branch: t-089-config-precedence-admission
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-089-config-precedence-admission
Independent check: tester
Resume: none

## Goal

Successor of rejected T-087 (itself successor of rejected T-076). The artifact
at f6bc519631813c07583e7c5b527df97671266f84 repaired the single-alias bypass
but independent tester T-088 proved F-01: repeated `--config` keys keep the
FIRST value in the resolved identity while Codex applies the LAST - so
`--config model_reasoning_effort=high --config=model_reasoning_effort=low`
is admitted as high while the worker receives low. T-088 also flagged that
the new config-key parsing now applies to every tool's args (a demonstrated
cross-tool parsing change the base did not have). Branch from that preserved
commit, make repeated-key resolution match the downstream tool's effective
value (last wins for Codex config keys), scope each tool's recognized
override forms to that tool's documented flags only, and add regression
tests. Do not re-implement or re-verify what T-086/T-088 already proved pass.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-087-codex-config-alias-admission.md (rejected contract; its artifact is your base)
- .agentflow/tasks/T-088-verify-config-alias.md (Result: F-01 + cross-tool hazard + inherited limitations)
- .agentflow/tasks/.runtime/T-088.evidence/T-088.live-probes.json + T-088.codex-precedence-sources.json (the probe and Codex precedence evidence)
- .agentflow/tools/route.py (env_selected, _config_kv/_config_value), .agentflow/tools/run_task.py (selected_model, remove_overridden, config_kv)
- .agentflow/tests/test_routing_core.py, .agentflow/tests/test_run_task.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/tick.py
- .agentflow/tools/route.py
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/typesafe.md
- .agentflow/docs/model-options.json (policy text only; preserve catalog and holds)
- .agentflow/VERSION
- AGENTS.md (version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, other Task Files, .agentflow/tasks/.runtime/
- T-040, T-074, T-082, T-076 and T-087 worktrees (read only)
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] G-01: Branch moved onto f6bc519631813c07583e7c5b527df97671266f84 once; the delta vs that commit is only this fix and `git diff main...HEAD` stays inside this contract's Allowed files.
- [ ] G-02: Repeated override keys resolve to the value the downstream tool effectively applies (Codex config keys: last occurrence wins): `--config model_reasoning_effort=high --config=model_reasoning_effort=low` is resolved as low and refused against a >=high requirement before CLI/lease/spawn; the same repeated-`low` case admitted at a >=low requirement records low; repeated `-c` values follow the same last-wins rule; a single adequate `--config` still admits with the resolved identity.
- [ ] G-03: Config-key parsing applies only to the tool whose documented flags they are: `AGENTFLOW_DEVIN_ARGS`/`AGENTFLOW_CLAUDE_ARGS`/`AGENTFLOW_AGY_ARGS` carrying `--config` are not interpreted as Codex config (preserved verbatim in argv, never silently dropped), while `AGENTFLOW_CODEX_ARGS` keeps the `-c`/`--config`/`--config=` forms. The admitted identity always equals the effective outgoing argv.
- [ ] G-04: Regression tests cover the repeated-key refusal/admission, the cross-tool non-interpretation, and preserve the T-086 spellings coverage; disposable launches/fake CLIs only, no live TypeSafe calls.
- [ ] G-05: All scoped Checks pass verbatim; one full-suite run after the coherent change recorded honestly; VERSION/CHANGELOG/AGENTS consistent at 2.15.3 (the entry may gain one line; no second release); T-040 not claimed complete; T-078 ownership of backup/report integration unchanged.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for G-05. Scoped Checks above are rerun
at acceptance/integration; do not multiply whole-suite runs without cause.

## Execution bounds

20-minute cap (the full suite takes ~7.5 min; keep the survey tight - the
defect shape and evidence are handed to you). Reset the branch onto f6bc519,
failing repeated-key regression first, then the smallest fix. Result must
include explicit `- G-01: pass - <evidence>` outcome lines for G-01..G-05;
put `evidence:` markers at line end followed only by intended claim paths
(`.runtime` evidence basenames must start `T-089.`); path names inside prose
are mentions.

## Result

Outcome: completed
Change: 52b06aacbd1a5b5874b82cf8ff1813d17ac65a40 on t-089-config-precedence-admission

Files:
- .agentflow/tools/route.py - env_selected: `-c`/`--config` k=v parsed only for codex; repeated `model`/`model_reasoning_effort` keys resolve last-wins (the value Codex's ordered override layer applies); the dedicated -m/--model/--effort flag layer outranks the -c layer, matching Codex's ConfigOverrides
- .agentflow/tools/run_task.py - selected_model resolves the env `model` config key the same way (codex-only, last-wins, flag layer outranks); remove_overridden/env_args take the tool so `-c`/`--config` filtering applies only to codex - other tools' same-spelled tokens pass through verbatim
- .agentflow/tests/test_routing_core.py - env_selected last-wins cases (mixed spellings, both directions, flag-vs-config precedence) and cross-tool non-interpretation cases for devin/claude/agy
- .agentflow/tests/test_run_task.py - disposable-launch regressions: repeated high-then-low refused at >=high before CLI/lease/spawn in `--config`/`--config=` and `-c` forms, the same final low admitted and recorded at >=low, devin `--config` tokens not interpreted and delivered to argv; ArgvParity last-wins and verbatim-preservation cases
- CHANGELOG.md - one clause inside the existing 2.15.3 entry; no second release

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (62 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (406 passed / 0 failed / 3 skipped of 409 run, 484.1s) - the single post-change whole-suite run

Criteria:
- G-01: pass - branch moved onto f6bc519631813c07583e7c5b527df97671266f84 once (`git reset --hard` at session start on a clean worktree); HEAD is that commit plus exactly this fix; `git diff f6bc519..HEAD` touches only route.py, run_task.py, the two test files and CHANGELOG.md; `git diff main...HEAD` names only this contract's Allowed files (VERSION, ai-handoff-protocol.md, model-options.json, typesafe.md, .agentflow/tests/, tools/route.py, tools/run_task.py, AGENTS.md, CHANGELOG.md); worktree clean. evidence: .agentflow/tasks/.runtime/T-089.diff-evidence.txt
- G-02: pass - repeated keys resolve to the value the downstream tool applies: live disposable launches refuse `--config model_reasoning_effort=high --config=model_reasoning_effort=low` and `-c ...=high -c ...=low` at >=high before CLI/lease/spawn (no attempt record created); the same repeated-final-low flags at a >=low requirement admit and record effort/tier low; a single adequate `--config` still admits with the resolved identity (T-087 test kept). Dedicated -m/--model flags outrank `-c model=` regardless of position, matching Codex's structured overrides over its ordered -c layer. evidence: .agentflow/tools/route.py .agentflow/tools/run_task.py .agentflow/tests/test_run_task.py .agentflow/tests/test_routing_core.py .agentflow/tasks/.runtime/T-089.test_run_task.log .agentflow/tasks/.runtime/T-089.test_routing_core.log
- G-03: pass - config-key parsing is scoped to the tool that documents it: `_config_kv`/`config_kv` are consulted only when tool == "codex" in env_selected, selected_model and remove_overridden; a live devin launch with `AGENTFLOW_DEVIN_ARGS="--config model=swe-2-medium --config model_reasoning_effort=low"` is not read as a downgrade, is admitted at the header identity, and all four tokens reach the worker argv verbatim (`<env arg>` count 4, never dropped); AGENTFLOW_CODEX_ARGS keeps the -c/--config/--config= forms; claude/agy covered by unit cases. evidence: .agentflow/tools/route.py .agentflow/tools/run_task.py .agentflow/tests/test_run_task.py .agentflow/tests/test_routing_core.py .agentflow/tasks/.runtime/T-089.test_run_task.log .agentflow/tasks/.runtime/T-089.test_routing_core.log
- G-04: pass - regressions cover the repeated-key refusal and the >=low admission through real launcher subprocesses (disposable repos, fake codex/devin CLIs, synthetic persisted assessments, no live TypeSafe, no real Codex), the cross-tool non-interpretation and verbatim delivery, plus the T-086 spellings coverage preserved (test_env_selected_parses_documented_flag_forms and the three T-087 launch tests all pass). evidence: .agentflow/tests/test_run_task.py .agentflow/tests/test_routing_core.py .agentflow/tasks/.runtime/T-089.test_run_task.log .agentflow/tasks/.runtime/T-089.test_routing_core.log
- G-05: pass - all three scoped Checks pass verbatim above; the one whole-suite run after the coherent change recorded honestly (409 run: 406 passed, 3 skipped, 0 failed); VERSION and AGENTS.md stay at 2.15.3 and the existing 2.15.3 CHANGELOG entry gained only the precedence/scope clause - no second release; T-040 is not claimed complete; T-078's backup/report integration ownership is unchanged. evidence: .agentflow/tasks/.runtime/T-089.test_route.log .agentflow/tasks/.runtime/T-089.test_run_task.log .agentflow/tasks/.runtime/T-089.test_worker_watchdog.log .agentflow/tasks/.runtime/T-089.full-suite.log CHANGELOG.md

Found, not fixed:
- Inherited limitations flagged by T-088 remain out of this contract's scope: whitespace splitting of a quoted `--config` value, non-k=v `--config` values ignored for identity but kept in argv (this layer is not a config-syntax validator), and no TOML escape decoding in _config_value (a `"\u006cow"`-style escape resolves literally).
- Repeated `-m`/`--model`/`--effort` dedicated flags keep first-wins semantics (unchanged from the base); Codex rejects duplicated dedicated flags at argv parse, so there is no silent divergence to repair.

Proposed memory updates:
- T-089 repaired the T-088 F-01 precedence defect at 52b06aa on t-089-config-precedence-admission: repeated Codex config overrides resolve last-wins (the value Codex applies) and `-c`/`--config` parsing is scoped to codex only; awaits independent re-verification of the complete alias/identity guarantee before the T-076 line can merge.
