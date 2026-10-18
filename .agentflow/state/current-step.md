# Current Step

2026-10-18 (5th update, background devin): the whole T-040 routing line is on
main. T-076 rejected on T-086 D-01 (codex --config alias bypass) -> T-087
rejected on T-088 F-01 (repeated-key precedence + cross-tool hazard) ->
T-089 repaired+verified (T-090 pass) and merged at 52b06aa (2.15.3).
T-078 scheduler/reports artifact completed at 0ba5d37 but rejected on two
self-reported residuals (S-05 route.py preferred-CLI exclusion, S-03
unrecorded full suite) -> T-091 repaired at 0bf4ac0 (prefer-scoped
exemption + 424-test suite green + inherited fixture repairs) -> its
tester T-092 assessed astra/xhigh at LOW confidence 0.34 - the new
admission gate now refuses low-confidence launches, so T-092 is locked
on a human Routing exception: decision (questions.md, options A-D incl.
a fast-path re-scope).

Next once the human answers: apply the chosen header/scope, launch T-092 ->
accept T-091 -> T-036 (refresh assessment) -> T-038 -> T-044 -> T-046 ->
T-048; T-066 waits on T-091 too. Rejected draft branches kept for the
human's cleanup: t-076, t-082, t-087 (+ worktrees).
Human (2026-10-18) prefers Devin for development, testing and orchestration,
reports no Devin usage limits until 2026-11-01 (no exact cutoff time). This is
qualitative human availability, not measured balance; preserve actual holds,
adequacy and wall-clock caps. Independent tests use fresh exact-SHA sessions;
other-CLI preference must not override this human instruction. T-036 must fix
obsolete Result examples.

Conductor PID 10656, 1-minute rounds, hidden Start-Process defaults, positive
1200s worker bound, Devin coordinator. Autostart at logon remains off;
verified current-session restart is in runbook/worker-recovery.md.

T-040/T-072 cancelled as superseded, never falsely done; drafts and patches
preserved. Stage 4 bounded cycle closed (external rollout deferred), Stage 5
current. Only AgentFlow/fixtures; no push/publication or other-project
changes. Preserve concurrent questions.md changes.
