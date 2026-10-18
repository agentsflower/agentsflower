# TypeSafe AI in AgentFlow

`route.py` asks TypeSafe AI's System One model, Jev, which of the project's options should take a task. Anyone who
uses or changes this integration works from the official documentation, not from memory or third-party pages:

- Start here: https://docs.typesafe.ai/introduction (index for tools: https://docs.typesafe.ai/llms.txt)
- API: https://docs.typesafe.ai/api.md - `POST https://api.typesafe.ai/v1/systemone`, `Authorization: Bearer <key>`,
  body `{state, model, questions}`; errors 401 key, 422 validation, 429 rate limit, 529 overloaded (back off, retry)
- Questions: https://docs.typesafe.ai/primitives/choice.md (up to 255 options), https://docs.typesafe.ai/primitives/score.md
  (2-10 ordered levels), https://docs.typesafe.ai/primitives/noul.md, https://docs.typesafe.ai/primitives/advanced.md
- State: https://docs.typesafe.ai/concepts/state.md - text only; an object with named fields for most requests
- Confidence: https://docs.typesafe.ai/confidence.md
- Building: https://docs.typesafe.ai/concepts/how-to-build-with-system-one.md, https://docs.typesafe.ai/patterns/intent-routing.md
- Models, limits, price: https://docs.typesafe.ai/models.md
- Keys: https://console.typesafe.ai/keys; SDK variables `TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`

## Rules from the documentation that route.py follows

1. Jev makes fast, atomic, typed judgments; it is not for extended reasoning. Decompose: several narrow questions in
   one request (they run in parallel), combined by deterministic code. route.py asks which tool/model family fits,
   which generic reasoning effort the task needs, and a 3-level "complexity" score. Code maps the chosen effort to
   the closest level that the selected model supports (preferring the stronger level on a tie), and escalates a pick
   whose `max_complexity` is exceeded to its `escalate_to` option.
2. State is an object with named fields and only what the decision needs (the task's title, role, goal, acceptance
   criteria, allowed files, checks, repositories); questions and policy stay out of the state. The state budget is
   32k tokens (64k per request): long fields are clipped. English gives the best accuracy (Task Files are English).
3. Choice criteria are objects: `what`, `not_for`, `examples`, supported effort levels, cost, latency, and context draw
   the boundary between options. Write them in `model-options.json`; the project policy goes into the question's
   instructions. Use `model` + `efforts` when the CLI takes a separate effort flag. Use `model_by_effort` when the
   effort is part of the concrete model id, as with Devin and the installed Antigravity CLI. `tier` declares the
   capability ceiling of an effort-less model; `quota_group` binds an option to a provider billing group, so a
   group hold does not blanket the whole tool.
4. Confidence: `(p_max - 1/n) / (1 - 1/n)` for a choice. For a model with selectable effort, routing confidence is
   the lower of the model and effort confidences. Bands: >= 0.9 act automatically (`--apply`), 0.5-0.9 a recommendation
   the Orchestrator confirms, < 0.5 no decision (tool-routing.md decides). The docs say to start conservative and
   calibrate on your own results: keep `T-NNN.route.json` and compare it with how tasks went.
5. Pin the Jev version you calibrated on (`jev_model` in `model-options.json`, default `jev-1.13.0`); move to a new
   version on purpose, re-checking the bands.
6. Every call records Jev's version, token usage and `x-typesafe-request-id`; quote the request id to TypeSafe support.
   Price: input tokens only (see Models); one route call is about 1k input tokens.
7. The key is a secret: environment `TYPESAFE_API_KEY` or a file named by `AGENTFLOW_TYPESAFE_KEY_FILE`, outside the
   repository; never printed, logged or committed. Tests use a local stand-in server, never the real service.
8. The option choice probabilities rank configured candidates, but selection is requirement-first: only options
   that can express the assessed effort (lifted by the project `floor` in model-options.json, never lowered) and
   complexity are candidates. Among them the `floor` option leads, then `prefer`red CLIs, then the rest by Jev
   probability. The backup is the highest-ranked adequate candidate on another CLI platform - a backup below the
   requirement is ineligible. Missing executables and observed quota holds are excluded before the call and
   recorded per option; an adequate-but-held option is named so a blocked launch knows what it waits on. CLI model
   entitlement and account access can still fail only when a real session starts.
9. `plan_route.py` uses the same atomic Jev questions on a short planning goal and never changes the user's current chat. `route_report.py` reads routing metadata, task outcomes, and attempt histories to compare similar tasks; its counts are not a causal measure of model quality. It does not infer unavailable worker cost or token use.
10. Every route.py call persists an `assessment` event (schemaVersion 1) in
    `.agentflow/tasks/.runtime/T-NNN.route.json`, bound to `requirementsHash` - the task header without the routing
    fields (Tool/Model/Backup/Routing exception/Resume). Status is `ok`, `blocked`, `low-confidence` or `failed`;
    a missing, stale or non-ok record is a diagnosable block, never an admission. A `Routing exception:` header
    line is the auditable human override and is recorded as a human decision, never as Jev evidence.
    `route.assessment_problems()`, `route.admission()`, `route.backup_ok()` and `route.log_admission()` are the
    launch-side API wired into the launcher (T-076): every launch and retry is refused without a usable record,
    and `admission()` re-checks the resolved model/effort after `AGENTFLOW_<TOOL>_ARGS` overrides against the
    recorded requirement. The scheduler uses the same API (T-078): `tick.py run` turns a ready task whose record
    fails `assessment_problems()` into a diagnosable need instead of a doomed launch, and a backup switch
    (`AGENTFLOW_BACKUP_ROUTING=on`) rewrites the header only after `backup_ok()` confirms the recorded backup
    meets the requirement and carries no live group hold. `route_report.py` items expose the assessment's
    status/band, `required`, `floor`, `excluded`/`inadequate`/`adequateHeld` and `blocked` reasons plus the
    admission/human-exception counts, source, deviation and reason; absent metadata stays `null`, never invented.
