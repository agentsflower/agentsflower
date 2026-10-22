# T-112: Independently verify hidden background process consoles

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Verifies: T-066 @ 3c8d9e6db30f2da718acbfca524650f4360977ee

## Goal

Independently evaluate the exact T-066 artifact (3c8d9e6db30f2da718acbfca524650f4360977ee)
against every A-01..A-05 criterion in its Task File, in a disposable checkout.
The artifact configures Windows background processes (conductor, automatic Orchestrator,
worker CLI, panel starts and Task Scheduler registration) to run on hidden consoles
without taskbar entries or focus theft, sets stdin to an EOF'd pipe to prevent prompts
from hanging unattended sessions, updates docs/guides, and aligns version metadata to 2.15.11.
Fresh independent session per protocol.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-066-hidden-background-processes.md
- The candidate diff `git diff main...3c8d9e6db30f2da718acbfca524650f4360977ee` in disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-066 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (A-01) Background conductor, automatic Orchestrator, worker CLI and managed helpers create no visible console or focus theft on Windows. Audit scheduled-task registration and manual panel start.
- [ ] V-02: (A-02) Process creation controls at the parent launch boundary (-WindowStyle Hidden, CREATE_NO_WINDOW); POSIX behavior and PowerShell 5.1/pwsh compatibility preserved.
- [ ] V-03: (A-03) Logs and panel status available; exit codes, PID identity, leases, stop and timeout tree cleanup retain behavior; stdin EOF prevents unattended hangs.
- [ ] V-04: (A-04) Targeted regressions pass and cover all changed launch paths; verify on a real Windows desktop and record observed window/focus behavior.
- [ ] V-05: (A-05) VERSION 2.15.11, AGENTS block, CHANGELOG and affected guides aligned with honest migration notes.
- [ ] V-06: Full regression suite passes verbatim; map all A-01..A-05 to concrete evidence/outcomes.

## Checks

- `python -m unittest discover -s .agentflow/tests`

## Execution bounds

Run the scoped checks verbatim on the checked SHA. Save evidence in AGENTFLOW_EVIDENCE with basenames starting `T-112.`.
Use the current gate format in Result: one `- V-01: pass - <evidence>` line for each V-01..V-06 plus `Verdict:`.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests` -> pass (466 passed / 0 failed, 4 skipped; evidence: .agentflow/tasks/.runtime/T-112.evidence/T-112.unittest-run3.txt). Two earlier verbatim runs each hit one transient failure in tests untouched by the artifact - run1 test_worker_watchdog.test_launch_persists_the_resolved_timeout_and_deadline (30s wait expired while my desktop exercise competed for CPU; module rerun 14/14 green), run2 test_done_gate.test_in_scope_evidence_must_exist (os.replace WinError 5, the Windows flake already recorded in known-issues.md; module rerun 27/27 green). Evidence: T-112.unittest.txt, T-112.unittest-run2.txt.
Criteria:
- V-01: pass - disposable fixture on the real interactive desktop (session 1, Windows 10.0.19045.6466): background Orchestrator session via `conductor.ps1 -Once` pid 17100 MainWindowHandle=0 for its whole life; conductor via panel `-Start` pid 96796 and via registered `\AgentFlow\` task + `schtasks /Run` pid 5964 both MainWindowHandle=0; 236 foreground samples during all launches showed no focus change. Control probe proves the metric is meaningful: `-WindowStyle Hidden` -> MainWindowHandle 0, `Minimized` -> nonzero, visible new console -> nonzero. Helper audit: worker children spawned without flags by the CREATE_NO_WINDOW worker get no console at all (cmd/.bat/python children GetConsoleWindow()=0), so no hidden flash path remains. Evidence: .agentflow/tasks/.runtime/T-112.evidence/T-112.desktop.txt, .agentflow/tasks/.runtime/T-112.evidence/T-112.windowstyle-probe.txt.
- V-02: pass - diff audit: every changed parent boundary carries a creation control (`Start-Process -WindowStyle Hidden` for session and conductor starts, scheduled-task action, `-WindowStyle Hidden` shortcut; `CREATE_NO_WINDOW` for the tool spawn in run_logged; worker and probe spawns already carried CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP); POSIX keeps `start_new_session` untouched. PS 5.1.19041.6456 and pwsh 7 both verified: SetStdHandle mechanism runs on 5.1 and a `set /p` child returns at once on both shells. Evidence: .agentflow/tasks/.runtime/T-112.evidence/T-112.desktop.txt, .agentflow/tasks/.runtime/T-112.evidence/T-112.windowstyle-probe.txt.
- V-03: pass - live state recorded pid+pidStart identity, machineLease claimed/activated/released, exitCode 0, finishedAt; session log written via Tee and contains `stdin-read:` proving EOF reached the tool's `set /p` (no silent prompt hang); `-Status` reported the running conductor (exit 0) and `-Stop` terminated both panel- and scheduler-started conductors; the unchanged suite re-proved stop/timeout tree cleanup. Worker side stdin is DEVNULL, covered by test_worker_and_tool_own_no_window.
- V-04: pass - 5 targeted regressions cover every changed launch path (session spawn, panel start, registered task action, worker+tool spawn, static boundary guard) and all passed in run3; the independent desktop exercise above observed real window/focus behavior rather than static flags. Skipped=4 are platform/optional-dependency skips (mcp SDK absent), matching the developer's report.
- V-05: pass - VERSION=2.15.11, AGENTS.md block=2.15.11 (CLAUDE.md holds no version), CHANGELOG has a dated 2.15.11 entry whose migration notes match the implementation (re-register via -Unregister/-Register; -Stop/-Start restarts the conductor without touching sessions/workers); protocol and both guides describe the hidden behavior and the stale conductor.env.json mention is gone; install.py reads VERSION at runtime. Observation only: README badge and RELEASE_NOTES.md still say 2.15.10 - outside this task's allowed files, but the previous release commit did sync them, so the Orchestrator may want a release-notes sync task.
- V-06: pass - the verbatim suite passes on the artifact (466/0/4 in run3); the two transient single-test failures in earlier runs are in files untouched by the diff, each green on isolated rerun, one matching a documented recurring Windows flake; every A-01..A-05 maps to concrete evidence above.
New defects (outside the task):
- none attributed to the artifact; environment flakes observed: the recurring Windows os.replace WinError 5 (already in known-issues.md) and one 30s wait timeout under heavy parallel load.
Cannot verify, needs:
- nothing
Proposed memory updates:
- none beyond what T-066 already proposed (its decisions.md entry stands).
