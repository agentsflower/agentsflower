# Current Step

2026-10-21 (10th update, background devin): the T-095 carrier verified PASS
on 0477331, but the trial merge conflicts on release metadata (branch 2.15.4
vs main 2.15.5) - the anticipated stale-branch case. T-095 rejected ->
T-096 merge-only successor launched as managed devin attempt 1 (pid 3092,
deadline ~08:4xZ, log .runtime/T-096.1.log): merge t-095-fixed-clock-carrier
into a branch from main, resolution pinned (VERSION/AGENTS block = 2.15.5,
CHANGELOG = verbatim 2.15.5 + 2.15.4 entries), full suite on the merge SHA.
Jev ok 0.86 band medium, devin-swe-2 swe-2-high confirmed.

Next: when T-096's Result lands, `gate.py verify T-096` then `accept.py`
(Independent check: none per contract) -> T-036 (refresh assessment before
launch) -> T-038 -> T-044 -> T-046 -> T-048; T-066 also unblocks on T-096.
Rejected draft branches kept for the human's cleanup: t-076, t-082, t-087
(+ worktrees); keep branches t-094-fixed-clock-test-repair and
t-093-fixed-clock-test-repair and the T-091 worktree/branch 0bf4ac0 until
T-096 merges; t-095-fixed-clock-carrier is the merge source - accept.py
cleans it.

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
