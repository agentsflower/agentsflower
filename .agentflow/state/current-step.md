# Current Step

2026-10-16: main is now 2.11.9 (merge eb59c7c). T-020 ported the T-016 candidate
onto main and repaired the three T-019 Linux defects; T-021 independently
verified the exact commit on a real Linux kernel in Docker (151 tests, 0 failed,
18 Windows-only skips) and accepted Verdict pass. T-019/T-020/T-021 are done.

Next action waits on the human: T-018 stays blocked - its question is now only
the macOS route (real macOS host, or Multi-OS CI branch for the human's manual
push; see questions.md). Re-scope T-018 before unblocking: Docker now covers
Linux, and accept.py was never in its ownership. Nothing else is runnable:
no ready tasks, no undecided results.

Housekeeping for the human: rejected branches/worktrees t-001, t-012, t-014,
t-016 remain preserved per the cleanup-agreement rule; stray untracked `nul`
file is foreign, left untouched; worker-created ref
refs/remotes/origin/t-020-linux-defect-repair was deleted after the merge.

Separate open risks (known-issues.md): recurring machine_capacity._locked
os.replace WinError 5 flake (T-021 reproduced twice; retry-backoff would
harden); conductor.ps1 writes raw AGENTFLOW_* into conductor.env.json.
No push, publication or production deployment by agents.
