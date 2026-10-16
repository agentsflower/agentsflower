# Session Log

## 2026-10-16: Recover agy interactive hang

Observed T-002 process alive for 15h with no Result/log; stopped using launcher.
Human authorized execution. Prepared T-012 successor for Python port plus bounded
noninteractive agy review, rejected T-001 with preserved artifact, cancelled T-002.

## 2026-10-15: Launch T-001 via Devin

Human authorized launch of T-001 on Devin (swe-2-high) and confirmed that external
projects do not block AgentFlow template work. Template rollout into client projects
will occur only after AgentFlow changes and tests are complete. Ledger T-001 set to
ready, then launched via launcher.

## 2026-10-15: Prefer Devin for release work

Human changed resource routing. Queried Devin/agy model catalogs, assigned
T-001 to Devin swe-2-high and proposed agy gemini-3.8-flash-high for T-002.
No inference probes or workers launched; model access/quotas are not inferred
from catalog listings.

## 2026-10-15: Public release planning

Read the production roadmap and implementation. Human approved T-001 through
T-011 and scope decisions recorded in decisions.md. Prepared only T-001; no
workers launched. CLI executables found for Claude, Codex, Devin and agy; model
access and quotas remain unknown. Added mandatory pre-start resource checks.

Chronological log of work on the AgentFlow template.

## 2026-05-21

- Base AI Project Memory: protocol, handoff, current-step, decisions, known-issues, session-log.

## 2026-10-01

- Team layer: roles, Task Files, Task Ledger, `/start-role`, protocol sections "Roles and memory ownership", "Starting a role session", "Task lifecycle", "Planning levels", "Git rules", `AGENTS.md`, `roles/tool-routing.md`.

## 2026-10-02

- Launcher and ledger defects from migrating a live project fixed; preflight, `## Checks`, production opt-in added.

## 2026-10-03

- FPF audit of all files; refactor to 2.0.0 in five commits: P0 enforcement, P1 state and evidence, P2 rule order and contradictions, P3 template vs project, P4 English machine-facing text. Details: `CHANGELOG.md`, `state/decisions.md`.

## 2026-10-07: 2.2.0

- Moved the template into `.agentflow/` with `git mv`; ported the Watermark Remover adaptation (`paths.py`, relocated
  paths, dashboard history and links, layout tests) and its fixes; added `install.py`, `accept.py`, VERSION, tests.
- Protocol, roles, tool routing, Task File template, README, GUIDE, CHANGELOG updated. 19 tests pass.


## 2026-10-10: Launcher reliability

Implemented 2.11.3 launcher, end-check and acceptance repairs with regression tests in disposable repositories; deployment to the pilot follows the installer workflow.

Final validation: 105/105 tests pass (including PowerShell 5.1/7 and fake-worker
tick launch). Pilot full suite: 105/105; focused lifecycle rerun: 7/7. Pilot
update committed as 66deac8 on master; no template drift or product changes.
Conductor restarted hidden and reports zero needs/waits, with autostart enabled.
A test-only temporary-directory cleanup race was fixed by waiting for worker exit.

## 2026-10-12: Shared resource scheduling and Jev evidence

- Completed and merged the prepared 2.11.4 junction-cleanup release separately. Its 107 tests passed with the legacy Codex machine limit fixed at 1 for that historical test run.
- Released 2.11.5 dispatcher observation, 2.11.6 Jev primary/backup routing, 2.11.7 opt-in shared grants, and 2.11.8 planning advice and read-only routing reports. The final template suite passed 124 tests, including real PowerShell grant-to-lease launch with a fake worker; no real worker model was called by tests.
- Installed 2.11.8 in Transcript Youtube (master@e6c088d) and Watermark Remover (master@c512c70); each installation passed 124 tests. Upstream drift is clean for both. Transcript's real Jev planning probe returned a medium-confidence recommendation with request ID; the machine remains in dispatcher `shadow` mode and backup auto-switching is off.
- Gemini to Word remains at 2.11.3 with manual tester T-009 running and uncommitted template-owned `accept.py`/`run-task.ps1`; do not update it or activate shared grants until that work is resolved. No push or production deployment was made.

2026-10-15: Human corrected rule ownership: AgentFlow repository, not TuScript. Root AGENTS.md now pins source authority to vcherstar/AgentFlow; decisions record instruction. Misplaced TuScript rule reverted in its own history. Required precommit unittest run: 124 tests, errors=2 in test_launcher_lifecycle.test_dispatch_grant_becomes_worker_lease due PermissionError/WinError32 on temporary runtime file and teardown directory held by process. Documentation-only change; no framework code changed, no claim of green suite. Existing untracked nul untouched.
