# Current Step

2026-10-18 (2nd update): T-074 developer completed and is in `review`
(Change: 5a6510c9b76201ccce35d1a10ce685be0d76a6e2 on
t-074-routing-core-recovery, attempt 1 exited clean at 06:17:59Z).
Independent tester T-075 written and added `ready`, then moved to `blocked`:
its persisted Jev assessment (req_01a14dab3ab875c5b09fa66a87ab71ed) is low
confidence 0.48 and demands gpt-6-astra class at xhigh (complexity 1.97/2),
so the mandatory routing policy requires an explicit human decision before
launch. Question with options is in state/questions.md.

Next once answered: set Model per the human's choice, launch T-075, then
`accept.py T-074` on a pass -> launch T-076 (assessment medium 0.70,
devin-swe-2 high) -> T-078 -> T-036 -> T-038; T-066 waits on T-078.

Human (2026-10-18) prefers Devin for development, testing and orchestration,
reports no Devin usage limits until 2026-11-01 (no exact cutoff time). This is
qualitative human availability, not measured balance; preserve actual holds,
adequacy and wall-clock caps. Independent tests use fresh exact-SHA sessions;
other-CLI preference must not override this human instruction. T-076/T-078
include tester-routing alignment; T-036 must fix obsolete Result examples.

Conductor PID 10656, 1-minute rounds, hidden Start-Process defaults, positive
1200s worker bound, Devin coordinator. Autostart at logon remains off;
verified current-session restart is in runbook/worker-recovery.md.

T-040/T-072 cancelled as superseded, never falsely done; drafts and patches
preserved. Stage 4 bounded cycle closed (external rollout deferred), Stage 5
current. Only AgentFlow/fixtures; no push/publication or other-project
changes. Preserve concurrent questions.md changes.
