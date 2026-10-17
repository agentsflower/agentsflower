# Session Handoff

As of 2026-10-17 main is local-ahead (last pushed baseline main@50adf65 v2.12.0;
local HEAD contains Stage 5 work through 2.13.1 pending acceptance merge).
Remote CI run 39026298541 FAILED on windows/macos test jobs (logs need auth;
details in known-issues.md).

CURRENT HUMAN SCOPE (2026-10-17, latest wins): foreground Orchestrator, holder
devin, model swe-2-high. Repository-only: all work in AgentFlow and its own
task/disposable checkouts. WatermarkRemover must NOT be rolled back and must
NOT be touched again - no updates, commits or worker launches; no other product
repository either. Supersedes all earlier pilot rollout authorization.
Installer/migration validation happens in disposable AgentFlow fixtures;
external rollout criteria are recorded out of scope, never fabricated done.
No push, tags, publication or deployment.

MANDATORY ROUTING: every worker launch needs a persisted route.py Jev
assessment (.agentflow/tasks/.runtime/T-NNN.route.json) under
docs/model-options.json. swe-2-high is the floor, never a downgrade of an
assessed-stronger task; adequate Devin models first, then other CLIs; no
adequate model = block with reason; codex is environment-blocked for workers
on Windows (sandbox denies writes outside checkout - Result file and Python
tempdirs; evidence .runtime/T-029.1.log); agy tool-wide hold until
2026-10-21T22:09Z covers Claude/GPT families, agy-gemini is a separate quota
group. Enforcement implementation task: T-040.

QUEUE: T-053 tester running on T-052 @ 5b3797b (do not duplicate); then T-032
-> tester T-033 -> T-034 -> T-035 -> T-040 -> T-041 -> T-036 -> T-037 -> T-038
-> T-039; dashboard T-044 -> T-045 -> T-046 -> T-047 -> T-048 -> T-049 after
T-038 and the human's mockup variant selection (questions.md lists the five
selection questions; mockups live in .agentflow/dashboard/mockups/). Task
headers carry assessed models (swe-2-max for T-030/32/34/36/40/44/50;
swe-2-high for T-038/42/46/48/52/53).

A false devin tool-limit may reappear while T-052's detector fix is unmerged:
worker Result prose about quota limits trips learn_limits; recorded reason is
a prose fragment, never a provider message. Clear it via the registry and
.agentflow/tasks/.runtime/tool-limits.json, preserving the agy hold.

Preserve rejected worktrees (t-028-lifecycle-trust @ 2c58157, t-030-recoverable-
handover @ f6d746b - both are the base of their accepted successors).
Checkpoint memory on a task branch with the standard checks, merge to main,
clean up. Russian user updates, English machine evidence.
