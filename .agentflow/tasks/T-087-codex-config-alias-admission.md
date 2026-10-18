# T-087: Repair admission bypass via codex --config effort alias

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-086
Branch: t-087-codex-config-alias-admission
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-087-codex-config-alias-admission
Independent check: tester
Resume: none

## Goal

Successor of rejected T-076. The artifact at
07fbeed18e6a8d1a60eee491e1b81171b8090a6d is complete except one diagnosed
high-severity defect (independent tester T-086, D-01): an env effort
downgrade through Codex's supported `--config model_reasoning_effort=low`
alias is admitted and reaches the outgoing argv, while the equivalent
`-c model_reasoning_effort=low` is correctly refused - `route.env_selected`
parses only `-c`. Branch from that preserved commit, repair the resolved-env
identity parsing so every documented Codex override form
(`-c k=v`, `--config k=v`, `--config=k=v`, plus the model key where
supported) feeds the admission check, add regression tests reproducing the
live probe, and keep the rest of the artifact untouched. Do not re-implement
or re-verify what T-086 already proved pass.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/tasks/T-076-routing-launch-integration.md (rejected contract; its artifact is your base)
- .agentflow/tasks/T-086-verify-launch-admission.md (Result: D-01, live-probe evidence)
- .agentflow/tasks/.runtime/T-086.evidence/T-086.codex-alias.json + T-086.live-probes.json (the bypass probe)
- .agentflow/tools/route.py (env_selected/identity_problems/admission), .agentflow/tools/run_task.py (env_args/model_args)
- .agentflow/tests/test_route.py, .agentflow/tests/test_run_task.py

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
- T-040, T-074, T-082 and T-076 worktrees (read only)
- Account, quota and model catalog settings
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] D-01: Branch moved onto 07fbeed18e6a8d1a60eee491e1b81171b8090a6d once; the delta vs that commit is only this fix and `git diff main...HEAD` stays inside this contract's Allowed files.
- [ ] D-02: The resolved-env identity the admission check sees covers every documented Codex override form: `AGENTFLOW_CODEX_ARGS` carrying `--config model_reasoning_effort=low`, `--config=model_reasoning_effort=low` and `-c model_reasoning_effort=low` are all refused against a >=high requirement before CLI/lease/spawn; an adequate `--config` value is admitted and recorded with the resolved identity; other `--config` keys do not corrupt parsing. Model downgrades through `--config model=` are likewise refused where the form is documented.
- [ ] D-03: Live-style regression tests reproduce the T-086 probe shape (disposable launch or direct admission call) for each form; no live TypeSafe calls, no real Codex required.
- [ ] D-04: All scoped Checks pass verbatim; one full-suite run after the coherent change recorded honestly; VERSION/CHANGELOG/AGENTS still consistent (2.15.3 patch entry may gain one line that the `--config` alias is covered; no second release); T-040 not claimed complete; automatic backup/report integration still owned by T-078.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_route.py`
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py`
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py`

## Required pre-commit check

Run `python -m unittest discover -s .agentflow/tests` once after the coherent
change (root AGENTS.md) and record it for D-04. Scoped Checks above are rerun
at acceptance/integration; do not multiply whole-suite runs without cause.

## Execution bounds

20-minute cap (the full suite takes ~7 min). Reset the branch onto 07fbeed,
write the failing regression first, then the smallest parsing fix. Result
must include explicit `- D-01: pass - <evidence>` outcome lines for
D-01..D-04; put `evidence:` markers at line end followed only by intended
claim paths (`.runtime` evidence basenames must start `T-087.`); path names
inside prose are mentions.

## Result

Outcome: completed
Change: f6bc519631813c07583e7c5b527df97671266f84 on t-087-codex-config-alias-admission

Attempt 1 ended as timeout after producing the complete artifact; this attempt verified that
commit and ran the required checks instead of starting over.

Files:
- .agentflow/tools/route.py - `_config_kv`/`_config_value` helpers; `env_selected` feeds the `model` and `model_reasoning_effort` keys from every documented Codex override spelling (`-c k=v`, `--config k=v`, `--config=k=v`) into the resolved-env identity admission sees
- .agentflow/tools/run_task.py - `config_kv`/`config_value`; `selected_model` resolves the env `model` config key in all spellings (the probed identity); `remove_overridden` strips `-c`/`--config` model/effort pairs in all spellings when the Task File wins
- .agentflow/tests/test_routing_core.py - `env_selected` cases for all alias spellings, a TOML-quoted value and unrelated `--config` keys
- .agentflow/tests/test_run_task.py - disposable-launch regressions: effort and model downgrades refused per spelling, an adequate `--config` admitted and recorded with the resolved identity, argv parity when the task header wins
- CHANGELOG.md - one line inside the existing 2.15.3 entry noting `--config` alias coverage; no second release

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (58 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_worker_watchdog.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (400 passed / 0 failed / 3 skipped of 403 run, 453.6s)

Criteria:
- D-01: pass - the branch is 07fbeed18e6a8d1a60eee491e1b81171b8090a6d plus exactly one commit f6bc519; `git diff 07fbeed..HEAD` touches only route.py, run_task.py, the two test files and CHANGELOG.md, and `git diff main...HEAD` names only Allowed files (VERSION, ai-handoff-protocol.md, model-options.json, typesafe.md, tests, tools, AGENTS.md, CHANGELOG.md). evidence: .agentflow/tasks/.runtime/T-087.diff-stat.txt
- D-02: pass - `route.env_selected` and `run_task.selected_model`/`remove_overridden` share one parser covering `-c k=v`, `--config k=v` and `--config=k=v` for `model_reasoning_effort` and `model`; live-style launches refuse `--config model_reasoning_effort=low`, `--config=model_reasoning_effort=low` and `-c model_reasoning_effort=low` before CLI/lease/spawn, admit an adequate `--config` value recording effort xhigh with tier xhigh, keep unrelated `--config` keys harmless, and refuse `--config model=` downgrades in every spelling. evidence: .agentflow/tools/route.py .agentflow/tools/run_task.py .agentflow/tests/test_run_task.py
- D-03: pass - `RoutingAdmissionTests` reproduce the T-086 probe shape: real launcher subprocesses against disposable Git repositories with synthetic persisted assessments and a fake codex executable (`codex_assessment` fixture, `AGENTFLOW_CODEX_MODEL_PROBE=on`); no live TypeSafe calls and no real Codex; the argv-parity and `selected_model`/`env_selected` unit tests pin each spelling. evidence: .agentflow/tests/test_run_task.py .agentflow/tests/test_routing_core.py .agentflow/tasks/.runtime/T-087.test_run_task.log
- D-04: pass - all three scoped Checks pass verbatim above; the one post-change full suite ran once (403 tests, 3 skipped); VERSION and AGENTS.md stay at 2.15.3 and the CHANGELOG 2.15.3 entry gained only the `--config` alias line with no second release; T-040 is not claimed complete and automatic backup/report integration stays with T-078. evidence: .agentflow/tasks/.runtime/T-087.test_route.log .agentflow/tasks/.runtime/T-087.test_run_task.log .agentflow/tasks/.runtime/T-087.test_worker_watchdog.log .agentflow/tasks/.runtime/T-087.full-suite.log CHANGELOG.md

Found, not fixed:
- Nothing new; the T-086 findings already owned by T-078 (tick.use_backup ignoring route.backup_ok at selection time, the fresh-tester Devin-exclusion gap S-05) are unchanged by this fix.

Proposed memory updates:
- T-087 repaired the D-01 admission bypass: every documented Codex override spelling now feeds the resolved-env identity; commit f6bc519 on t-087-codex-config-alias-admission awaits verification and a T-076 successor re-test before merge.
