# Questions for the human

- Roadmap layout selection RESOLVED by the human on 2026-10-18:
  all three mockups A (cards), B (journey), C (matrix) are approved.
  Implement a view selector allowing navigation between all three layouts.
  Do not gate implementation on choosing a single variant. Stage ordering,
  diagnostics placement, task-table depth and extra filters were not explicitly
  selected; retain mockup behavior unless a further decision is needed.
- Optional public README source input: exact AI Home Design SaaS URL and
  YouTube Transcript Extension listing URL. Never invent missing IDs/URLs.
- External release gate: CI run 39026298541 on 50adf65 FAILED - all
  windows-latest and macos-latest test jobs exit 1 at the unittest step;
  ubuntu tests and both package-integration jobs pass. Logs are not readable
  without repository auth (API 403). Needed from the human: open the run in the
  browser and paste the failing test names/step output, or authenticate `gh`,
  so the runner-specific failure can be fixed; a rerun happens on the next
  authorized push anyway. Tag/release publication remains human-only.

No additional plan approval is needed for the completed local task pool.

## 2026-10-18 - T-075 tester launch needs a routing decision (RESOLVED: human approved Option B, Devin swe-2-max; T-075 done 2026-10-18) (RESOLVED)

- Task: T-075 (independent tester for completed T-074 @ 5a6510c).
- Resolution: Human approved Option B on 2026-10-18 - scoped auditable exception
  for Devin swe-2-max (same precedent as T-081).
- What was unblocked: T-075 launch; behind it T-074 acceptance, then the
  T-076 -> T-078 -> T-036 -> T-038 chain and T-066.

## 2026-10-18 - T-092 tester launch needs a routing exception decision (RESOLVED: human chose Option D; codex+claude CLIs excluded) (RESOLVED)

- Task: T-092 (independent tester for T-091 @ 0bf4ac0 - closes the last T-078
  residuals: preferred-CLI independence exemption + full-suite evidence).
- Question: the persisted Jev assessment (req_01a14ea7e1837102b871a4fae80b1749)
  is low confidence (0.34): it demands gpt-6-astra class at xhigh effort
  (complexity 1.96/2). The new admission gate (T-076/T-089, now on main)
  refuses the launch without an explicit auditable human exception - the
  machinery you mandated is working. Which do you approve?
  - A: write Routing exception: <reason> in the T-092 header, launch Devin
    gpt-6-astra-xhigh - adequate Devin option meeting the assessed
    requirement, consistent with your Devin preference.
  - B: write Routing exception: <reason> in the T-092 header, launch Devin
    swe-2-max - the scoped exception you chose for T-075 (precedent T-081).
  - C: Codex gpt-6-astra xhigh (Jev's pick) - but Codex tester writes were
    environment-blocked on this machine, so a fresh attempt may fail again.
  - D: re-scope T-092 to a fast-path re-check (T-085 precedent): the bulk of
    the artifact was already independently verified by T-083/T-086/T-088/
    T-090; a narrower contract lowers the assessed complexity and may pass
    the admission gate without an exception. The Orchestrator rewrites and
    re-assesses; no header needed.
- Resolution: the human chose Option D on 2026-10-18 - re-scope T-092 to a
  fast-path re-check (T-085 precedent), Orchestrator rewrites and re-assesses,
  no Routing exception header needed. The human also clarified that the Codex
  and Claude CLIs currently have no usable resources and do not work; both are
  now statically excluded in docs/model-options.json ("until" fields + policy)
  and must be treated as unavailable in every subsequent assessment until the
  human restores them.
- What waits on it: T-092 rewrite+launch -> T-091 acceptance -> T-036 -> T-038 ->
  T-044 -> T-046 -> T-048 and T-066.

## 2026-10-21 - T-036 and T-066 launches need a routing decision (RESOLVED: human chose Option C + check all available models on low confidence) (RESOLVED)

- Task: T-036 (docs alignment, leads the T-038->T-044->T-046->T-048 chain) and
  T-066 (hidden Windows consoles, queued behind the chain on purpose).
- Situation: T-096 merged the routing stack at 08:32Z, so both are unblocked.
  Fresh Jev assessments now refuse at the admission gate, consistently:
  - T-036: req_01a15d98 + req_01a15d9861 - devin-swe-2 at 0.75-0.81 but effort
    xhigh confidence 0.42-0.45 -> status low-confidence (complexity ~1.86/2).
  - T-066: req_01a15d98d2 - devin-swe-2 at 0.92, effort xhigh confidence 0.42
    -> status low-confidence (complexity 1.98/2).
- Resolution: human chose Option C on 2026-10-21:
  1. Re-scope T-036 into smaller, focused tasks with lower assessed complexity
     (separating core instructions/protocol alignment, shipped features docs,
     and user guides/Russian translation parity).
  2. The available model catalog is defined by what is live in the Devin CLI
     (`devin models list`), including swe-2, claude-opus-5.5, claude-sonnet-5.5,
     gpt-6-astra, gpt-6-sol, gpt-6.1-sol, gemini-4-argon, gemini-3.8-flash,
     deepseek-v4-pro, kimi-k3, and other supported families. In cases of ambiguity,
     uncertainty, or low confidence for a candidate, Jev/routing must evaluate the
     other available models in the Devin CLI catalog to select one with higher
     confidence rather than halting.
- What was unblocked: Orchestrator re-scopes T-036 into smaller subtasks under the
  Devin CLI model catalog policy, assessments rerun for high-confidence launch.

## 2026-10-21 - T-066 unlaunchable after catalog re-assessment (RESOLVED: automatic model/platform rotation mandated; no waiting for quota resets) (RESOLVED)

- Task: T-066 (hide Windows background process consoles), stays queued behind
  the T-097 -> T-098 -> T-099 -> T-038 -> T-044 -> T-046 -> T-048 chain.
- Situation: Jev assesses T-066 with devin-swe-2 at 0.96 confidence, but effort
  confidence is 0.45.
- Human instruction (2026-10-21): Waiting for an external platform limit reset (e.g.
  Antigravity until 22:09Z) is rejected. The project must implement and rely on
  automatic rotation of platforms and models based on live availability and capacity.
  When an option or platform is held or uncertain, the orchestrator/router rotates
  through available catalog models and backups without stalling for hours.
- Resolution: Automatic platform/backup rotation enabled by default in tick.py;
  Option C (waiting for agy reset) discarded. T-066 will proceed via dynamic rotation
  to an adequate available model or re-scoping when reached in the queue.
- What waits on it: only T-066; the documentation chain proceeds regardless.

## 2026-10-24 - Stage 7 cannot close: seven `done` ledger rows lack Task Files

- Found by `gate.py stage 7` (read-only check after T-130/T-131 acceptance).
- Missing Task Files in `.agentsflower/tasks/`: T-121, T-123, T-124, T-126,
  T-127, T-128, T-129 - all ledgered `done` (Studio UI, skills ecosystem,
  multi-project gateway work, already on main at 2.17.0). No trace of the
  files in git history or any worktree, so they were likely authored in a
  session that never committed them, or executed without one.
- Options: (a) reconstruct skeletal Task Files matching the merged diffs so the
  gate has contracts to check; (b) a human decision to retire/amend those rows
  or the stage's exit accounting; (c) leave Stage 7 open.
- What waits on it: Stage 7 closure only. No open tasks depend on the answer.
