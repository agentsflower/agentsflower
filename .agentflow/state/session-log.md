# Session Log

## 2026-10-17: Accept runtime baseline and enable the rest of the pool

T-022 and independent T-023 passed 158 full-suite tests plus focused checks;
accept.py verified, merged and cleaned T-022 (main 2.11.11). T-009 produced correct
CI files/152-test developer pass, but old-branch acceptance failed an intermittent
test_route case; preserved and rejected to T-026 integration after runtime repair.
Queue dependencies updated. No test or release gate waived. Prepared a complete
handoff for Devin background continuation to conserve Codex; root will release
writer ownership before starting the coordinator. No push or publication.

## 2026-10-17: Resume the full approved release queue

Read current repository: background Devin had completed T-020/T-021 and merged
2.11.9 Linux fixes. Human now explicitly authorizes all remaining pool tasks.
Created/approved CI, reliability, package CLI, MCP, English metrics and final docs
contracts with serialized shared metadata. Cancelled obsolete T-018 placeholder.
Live pre-start check reproduced Devin untrusted-temp-cwd refusal. T-024 repaired
only built-in probe argv using narrow native Manual adapter; T-025 independently
passed 27 focused, 152 full and a real Devin probe after harness-only recovery.
accept.py verified and merged bootstrap to 2.11.10; no source/code changes by the
Orchestrator. Started ordinary Devin T-022 and T-009 after real inference checks.
No push/publication. Current queue and actual evidence references are in ledger.

Checkpoint validation after all workers exited: main 2.11.8 full suite ran
124 tests, one WinError 5 error in test_tick via machine_capacity._locked/os.replace.
Recorded as recurring baseline registry reliability issue. Product candidate
1e0bd87 independently passed 151 tests in T-017; no product merge performed.

## 2026-10-16: Linux defect repair merged via Docker evidence (background devin)

Decided T-019's fail Verdict: T-016 stays rejected; T-019 verified and done.
Created successor T-020 (developer, devin): ported 1e0bd87 onto main and repaired
the three T-019 defects - run_logged tool spawn now leads its own POSIX session
(no killpg self-kill), kill_tree signals the tree's process groups via /proc
with ps fallback, accept.py drops `merge-tree --quiet` (git 2.47), test_endcheck
merge fixture carries git identity. Commit bafc2a0. T-021 (tester, devin -
Codex conserved per human routing, agy/claude limited) independently re-ran the
Docker Linux gate on the exact SHA: 151 tests, 0 failed, 18 Windows-only skips;
Verdict pass. Windows verbatim suite hit the known registry os.replace WinError 5
flake twice (different tests, green standalone) - reported, not T-020's code.
T-020 accepted and merged to main (eb59c7c). T-018 stays blocked: its question
now reduces to the macOS route (questions.md). No push or release.

## 2026-10-16: Complete local launcher hardening; hold real Unix gate

T-015 found concrete defects despite 149 tests: accepted the failing review,
rejected T-014 to T-016. T-016 on Devin medium produced exact SHA
1e0bd876a4c3247416f6ccc3dd9c89970a36d695; developer 151 tests green twice.
T-017 separately repeated probes/secret/timeout/routing checks and full suite:
151/0/0, all local criteria pass, overall unverified only for actual Linux/macOS.
Accepted T-017 as a completed review via accept.py; no code merge. T-016 rejected
to prepared blocked T-018 under the protocol's non-pass successor rule. All worker
processes exited, no new worker launched. Human question asks Unix hosts vs CI
branch for human push. Conductor env-file risk logged separately. No push/release.

## 2026-10-16: Launcher recovery and independent review completed

T-012 attempt 1 Devin high copied port but made no repairs; stopped safely.
Attempt 2 agy Opus read sources then quota failure; Sonnet/GPT-OSS also exhausted.
Attempt 3 Devin medium completed 87de72c, 147 tests green. T-013 on separate Devin
high session repeated 147 tests green and verified Windows timeout/noninteractive
behavior; unverified for actual Unix. Accepted review via accept.py, rejected
artifact to T-014 because required selected-model inference preflight is still
missing. Prepared T-014 but did not launch; awaiting human Unix/CI verification
route. No product commit merged and no push. Evidence in T-013.evidence runtime.

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

2026-10-17 (devin-background): T-003 developer completed at 1849b2bf. Wrote Tester contract T-004-verify-package-cli.md (Verifies T-003 @ 1849b2bf, tool devin, swe-2-medium), ledger ready, attempt 1 launched (log .agentflow/tasks/.runtime/T-004.1.log). Initially misfiled as T-027; cancelled unused and recreated under the reserved ID T-004.

2026-10-17 (devin-background): T-005 developer completed at 1665318 (optional MCP server, installer --mcp/--mcp-client, VERSION 2.11.13, CI mcp job). Wrote Tester contract T-006-verify-mcp-server.md (Verifies T-005 @ 1665318, tool devin, swe-2-medium), ledger ready, attempt 1 launched (log .agentflow/tasks/.runtime/T-006.1.log).

## 2026-10-17: T-010 result in, T-011 final local review launched

T-010 developer completed at 0fcd773 (English GUIDE, README, RELEASE_NOTES,
real T-008 dashboard.png, 2.12.0 metadata sync; 204 tests + check_package pass).
Orchestrator wrote the reserved T-011 Task File (tester, devin, swe-2-medium),
ledger ready, attempt 1 launched. Verdict pass -> tick auto-accepts T-010. Any
other verdict -> Orchestrator decides; remote CI/macOS push remains the human's
separate release gate.
