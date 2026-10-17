# T-024: Repair noninteractive probe trust flags

Role: developer
Tool: codex
Stage: 6
Depends on: none
Branch: t-024-probe-bootstrap
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-024-probe-bootstrap
Independent check: tester
Resume: none

## Goal

Repair the reproduced bootstrap deadlock: Devin account auth succeeds, but its
model probe in an empty temp cwd fails because workspace trust defaults to true.
Direct CLI with --respect-workspace-trust false --permission-mode auto returned
ACCESS_OK in the same untrusted parent. Keep inference proof, selected model,
opt-in, timeout and no-secret evidence intact. Also supply the existing Codex
read-only probe's required non-repository flag, if confirmed by installed help.

Native Codex worker is used narrowly through a launcher-prepared Manual attempt:
all CLI automatic workers are blocked by the malformed probe; user prioritizes
Devin and conserves Codex. Native session identity is inherited, not claimed as a
particular CLI model. No new launch scripts or disabling probes. No recursive agents.

## Read first

- AGENTS.md
- .agentflow/docs/project-rules.md
- .agentflow/roles/developer.md
- .agentflow/docs/ai-handoff-protocol.md (role startup, standing rules, git rules)
- .agentflow/tools/run_task.py (MODEL_PROBE_ARGS and resource_check only)
- .agentflow/tests/test_run_task.py (probe tests)

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tests/test_run_task.py
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/
- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/machine_capacity.py
- other project files

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] B-01: Audited Devin inference probe works noninteractively in an empty untrusted temp directory using explicit supported trust handling and read-only/auto tool policy. It must not use dangerous permission mode. Selected model is still passed, opt-in/timeout/evidence remain unchanged.
- [ ] B-02: Verify Codex exec help locally; its read-only probe can operate outside a git repository with the supported skip-repository check flag. No sandbox downgrade, no silent fallback or arbitrary custom model probes.
- [ ] B-03: Add focused argv regressions with fakes. Test genuine denial still fails closed. No actual paid calls in unit tests; Orchestrator checks real availability after acceptance.
- [ ] B-04: Bump intermediate VERSION to 2.11.10, synchronize AGENTS template block/changelog migration notes. Do not write canonical decisions; propose them in Result. One task commit, exact full SHA copied from git, clean worktree.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - bounded probe argv and refusal regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory regression suite; report any existing registry flake honestly.

## Result
Outcome: completed
Change: 183171c19e2e115dfdc6f23af92b42471134e3af on t-024-probe-bootstrap
Files:
- .agentflow/tools/run_task.py - explicit Devin trust false/permission auto and Codex skip-git-repo-check in built-in probes only.
- .agentflow/tests/test_run_task.py - fake argv, empty cwd, timeout, selected-model evidence and genuine-denial regressions for both tools.
- .agentflow/VERSION - 2.11.10.
- AGENTS.md - synchronized template version.
- CHANGELOG.md - release and installed-project migration notes.
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (27 passed / 0 failed).
- `python -m unittest discover -s .agentflow/tests` -> fail (151 passed / 1 failed): conductor test_hand_over_then_next_tool_after_a_usage_limit timed out waiting for session 2.
- `python -m unittest discover -s .agentflow/tests -p test_conductor.py -k test_hand_over_then_next_tool_after_a_usage_limit` -> pass (1 passed / 0 failed), single targeted rerun.
- `git diff --check` -> pass; final worktree clean; one task commit.
Criteria without a command:
- B-01: installed `devin --help` confirms print mode fails in untrusted cwd by default and supports `--respect-workspace-trust false`; auto approves read-only tools. Fake tests verify exact argv and denial. Existing real inference evidence belongs to Orchestrator; no real model calls made by worker.
- B-02: installed `codex exec --help` confirms `--skip-git-repo-check` allows non-Git cwd; read-only sandbox retained. Fake validates exact selected-model argv.
- B-03: new regression failed on missing bootstrap flags before product edit; final focused suite passes including existing opt-in, custom-probe refusal, timeout and secret tests. Fake interception performs no paid calls.
- B-04: version/block/changelog synchronized; canonical decisions intentionally delegated to Orchestrator.
Found, not fixed:
- Full-suite conductor session completion timeout reproduced once; isolated rerun passed. No registry os.replace error observed in this run; known registry flakiness remains outside scope (T-022).
Proposed memory updates:
- 2026-10-17: keep audited inference probes enabled and bounded; Devin temp-cwd probes explicitly skip workspace trust with auto read-only policy, Codex retains read-only sandbox and explicitly permits non-repository cwd. Install 2.11.10 before retrying automatic workers; no credential/trust configuration migration needed.
