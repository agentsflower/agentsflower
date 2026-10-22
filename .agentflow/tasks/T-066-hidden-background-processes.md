# T-066: Hide Windows background process consoles

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-096
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
Outcome: completed
Change: 3c8d9e6db30f2da718acbfca524650f4360977ee on t-066-hidden-background-processes
Files:
- .agentflow/tools/conductor.ps1 - the background Orchestrator session is spawned with `Start-Process -WindowStyle Hidden` (console created hidden: no flash, taskbar button or focus theft) instead of a visible window; inside `-Orchestrate` the session moves its stdin to an inheritable anonymous pipe already at EOF (SetStdHandle), so every tool it launches reads end-of-input at once and no prompt can hang the unattended session; a setup failure is recorded in the session log instead of being silent; help text and comments updated to describe the hidden process.
- .agentflow/tools/conductor-panel.ps1 - `-Start` and the registered Task Scheduler action use `-WindowStyle Hidden` instead of `Minimized` (a minimized console still takes a taskbar slot); UI strings no longer promise a window; the live session row shows the session pid so a windowless session stays stoppable.
- .agentflow/tools/run_task.py - `run_logged` passes `CREATE_NO_WINDOW` explicitly to the tool CLI spawn inside a managed worker (own headless console at this boundary instead of relying on console inheritance); POSIX `start_new_session` untouched.
- .agentflow/tests/test_conductor.py - 4 new regressions: live session `MainWindowHandle==0` plus `set /p` EOF proof in the session log; panel `-Start` conductor hidden + status + stop; registered task action audited via Task Scheduler; static guard for the hidden-spawn and stdin-EOF mechanism.
- .agentflow/tests/test_run_task.py - new regression: managed worker and its recorded tool process own no window (`MainWindowHandle==0`) and stdin is EOF.
- .agentflow/docs/ai-handoff-protocol.md - background Orchestrator described as a hidden headless process (was "visible window").
- GUIDE.md, GUIDE.ru.md - conductor/panel section states the hidden behavior; stale `conductor.env.json` mention removed.
- .agentflow/VERSION, AGENTS.md, CHANGELOG.md - 2.15.11 metadata, changelog entry and migration notes (re-register autostart for the Hidden action; restart the conductor without interrupting a running session or workers).
Checks:
- `python -m unittest discover -s .agentflow/tests` -> pass (466 passed / 0 failed, 4 skipped, twice: once mid-implementation and once on the final tree)
- Disposable-fixture Windows desktop check (script-driven, this interactive session) -> pass (39/39 observations). Windows 10.0.19045.6466, pwsh 7.6.7, Windows PowerShell 5.1.19041.6456, Python 3.13.7. Observed: three background Orchestrator sessions spawned by `conductor.ps1 -Once` (fresh need each round; identical needs correctly hit the cooldown) each had MainWindowHandle=0, foreground window never changed at 100 ms sampling, `set /p` returned EOF inside the tool, exit code 0 and machine lease recorded then released; conductor via panel `-Start` (x2) and via a registered `\AgentFlow\` scheduled task launched by `schtasks /Run` each had MainWindowHandle=0 and no focus change; `-Status` reported the running conductor, `-Stop` stopped it, `-Unregister` removed the task; an idle round was clean. Worker-side desktop evidence: `test_worker_and_tool_own_no_window` spawns the real launcher stack on this desktop and measures MainWindowHandle==0 on the recorded worker and tool pids.
- Migration notes reviewed in CHANGELOG 2.15.11: `conductor-panel.ps1 -Unregister` then `-Register` refreshes an existing registration to the Hidden action; `-Stop`/`-Start` restarts the conductor without touching a running background session or launcher-owned workers.
Criteria:
- A-01: pass - session, conductor (`-Start` and scheduled task), worker and tool processes measured with MainWindowHandle==0 on the real desktop across repeated launches; no taskbar button exists without a window; foreground window unchanged during every launch; explicit human terminals unaffected (the panel window itself stays visible). Evidence: .agentflow/tests/test_conductor.py (test_background_session_is_hidden_and_cannot_hang_on_stdin, test_panel_start_runs_the_conductor_hidden_and_status_sees_it, test_autostart_registration_runs_hidden_not_minimized), .agentflow/tests/test_run_task.py (test_worker_and_tool_own_no_window).
- A-02: pass - creation controls at each parent boundary: `-WindowStyle Hidden` (wShowWindow at creation) for session/conductor starts, `CREATE_NO_WINDOW` for worker and tool spawns; POSIX branch and PS 5.1/pwsh 7 both exercised (the EOF-pipe mechanism was verified on both shells before use). Not output redirection: the mechanism is the creation flag/style. Evidence: .agentflow/tools/conductor.ps1, .agentflow/tools/run_task.py, .agentflow/tests/test_conductor.py (test_launch_boundaries_carry_creation_controls).
- A-03: pass - logs (session log via Tee, attempt logs), `-Status`, pid+pidStart identity, machine lease claim/activate/release, `-Stop`, watchdog and timeout tree cleanup all unchanged and re-verified by the unchanged-passing suite (466 tests including stop/tree-kill/timeout regressions); stdin moved to an EOF'd pipe inside the session so a prompting tool fails fast (proven by `set /p` returning in the session log).
- A-04: pass - targeted regressions cover every changed launch path and were run on this real Windows desktop; the separate fixture exercise recorded window/focus observations for the session (x3), panel start (x2) and scheduled-task start, plus stop/unregister cleanup.
- A-05: pass - VERSION 2.15.11, AGENTS.md version block, CHANGELOG entry with migration notes, protocol and both guides agree; install.py has no embedded version copy (reads VERSION at runtime); test_install.py coverage stays green.
Found, not fixed:
- `msg.exe` remains the notification fallback in `Send-Notice` and shows a desktop dialog - intentional user-facing UI when balloon tips fail, not a background-process window.
- `-Once`/`conductor.ps1` run by hand in a human terminal keeps a visible console for that invocation - that is an explicit human-opened terminal, which A-01 requires to remain usable.
- A console app cannot create a console that never exists at all: `-WindowStyle Hidden` produces a hidden console window; the strongest alternative (`CreateNoWindow`/DETACHED_PROCESS via UseShellExecute=false) was prototyped and rejected for this boundary because `bInheritHandles` leaks the parent's inheritable handles into the session (a pipe-capturing `-Once` caller would wait for the session's lifetime) and descendants could still create visible consoles.
Proposed memory updates:
- decisions.md (dated): "Windows background work is hidden: the conductor, its scheduled-task/panel starts and automatic Orchestrator sessions run on consoles created hidden (-WindowStyle Hidden), and sessions move stdin to an EOF'd pipe so no prompt can hang them; CreateNoWindow/DETACHED_PROCESS were rejected at the session boundary because UseShellExecute=false handle-inheritance leaks the parent's pipes into the session (a capturing -Once caller would wait for the session's lifetime) and DETACHED_PROCESS lets grandchildren create visible consoles. Managed workers keep CREATE_NO_WINDOW; run_logged now applies it to the tool spawn too."
