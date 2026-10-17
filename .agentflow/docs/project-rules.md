# Template repository parameters

- Main branch: main.
- Human language: Russian.
- Team Mode is authorized; Single Mode is appropriate for a scoped maintenance task.
- Worker worktrees, when needed: `E:\Projects\AgentFlow\worktrees`.
- Automated tests may create disposable repositories/checkouts in the OS temporary directory.
- This repository's product is the AgentFlow template. Release and verification
  requirements are in [AGENTS.md](../../AGENTS.md#project-rules).
- No push or production deployment without an explicit human request.

Workflow, role ownership and communication: [protocol](ai-handoff-protocol.md).

## Current execution authorization (human, 2026-10-17)

- Execute sequentially: verify the already-closed Stage 3; complete a bounded
  Stage 4 drift review/rollout cycle; then implement Stage 5 per improvement-plan.md.
  Reconcile existing implementations rather than duplicating completed work.
- Human authorizes decomposition, task approval and Developer/Tester execution
  within that scope without another plan approval. Preserve stage ordering.
- Orchestration uses Devin swe-2-high. Prefer the same model for workers, while
  assessing task difficulty. Before assigning a required stronger model, freshly
  check concrete Gemini, Claude and GPT options in agy for inference access and
  resources. Catalog presence is not quota evidence; remaining quota unknown must
  be explicit. Respect observed limits; do not bypass a quota failure.
- Align all affected documentation with accepted behavior through scoped Developer
  tasks, including README, English/Russian guides, protocol, roles/tool notes and
  migration/release documentation. Serialize shared release metadata.
- The planned local WatermarkRemover pilot update is authorized after reading its
  rules and checking active writers/local changes. Preserve project-owned state,
  settings and open tasks; use installer dry-run. Conflicts require resolution,
  never overwriting another writer or changing production.
- No tags, publication or deployment. The earlier push authorization covered
  completed v2.12.0 origin/main; it does not authorize future stage pushes.

## Mandatory assessed-adequacy routing (human, 2026-10-17)

Supersedes the default-only worker routing above. Full text:
`.agentflow/tasks/.runtime/required-routing-policy-2026-10-17.md` (imported as
durable rules below; the runtime file stays the handover record).

- Every task (Developer/Tester/Deployer) needs a persisted Jev assessment via
  `route.py` before execution. Requirements are evaluated independently of
  availability. `.agentflow/docs/model-options.json` is the live config
  (created 2026-10-17; TypeSafe key via AGENTFLOW_TYPESAFE_KEY_FILE, never
  printed or committed).
- swe-2-high is the project floor and preference, not permission to run tasks
  requiring more. If assessment requires stronger, swe-2-high is ineligible;
  adequate concrete Devin models are searched first (swe-2-max, gpt-6-astra-*,
  claude-opus-5-5-* families are configured), then other CLIs. Missing,
  low-confidence or failed assessment blocks the launch - no silent manual
  fallback; an explicit auditable human exception may replace it.
- At launch the resolved model/effort after env/CLI overrides must not be
  lower than the assessed selection; retries, fallbacks and backups satisfy
  the same requirement. Changed contracts invalidate the assessment.
- Observed holds stay honored: a blocked model family does not imply the whole
  tool is blocked (quota groups), and exhausted models are never bypassed.
  No numeric quota balances are persisted; catalog presence is not quota
  evidence; unknown stays unknown.
- The enforcement code is its own scoped Developer task (T-040) with an
  exact-SHA independent Tester; until it lands, admission is the Orchestrator's
  recorded route.py assessment plus this file.
