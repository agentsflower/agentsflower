# Current Step

2026-10-21 (9th update, background devin): T-094 rejected - its `Allowed
files` used comma-separated bullet lines, which gate.py never parses
(first whitespace token only), so verify flagged five inherited-base files
and acceptance could never pass. Orchestrator authoring defect, not a product
defect; artifact 0477331 complete+green. Carrier T-095 (same scope, Allowed
files one path per line, carries 0477331 via `git reset --hard`, Jev ok
0.81 band medium, devin-swe-2 swe-2-high confirmed) launched as managed devin
attempt 1 (pid 29976, deadline ~08:3xZ, log .runtime/T-095.1.log).

Next: when T-095's Result lands, `gate.py verify T-095` then `accept.py`
(Independent check: none per contract) -> T-036 (refresh assessment before
launch) -> T-038 -> T-044 -> T-046 -> T-048; T-066 also unblocks on T-095.
Expect merge conflicts on VERSION/CHANGELOG/AGENTS.md vs main 2.15.5 -
resolve via the standard merge-fix successor if the trial merge fails.
Rejected draft branches kept for the human's cleanup: t-076, t-082, t-087
(+ worktrees); keep branch t-094-fixed-clock-test-repair (holds carried
0477331) and t-093-fixed-clock-test-repair (carry commit 0b82f61) until the
carrier merges; the T-091 worktree/branch 0bf4ac0 is the stack's base - keep
it until T-095 merges.

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
