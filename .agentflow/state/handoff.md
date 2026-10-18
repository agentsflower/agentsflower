# Session Handoff

Background session devin, 2026-10-18 ~21:37Z (devin-background): claimed
heartbeat; the manual T-092 tester attempt (run in the human's session
while the devin CLI was unauthenticated) completed verdict FAIL on T-091 @
0bf4ac0 - verified, accepted (verdict=worst criterion). Defect isolated to
test_routing_scheduler.py's fixed AT constant: its recorded "live" hold
expired at 13:00Z, breaking the suite deterministically. T-091 rejected;
T-093 successor (carry 0bf4ac0 + now-relative holds) was authored, assessed
(req_01a150e, devin swe-2-high, medium band) and launched -Manual by a
concurrent human-side burst at 21:31Z; attempt running. T-036/T-066 Depends
on repointed T-091 -> T-093. devin CLI authenticated again - managed
launches usable. Removed a duplicate T-093 file I had authored in parallel.
What waits: T-093 manual Result -> verify -> accept (Independent check:
none) -> T-036 (refresh assessment) -> T-038 -> T-044 -> T-046 -> T-048,
T-066.

State: T-040 routing line merged through 2.15.4-dev (T-082/T-084 holds at
2.15.2, T-076/T-089 launch admission at 2.15.3). T-091 worktree/branch
t-091-tester-independence-preference @ 0bf4ac0 is T-093's base - keep it.
Rejected draft branches kept for the human: t-076, t-082, t-087.

Confirmed prior stall cause: Windows idle standby 04:49-07:45 Moscow 2026-10-18;
fixed by accepted 2.15.1 (T-080/T-081). Manual sleep/lid stays a user action.

Human prefers Devin for all roles, reports no usage limits until 2026-11-01
(qualitative, not measured). Codex and Claude CLIs statically excluded in
docs/model-options.json ("until" fields) until the human restores them;
Devin-hosted families unaffected. agy limited until 2026-10-21T22:09Z.

Conductor is running hidden (PID 10656), 1-minute rounds, 1200s worker cap.
Autostart at logon off; current-session restart in runbook/worker-recovery.md.

Result criteria need `- ID: pass - evidence`; T-036 aligns the stale role
examples. Only AgentFlow and disposable fixtures; no external rollout/push/
tags/releases. Source authority remains origin vcherstar/AgentFlow.

Read: project-rules.md, current-step.md, questions.md (all resolved or
waiting on the human), ledger, T-092 Result, T-093 task file.
