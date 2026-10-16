# Session Handoff

As of 2026-10-16: main contains planning/recovery records, no launcher product merge.

T-001 rejected, T-002 cancelled after interactive agy hang. T-012 recovered port
on Devin medium and produced 87de72c in t-012-launcher-recovery. T-013 independently
verified Windows behavior and 147 tests, completed with Verdict unverified for
real Unix coverage; accepted as a review via accept.py. T-012 rejected to T-014:
selected-model inference access is not established by current auth/catalog probes.
T-014 prepared, blocked; no workers running. See current-step and ledger.

Need human's Unix verification route (real hosts or Actions after manual push).
Code follow-up also handles secret-safe probe evidence and visibility policy.
Do not accept 87de72c on Windows tests alone. Preserve both original candidate
worktrees; untracked nul is unrelated. No push or GitHub publication authorized.

First reads: current-step.md, decisions.md, T-013 Result, T-014 contract.
