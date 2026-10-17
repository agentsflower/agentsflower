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
