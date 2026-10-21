# Current Step

2026-10-21 (12th update, background devin): T-036 re-scope is executing.
T-097 (core instructions/protocol alignment) is `in progress` - devin worker
attempt 1 running since ~08:54Z on swe-2-high. T-098 (shipped-features docs)
and T-099 (GUIDE.ru parity + release metadata) Task Files are written and
both have `ok` Jev assessments (devin-swe-2 -> swe-2-high, medium band).

Chain order: T-097 -> T-098 -> T-099 -> T-038 -> T-044 -> T-046 -> T-048,
then T-066 (Allowed-files overlap, deliberate queue).

Blocked on the human (questions.md 2026-10-21, OPEN): T-066 launch - the
catalog re-assessment still yields effort-xhigh confidence 0.45
(complexity 1.98/2); all other Devin catalog models scored ~0. Options:
Routing exception header (swe-2-max, T-075/T-081 precedent), approved
re-scope, or wait for agy's limit expiry 2026-10-21T22:09Z.

Rejected draft branches kept for the human's cleanup: t-076, t-082, t-087,
t-093, t-094, t-095 (+ their worktrees); the T-091 worktree/branch 0bf4ac0
is merged history - cleanup is safe but stays the human's call.

Human (2026-10-18) prefers Devin for development, testing and orchestration,
reports no Devin usage limits until 2026-11-01 (qualitative, not measured).
Codex and Claude CLIs are statically excluded in docs/model-options.json
until the human restores them; the live Devin CLI catalog (`devin models
list`) is the model pool authority, and low confidence must trigger
evaluation of the whole catalog before halting.

Conductor PID 10656, 1-minute rounds, hidden Start-Process defaults, 1200s
worker bound. Autostart at logon remains off; verified current-session
restart is in runbook/worker-recovery.md.

Stage 5 current. Only AgentFlow/fixtures; no push/publication or
other-project changes. Preserve concurrent questions.md changes.
