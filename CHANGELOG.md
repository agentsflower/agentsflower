# Changelog

What changed in each AgentFlow version. Why it changed: `.agentflow/state/decisions.md`. The version of an installed project: `.agentflow/VERSION` (2.1.x: `AgentFlow version:` in its `AGENTS.md`).

## 2.15.8 - 2026-10-21

Roadmap data layer for the dashboard (T-044, planning draft
`.agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md` sections 1-3;
mockup selection recorded in decisions.md 2026-10-18). `build.py` now parses
`docs/project-plan.md` into stage records and joins them with ledger, Task File
and `.runtime/` evidence into one `schemaVersion: 1` payload shared by both
pages. All additions are additive: existing task fields are unchanged (a golden
fixture in `test_dashboard.py` pins them against the pre-change build), and the
pages themselves render exactly as before - the roadmap UI lands separately.

- `stages[]`: every `### Stage <id>` section of the plan, in source order, with
  declared status (raw + normalized), verbatim exit criteria, linked task ids
  and execution counters with an explicit denominator. Declared status, task
  counts and criterion evidence stay three independent facts; no stage-completion
  percentage exists and a zero-task stage is "no local tasks", not 0%/100%.
- Optional authored plan syntax (documented in `dashboard/README.md`, never
  required): `- <ID>: <text>` criterion bullets with `evidence:` key=value
  lines, `Recurring:` cycle blocks, `References:` historical links. Local
  evidence refs must resolve under the project root; traversal, symlinks and
  non-http(s) URL schemes are rejected; external refs are displayed, never
  fetched.
- `tasks[].attempts` / `.routing` / `.verifications`: allowlisted views of the
  `.runtime/` records (attempt outcome, requested/effective model identity,
  routing assessment and admission events, gate verify results with `stale`
  artifact binding). Raw argv/env, paths, credentials, provider request ids and
  quota data are never exported; absent or malformed records degrade to `null`
  plus a diagnostic, never to invented values.
- `diagnostics`: source fingerprints (plan/ledger/tasks/runtime/git), warnings
  (duplicate stage ids, declared-vs-ledger mismatches, stale Verifies links,
  ledger stages absent from the plan) and gaps (missing plan, absent runtime,
  unstructured criteria). Duplicate stage ids are never resolved silently and
  unmapped tasks stay listed.
- `--demo` grew a six-stage fixture covering the plan's acceptance cases
  (zero-task and historical stages, a recorded recurring cycle, accepted tasks
  beside failed/pending external evidence, a duplicate-id warning, unmapped
  task) and embedded attempt/routing/verify records; demo mode still reads no
  canonical memory.

Migration: `install.py --update` replaces the template files. Installed
projects keep their existing `project-plan.md` untouched - plain
`Status:`/`Exit criteria:` plans parse as before; the authored metadata syntax
is opt-in. Projects that already wrote a roadmap view against the pre-1 payload
should adopt `schemaVersion` - all 2.15.x fields are still present. Rebuild the
dashboard (`python .agentflow/dashboard/build.py`) to pick up the new fields.

## 2.15.7 - 2026-10-21

Stage 5 close-out (improvement-plan section 6, T-038): a reproducible
scenario suite now exercises the lifecycle, recovery and evidence machinery
end to end in disposable repositories, an update test proves open tasks
survive `install.py --update`, and this entry consolidates the Stage 5
releases (2.12.1-2.15.7) into one migration path. This is the final Stage 5
version.

- `.agentflow/tests/test_scenarios.py` (new) drives the real `run_task.py`,
  `gate.py`, `accept.py`, `tick.py` and `ledger.py` in disposable git
  repositories through the plan's named cases: a bug-fix task carried from a
  red project check to an accepted merge, a contract-change task where a
  passed verify does not carry to a moved artifact or a moved base, a
  quota/limit recovery (classified `limit`, draft preserved, the recorded
  hold refuses a same-tool relaunch until it expires, the successor is
  told), and an interrupted-merge recovery (git state plus
  `T-NNN.accept.json` resume it - merged once, never twice). Simulated
  workers are marked `_simulated` in the test names; the real-platform
  variant is skipped unless `AGENTFLOW_REAL_PLATFORM=1`, never faked.
- The same module proves open-task migration safety: `install.py --update`
  onto a fixture project holding open Task Files and a mixed-status ledger
  preserves every project-owned byte (ledger, Task Files, rules, plan,
  state, model options, runbook) while replacing all template-owned files
  and entry-point blocks, and the preserved open task still parses under
  the new `gate.py` and reads under the new `ledger.py`.
- `.agentflow/docs/release-validation.md` gains the Stage 5 evidence map:
  what is locally verified, what still needs remote CI (the
  windows-latest/macos-latest failure of run `39026298541` stays an open
  gap) and what is simulation-only.

Migration: one `install.py --update` covers every intermediate Stage 5
release - template files are replaced cumulatively, so no step-wise update
is needed. Then apply the task-side notes the entries record: worker
launches need a routing assessment (`route.py T-NNN`) or a
`Routing exception:` header line (2.15.3/2.15.4), a running conductor must
be restarted to pick up the watchdog (2.15.1), and `model-options.json` may
gain `quota_group` (2.13.0), `floor`/`prefer` (2.15.2) and `recommended`
(2.15.5) - all optional project-owned settings. Open Task Files, the ledger
and state need no data migration. Scope honesty: no external rollout exists
or is claimed - the project has been repository-only since 2026-10-17, and
the remote-CI gap above stays open until a green
windows-latest/macos-latest run exists.

## 2.15.6 - 2026-10-21

Documentation-alignment train (T-097 core instructions, T-098 shipped-features
docs, T-099 Russian guide parity and release finalization): the user-facing and
folder-map documentation now describes what 2.15.x actually ships, role Result
examples match the gate's outcome-line format, every role file links the
protocol's canonical instruction-hierarchy rule, and the Russian guide carries
the same shipped facts as the English one.

- `.agentflow/roles/` (T-097): Developer/Tester/Deployer Result examples now
  demonstrate `- <id>: <verdict> - <evidence>` exactly as the completion gate
  requires, and every role file points at the protocol's "Instruction authority
  and ownership" section.
- `GUIDE.md` documents the shipped launch surface: routing admission
  (`T-NNN.route.json` assessment or a `Routing exception:` header), the free
  account probe (`AGENTFLOW_<TOOL>_PROBE`) and the opt-in selected-model probe
  (`AGENTFLOW_<TOOL>_MODEL_PROBE=on`), the enforced worker clock
  (`AGENTFLOW_WORKER_TIMEOUT`, `--watchdog`) and the other autonomy budgets,
  the `gate.py done` completion check with the opt-in Codex Stop-hook adapter,
  quota-group-scoped holds and the declared quota-policy files, and the three
  `AGENTFLOW_SHARED_DISPATCHER` modes. The `agentflow` subcommand list now
  includes `done` and `hooks`; the Codex Windows-sandbox limitation is stated,
  and the fixed per-tool worker argv is documented (the agy tester runs
  non-interactive `-p --output-format stream-json`; Devin workers get
  `--permission-mode dangerous --respect-workspace-trust false`, the opt-in
  probe `--permission-mode auto`).
- `.agentflow/README.md`'s folder map names every shipped tool
  (`tick.py`, `hooks.py`, `power_guard.py`, `limit_detection.py`,
  `quota_groups.py`, the Windows-only conductor helpers, and the rest) and the
  optional `quota-policy.json`/`quota-samples.json` project files.
- `README.md`, `RELEASE_NOTES.md` and `release-validation.md` no longer claim
  the remote CI matrix never ran: run `39026298541` (2026-10-17) is recorded —
  ubuntu test and both package jobs green, windows/macos test jobs failed
  (environment-specific, open), mcp jobs skipped — and there is still no green
  macOS result. The version badge matches `.agentflow/VERSION`.
- `docs/typesafe.md` was audited against `route.py`'s current
  assessment/admission behavior and needed no correction.
- `GUIDE.ru.md` (T-099) is rewritten to section-by-section parity with
  `GUIDE.md`: the same install/update/migrate/package/MCP/machine-resource
  surface, launch checks and worker bounds, fixed per-tool worker argv and
  recovery semantics, in Russian. Its stale claims now match the shipped
  behavior: managed workers are detached background processes watched through
  the attempt log and `--status` (no console windows to babysit), the
  dashboard UI is English, the agy CLI tester is non-interactive, and the 2.1
  migration follows the installer's refusal path. The Russian-only operational
  sections the English guide does not carry (machine preparation, TypeSafe
  setup, the per-tool smoke check, the day scenario and the cheat sheet) are
  dropped — parity is one factual surface. `RELEASE_NOTES.md` becomes the
  release notes of this train's pending release instead of the
  never-published 2.12.0 plan.
- `.agentflow/roles/tool-routing.md`: the Antigravity CLI note now says both
  managed roles run non-interactive `-p --output-format stream-json` (the
  Developer adds `--dangerously-skip-permissions`); only the IDE stays
  `-Manual`.

Migration: run `install.py --update` to pick up the updated `.agentflow/README.md`,
`typesafe.md`, role files (including `tool-routing.md`), and the
`AGENTS.md`/`CLAUDE.md` version blocks; `GUIDE.ru.md` is template-side
documentation and is not installed into a project. No configuration changes are
required; the corrected documents describe behavior that 2.15.x already shipped —
no workflow, option or contract changed.

## 2.15.5 - 2026-10-20

Jev-led model selection inside the preferred CLI and a Devin pool update
(human instruction, 2026-10-20): among adequate options Jev's own ranking now
picks the model, a configured per-tier `recommended` list orders ties and
unranked candidates, and `devin-gemini-4-argon` joins the option pool.

- `model-options.json` gains `devin-gemini-4-argon`
  (`gemini-4-argon-low/-medium/-high`, 1M-token context, devin quota group,
  developer/tester roles): a top-context model for very complex tasks whose
  assessed requirement stays at or below high effort - its strongest variant
  reaches only `high`, so xhigh+ requirements still belong to astra, opus or
  swe-2-max. This fulfils the recorded 2026-10-18 instruction to include
  Argon in the top-tier pool; the legacy argon negative assertion in
  `test_quota_groups.py` is removed and the variant now resolves inside the
  devin group.
- New `recommended` map in `model-options.json`: assessed effort tier ->
  ordered option list (with a `default` list when the tier names none). Jev
  sees it as a `recommended_for` hint on each option criterion; code applies
  it only as the fallback order for probability ties and unranked adequate
  candidates - it never creates eligibility and never lowers the
  requirement.
- `admission_order` ordering is now: preferred CLIs first, inside each group
  by Jev probability, the `recommended` list ordering ties, then name. The
  configured `floor` option no longer has a dedicated first rank - it still
  lifts the requirement effort and leads the low-tier recommended lists.
  Assessment records persist the applied `recommended` list, and
  `selectionReason` names a Jev rank, a policy preference, a recommended
  tie-break or a name-order break.
- `plan_route.py` forwards the map into the Jev questions and uses the same
  ordering for planning recommendations.

Migration: run `install.py --update`. Projects wanting the new ordering add a
`recommended` map to their `docs/model-options.json`; without it selection
falls back to prefer + Jev probability (the floor's dedicated first rank is
gone there too). To adopt Devin Argon add the `devin-gemini-4-argon` option
and verify the concrete model ids against `devin models list` - the local
catalog was not checked for this change (CLI unauthenticated).
## 2.15.4 - 2026-10-18

Scheduler integration of the routing assessment (T-078, third bounded delivery
of T-040): `tick.py run`'s automatic launches and backup switches now consult
the persisted assessment before acting, and `route_report.py` exposes the
record's safe metadata.

- `tick.py`'s `decide()` calls `route.assessment_problems()` for every ready
  task before reporting `launch`: a missing, stale or non-ok assessment
  becomes an actionable `need` in `tick.json` (route the task or write a
  `Routing exception:` header line) instead of a launch the launcher would
  refuse anyway. The launcher's `route.admission()` stays the final
  authority: it re-checks the resolved model/effort after
  `AGENTFLOW_<TOOL>_ARGS` overrides on every real launch.
- `use_backup()` rewrites an unstarted task's header only after
  `route.backup_ok()` confirms the recorded `Backup Tool:`/`Backup Model:`
  meets the task's recorded requirement and carries no live hold on its
  quota group. An inadequate or group-held backup never replaces a primary;
  group holds stay scoped (`<tool>:<group>`).
- The automatic scheduler applies no same-CLI independence removal: a
  tester task admitted on the same tool as the task it checks launches on
  it — tester independence is the fresh worker session on a disposable
  checkout of the exact artifact (review isolation), and human-reported
  availability never overrides an observed hold or the recorded adequacy
  floor. T-091 landed the same rule at assessment time: a configured
  preferred CLI is never removed by the tester-independence exclusion.
- `route_report.py` task items now carry `assessmentStatus`,
  `assessmentBand`, `required`, `floor`, `excluded`, `inadequate`,
  `adequateHeld`, `blocked`, `admissions`, `humanExceptions`,
  `admissionSource`, `admissionDeviation` and `humanExceptionReason`.
  Absent metadata stays `null` — never fabricated.
- `_template.md` documents the optional `Routing exception:` header field:
  the auditable human override of routing admission.

Migration: automatic launches now need the same recorded assessment that
direct launches already require — run `python .agentflow/tools/route.py
T-NNN` for open ready tasks (the Orchestrator does this per the mandatory
routing policy), refresh it after a contract change, or record a
`Routing exception:` header line for an auditable human override. With
`AGENTFLOW_BACKUP_ROUTING=on`, a header `Backup Tool:` weaker than the
recorded requirement or on a held quota group is left unused — re-route the
task to record a usable backup. Legacy route histories without
schemaVersion-1 assessment records report the new fields as `null`.

## 2.15.3 - 2026-10-18

Launch enforcement of the routing assessment (T-076, second bounded delivery
of T-040): every worker launch that passes through `run_task.py` - direct,
`--manual`, tick-driven and every retry - is now admitted on the persisted
assessment record. Automatic scheduling, backup selection and reporting
integration remain with T-078.

- `run_task.py` calls `route.admission()` after preflight and the launch
  budgets, before any probe, lease or spawn: the latest `assessment` event
  must exist, match the task's current `requirementsHash` and be `ok`, and
  the resolved tool/model/effort after `AGENTFLOW_<TOOL>_ARGS` overrides must
  still meet the recorded requirement. Missing, stale, `blocked`,
  `low-confidence` or `failed` records refuse the launch; a retry cannot
  downgrade through environment flags or a weaker relaunched tool. The
  resolved-env identity covers every documented Codex override spelling -
  `-c k=v`, `--config k=v` and `--config=k=v`, including the `model` key
  (T-087; repeated keys resolve last-wins - the value Codex applies - and
  the spellings are parsed for codex only, T-089). Each
  admitted launch appends an `admission` event to `T-NNN.route.json` (safe
  metadata only); a `Routing exception:` header line is the auditable human
  override and is recorded as a `human-exception` event, never as Jev
  evidence.
- The instance routing policy in `model-options.json` now encodes the
  human's 2026-10-18 preference: Devin for development, fresh independent
  testing and orchestration - tester independence is a fresh session on an
  isolated checkout, not a different CLI. The human-reported Devin
  availability window through 2026-11-01 is noted as qualitative, not a
  measured balance. The model catalog and observed holds are unchanged.
- Disposable launch probes cover refused missing/failed/stale assessments, a
  refused env-args downgrade (also on retry), an admitted adequate selection
  and the recorded human exception.

Migration: worker launches now require a routing assessment - run
`python .agentflow/tools/route.py T-NNN` before launching a task (the
Orchestrator does this per the mandatory routing policy), or write a
`Routing exception: <reason>` header line for an auditable human override.
A project without `.agentflow/docs/model-options.json` can only launch via
the exception path until it configures options and routes a task. Adopt the
instance policy's `floor`/`prefer` keys and policy text to get the same
adequacy-first Devin preference.

## 2.15.2 - 2026-10-18

Routing assessment/admission core (T-074, first bounded delivery of T-040):
every `route.py` call now persists a requirements-bound assessment record,
and the admission API a launch will be gated on is exported for T-076 to
wire into `run_task.py`/`tick.py`. This release is API-only: launch
enforcement is still pending, T-040 is not complete.

- `route.py` persists `.agentflow/tasks/.runtime/T-NNN.route.json` as
  schemaVersion 1 `assessment` events bound to `requirementsHash` — the task
  header minus the routing fields (Tool/Model/Backup/Routing
  exception/Resume), so a routing retry never invalidates the record but a
  contract change does. `status` is one of `ok`, `blocked`,
  `low-confidence`, `failed`; every outcome, including a failed call, is
  persisted rather than silent.
- Selection is requirement-first: an option below the assessed effort or
  over its complexity cap is never a candidate, whatever its Jev rank. Among
  adequate options the configured `floor` leads, then `prefer`red CLIs, then
  Jev probability. New model-options.json keys: `floor`
  (`{"option", "effort"}`), `prefer` and per-option `tier`/`quota_group`
  documentation.
- New launch-side API for T-076: `route.assessment_problems()`,
  `route.admission()`, `route.backup_ok()`, `route.log_admission()`,
  `route.history()`/`route.latest_assessment()`. A missing, stale or non-ok
  record is a diagnosable block; a `Routing exception:` task header line
  overrides it and is logged as a `human-exception` event — distinguishable
  from Jev evidence, never presented as it. `admission()` re-checks the
  resolved model/effort after `AGENTFLOW_<TOOL>_ARGS` overrides; backups and
  retries must meet the same requirement and cannot bypass quota groups.
- Exit code 5 means blocked: nothing adequate is usable today, and the
  record names the per-option reason plus any adequate-but-held option.
- Draft regressions repaired: the route log follows the configured
  `FLOW_ROOT` (not an import-time constant), and an inadequate backup is
  rejected instead of kept — the obsolete test expecting a below-requirement
  Claude backup now asserts the adequate one.

Migration: nothing required — the record file is additive and launches are
not gated yet. Installed projects that want the floor/preference ordering
before T-076 may add `floor` and `prefer` to their
`.agentflow/docs/model-options.json`; existing `options` entries are
unchanged. Launch admission arrives with T-076.

## 2.15.1 - 2026-10-18

Urgent repair of worker bounds exposed by T-040 (T-072 watchdog and T-080
idle-sleep guard, delivered together). Careful attribution: T-040's observed
overrun hours were mostly confirmed connected standby (Kernel-Power 506/507
on the host), not proven to be the timeout bug's doing; the invalid-timeout
gap — `0` or a non-number silently disabling `AGENTFLOW_WORKER_TIMEOUT` — was
reproduced separately and is fixed here, along with the absence of any
deadline enforcement outside the worker.

- `AGENTFLOW_WORKER_TIMEOUT` resolves like every positive launcher bound: an
  invalid, zero or missing value keeps the default (1200s) — a managed worker
  is never unbounded. The CLI surface is unchanged.
- Non-manual attempts now persist `workerTimeout` (the resolved bound,
  including the `AGENTFLOW_TASK_TIMEOUT` remainder clamp) and `deadline` (the
  absolute instant, from the attempt's `startedAt`).
- New `python .agentflow/tools/run_task.py --watchdog` (optionally
  `T-NNN --watchdog`): scans the attempt history and stops every running
  non-manual attempt whose deadline passed, through the same guarded path as
  `--stop` — pid-and-start identity required for a kill, a possibly reused
  pid is never a target, leftover managed processes keep the task locked and
  diagnosed, and the expected-attempt guard (`--expect-attempt N`) refuses a
  stale stop so an old watchdog decision cannot kill a newer attempt. A
  running attempt whose worker already vanished closes as `dead`; a manual
  or unexpired attempt is never touched; the watchdog never relaunches — a
  successor stays the Orchestrator's decision.
- External stops and launches are serialized by the same
  `.runtime/launch.lock`: a stop waits (bounded, 15s) for an in-flight
  launch and re-reads the record inside the lock, so a stale decision can
  neither kill nor overwrite an attempt created meanwhile. `taskkill` on
  Windows and the post-kill process waits are bounded now too.
- Stops record `stoppedBy: {initiator, reason, at}`: `initiator` is
  `watchdog` for a deadline stop or `cli` for the `--stop` command line —
  a human or a script invoked it, the record does not claim which.
- New `tools/power_guard.py`: while a bounded worker runs, the worker
  process asks Windows to keep the system out of automatic idle sleep
  (`SetThreadExecutionState`, system execution only), so an idle timer
  cannot suspend it mid-attempt. It is released on every exit path and
  dropped by the OS if the worker dies. Limits: it never holds the display
  on, never requests away mode, cannot block an explicit user sleep/lid
  action, does nothing on POSIX, and changes no power plan, registry or
  scheduled task; a failed request is recorded on the attempt (`powerGuard`)
  and in its log rather than assumed. The watchdog deadline keeps its
  authority across a user-initiated sleep.
- `conductor.ps1` runs the watchdog at the top of every round, including
  while a background Orchestrator session is alive (never in `-DryRun`).

Migration: stop the running conductor, run `install.py --update`, then
start it again — a conductor already loaded in PowerShell keeps its old
round loop in memory and must be restarted to pick up the watchdog call.
Attempts started before the update carry no `deadline` field and are
bounded by the fallback `startedAt + AGENTFLOW_WORKER_TIMEOUT`; an attempt
with no readable deadline or start is left locked and diagnosed, never
killed on an unprovable bound. The guard needs no setup and no opt-in: it
rides the worker process and ends with it.

## 2.15.0 - 2026-10-18

Bounded autonomy and trustworthy lifecycle records (improvement-plan section
4): attempts record the model identity they were asked for and the one the
tool reported; operator quota wishes become a declared policy file instead of
prompt promises; attempts, duration, identical failures and platform switches
are capped; an opt-in Codex Stop-hook adapter validates the installed runtime
before enabling; a `done` PASS is reused only while every check input still
matches.

- Attempt records (`tasks/.runtime/T-NNN.json`) now carry `requestedModel` /
  `requestedEffort` from the Task File, `launch.argv` in safe form (the
  prompt becomes `<prompt>`, every `AGENTFLOW_<TOOL>_ARGS` token becomes
  `<env arg>` — a machine-arg secret can never enter runtime state),
  `toolVersion` (first `--version` line, bounded by
  `AGENTFLOW_VERSION_TIMEOUT`, `unknown` when the binary does not answer) and
  `effectiveModel` / `effectiveEffort` from what the tool itself reported in
  the session log. Identity the tool never reported stays `unknown` — never
  guessed. Attempts written before these fields exist stay valid.
- New attempts are refused with a diagnosable reason — nothing started,
  earlier records and recovery checkpoints preserved — when they would
  exceed `AGENTFLOW_MAX_ATTEMPTS` (8), `AGENTFLOW_TASK_TIMEOUT` (4h from
  attempt 1's start; its remainder also bounds a running worker),
  `AGENTFLOW_MAX_IDENTICAL_FAILURES` (3 consecutive failures with the same
  stop reason, exit code and normalized note) or `AGENTFLOW_MAX_TOOL_SWITCHES`
  (3 distinct platforms; a manual attempt is not a switch).
- Managed sessions carry `AGENTFLOW_ATTEMPT=<task>#<n>` and
  `AGENTFLOW_ATTEMPT_ROOT=<checkout root>`: a launch inside that root is a
  nested helper and is refused unless a project Preflight rule declares
  `- delegate: on` (default: zero helpers; delegation never bypasses the
  budgets or machine capacity).
- Declared quota policy: `.agentflow/docs/quota-policy.json`
  (`AGENTFLOW_QUOTA_POLICY` overrides, `off` disables) declares expectations —
  `{"policies": [{"tool", "group"?, "remaining": {"percent_below": n},
  "action": "pause|switch|report", "sample_max_age_seconds"?}]}` — and
  `quota-samples.json` next to it (`AGENTFLOW_QUOTA_SAMPLES` overrides) holds
  the readings keyed `<tool>` or `<tool>:<group>` with `at`,
  `remaining_percent` and optional `resets_at` (the quota window's end). A
  fresh below-threshold reading under `pause` waits launches; under `switch`
  they become needs and `next-orchestrator` skips the tool. With no fresh
  reading the state is `unknown` — nothing blocks on a wish, and the launch
  budgets remain the bound; malformed files fail closed (`StateError`). The
  policy file is never a claim that a percentage is enforced.
- `gate.py` verify/done records carry `checksHash` over the `## Checks`
  commands, the task's `Env:` block and the interpreter that runs them; a
  `done` PASS is reused only while it still matches. A changed check
  definition or runtime — or a legacy record without the field — is a new
  measurement.
- `plan_route.py recommend(..., kind="plan")` / `--kind` names the decision a
  recommendation feeds (recorded in the Jev state and the result); it frames
  the effort question without forcing a tier.
- New `hooks.py`: `python .agentflow/tools/hooks.py enable codex` validates
  the installed Codex version (`>= 0.114.0`) and hook feature surface at
  runtime, refuses unsupported runtimes without writing, prints the manual
  steps, and with `--write` adds one project-local `.codex/hooks.json` Stop
  entry (existing hooks kept; global config untouched — the `[features]`
  flag stays the operator's line). The `codex-stop` hook maps the session's
  cwd to its AgentFlow attempt, completes a finished manual session the same
  way `--mark-finished` does, runs `gate.py done`, and reports bounded
  actionable text; it is inert inside a managed worker session
  (`AGENTFLOW_ATTEMPT` set) and never accepts, spawns or treats a limit or
  `blocked` outcome as a reason to continue. `cli.py` gains a `hooks`
  passthrough.
- Migration for installed projects: `install.py --update` ships the new
  `run_task.py`, `tick.py`, `gate.py`, `plan_route.py`, `cli.py`,
  `conductor.ps1`, `hooks.py` and the updated protocol. No configuration
  changes are required; the new launch budgets apply at their documented
  defaults — widen or tighten them per machine with the `AGENTFLOW_*`
  settings. To opt into the Codex
  Stop hook, run `hooks.py enable codex` in a project and, if it validates,
  re-run with `--write`, then add the printed `[features]` line to the codex
  `config.toml`. Declare `.agentflow/docs/quota-policy.json` only if the
  project wants declared quota expectations enforced on fresh readings. Old
  verify records without `checksHash` stay valid evidence of what they
  measured but are never reused as a current `done` PASS. The shipped
  `gate.py` also carries the 2.14.1 evidence-scope fix below.

## 2.14.1 - 2026-10-18

Evidence-scope check fix: Result prose that merely looks path-like
(`verify/done`, `launch.argv`, `decisions.md`, or where a schema lives,
e.g. `.agentflow/docs/quota-policy.json`) was reported as declared
evidence outside the task's scope, blocking valid Results. Only evidence
claims are now validated: a path after an `evidence:`/`evidence=` marker,
or a bare path list.

- `gate.py` `evidence_tokens` splits claimed paths from mentions: the
  `evidence:`/`evidence=` marker makes following path-looking tokens
  claims, and an unmarked evidence text claims paths only when it is
  nothing but a repository-relative path list (first segment a top-level
  folder or an existing file, with `and`/`or` connectors). Prose mentions
  are skipped. The scope/existence checks for claimed evidence are
  unchanged: a declared file outside the task's Allowed files or missing
  on disk still fails.
- Migration for installed projects: `install.py --update` ships the new
  `gate.py` and the protocol wording. Results already written keep their
  shape; prose path mentions no longer fail verify. Declare evidence
  explicitly (`- X-NN: pass - evidence: <path>`) so it is still checked.
  No data migration is needed.

## 2.14.0 - 2026-10-17

Acceptance becomes an artifact-bound, criteria-covered completion gate
(improvement-plan section 3): required criteria carry stable IDs, evidence
paths are validated against the task scope, the verify record also binds the
base SHA(s) it was produced against, and `accept.py` runs the task's Checks
on the trial-merge result before any repository merges.

- Task Files: every required `Acceptance criteria` bullet carries a stable
  `X-NN:` ID; `gate.py preflight` refuses a task whose criteria lack IDs or
  repeat one. `.agentflow/tasks/_template.md` shows the form.
- The Result maps every required criterion ID to
  `- <id>: pass | partial | unverified | fail - <evidence>`; `gate.py verify`
  fails when a required criterion has no outcome line or a worse-than-pass
  verdict a role may not report (the Tester's Verdict stays its worst
  criterion - a completed negative review remains representable). Evidence
  written as file paths must exist inside the task's Allowed files (a Tester:
  the checked task's scope; a task's own `tasks/.runtime/` files stay
  citable).
- The verify record binds the base SHA(s) the evidence was produced against:
  a moved base, an edited header, a new attempt or a different artifact
  invalidates it (the base moving to the task's own merge is the exception).
  Records without the new fields bind only the artifact, per the documented
  legacy rule.
- `accept.py` runs an integrated check between the trial merge and the merge:
  the Checks execute on a detached checkout of the `git merge-tree` result
  per repository, and `.agentflow/tasks/.runtime/T-NNN.accept.json` records
  per-repository progress so an interrupted multi-repository acceptance
  resumes without claiming cross-repository atomicity.
- The `gate.py endcheck` merge-history audit scopes Task Files correctly: the
  product `.agentflow/tasks/_template.md` is template-owned, not a worker
  Task File, so a branch commit touching only it no longer fails the audit.
  Committed `T-*.md` files and `tasks/.runtime/` state still do.
- `python .agentflow/tools/gate.py done T-NNN` (or `agentflow done T-NNN`) is
  the single completion check acceptance, the launcher and an optional
  platform hook call: structured pass/fail reasons via `--out`, a still-bound
  PASS is reused instead of re-measured, and a check that fails on the base
  too is reported as a pre-existing failure, separate from one this change
  introduced.
- Migration for installed projects: `install.py --update` ships the new
  `gate.py`, `accept.py`, `ledger.py`, `cli.py`, `_template.md` and the
  updated protocol. Write new Task Files with `X-NN:` criterion IDs - a
  launch (or a new attempt of an old task) is refused without them; results
  already written keep their shape, and verify records predating
  `base`/`criteria` bind only the artifact under the legacy rule. No data
  migration is needed.

## 2.13.3 - 2026-10-17

Merge-history audit scope fix: a committed `.agentflow/tasks/_template.md`
change on a developer branch no longer fails the end check. `_template.md` is
template-owned product; a task that legitimately edits it was reported as
"commits Task Files".

- `gate.py worktree_copy_problems` audits `--name-only` output under
  `.agentflow/tasks` with `_template.md` excluded; a commit touching it
  together with real Task Files still flags and names the Task File, a
  committed `.runtime/` file still flags, and un-auditable history (octopus
  merge, unreadable diff) still fails closed. The flag message now names the
  offending paths.
- Migration for installed projects: `install.py --update` ships the corrected
  `gate.py` and protocol text (`tools/`, `docs/` are template-owned). No data
  or state change: attempts previously blocked only by a `_template.md`
  commit can be re-checked with `run_task.py T-NNN --recheck`.

## 2.13.2 - 2026-10-17

Roadmap mockups: the wide layout is repaired and the filter bar actually
renders. Two defects in the shared mockup chrome made the committed variants
misleading at desktop width and left the filter controls unpainted.

- `mockups/chrome.css` adds the grid spans the real page template sets inline:
  `.app>header`, `.fbcard` and `.fbchosen` now take `grid-column:1/-1`. Without
  them `.app`'s four explicit rows (`common.css`, inlined unchanged) were
  consumed by auto-placement: the filter panel landed in the left column, the
  stage rail on the right, and the stages and diagnostics were squeezed into
  the 26px "chosen" row under a blank center.
- `mockups/chrome.js` `mkFilters` now calls `fb.render()` once at creation and
  after every `onChange`, matching how the real pages drive `filterbar.js`;
  previously the dimension dropdowns, the "Showing N of M" counter and the
  selected-chips row never rendered in any variant.
- The three committed `roadmap-*.html` are regenerated by
  `mockups/build.py`; no output was hand-edited.
- Migration for installed projects: `install.py --update` ships the corrected
  mockup chrome (`mockups/` is template-owned). Installed projects get the fix
  on update; regenerate local copies with
  `python .agentflow/dashboard/mockups/build.py` if needed. The product
  dashboard is untouched.

## 2.13.1 - 2026-10-17

Fixup on the 2.13.0 recoverable handover (the two defects the independent
review found on the rejected T-030 artifact): quoted provider phrasing in a
worker's prose no longer trips `limitHit`, and a tool-wide refusal names the
tool-wide hold.

- `limit_detection.py` quote framing covers the report verbs `shows`,
  `prints`, `displays`, `writes`/`wrote`/`written`, `echoes`/`echoed` (and
  `displayed`, `printed`), and a match inside an already-open quote span is
  skipped at any exit code: `the banner shows "you've hit your usage limit"`
  stays subject matter, so a worker quoting the provider verbatim no longer
  records a false group-scoped hold. A bare provider line or an
  error-prefixed line still counts.
- `run_task.py resource_check` names the hold that actually blocks: under a
  bare `<tool>` hold the refusal reads `<tool> is limited until ...` even
  when the session consumes a quota group; a `<tool>:<group>`-scoped binding
  constraint still reads `<tool> group <group> is limited until ...`.
- Migration for installed projects: `install.py --update` ships the corrected
  `limit_detection.py` and `run_task.py` (`tools/` is template-owned). No
  data change: holds already recorded keep their keys and expiry; fewer
  false `limitHit`s simply record fewer group-scoped holds.

## 2.13.0 - 2026-10-17

Recoverable handover (improvement plan section 2; two audited candidates
generalized from the Transcript Youtube install): one shared provider-limit
detector, per-model quota groups for observed holds, classified attempt end
states, takeover that refuses to run alongside live managed children, and a
bounded recovery record that preserves uncommitted drafts.

- `.agentflow/tools/limit_detection.py` (new) is the single judge of whether a
  session log shows the tool's own provider/account limit; `run_task.py`
  (worker `limitHit`/`limitKind`/`limitPhrase`), `tick.py`
  (`limit`/`learn_limits`/`hit_limit`) and `conductor.ps1` now share it instead
  of three regex copies. Strong provider-directed phrases count at any exit
  code; weak quota/status words need failure evidence (nonzero exit, an
  error-prefixed line, an outer error event in stream-json); quoted
  subject-matter content (test output, a report about the product's own
  quotas) is skipped; retryable transport failures never match.
- `.agentflow/tools/quota_groups.py` (new) scopes observed holds per model
  quota group: `model-options.json` gains the optional `quota_group` field, a
  hold recorded under `<tool>:<group>` blocks only sessions of that group,
  bare-`<tool>` holds stay tool-wide and account/access failures always apply
  to the whole tool. The option named after the tool defines the default
  group's model, so unmodelled launches and background Orchestrators check the
  group they would actually consume. `tick.py limit --group`, `tick.py
  limit-migrate` and `machine_capacity.py claim --group`/`move-limit` manage
  scoped holds; launches, `tick.py run` and the conductor's next-orchestrator
  honor them.
- Attempt records classify the stop reason (`stopReason`: completed, limit,
  timeout, stopped, dead, environment, implementation, verification) from
  launcher facts - exit code, shared limit detection, end check - never free
  text alone, and record the quota group the session consumed (`quotaGroup`).
- A new attempt or `--stop` is refused with a diagnosable error while a
  managed child of the previous worker still runs: descendants by parent
  chain, plus the recorded tool session on POSIX and the worker's named job
  object on Windows (orphaned grandchildren that left the parent chain still
  count). Uncertain process ownership blocks concurrent writing instead of
  launching alongside a possibly live writer.
- An attempt that did not complete carries a bounded `recovery` record (per
  checkout: branch, HEAD, tracked modifications and untracked paths -
  paths/status only, file contents never enter runtime state; the stop reason;
  whether a Result exists), captured even when the worker left no commit and
  no Result. The next attempt's prompt carries a one-line handover (also
  printed for `--manual` starts).
- `Resume:` on the Task File: `<commit>` continues the preserved draft on the
  same branch and worktree (the commit must be an ancestor of its HEAD);
  `start fresh` discards only that worktree's draft; `none` leaves the
  worktree as found.
- Migration for installed projects: `install.py --update` delivers the two new
  tools (`tools/` is template-owned). Existing tool-wide holds keep working
  unchanged; a hold known to belong to one quota group can be rescoped with
  `tick.py limit-migrate <tool> <group>` (for example the recorded agy
  tool-wide hold to `agy:agy-claude-gpt` so a Gemini probe stays possible).
  Add `quota_group` to project `model-options.json` options to opt in; absent
  groups keep tool-wide semantics. `dispatch.py` still reads tool-wide holds
  only - a grant for a group-held tool is refused at the scoped claim and
  released, so active dispatch degrades to a wait, never to a blocked launch.

## 2.12.2 - 2026-10-17

Lifecycle trust, second round (improvement plan section 1, independent review
findings on 2.12.1): the fail-closed claim of 2.12.1 is now true at every
runtime-state reader, acceptance is bound to the attempt it verifies, and a
worker whose process identity is unconfirmed keeps its task locked.

- Every runtime-state reader validates the shape it depends on, not just JSON
  syntax: an empty container (`[]`, `null`, `{}`), a wrong-typed attempt field,
  a verify record with a non-boolean `ok`, a limit record that is not an object
  or whose `until` is not a string, a heartbeat without `holder`/`at`, a
  runtime file naming no task or another task, or an attempt naming another
  task are all diagnosable errors - never "no limits", "no orchestrator live"
  or "no evidence". A malformed heartbeat blocks an orchestration claim rather
  than being silently overwritten (`tick.py heartbeat --force` still takes over).
- `ledger.py set --status done` now requires a verify record bound to the task,
  the last attempt number, the current requirements hash and the full artifact
  SHA(s), with that attempt `exited`: a stale PASS from an earlier attempt or a
  different artifact no longer satisfies acceptance. Legacy records follow an
  explicit rule: a record without `taskId` belongs to the file it lives in, and
  a missing `attempt`/`headerHash` binds only the artifact.
- `--stop` and dead-worker recovery keep the task locked while a live pid's
  start identity is unconfirmed: no kill is sent to a possibly reused pid and
  the attempt is not closed, so a second claim cannot coexist with a worker
  that may still run. A verified stop or a verified identity releases the lock;
  `--status` reports the block and `tick.py` surfaces it as a need.
- `machine_capacity` lease liveness uses the same pid + recorded start identity
  rule as the launcher on every platform: POSIX honors the recorded start,
  Windows `GetProcessTimes` failure or an unmeasurable identity is not "alive",
  and a reused pid can no longer fool a stale lease.
- `route._log` (`T-NNN.route.json`) and the ledger's `tasks.md` save now use the
  same temp-file-plus-`os.replace` atomic write as the runtime JSON writers.
- Migration for installed projects: `install.py --update`. A wrong-shaped
  `tool-limits.json` or `orchestrator.json` now blocks launches and
  orchestration claims until repaired - the intended fail-closed behavior. An
  attempt whose pid is alive but unverifiable keeps its lock: end the process
  and `--stop` again. Legacy verify records remain valid under the documented
  binding rule; re-running `gate.py verify` writes a fully bound record.

## 2.12.1 - 2026-10-17

Trustworthy task lifecycle (improvement plan section 1): claims, attempts and ledger
transitions now pass verified state only, and malformed runtime state fails closed
instead of reading as "no active work".

- `ledger.py set` can no longer bypass the approval gate: a row whose Notes still start
  with "awaiting approval" accepts only `approve`, a terminal `rejected`/`cancelled`, or a
  `--notes` update that keeps the prefix. `--status in progress` additionally requires a
  running attempt recorded by the launcher - a claim exists only while a real attempt runs.
- Runtime JSON is written atomically everywhere (attempt `T-NNN.json`, `T-NNN.verify.json`,
  `tick.json`, `tool-limits.json`, `orchestrator.json`, gate `--out` hand-off files), and a
  malformed or structurally invalid record fails closed with a diagnosable error at read
  time - never as "no active work" or "no evidence". Attempt and verify records are
  schema-checked on read; `run_task.py --status` marks an unreadable file `state-error`
  instead of skipping or crashing.
- Verify records now bind task ID, attempt number, requirements hash (Task File header
  hash) and the full artifact SHA; attempt records carry `taskId`. Legacy records stay
  valid evidence: a record without `taskId` belongs to the file it lives in.
- `tick.py` judges a worker process by pid plus recorded start identity - the same rule
  the launcher uses, on every platform - so a reused pid can no longer impersonate a live
  worker.
- Regression coverage: the empty `--live` argv defect (PowerShell 5.1), octopus-merge
  audit refusal and ordinary-merge history audit in disposable repositories, approval-bypass
  and terminal-state launch refusals, schema validation and malformed-state fail-closed tests.
- Migration for installed projects: `install.py --update`. In-flight attempts and legacy
  verify records remain valid; nothing is rewritten. A corrupt `T-NNN.json` now blocks
  launches and the ledger `in progress` transition until repaired or removed - that is the
  intended fail-closed behavior, not a regression. A direct `ledger.py set --status
  in progress` used outside the launcher stops working by design: issue attempts through
  `run_task.py` (or `run-task.ps1`).

## 2.12.0 - 2026-10-17

Public-release documentation milestone. No tool, protocol, role or dashboard
behavior changes in this release; 2.12.0 collects the cross-platform launcher,
unified CLI/package, optional MCP server, English evidence dashboard and the CI
matrix delivered by 2.11.9-2.11.14 and ships the docs that describe them.

- `GUIDE.md` is now in English; the previous text moved unchanged to
  `GUIDE.ru.md`. The guide covers installing from source and from the locally
  built `agentflow-sdlc` package, update preservation, workspace installs,
  Windows/Linux/macOS paths, the optional MCP server and its
  `--enable-orchestrator-tools` operator flag, opt-in machine resource sharing,
  the worker lifecycle, honest dashboard metrics and `--demo`, recovery
  commands and the supported permission boundaries. The conductor/autostart
  helpers are documented as Windows-only.
- `README.md` rewritten for the public release: value proposition, CI/license/
  version/Python/MCP badges (no invented green results), a Mermaid diagram of
  the single-writer Orchestrator, task contracts, isolated Developer/Tester
  artifacts, gate and acceptance flow with the Deployer consuming an accepted
  SHA only after human approval; maintainer-attested October 2026 production
  figures presented as an aggregate snapshot; the real dashboard screenshot at
  `.agentflow/docs/assets/dashboard.png` (T-008 evidence, real local build).
- `RELEASE_NOTES.md` added: release contents, evidence limits (no remote CI
  run, no green macOS result, store listing links unresolved), and the
  human-only push, CI-verification, tag and GitHub Release commands.
- Migration for installed projects: none required - no template-owned runtime
  file changed. Optionally copy the new docs conventions; `install.py --update`
  remains the way to receive template updates.

## 2.11.14 - 2026-10-17

- Dashboard interface is English by default (human-approved): all labels, filters, roles,
  Gantt, timeline and the summary view in `index.html`/`graph.html`. Machine values stay
  separate next to the display labels (`statusKey`, `roleKey`, `verdict`), and the three
  distinct fields ledger `Status` / worker `Outcome` / tester `Verdict` are unchanged.
  `UI-RULES.md`, the data contract in `dashboard/README.md` and the protocol Dashboard
  section document the English default; other project communication stays as configured.
- Tester check links now come from the Task File `Verifies:` field and its SHA, not a
  title regex. `checkedBy` entries carry `{id, verdict, status, sha, stale}`; a SHA that no
  longer matches the checked task's current commit is flagged as a stale link.
- Evidence metrics via `tools/route_report.py metrics()`: first-pass gate rate = first
  recorded `gate.py verify` record per task (`.runtime/T-NNN.verify.json`), denominator
  only tasks with that evidence, grouped by recorded role/tool; lead time from attempt
  timestamps; tester verdict counts (a `fail` verdict is a valid negative report).
  Missing history, runtime, cost or token telemetry is N/A, never zero or an invented
  saving; no causal model-quality claims. The metrics render in the graph page summary view.
- `python .agentflow/dashboard/build.py --demo` builds the same pages from a deterministic
  fixture with a DEMO DATA badge — no reads of project memory, no writes outside `out/`,
  safe for screenshots and layout review. Layout preserved; `test_dashboard.py` covers
  labels, Verifies links, stale detection and demo isolation; `test_route_report.py`
  covers first-record semantics, absent evidence, denominators and verdict separation.
- Migration: installed projects get the new dashboard and `route_report.py` through
  `install.py --update`. Re-run `python .agentflow/dashboard/build.py` to refresh the view;
  `--demo` needs no project state. Nothing else changes.

## 2.11.13 - 2026-10-17

- Optional MCP server `.agentflow/tools/mcp_server.py` on the official released SDK
  (`pip install "agentflow-sdlc[mcp]"` == `mcp>=2.3,<3`, PyPI 2.x, Python >=3.10). Core stays
  stdlib-only: without the extra the script exits 2 with an install-extra diagnostic on stderr
  (no hidden installation, no homegrown JSON-RPC fallback). Stdio tools: `agentflow_status`,
  `agentflow_get_task`, `agentflow_query_ledger` (read-only hints set), `agentflow_run_gate`
  (runs the real gate.py, not labelled read-only) and `agentflow_accept_task` only behind an
  explicit `--enable-orchestrator-tools` startup flag -- an operator control of the server
  surface, not proof of the caller's role. All subprocesses run without a shell; stdout is
  protocol traffic only. `agentflow mcp` starts the server of a discovered project.
- `install.py --mcp` (explicit opt-in) merges an `agentflow` entry into the client's project
  MCP config: `.mcp.json` for Claude Code, `.cursor/mcp.json` for Cursor (`--mcp-client`;
  a project `.mcp.json` is not auto-discovered by Cursor). The merge preserves unrelated keys
  and foreign servers, refuses malformed JSON and an unmanaged conflicting `agentflow` entry
  before writing anything, points at the target's own installed server with privileged tools
  off, and persists no credentials.
- `.agentflow/tests/check_mcp.py` is the explicit optional-SDK integration (not in unittest
  discover): disposable venvs provision `mcp>=2.3,<3` and the packaged wheel, prove the
  missing-SDK diagnostic, a real stdio handshake/list-tools/read-only tool calls, rejection of
  invalid input, the privileged tool absent by default and present with the flag, and the
  packaged `agentflow mcp` entry. `test_mcp_server.py` covers SDK-independent validation;
  `test_install.py` covers config preservation and refusals. CI adds an `mcp` job on
  ubuntu/windows after the core suite.
- Migration: update the installed template with `install.py --update` (delivers
  `tools/mcp_server.py` and the installer flags). To expose the server to a client, run
  `install.py --update --mcp [--mcp-client cursor]` in the project and install the `mcp` extra
  in the interpreter that will run it. No configuration changes are needed otherwise.

## 2.11.12 - 2026-10-17

- New distributable package `agentflow-sdlc` (`pyproject.toml` + `setup.py`, setuptools; local project
  distribution name, not a PyPI claim): `python -m build` produces a wheel and an sdist that carry
  `agentflow/template/` -- the installer-owned `.agentflow` files generated at build time from the single
  source (no second tracked tree, no state/, task contracts, project rules/plan, runtime files or
  maintainer root instructions). Runtime is Python 3.10+ stdlib only; `build`/`setuptools` are development
  tooling. A wheel built from the sdist reuses the generated tree, so neither artifact needs the checkout.
- New unified CLI `.agentflow/tools/cli.py` (also the `agentflow` console entry of the package):
  `install` (all installer flags), `run T-NNN --role <role>` (the role must match the Task File -- a
  mismatch starts nothing -- and the deployer always launches `--manual`), `gate`/`accept`/`ledger`
  passthrough, `dashboard [--open]`, `--version`, and `--project <dir>` for project discovery. Project
  commands walk up to an installed `.agentflow` (protocol file plus `template-source.json` or `state/`),
  run that project's own tool scripts without a shell and keep their exit codes; the bundled memory inside
  site-packages is never a project.
- `.agentflow/tests/check_package.py` is the explicit build integration (not in unittest discover):
  disposable venvs provision `build`/`setuptools`, exercise the wheel and the sdist outside the source,
  install and update a git project on a path with spaces, and check provenance, preservation and zero
  core runtime dependencies. `.agentflow/tests/test_cli.py` covers routing and refusal paths.
- Migration: update the installed template with `install.py --update` (delivers `tools/cli.py`; the
  `agentflow` command additionally requires building and installing `agentflow-sdlc` locally). No
  configuration changes are needed.

## 2.11.11 - 2026-10-17

- `machine_capacity.py` hardens the Windows registry write: `os.replace` of `registry.json` retries only
  transient sharing/access failures (ERROR_SHARING_VIOLATION, ERROR_ACCESS_DENIED) with a short bounded
  backoff. A permanent failure preserves the previous registry, removes the temp file and fails closed;
  locking, lease fairness and cleanup are unchanged.
- `conductor.ps1` hands the session environment to the spawned Orchestrator window in memory only: the
  `AGENTFLOW_*` set is DPAPI-encrypted (CurrentUser) onto the child command line and decrypted in the new
  process. `conductor.env.json` is no longer written, and a leftover plaintext file from an older version is
  removed at the next handover, so raw `AGENTFLOW_*` values are never persisted.
- `gate.py` no longer treats the documented `Rebuild together` answer `- nothing` as a shared resource:
  independent tasks declaring it stop blocking one another; real resource overlap is still refused.
- Built-in model probes were re-reviewed against the installed CLI help: codex (`exec --sandbox read-only
  --skip-git-repo-check`), claude (`-p` skips the trust dialog, empty `--allowedTools`), agy
  (`-p --output-format stream-json`) and devin (`-p --respect-workspace-trust false --permission-mode auto`)
  already run noninteractive inference in an empty temporary directory without repository writes or permission
  escalation; the argv contract is now pinned by tests.
- Migration: update the installed template with `install.py --update`. On Windows, delete a leftover
  `.agentflow/tasks/.runtime/conductor.env.json` if one exists (the conductor also removes it itself at the
  next Orchestrator handover). No configuration changes are needed.

## 2.11.10 - 2026-10-17

- Built-in Devin model probes explicitly use `--respect-workspace-trust false` and `--permission-mode auto`
  so noninteractive inference can run in the empty untrusted temporary directory with read-only tool approval.
- Built-in Codex model probes add `--skip-git-repo-check` while retaining the `read-only` sandbox.
  Model selection, opt-in, timeouts, refusal on denial and safe evidence remain unchanged.
- Migration: update the installed template with `install.py --update` before retrying automatic workers.
  No workspace trust or credential configuration changes are needed; model probes still require explicit opt-in.

## 2.11.9 - 2026-10-15

- Ported the worker launcher to Python 3.10+ stdlib: `.agentflow/tools/run_task.py` now owns launch, `-Status`,
  `-Stop`, `-Manual`, `-MarkFinished`, `-Recheck`, the internal worker and dispatch-grant exchange, with the same
  runtime state, gates, worktrees, setup links, capacity claims and ledger issuance as before. It runs on Windows,
  macOS and Linux without PowerShell.
- `run-task.ps1` is now a thin compatibility wrapper: it translates the old parameter names to `run_task.py` and
  preserves its exit code, so tick.py, conductor.ps1 and existing instructions keep working on Windows.
- Before a worker starts, the launcher checks the tool executable, a free authenticated-access probe
  (`codex login status`, `claude auth status`, `devin auth status`, `agy models`; overridable per machine with
  `AGENTFLOW_<TOOL>_PROBE`), observed quota/access limits and machine capacity. An unsupported or failing check
  refuses the unattended launch with an actionable diagnostic instead of guessing account access; `AGENTFLOW_<TOOL>_PROBE=off`
  declares a tool uncheckable. The observation's source and time are recorded in the attempt's `resourceCheck` (no secrets).
- The supported permission matrix (tool x role) is explicit in `run_task.py`; a combination outside it refuses to
  launch rather than silently downgrading isolation. Review isolation for testers still comes from the disposable
  checkout plus the end-of-attempt check; only codex adds a preventive sandbox. agy testers now run in
  noninteractive print mode with streaming output (`-p --output-format stream-json`) instead of `-i`, which could
  hang a Tester attempt; no permission flags are added for testers.
- Every launched worker runs under a wall-clock limit the launcher enforces itself: `AGENTFLOW_WORKER_TIMEOUT`
  seconds (default 1200, 0 disables). On expiry it kills the managed process tree, records a timeout error and
  releases the machine lease; captured output keeps streaming into the attempt log while the tool runs.
- Process-start identity is now also measured on macOS (`ps -o lstart=`, as a /proc fallback): `--stop` and
  recovery no longer kill a pid whose recorded identity cannot be confirmed - a possibly reused pid is refused.
- Unattended launches now prove access to the task's selected concrete model, not only the account:
  `AGENTFLOW_<TOOL>_MODEL_PROBE=on` runs the built-in audited inference check (it may cost tokens, so nothing runs
  it without opt-in). Custom probe argv is no longer accepted - it cannot be told apart from an auth/catalog
  check - so any other value fails closed. Unset/`off` refuses an unattended launch with an actionable
  diagnostic; the check runs without repository tools or writes under its own timeout, and records model
  identity, observation source/time and outcome. A probe success is never reported as a remaining-quota figure.
- Probe and launch evidence is safe metadata only: operator-supplied probe argv and `AGENTFLOW_<TOOL>_ARGS` are
  recorded as hashes, built-in probe argv verbatim (they are constants); user argv and probe output never appear
  in runtime files or diagnostics. Both access and model probes run under strict timeouts
  (`AGENTFLOW_PROBE_TIMEOUT`/`AGENTFLOW_MODEL_PROBE_TIMEOUT`) that kill the probe's whole process tree on expiry.
- The worker environment is handed over through the spawn call only; the plaintext
  `.runtime/T-NNN.env.json` handover file was removed, so secret-bearing `AGENTFLOW_*` values are never
  serialized to disk.
- `limitHit` now requires a nonzero exit plus observed limit wording: a successful report that merely mentions
  quota or rate-limit text no longer marks the tool limited.
- The visible-window rule now matches the implementation: workers are detached launcher-managed processes
  observed through the log, `--status` and `--stop`, with a guaranteed launcher-enforced wall clock.
- Machine `AGENTFLOW_*` variables no longer leak into the test fixtures (test_parallel, test_tick,
  test_machine_capacity, test_dispatch, test_conductor isolate the environment), so the verbatim suite does not
  depend on what the machine exports.
- New `AGENTFLOW_WORKER_PYTHON` selects the worker's interpreter independently of `AGENTFLOW_PYTHON`.
- Tests are portable: Python fake workers and disposable repositories cover launch/status/stop of descendants,
  manual/recheck, failed handoff, concurrent refusal, approval/terminal refusals, argv precedence, setup-link
  safety, grants/capacity and resource preflight. No real model calls.
- Linux defect repairs found by real-kernel verification (T-019): on POSIX the tool process now leads its own
  session (`start_new_session`), so a worker wall-clock timeout kills only the managed tree and the worker
  survives to record the error attempt; `kill_tree` signals the process groups of the whole tree, so `--stop`
  still reaches a tool in its own session. Windows (`taskkill /T`) is unchanged.
- `accept.py`'s trial merge no longer passes `--quiet` to `git merge-tree --write-tree`, an option stock
  git 2.47.x does not support; a conflict still stops the accept before any repository is merged.
- A `test_endcheck.py` merge fixture now passes `-c user.name`/`-c user.email` like every neighboring git call,
  so the suite does not depend on a host-global git identity.

Migration: stop idle conductors, run `install.py --update`, then restart them. Windows callers may keep using
`run-task.ps1` (it delegates); on macOS/Linux use `python .agentflow/tools/run_task.py`. For unattended launches,
each tool needs a working free access probe: the built-in ones fit current codex/claude/devin/agy CLIs; if a CLI has
none on your version, set `AGENTFLOW_<TOOL>_PROBE` to one or launch that tool's tasks with `-Manual`. Every
unattended launch additionally needs an opted-in selected-model inference check: set
`AGENTFLOW_<TOOL>_MODEL_PROBE=on` (may cost tokens), or run that tool's tasks with `-Manual`. A custom
`AGENTFLOW_<TOOL>_MODEL_PROBE` argv from an earlier draft is no longer honored and fails closed; move any
account/catalog check it held to `AGENTFLOW_<TOOL>_PROBE`. If you relied on `.runtime/T-NNN.env.json`, read the
attempt's environment from your own launch configuration instead - it is no longer written. Conductor and autostart remain Windows-only. Do not update tools during active attempts.

## 2.11.8 - 2026-10-12

- Added `plan_route.py` to ask Jev for a planning model from the project's usable CLI options. It compares the recommendation with an optionally supplied current chat model, records the request ID and complexity, and never changes the chat or worker Task Files. The runtime log stores a goal hash, not the full goal text.
- Added `route_report.py` to join routing history with task status and attempts. It reports primary/backup use, acceptance, first-attempt pass, and measured attempt time, grouped by role, complexity and recommended model. `--all-projects` combines installations that have this version and identifies older installations. Worker cost and token use remain unknown unless a CLI supplies them.
- Route history now explicitly records the eligible model options sent to Jev. Tests use a local stand-in and fixtures, with no real Jev or worker calls.

Migration: stop idle conductors, run `install.py --update`, then restart them. The new reports read existing runtime files; no ledger or Task File migration is required. Planning advice is optional and does not alter the user's current IDE model. Keep active shared dispatch disabled until all participating installations use grant-aware launchers.

## 2.11.7 - 2026-10-12

- Added opt-in active shared dispatch. With `AGENTFLOW_SHARED_DISPATCHER=active`, each project's tick registers ready tasks in the machine registry. A round-robin decision grants a short-lived reservation to one project; the launcher atomically converts that grant into its existing worker lease. Grants expire after 60 seconds, ready registrations after 10 minutes.
- In active mode, machine and project concurrency caps are checked separately. A project capped at one can share a machine capacity of two with another project capped at one. Existing launch behavior remains the default and `shadow` still previews the allocation without grants.
- Tests cover project turns, mismatched and expired grants, capacity, and a real PowerShell launcher with a fake worker. No real model calls were used.

Migration: stop idle conductors and update every project that will join active dispatch before enabling it; old launchers do not honor grants. Start with `AGENTFLOW_SHARED_DISPATCHER=shadow`, compare reports, then set `active` and restart the conductors. Revert to `shadow` or unset the variable to restore the previous launch path. Do not update tools during active attempts. The registry adds optional dispatch state and does not migrate Task Files or ledgers.

## 2.11.6 - 2026-10-12

- Jev routing now saves one primary and one backup model on different CLI platforms. The backup is the highest-ranked eligible alternative in the choice probabilities; both choices and their evidence are recorded in the route history.
- Before asking Jev, routing excludes CLI tools missing from this machine and platforms with an observed shared usage limit. A configured model still requires a real launch to confirm account and model access.
- With `AGENTFLOW_BACKUP_ROUTING=on`, tick switches an unstarted ready task to its saved backup when the primary platform is limited or has no free machine slot. The Task File and ledger are updated before launch; started tasks are never rewritten. This feature is off by default for staged rollout.

Migration: stop an idle conductor, run `install.py --update`, then restart it. Existing Task Files without backup fields keep their previous behavior. Route new tasks with Jev to record both models; enable `AGENTFLOW_BACKUP_ROUTING=on` only after reviewing the saved alternatives. No ledger schema migration is needed.

## 2.11.5 - 2026-10-12

- Added a shared dispatcher in observation mode. It reads ready tasks from all registered projects, simulates fair allocation against the shared machine registry, and reports selections and waits without granting slots or launching workers.
- `tick.py` includes that report when `AGENTFLOW_SHARED_DISPATCHER=shadow`; its existing launch and acceptance path remains active. Tests cover two-project fairness, occupied slots, and unchanged launches.
- Isolated the Codex capacity test from the user's machine override and made the acceptance test match a Git command rather than a `worktree` folder name.

Migration: stop an idle conductor, run `install.py --update`, then restart it. Set `AGENTFLOW_SHARED_DISPATCHER=shadow` to collect observations; omit it for existing behavior. No task-file or ledger migration is needed. Do not update tools during active attempts.

## 2.11.4 - 2026-10-11

- Removing a checkout no longer empties a `Setup: - link:` target. `git worktree
  remove` and a recursive delete follow a junction and delete the target's
  contents; installed projects repeatedly lost the main folder's `node_modules`
  when a tester checkout was re-created or an accepted developer worktree was
  removed. The launcher and `accept.py` now unlink the junction itself first.
- Regression coverage: a junction inside a checkout is removed while its target
  keeps its contents; a real directory at the same path is left alone.

Migration: stop an idle conductor, run `install.py --update`, then restart it.
Do not update tools during active attempts. Already prepared checkouts keep
working; their links are unlinked at the next removal.

## 2.11.3 - 2026-10-10

- The launcher records issuance (`in progress`) for direct, automatic and manual
  launches before worker handoff; tick no longer repeats that transition. Failed
  handoff is recorded as an error attempt and releases its machine reservation.
- Omit an empty `--live` argument, preserving Windows PowerShell 5.1 compatibility.
- Audit unique commits without path-limited history simplification. Main-branch
  memory inherited through a merge is allowed; task-file edits, reverted edits
  and merge-resolution edits remain rejected. Unsupported merge audits fail closed.
- Acceptance refuses missing, ready, blocked or final rejected/cancelled ledger
  states before verification or merge. Worker processes start in hidden windows.
- Regression coverage includes real PowerShell 5.1/7 launches, duplicate/retry and
  failed launches, and a disposable end-to-end manual launch/acceptance cycle.

Migration: stop an idle conductor, run `install.py --update`, then restart it.
Do not update tools during active attempts. Existing incorrectly recorded tasks
need an evidence-based one-time ledger reconciliation; no automatic promotion.
Git must support `show --remerge-diff` for auditing two-parent merge commits.

## 2.11.2 - 2026-10-10

- Communication now leads with the conclusion, keeps terminology stable, defines
  unfamiliar terms in plain language and formats procedures as numbered steps.
- Long processes may use compact text diagrams; sentence word counts are guidance,
  not hard limits, so brevity cannot remove information needed for correctness.
- An explicit request for an HTML explanation produces one self-contained interactive
  HTML file.

Migration from 2.11.1: run `install.py --update`. No project-owned files require
manual changes.

## 2.11.1 - 2026-10-10

- Clarify human instruction authority, configurable project parameters and mandatory
  acceptance safeguards; centralize communication and role-specific context loading.
- Define ordinary branches for Orchestrator/Single Mode changes, with the primary
  checkout back on the configured main branch before launches and acceptance.
- Entry points link to session procedures instead of imposing duplicate read lists.

Migration: run install.py --update. In project-owned instructions remove copied
workflow rules in favor of protocol links; keep main branch, mode, checkout roots
and engineering commands locally. Replace obsolete statistics bans, distinguish
historical install versions from VERSION, and remove contradictory main-folder-only
editing rules. User-global files are never changed by the installer.

## 2.11.0 - 2026-10-10

- New `.agentflow/tools/machine_capacity.py`: an OS-locked registry at `%LOCALAPPDATA%\AgentFlow\machine\registry.json` (per OS account) coordinates every AgentFlow project on the machine -- an atomic tool-slot claim before a launch (default: one Codex machine-wide; `AGENTFLOW_MACHINE_<TOOL>_MAX` and a project's `- parallel: <tool>=<n>` tighten it; the lowest active rule wins), a `PORT` reservation for workers, tool-limit times shared between projects, pending-claim handoff to the worker process, and dead-PID lease cleanup. `run-task.ps1` and `conductor.ps1` claim, activate and release leases; `tick.py` shares observed limits machine-wide and skips tools without capacity in `next-orchestrator`; a busy slot waits and is retried on a later round instead of failing. Found in a project: two AgentFlow projects on one machine could both start a Codex session on the single Windows sandbox account -- the failure 2.10.0 guards inside one project.
- `route.py` asks Jev a third question -- how much reasoning effort a task needs -- and deterministic code maps the generic tier to a level the chosen model supports: `efforts` lists the CLI's levels, `model_by_effort` holds concrete effort-specific model ids (Devin, the installed Antigravity), `default_effort` sets the fallback. Routing confidence is the lower of model and effort confidences. Claude takes `--effort`; `model-options.json` stubs and `typesafe.md` show the new shape.
- Usage-limit detection also covers disabled subscription or account access ("subscription access ... disabled", "ask your admin to enable access"): the same temporary-unavailability path as a quota, recorded machine-wide, so the next configured tool takes over at once and the preferred one is retried after its recorded reset. The conductor retries `next-orchestrator --skip` when a claim loses a race.
- New `.agentflow/tools/upstream.py` keeps the template itself current: it compares each installed project with its recorded template in both directions -- a template-owned file that differs at the same version is an upstream candidate, a missing or older file means `install.py --update`, a project addition inside a template-owned directory is reviewed as a new template file or kept project-owned. `install.py` records the template path and version in `.agentflow/template-source.json`; `machine_capacity.py` keeps the known project roots (`projects` command); the conductor runs `upstream.py --check` for its project once a day and notifies on drift. Changes that flow upstream are generalized first (protocol, "Installing or updating AgentFlow").
- `test_machine_capacity.py`, `test_upstream.py`; `test_route.py`, `test_tick.py`, `test_conductor.py`, `test_launcher_args.py`, `test_parallel.py` cover the new behavior.

Migration from 2.10.x: `install.py --update`. To route effort, take the new `efforts` / `model_by_effort` fields into `.agentflow/docs/model-options.json` (the stub shows the shape; options without them behave as before). Sessions started by an older version hold no lease; nothing to do for them.

## 2.10.0 - 2026-10-09

- New project Preflight rule `- parallel: <tool>=<n>`: `gate.py preflight --tool` (passed by `run-task.ps1`, so also by `tick.py` and the conductor) refuses a launch while n attempts of that tool are running. Found in a project: two Codex sessions at once on Windows rewrote each other's sandbox account logon, Windows locked the sandbox account and the user's own account (error 1909), and both testers lost their environment.
- `test_parallel.py`; `test_accept.py` no longer depends on the template checkout being clean.

Migration from 2.9.x: `install.py --update`; on Windows add `- parallel: codex=1` under `## Preflight` in `.agentflow/docs/project-rules.md`.

## 2.9.2 - 2026-10-09

- The end check fails a developer attempt that wrote its Result into the Task File copy inside its worktree (the main Task File stays empty) or committed a Task File on its branch; the message says how to recover. The worker prompt and the developer role now say it explicitly. Found in a project: Devin wrote and committed its Result in the worktree copy; the attempt looked fine, acceptance saw an empty Result.
- `test_endcheck.py` covers both.

Migration from 2.9.1: `install.py --update`.

## 2.9.1 - 2026-10-09

- Fix: the end check failed a worker that appended the missing `## Result` heading after an empty line: the header hash counted the extra trailing blank line. `gate.py header()` now ignores trailing whitespace; hashes of existing baselines stay valid.
- New `run-task.ps1 T-NNN -Recheck`: runs the end check again for an attempt that exited 0 but failed it, and marks it `exited` when it now passes (the old note is kept).
- `test_endcheck.py`.

Migration from 2.9.0: `install.py --update`; an attempt failed only by this, `run-task.ps1 T-NNN -Recheck`.

## 2.9.0 - 2026-10-08

- A planned task waits for the human's approval. `ledger.py add` without `--status` creates it `blocked` with Notes `awaiting approval`; `gate.py preflight` refuses to launch it and `tick.py` lists it as waiting for approval; `ledger.py approve T-NNN ...` makes it `ready`. Successors and Tester tasks within an approved goal are added with `--status ready`. A background Orchestrator never approves. Found in a project: with the conductor running, a task added as `ready` before the human's yes would have been launched within minutes.
- `test_approval.py`.

Migration from 2.8.0: `install.py --update`. Tasks already in the ledger keep their status.

## 2.8.0 - 2026-10-08

- The conductor runs once per project: a named mutex makes a second instance (the logon task, another window) exit at once. It records its pid and the time of its last round in `conductor.json`.
- New `.agentflow/tools/conductor-panel.ps1` (Windows PowerShell 5.1 and 7): `-Install` registers autostart at logon (Task Scheduler folder `\AgentFlow\`, no time limit), puts an "AgentFlow - <project>" shortcut on the desktop and starts the conductor. Without arguments it opens a window for the human (Russian): autostart, conductor and its last round, the live Orchestrator, the background session, the last tick, tool limits, questions, what waits for a decision; buttons for autostart on/off, start/stop, a dry run, questions, session log, state folder, Task Scheduler. `-Status` / `-Start` / `-Stop` / `-Register` / `-Unregister` / `-Shortcut` from the console.
- Orchestrator role: before the loop, check the conductor (`-Status`), start it if needed, and tell the human about `-Install` when autostart is off.

Migration from 2.7.0: `install.py --update`, then once per project and machine `.agentflow\tools\conductor-panel.ps1 -Install`.

## 2.7.0 - 2026-10-08

- New `.agentflow/tools/conductor.ps1`, the watcher the human leaves open: every 3 minutes `tick.py run`; when there are needs and no Orchestrator is live, a background Orchestrator session in a visible window on the first free tool of `AGENTFLOW_ORCHESTRATORS`, with the developer command line of `run-task.ps1` (full access) and `AGENTFLOW_ORCHESTRATOR_<TOOL>_ARGS`. A session that hits a usage limit records it and the next round hands over to the next tool at once; the same needs are otherwise handed over again only after `-CooldownMinutes` (60). Windows notifications for acceptances and launches, hand-overs, finished sessions, all tools limited, and changes in `questions.md`. `-Once -DryRun` shows what it would do.
- `test_conductor.py` runs it in real PowerShell with a fake `tick.py` and fake tools: dry run, a live Orchestrator left alone, hand-over, the next tool after a limit, cooldown, all tools limited.

Migration from 2.6.0: `install.py --update`; in Claude Code add an allow rule for `.agentflow/tools/conductor.ps1` if Claude should start it.

## 2.6.0 - 2026-10-08

Orchestration survives the end of an Orchestrator session (usage limit, closed window):

- New `.agentflow/tools/tick.py`: `run` takes the steps that need no judgment (accept a Tester with `Verdict: pass`, accept a Developer whose Tester is done or whose check is `none`, launch ready tasks whose dependencies are done and whose tool is not limited) through `accept.py` and `run-task.ps1`, and lists the rest as needs in `.runtime/tick.json`; `--dry-run` changes nothing. `heartbeat` / `release` keep one Orchestrator at a time (a heartbeat older than 20 minutes is not live; while one is live, `run` only reports). `limit` and `tool-limits.json` remember when a limited tool is usable again, learned from attempt logs ("resets 3:30pm", "resets in 158h43m"; one hour otherwise). `next-orchestrator` picks the first free tool of `AGENTFLOW_ORCHESTRATORS` (default `claude,codex,devin,agy`).
- Protocol section "Autonomous orchestration": what a background Orchestrator may do (the approved plan only: launch, accept, reject, recovery, successors, Tester tasks) and may never do (new scope, plan or rule changes, push, publish, deploy, production); questions for the human go to the new `.agentflow/state/questions.md`.
- Orchestrator role: heartbeat after every step; on its own limit it records it and releases.
- `test_tick.py`: decisions, acceptance chains in one tick, refused acceptance, limits and reset times, heartbeat ownership.

Migration from 2.5.x: `install.py --update` (creates `questions.md`).

## 2.5.3 - 2026-10-08

- Fix: `accept.py` refused every acceptance once the committed memory (for example the ledger) had changed: the trimmed `git status` output lost the first line leading space, so `.agentflow/...` read as `agentflow/...` and counted as a change outside the memory. It now reads `git status --porcelain -z` raw. Tests commit the memory before acceptance, as a real main folder does, and check that a real change outside it still blocks.

Migration from 2.5.x: `install.py --update`.

## 2.5.2 - 2026-10-08

- Fix: tester tasks in a single-repository project could not launch since 2.3.0. The task JSON for `run-task.ps1` carried the single repository commit under an empty key, which PowerShell `ConvertFrom-Json` rejects; `gate.py` now writes that key as `.`. A new test reads a tester task JSON with real PowerShell.

Migration from 2.5.x: `install.py --update`.

## 2.5.1 - 2026-10-08

- Fix: a task `Model:` line now replaces the matching flags from `AGENTFLOW_<TOOL>_ARGS` instead of adding a second copy. Devin exited at start ("--model cannot be used multiple times") when both were set, and for Codex a machine `-c model_reasoning_effort` silently overrode the task effort.
- New `test_launcher_args.py` runs the launcher functions in real PowerShell.

Migration from 2.5.0: `install.py --update`.

## 2.5.0 - 2026-10-08

TypeSafe integration rebuilt from the official documentation (https://docs.typesafe.ai):

- New template-owned `.agentflow/docs/typesafe.md`: links to every relevant documentation page and the rules
  `route.py` follows; the protocol and tool routing point to it.
- `route.py`: state is an object with named fields, clipped well under the 32k-token budget; one request asks two
  atomic questions in parallel - choice "option" and 3-level score "complexity" - combined in code (a pick whose
  `max_complexity` is exceeded escalates to its `escalate_to`); choice criteria are objects (`what`, `not_for`,
  `examples`; the old `describe` still works); the policy goes into the instructions; confidence bands from the docs
  (>= 0.9 apply, 0.5-0.9 confirm - exit 4, < 0.5 no decision - exit 3; `--threshold` removed); Jev pinned to
  `jev-1.13.0` (`jev_model` in the options file); `TYPESAFE_BASE_URL` (the SDK's name; `TYPESAFE_API_BASE` is gone);
  the request id also on errors.
- Tests: the stand-in server checks the documented request shape; tests clear every `TYPESAFE_*` variable so they can
  never reach the real service.

Migration from 2.4.x: `install.py --update`; in `model-options.json` rename `describe` to `what` (optional), add
`not_for` / `examples`, and `max_complexity` / `escalate_to` where a stronger option should take hard tasks.

## 2.4.1 - 2026-10-08

- route.py prints and logs the TypeSafe usage (input and output tokens) and the request id (`x-typesafe-request-id`) of every call, so a call can be matched with the TypeSafe dashboard or support.

Migration from 2.4.0: `install.py --update`.

## 2.4.0 - 2026-10-08

- Task File line `Model: <model>[, effort=<level>]`: the launcher adds the tool's flags (codex `-m` and `-c model_reasoning_effort`, agy `--model` / `--effort`, claude and devin `--model`). New machine variables `AGENTFLOW_CLAUDE_ARGS`, `AGENTFLOW_AGY_ARGS`, `AGENTFLOW_DEVIN_ARGS`.
- New `.agentflow/tools/route.py`: recommends the tool and model for a task with TypeSafe AI (Jev, one choice question over the project's options) and, with `--apply`, writes `Tool:` / `Model:` into a task that has not started. Options and a policy in words live in the new project-owned `.agentflow/docs/model-options.json` (with `from` / `until` windows and roles); a tester never gets the developer's tool while another option remains. The key stays outside the repository (`TYPESAFE_API_KEY` or `AGENTFLOW_TYPESAFE_KEY_FILE`) and is never printed. No key, an API error or low confidence: exit 3, decide by Tool Routing.
- Tests: `test_route.py` against a local stand-in for the API.

Migration from 2.3.0: `install.py --update` (it creates the `model-options.json` stub); fill the options and set the key variable to use `route.py`.

## 2.3.0 - 2026-10-08

- Workspace mode: a folder that holds several repositories. Its root becomes a small memory repository (it tracks only AgentFlow files and the root entry points; the product repositories are ignored by it and stay independent); `.agentflow/workspace.json` lists the repositories. Task Files name them in `Repo:`; paths start with the repository folder; commits are `<repo>@<SHA>, ...` in `Change:`, `Verifies:`, `Deploys:`. One branch per task in every named repository; `Worktree` holds one worktree per repository.
- `gate.py`: repositories per task, per-repository branch / worktree / diff / merge checks, tester checkouts per repository (`checkouts` in the task JSON drive `run-task.ps1`). Single-repository projects behave as before.
- `accept.py`: a trial merge (`git merge-tree`) in every repository before any merge; untracked files no longer block acceptance; the workspace memory repository does not count its product repositories as changes.
- `run-task.ps1`: creates and removes worktrees and tester checkouts per repository; a developer worktree is re-created on an existing task branch.
- `install.py`: `--workspace`, `--repos`, `--git-init`; finds the repositories by their `.git`; points to the workspace option when a folder of repositories is refused.
- Tests: `test_workspace.py` runs the real tools end to end on throwaway repositories (single repository, two repositories, a file outside Allowed files, a conflict in one repository, tester and Repo validation).

Migration from 2.2.0: `install.py --update`. Projects with one repository change nothing.

## 2.2.0 - 2026-10-07

Lessons from running the Watermark Remover project in Team Mode with Claude Code, Codex, Devin and Antigravity.

Layout and installation:

- Everything AgentFlow owns lives in `.agentflow/` (protocol, roles, commands, Task File template, tools, dashboard, tests, VERSION, README). The project root keeps only `AGENTS.md`, `CLAUDE.md`, `.claude/commands/` pointers and a `.gitignore` block, so AgentFlow no longer collides with a project's own `docs/`, `tasks/` or `tools/`. Tools find both roots through `.agentflow/tools/paths.py`; the dashboard still reads ledger and Task File history from before the move.
- New `.agentflow/tools/install.py`: installs into an existing repository or updates it (`--update`, `--dry-run`, `--inside-repo`). It deletes nothing, adds a marked block to existing `AGENTS.md`, `CLAUDE.md` and `.gitignore` instead of rewriting them, keeps foreign `.claude/commands/` files and project-added files in `.agentflow/`, creates missing project-owned stubs, refuses a non-root or non-git target, an existing install without `--update`, a 2.1 root layout, and an update over uncommitted template-owned changes.
- Version: `.agentflow/VERSION`. Project rules: `.agentflow/docs/project-rules.md` (also `engineering-rules.md`, and rules in `AGENTS.md` outside the AgentFlow block).

Tools:

- New `.agentflow/tools/accept.py`: verify -> merge `--no-ff` -> ledger `done` -> worktree remove -> `branch -d`, stopping at the first failure and aborting a failed merge. Testers: verify and ledger only.
- `gate.py`: Task File fields are read from the header only (a report line `Target: local` broke the end check); a short `Change:` SHA is expanded to the full one.
- `run-task.ps1`: `devin` tool (`-p --permission-mode dangerous --respect-workspace-trust false`); `agy` developers run in print mode with `--output-format stream-json` (no manual `/exit`); `AGENTFLOW_CLAUDE`, `AGENTFLOW_AGY`, `AGENTFLOW_DEVIN`, `AGENTFLOW_PYTHON` overrides; `python` falls back to `py -3` when it is the Microsoft Store stub; `AGENTFLOW_*` and `PATH` are handed to the worker window through `tasks/.runtime/T-NNN.env.json` (a Store-packaged pwsh does not pass its environment); QuickEdit is switched off in worker windows (a click paused them); "session limit" and "hit your limit" count as usage limits.
- New tests: `test_layout.py`, `test_install.py`, `test_accept.py`.

Protocol and roles:

- Result rules: the Result is everything after the last `## Result` line; nothing above it changes, blank lines included; headers never repeat that heading text; no report line starts with a header field name.
- New "Successors and re-tests": merge-only successor for a branch that predates a fix on main; re-tests reuse earlier evidence; a same-tool Tester only when no other tool is free.
- Launching workers: machine setup (environment handover, Python, QuickEdit) and the Claude Code permission the human must grant for the Orchestrator to launch workers.
- Orchestrator: foundation task first (shared files and contracts), one owner per shared file, an early preview build for the human, acceptance through `accept.py`, no `;`-chained state changes.
- Developer: commit early and amend the single task commit on long tasks. Tester: report placement rules; mark checks blocked by the environment `unverified`.
- Tool routing: Devin, plan for limits (Claude worker sessions can end in minutes, Antigravity quotas for days, the Codex sandbox on Windows can refuse processes), the Codex desktop-app CLI path.
- GUIDE: installation into an existing project, update, migration from the root layout, machine setup.

Migration from 2.1.x (root layout):

1. In a branch, `git mv` the AgentFlow folders into `.agentflow/` (`docs/ai-handoff-protocol.md`, `docs/project-plan.md`, `roles/`, `state/`, `tasks/`, `tools/`, `dashboard/`; `.claude/commands/*.md` -> `.agentflow/commands/`); keep project files that only share a folder name; move `docs/engineering-rules.md` too if it holds Project rules.
2. `python <template>/.agentflow/tools/install.py <project> --update --dry-run`, then without `--dry-run`.
3. Delete by hand the old 2.1 template text in `AGENTS.md` above `## Project rules` and the old slash-command list in `CLAUDE.md` (the installer never deletes); keep the project's rules.
4. Open Task Files: paths `tasks/`, `state/`, `docs/` -> `.agentflow/...`; finish running attempts before the move (their runtime state moves with `tasks/`).

Migration from a hand-made `.agentflow/` adaptation of 2.1.0: commit everything, then `install.py --update`; files the project added (wrappers, notes) are kept and listed.

## 2.1.0 - 2026-10-04

- New template-owned `dashboard/`: a read-only view for the human built from the ledger, Task Files, and git (`python dashboard/build.py` -> `dashboard/out/index.html`, `out/graph.html`). Task table with filters over every axis, task card, Gantt, timeline, dependency, successor and check links. Interface in Russian (it is human-facing); ledger statuses are shown as Russian labels.
- `dashboard/snapshot.py`: local versions of the dashboard sources with rollback; `dashboard/UI-RULES.md`: rules for changing the interface; `dashboard/README.md`: files and the data contract.
- Protocol: new section "Dashboard"; `dashboard/` added to the template-owned list. `.gitignore` gets `dashboard/out/` and `dashboard/versions/`.
- Orchestrator role: rebuild the dashboard when the human asks or a Stage closes.

Migration from 2.0.x: copy `dashboard/`, append the two `.gitignore` lines, replace `docs/ai-handoff-protocol.md` and `roles/orchestrator.md`. No Task File or ledger changes.

## 2.0.0 - 2026-10-03

- Tester review isolation: a disposable checkout of the `Verifies` commit; the launcher fails the attempt if the checked branch, worktree, or Task File changed. Codex is the first choice for Tester tasks.
- Every attempt goes through `tools/run-task.ps1`; `-Manual` gates and prepares sessions a human starts (Antigravity IDE, Deployer, live Tester on prod).
- Production approval: the human gives it in the Deployer session; the Deployer records `Approval: source=human target=prod sha=<SHA> at=<time>`.
- New `tools/gate.py`: preflight, end-of-attempt check, `verify` (acceptance evidence), `stage` (Stage check on the main branch).
- Attempt history in `tasks/.runtime/T-NNN.json`, one log per attempt; global launch lock.
- State families: Task state, Process state, Outcome, role result (Change / Verdict / Deployment), Stage state. Acceptance is the ledger transition `review -> done`, allowed only after a passing verify.
- `tools/ledger.py`: enforced transitions, `Updated` column, `done` needs a passing verify, `rejected` / `cancelled` need notes.
- Template and project separated: ownership list and install / update procedure in the protocol; the template's own `state/` and `docs/project-plan.md` are not copied; guide moved to `GUIDE.md`.
- Machine-facing instructions in English; human communication in Russian.

Migration from 1.x:

- Task File fields: `Checks: T-xxx, commit <SHA>` -> `Verifies: T-xxx @ <SHA>`; `Environment:` -> `Target:`; deployer `Deploys: <SHA>`; `Prod approved by human:` removed; section `## Environment setup` -> `## Setup`; section `## Review before merge` -> field `Independent check: tester | none - <reason>`.
- Result: `Status:` -> `Outcome: completed | blocked | failed` plus `Change:` (developer), `Verdict:` and `Criteria:` (tester), `Deployment:` (deployer).
- Ledger: `rework` -> `rejected` (successor in Notes); the `Updated` column is added automatically.
- Process states: `completed` -> `exited`, `failed` -> `error`.
- Stage status: `done` -> `closed`, `pending` -> `planned`; `Result:` -> `Exit criteria:`.
- Finish or re-issue open tasks after updating: a running 1.x attempt has no attempt history.

## 1.2.0 - 2026-10-02

- Launch preflight with project `## Preflight` deny / require rules, `## Checks` section, production opt-in through `AGENTFLOW_TARGET`.

## 1.1.0 - 2026-10-02

- Launcher and ledger defects found migrating a live project fixed.

## 1.0.0 - 2026-10-01

- Team layer: four roles, Task Files, Task Ledger, `/start-role`, tool routing, `tools/run-task.ps1`, `tools/ledger.py`, on top of the base AI Project Memory (2026-05-21).
