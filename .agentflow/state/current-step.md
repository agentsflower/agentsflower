# Current Step

2026-10-21 (11th update, background devin): the routing chain is fully
merged - T-094's verified artifact 0477331 was carried by T-095 (contract
re-authored one-path-per-line) and landed via merge successor T-096 @
6754959 / merge 8b588f9 (resolution: VERSION/AGENTS = 2.15.5, CHANGELOG =
verbatim 2.15.5 + 2.15.4 entries; full suite 424/0/3 on the merge SHA).
T-036/T-066 `Depends on` repointed T-094 -> T-096.

2026-10-21 (12th update): human confirmed Option C (re-scope T-036 into
smaller subtasks T-097 -> T-098 -> T-099) and full Devin CLI model availability
(devin models list). T-036 cancelled as superseded; T-097 (entry points,
instruction hierarchy, Result examples) authored, Jev assessed ok at complexity
1.25 (confidence 0.54, swe-2-high, 0.94 probability), launched as Devin attempt 1
(pid 73516 / devin pid 104952). T-038 repointed to T-099.

Next: when T-097's Result lands, independent verification -> T-098 -> T-099 ->
T-038 -> T-044 -> T-046 -> T-048; T-066 follows. Rejected draft branches kept
for human cleanup: t-076, t-082, t-087, t-093, t-094, t-095.

Human (2026-10-18) prefers Devin for development, testing and orchestration,
reports no Devin usage limits until 2026-11-01 (no exact cutoff time). This is
qualitative human availability, not measured balance; preserve actual holds,
adequacy and wall-clock caps. Codex and Claude CLIs are statically excluded
in docs/model-options.json until the human restores them. T-036 must fix
obsolete Result examples.

Conductor PID 10656, 1-minute rounds, hidden Start-Process defaults, positive
1200s worker bound, Devin coordinator. Autostart at logon remains off;
verified current-session restart is in runbook/worker-recovery.md.

T-040/T-072 cancelled as superseded, never falsely done; drafts and patches
preserved. Stage 4 bounded cycle closed (external rollout deferred), Stage 5
current. Only AgentFlow/fixtures; no push/publication or other-project
changes. Preserve concurrent questions.md changes.
