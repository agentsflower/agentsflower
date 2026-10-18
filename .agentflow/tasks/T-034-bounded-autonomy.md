# T-034: Bounded autonomous verification and resource policy - recorded model identity, quota policy, stop-hook prototype, check reuse

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-064
Branch: t-034-bounded-autonomy
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-034-bounded-autonomy
Independent check: tester
Resume: none

## Goal

Implement improvement-plan.md section 4: launches record exactly what model
configuration was asked for and what ran; human quota wishes become an explicit
policy file rather than prompt promises; attempts, retries and platform
switches are bounded; a Codex Stop-hook adapter exists as an opt-in prototype
that only activates after validating the installed runtime.

Attempt state note: attempt 1 hit the 2400s wall-clock limit - the worktree
holds an in-progress draft across ~16 files (git status). Commit a correct
intermediate state EARLY, then continue; do not restart by re-reading
everything; write the Result as soon as the artifact and checks are green.

## Read first

- .agentflow/docs/improvement-plan.md (section 4)
- .agentflow/docs/ai-handoff-protocol.md (Launching workers, Autonomous orchestration)
- .agentflow/state/known-issues.md
- .agentflow/tools/run_task.py, .agentflow/tools/tick.py, .agentflow/tools/conductor.ps1, .agentflow/tools/machine_capacity.py, .agentflow/tools/route.py, .agentflow/tools/plan_route.py, .agentflow/tools/gate.py
- .agentflow/docs/typesafe.md
- .agentflow/tests/test_tick.py, test_route.py, test_machine_capacity.py, test_run_task.py, test_parallel.py

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/tick.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/route.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/route_report.py
- .agentflow/tools/gate.py
- .agentflow/tools/cli.py
- .agentflow/tools/hooks.py or .agentflow/hooks/ (new - Codex stop-hook adapter, opt-in)
- .agentflow/tools/install.py (only if the new adapter file must be delivered to installed projects)
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/docs/model-options.json schema documentation where it lives today
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/docs/project-rules.md
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects, their machine leases and their model-options.json
- Codex/Claude/Devin/agy global configs (the adapter is installed by an explicit human or install flag, never silently)

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] B-01: Every attempt record stores the requested `Model:`/effort, the resolved launch argv configuration (safe form - no secrets), the tool CLI version when cheaply available, and the effective model/effort when the tool reports it; unavailable runtime identity is recorded as unknown, never guessed. Existing attempts without the fields keep working.
- [ ] B-02: A quota policy file (project-owned, documented schema: platform/account, quota window, remaining threshold, sample age, action pause|switch) is read by tick/conductor where declared. A "leave N% reserve" policy without actual usage readings reports unknown and falls back to explicit time/attempt caps; the implementation never claims a percentage it cannot measure. Other projects sharing the account and polling/in-flight overshoot are named in the documented limits of the mechanism.
- [ ] B-03: Attempt and task duration, retry count, repeated identical failures and tool/platform switches are bounded by configurable caps (defaults documented); a budget stop preserves the checkpoint (recovery capture from the lifecycle work) and terminates the managed process tree safely.
- [ ] B-04: Machine, project and platform concurrency caps are enforced including nested sessions where detectable; where a project forbids delegation the launcher enforces zero helpers. Consumption is measured when the platform exposes it; concurrency is never asserted to cause cache growth.
- [ ] B-05: Codex Stop-hook adapter: check the installed Codex version and supported hook surface at runtime before enabling; opt-in only (an install.py flag or a documented manual step), calls the common completion command from the evidence-gate work, returns bounded actionable failure text on failure, and falls back to the runner/acceptance path when unsupported. It never recursively spawns workers, never accepts its own result, and never treats user stop/quota exhaustion/an explicit blocker as a reason to continue.
- [ ] B-06: Check reuse: a passing check record is reused only when artifact SHA, requirements hash, check definitions and relevant environment match the new evaluation; any changed input invalidates it. Repeated identical failures terminate with preserved work.
- [ ] B-07: Coordinator/model effort selection by decision difficulty is expressible through routing policy and Jev (plan_route.py); mechanical dispatch may use low effort while debugging/risky acceptance gets more. No forced-low default.
- [ ] B-08: Full suite passes verbatim; increment VERSION, sync AGENTS block and CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - recorded identity, caps, safe stop.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - quota policy, retry/failure bounds.
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` - concurrency caps.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: ccd74ba on t-034-bounded-autonomy
Files:
- .agentflow/tools/run_task.py - attempt records carry requestedModel/requestedEffort, safe-form launch.argv (`<prompt>`/`<env arg>` masking), bounded toolVersion, effectiveModel/effectiveEffort parsed from the session log; launch budgets AGENTFLOW_MAX_ATTEMPTS/AGENTFLOW_TASK_TIMEOUT/AGENTFLOW_MAX_IDENTICAL_FAILURES/AGENTFLOW_MAX_TOOL_SWITCHES refuse a new attempt and preserve records and recovery checkpoints; nested-launch markers AGENTFLOW_ATTEMPT/AGENTFLOW_ATTEMPT_ROOT
- .agentflow/tools/tick.py - declared quota policy reader (quota-policy.json + quota-samples.json), policy_hold in decide/next-orchestrator, run/status reporting; malformed files fail closed
- .agentflow/tools/conductor.ps1 - surfaces quotaPolicy states and names below-threshold policies in the all-limited notice
- .agentflow/tools/gate.py - checksHash (checks + Env: + interpreter) written into verify/done records and required for done-PASS reuse; delegation_allowed() implements the Preflight `- delegate: on` rule
- .agentflow/tools/plan_route.py - --kind names the decision a recommendation feeds, recorded in Jev state and result, frames the effort question without forcing a tier
- .agentflow/tools/hooks.py - new opt-in Codex Stop-hook adapter: validates installed version and hook feature surface before enabling, `--write` touches only project-local .codex/hooks.json, codex-stop completes a manual session and runs `gate.py done`, advisory and inert inside managed sessions
- .agentflow/tools/cli.py - `agentflow hooks` passthrough
- .agentflow/tests/test_run_task.py, test_tick.py, test_done_gate.py, test_plan_route.py, test_hooks.py - coverage for identity recording, budgets, nested launches, quota policy, check-reuse binding, kind, and the adapter
- .agentflow/docs/ai-handoff-protocol.md - documents the new attempt-record fields, the four launch budgets, the delegate Preflight rule, declared quota policy (Autonomous orchestration 3e) with the mechanism's named limits, checksHash binding and the hook adapter
- .agentflow/VERSION, AGENTS.md - 2.14.0 -> 2.15.0
- CHANGELOG.md - 2.15.0 entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (49 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (52 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (346 passed / 0 failed, 3 skipped)
Criteria without a command:
- B-01: pass - run_task.py stores requestedModel/requestedEffort, masked launch.argv, toolVersion from a bounded `--version` call, and effectiveModel/effectiveEffort only from structured init/config events or model:/effort: header lines in the log; unreported identity stays `unknown`; fields are additive so records predating them keep working (test_attempt_records_launch_identity, test_attempt_identity_is_unknown_when_the_tool_reports_nothing, test_manual_attempt_records_requested_model_and_unknown_runtime)
- B-02: pass - .agentflow/docs/quota-policy.json schema (tool, optional quota group, remaining.percent_below, action pause|switch|report, sample_max_age_seconds; readings keyed `<tool>`/`<tool>:<group>` with at/remaining_percent/resets_at as the window end) read by tick decide/next-orchestrator/status/run and by conductor.ps1; no fresh reading reports `unknown` and never blocks, so the launch budgets remain the bound; shared-account consumers and in-flight overshoot are named limits in the protocol text (5 new test_tick policy tests)
- B-03: pass - caps on attempts (8), task wall clock (4h from attempt 1, its remainder also bounds the running worker's kill-tree timeout), consecutive identical failures (3, same stopReason+exitCode+normalized note) and distinct platforms (3, manual exempt); every refusal starts nothing and leaves records/checkpoints intact (test_attempt_and_duration_budgets_refuse_new_attempts, test_repeated_identical_failures_stop_relaunching, test_tool_switch_budget)
- B-04: pass - existing machine_capacity registry caps (AGENTFLOW_MACHINE_<TOOL>_MAX, `- parallel: <tool>=<n>`) still enforced (12 green tests); nested sessions detected by the attempt markers and refused unless a project Preflight declares `- delegate: on`; delegation still obeys budgets and capacity (test_nested_launches_need_a_delegate_rule); nothing asserts concurrency causes cache growth
- B-05: pass - hooks.py enable validates `codex --version` (>= 0.114.0) and the `features list` surface at runtime, refusing unsupported/mute runtimes without writing; opt-in twice (prints steps, --write adds one project-local Stop entry); codex-stop runs the common `gate.py done`, returns bounded actionable text, marks a finished manual session via cmd_mark_finished, is inert under AGENTFLOW_ATTEMPT, and treats limitHit/blocked/foreign cwd as stop, never continue (test_hooks.py, 13 tests)
- B-06: pass - every verify/done record carries checksHash over ## Checks + Env: block + interpreter; bound_record reuses a PASS only on artifact+requirements+base+checksHash match, so a changed check input or a legacy record without the field forces a new measurement; repeated identical failures terminate with preserved work (test_done_reuse_is_bound_to_check_definitions_and_environment, test_repeated_identical_failures_stop_relaunching)
- B-07: pass - plan_route.py `kind` (CLI `--kind`, recommend() kwarg) is recorded in the Jev state and the result and frames the effort question for dispatch vs debugging/risky acceptance; no tier is forced (test_kind_reaches_the_jev_state_and_result)
- B-08: pass - full suite 346 passed verbatim; VERSION 2.15.0, AGENTS.md block synced, CHANGELOG entry with migration notes; decisions.md text proposed below
Found, not fixed:
- none
Proposed memory updates:
- decisions.md (date 2026-10-18): "T-034 (2.15.0): bounded autonomy - attempts record requested Model:/effort plus the identity the tool itself reported (unreported stays `unknown`, never guessed); operator quota wishes moved from prompt promises into .agentflow/docs/quota-policy.json consumed by tick/conductor, where a policy without a fresh reading is `unknown` and never blocks - launch budgets stay the bound; attempts (8), task duration (4h), identical failures (3) and platform switches (3) are capped by AGENTFLOW_* settings; nested launches are refused unless a project Preflight declares `- delegate: on`; an opt-in Codex Stop-hook adapter (hooks.py) validates the installed runtime before enabling and stays advisory; done-PASS reuse is bound by checksHash over checks+env+interpreter so changed check inputs force re-measurement."
