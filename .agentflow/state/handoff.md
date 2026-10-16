# Session Handoff

As of 2026-10-16: main product remains AgentFlow 2.11.8; no candidate code merged.

Latest candidate: 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 in
E:\Projects\AgentFlow\worktrees\agentflow-t-016-probe-hardening, version 2.11.9.
It fixes agy Tester -i hang, adds streaming and 1200s worker bound, built-in-only
opt-in model checks, probe tree bounds, hash-only sensitive config evidence,
spawn-only env handover and successful-report limitHit regression.

T-017 independently passed all local criteria and 151 tests on Windows 10 /
Python 3.13. Overall unverified only for actual macOS/Linux paths. Accepted review
through accept.py; T-016 rejected to blocked T-018 per lifecycle. No workers live.

Human question pending in questions.md: actual Unix hosts vs CI branch for human
manual push. No push or release by agents. Preserve 06b7e3a, 87de72c, 549245f,
1e0bd87 branches/worktrees and tester evidence. Do not accept on Windows-only proof.

Known separate risk: conductor.ps1 writes raw AGENTFLOW_* into conductor.env.json.
Old main limitHit heuristic can misread successful prose; inspect logs before any
resource correction. Candidate has the fix. Untracked nul is foreign; untouched.

First reads: current-step.md, questions.md, T-017 Result, T-018 contract, decisions.md.
