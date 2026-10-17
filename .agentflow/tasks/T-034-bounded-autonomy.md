# T-034: Bounded autonomous verification and resource policy - recorded model identity, quota policy, stop-hook prototype, check reuse

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-032
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
