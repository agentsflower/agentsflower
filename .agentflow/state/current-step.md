# Current Step

2026-10-21 (13th update, background devin): the T-036 re-scope train is
landed - T-097 (25b8b2e), T-098 (38f94f6) and T-099 (4519a63) are all `done`
with independent tester passes (T-100/T-101/T-102). Version is 2.15.6 on
main. T-038 (evaluation scenarios, migration proof, Stage 5 release
metadata) is `in progress` - devin worker attempt 1 running since ~12:11Z
on swe-2-high.

Chain order remaining: T-038 -> T-044 -> T-046 -> T-048, then T-066
(Allowed-files overlap with T-044..T-048 docs, deliberate queue). T-066 is
`ready` - the new rotation routing (route.py low-confidence candidate
rotation + AGENTFLOW_BACKUP_ROUTING=on by default, human-mandated
2026-10-21) admits swe-2-max at medium confidence.

Note: two T-098/T-099 attempts hit the 2400s wall clock while the full
suite ran and were resumed on their preserved drafts via `Resume:` -
pattern works as designed. A transient WinError-5 os.replace flake in
temp-dir tests was seen twice; unrelated to the changed files.

Rejected draft branches kept for the human's cleanup: t-076, t-082, t-087,
t-093, t-094, t-095 (+ their worktrees); the T-091 worktree/branch 0bf4ac0
is merged history - cleanup is safe but stays the human's call.

Human (2026-10-18) prefers Devin for development, testing and orchestration,
reports no Devin usage limits until 2026-11-01 (qualitative, not measured).
Codex and Claude CLIs are statically excluded in docs/model-options.json
until the human restores them; the live Devin CLI catalog (`devin models
list`) is the model pool authority, and low confidence must trigger
evaluation of the whole catalog before halting.

Conductor PID 10656, 1-minute rounds, hidden Start-Process defaults, 2400s
worker bound. Autostart at logon remains off; verified current-session
restart is in runbook/worker-recovery.md.

Stage 5 current. Only AgentFlow/fixtures; no push/publication or
other-project changes. Preserve concurrent questions.md changes.
