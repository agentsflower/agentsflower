# Current Step

2026-10-21 (8th update, background devin): T-093 resolved as rejected - its
manual attempt was stopped with no Result and a raced-in managed attempt 2
was stopped after committing the correct repair 0b82f61 onto 0bf4ac0 (kept
on branch t-093-fixed-clock-test-repair). Successor T-094 (identical
contract, carries 0b82f61, swe-2-high assessment ok) launched as managed
devin attempt 1. T-036/T-066 Depends on repointed to T-094 in ledger and
Task File headers.

Next: when T-094's Result lands, `gate.py verify T-094` then `accept.py`
(Independent check: none per contract) -> T-036 (refresh assessment before
launch) -> T-038 -> T-044 -> T-046 -> T-048; T-066 also unblocks on T-094.
Expect merge conflicts on VERSION/CHANGELOG/route.py vs main 2.15.5 -
resolve via the standard merge-fix successor if the trial merge fails.
Rejected draft branches kept for the human's cleanup: t-076, t-082, t-087
(+ worktrees); the T-091 worktree/branch 0bf4ac0 is T-094's base - keep it
until T-094 merges; keep branch t-093-fixed-clock-test-repair too (holds
carry commit 0b82f61).

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
