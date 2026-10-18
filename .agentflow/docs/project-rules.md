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
- Repository-only scope (explicit human clarification, 2026-10-17): all further
  work is restricted to AgentFlow and its own task/disposable test checkouts.
  WatermarkRemover is a separate project: no rollback of the previous update
  and no further changes, updates, commits or worker launches there.
  No modifications or rollout in any other product repository. Earlier pilot
  references are historical/deferred scope, never current authorization.
  Validate installer/migration/rollout in disposable AgentFlow fixtures;
  keep any unmet external rollout criterion explicitly out of scope.
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
- The enforcement code is delivered by T-074/T-076/T-078 (the bounded
  replacement of T-040), each with an exact-SHA independent Tester; until it lands, admission is the Orchestrator's
  recorded route.py assessment plus this file.

## Urgent execution discipline (2026-10-18)

Implements the human's request to diagnose stalled work and restore bounded
progress; rationale and scoped routing exceptions are in state/decisions.md.

- Use the gate's actual Result syntax for every criterion:
  `- A-01: pass - <evidence>` (or partial/unverified/fail with the task's ID).
  Older role examples without the colon and explicit verdict are obsolete;
  T-036 must align those examples. Never invent evidence to satisfy the parser.
- Run the mandatory whole suite before a code commit, once after a coherent
  change. Do not repeat a green whole suite merely to change redirection,
  display format or confidence wording. Changed inputs or a diagnosed failure
  justify new checks; acceptance contracts use relevant scoped commands.
- A timeout requires inspection of preserved progress and the actual cause,
  not a blind fresh context or an unchanged retry. A same-task Devin native
  conversation may be resumed through the launcher after verified stop; never
  share it across tasks, and never leave its resume flag in global settings.
- Keep attempt/verification history and drafts. A successor changes a real
  scope or fixes a diagnosed defect; it is not a way to hide failed attempts or
  silently reset a budget. Preserve required routing and independent review.

## Devin preference and reported availability (human, 2026-10-18)

- Prefer Devin for development, independent testing and orchestration. The
  human reports no Devin usage limits until 2026-11-01 (exact cutoff time not
  supplied). This is human-reported qualitative availability, not a measured
  numeric account balance.
- Independent testing still uses a fresh session and an isolated checkout of
  the exact artifact. The human's Devin preference supersedes the generic
  preference for a different CLI; independence and evidence are not waived.
- Preserve mandatory assessed adequacy, concrete model access probes, task
  duration/attempt caps and any actual observed provider hold. Use another
  tool only when no adequate Devin option is usable; never lower requirements
  or bypass an observed quota failure because of the availability report.
- The Codex and Claude CLIs have no usable resources and do not work (human,
  2026-10-18). Every subsequent assessment must treat both as unavailable;
  they are statically excluded via `until` fields in docs/model-options.json.
  Devin-hosted model families are unaffected. Restore by removing those
  fields when the human reports resources back.
