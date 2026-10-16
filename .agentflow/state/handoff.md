# Session Handoff

Background session devin, 2026-10-16T21:30Z: decided T-019's fail verdict
(T-016 stays rejected, T-019 done), created and ran T-020 developer + T-021
tester, verified and merged the Linux defect repair to main (eb59c7c).
Waits: T-018 blocked on the human's macOS route (questions.md); nothing else
runnable - no ready tasks, no undecided results.

As of 2026-10-16, main@eb59c7c: product is AgentFlow 2.11.9 - the T-016
launcher-hardening candidate plus T-020's Linux defect repairs is merged.

Verified state: T-019 produced real Linux evidence on candidate 1e0bd87 via
Docker (python:3.12-slim, WSL2 kernel) - Verdict fail with three reproducible
defects. T-020 (devin) ported the candidate onto main and repaired them
(bafc2a0): run_logged spawns the tool in its own POSIX session so killpg cannot
self-kill the worker; kill_tree signals the whole tree's process groups
(/proc first, ps fallback - slim images ship no ps); accept.py drops
`merge-tree --write-tree --quiet` (unsupported by git 2.47.3); test_endcheck
merge fixture carries an explicit git identity. T-021 (devin, same tool -
Codex conserved, agy/claude limited) independently verified the exact SHA on
real Linux: 151 tests, 0 failed, 18 Windows-only skips, Verdict pass.

Waits for the human: T-018 blocked; its question is now only the macOS route
(real macOS host or Multi-OS CI branch for the human's manual push -
questions.md). Re-scope T-018 before unblocking: Docker covers Linux and
accept.py was outside its ownership. Rejected branches/worktrees t-001, t-012,
t-014, t-016 preserved awaiting cleanup agreement. Untracked `nul` file left
untouched (foreign). No push or release by agents.

Open risks (known-issues.md): recurring machine_capacity._locked os.replace
WinError 5 flake (T-021 saw it twice; retry-backoff candidate, not this
commit's code); conductor.ps1 raw env handover still needs its own repair.

First reads: current-step.md, questions.md, known-issues.md, T-021 Result.
