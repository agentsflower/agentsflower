# Session Handoff

Background session devin, 2026-10-24 ~12:32Z (devin-background): cleared the
last open need. T-131's accept had stopped at `gate.py verify` - the tester
wrote evidence under `.runtime/T-131.evidence/` but without the required
`T-131.` basename prefix. Repaired by renaming the three evidence files and
fixing the claimed paths in the Result (verdict/evidence content unchanged;
same surgical-fix precedent as T-100). verify PASS -> T-131 accepted -> tick
mechanically accepted T-130: merged main 3d89d3c, branch/worktree cleaned.
Ledger is fully clean - every row done/rejected/cancelled, nothing ready.

What waits: `gate.py stage 7` FAILs - seven `done` rows (T-121, T-123, T-124,
T-126..T-129) have no Task File in `.agentsflower/tasks/` and none in git
history. Human decision needed (reconstruct skeletons vs amend the rows) -
details and options in questions.md 2026-10-24. Stage 7 stays `current`;
closing it is a plan update beyond the background mandate.

State: main 3d89d3c @ 2.17.0 holds Stage 7 output end to end: Graft
integration, Studio cockpit, skills registry, multi-project gateway+explorer,
local-model failover, project CLI. Old rejected-draft worktrees/branches
(t-076, t-082, t-087, t-093, t-094, t-095, plus many pre-Stage-7 leftovers in
`worktrees/`) remain for the human's cleanup call.

Known-issues gained: `.runtime` evidence requires the `T-NNN.` BASENAME
prefix, the folder name alone is not enough; and the stage-7 missing-files
gap (both dated 2026-10-24). Earlier entries: `evidence:` marker may appear
once per Result line; paths() one-path-per-bullet (resolved).

Human prefers Devin for all roles, no usage limits reported until 2026-11-01.
Codex/Claude CLIs statically excluded in model-options.json until restored.
Conductor runs hidden; autostart off; restart steps in
runbook/worker-recovery.md. Source authority remains origin
agentsflower/agentsflower.

Read: project-rules.md, current-step.md, questions.md (stage-7 gap entry),
ledger, T-131 Result.
