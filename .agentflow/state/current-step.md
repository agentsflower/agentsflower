# Current Step

2026-10-18 (6th update, foreground devin): the human answered the T-092
question - Option D: re-scope T-092 to a fast-path re-check (T-085
precedent; the bulk of 0bf4ac0 was already independently verified by
T-083/T-086/T-088/T-090), no Routing exception header. The Orchestrator
rewrites the contract and re-assesses; the narrower scope should clear
the admission gate. The human also clarified that the Codex and Claude
CLIs have no usable resources and do not work - both are now statically
excluded in docs/model-options.json ("until" 2026-10-17 on all
codex-*/claude-* options + policy text) until the human restores them;
Devin-hosted families incl. devin-claude-opus-5.5 are unaffected. Prior
state: the whole T-040 routing line is on main. T-089 repaired+verified
(T-090 pass) and merged at 52b06aa (2.15.3); T-091 repaired T-078's
residuals at 0bf4ac0 and waits in review on its tester.

Next: rewrite+re-assess T-092 as a fast-path re-check, launch it ->
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
