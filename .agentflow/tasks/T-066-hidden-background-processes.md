# T-066: Hide Windows background process consoles

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-078
Branch: t-066-hidden-background-processes
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-066-hidden-background-processes
Independent check: tester
Resume: none

## Goal

Run AgentFlow background work on Windows without flashing console windows,
taskbar entries or focus theft. Preserve logs, status, cancellation, process
identity, machine leases and timeout cleanup. Human requested queueing on
2026-10-17; do not interrupt current tasks to implement this task.

## Read first

- .agentflow/docs/project-rules.md (persisted Jev assessment required before execution)
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/tools/conductor.ps1
- .agentflow/tools/conductor-panel.ps1
- .agentflow/tools/run_task.py
- .agentflow/tools/tick.py
- .agentflow/tools/gate.py
- .agentflow/tests/test_conductor.py

## Allowed files

- .agentflow/tools/ (only background process launch and lifecycle paths)
- .agentflow/tests/ (targeted regression coverage)
- .agentflow/docs/ai-handoff-protocol.md (background visibility behavior only)
- README.md, GUIDE.md, GUIDE.ru.md (affected operating instructions only)
- .agentflow/VERSION
- AGENTS.md, CLAUDE.md (AgentFlow version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/ (propose dated decision and memory updates in Result)
- Other Task Files and runtime records
- .agentflow/dashboard/
- Other repositories, existing scheduled tasks, running sessions or machine leases
- Remotes, publication and deployment

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] A-01: Background conductor, automatic Orchestrator, worker CLI and their AgentFlow-managed helper launches create no visible console or focus theft on Windows. Audit scheduled-task registration and manual panel start; Minimized is not hidden. Explicit human-opened terminals remain usable.
- [ ] A-02: Use suitable Windows process creation controls at the parent launch boundary; output redirection or CLI quiet flags alone do not satisfy A-01. Preserve POSIX behavior and Windows PowerShell 5.1 / pwsh compatibility.
- [ ] A-03: Logs and panel status remain available; exit codes, PID/start identity, leases, stop and timeout tree cleanup retain their behavior. No interactive authentication prompt may hang an unattended launch silently.
- [ ] A-04: Targeted regressions cover all changed launch paths. Independently verify repeated launches on a real Windows desktop and record observed window/focus behavior; static flags alone are not desktop evidence.
- [ ] A-05: Patch version, entry-point version blocks, changelog and affected guides agree. Migration notes explain how an installed project refreshes an existing conductor autostart registration and restarts background services without interrupting active workers; no external rollout in this task.

## Checks

- `python -m unittest discover -s .agentflow/tests` - regression suite, including targeted tests added for A-01 through A-03.
- Windows desktop check in a disposable AgentFlow fixture: start conductor from panel and registered autostart, launch a background Orchestrator and worker, exercise helper/check launches repeatedly; verify no console/taskbar/focus interruption and inspect logs/status, normal exit and bounded stop/timeout cleanup. Record Windows/shell versions and actual observations for A-01 through A-04.
- Review migration instructions and synchronized release metadata for A-05.

## Result
