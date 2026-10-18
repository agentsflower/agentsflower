# Decision Log

## 2026-10-18: Urgent stalled-work repair and scoped routing exception

Subsequent read-only diagnostics identified the stop actor: Devin session
maddening-museum (background Orchestrator) invoked T-040 --stop, then relaunched
at 04:48:42Z. Its public commentary cited post-suspend recovery. Windows System
events independently confirm Kernel-Power 506 (Idle Timeout) at 04:49:19 Moscow
and 507 (Lid) at 07:45:24. Thus most of the first attempt's apparent three-hour
duration was standby, not model execution. Do not diagnose a hung model from
the attempt text log alone: Devin session metadata showed continued tool calls
even while that log had no new prose. T-080 adds a process-scoped idle-sleep
guard; never change global power plans or override deliberate sleep/lid policy.
The human explicitly extended the swe-2-max exception to T-080 and its
independent tester in response to the scoped question in this chat. Persisted
T-080 assessment request req_01a14d6b07c67795ba87831f8ed31bc4 remains low
confidence (0.41); the exception is not relabeled as Jev evidence.

Human requested diagnosis, urgent correction and forward task progress instead
of hours-long retries. T-040 attempt 1 was explicitly stopped at 04:48:11Z
(the old stop record has no actor/reason beyond --stop); attempt 2 was started
by another coordinator at 04:48:42Z. For coordinated repair, this session
stopped the conductor and its background Orchestrator, then stopped T-040 via
the launcher, preserving its worktree and a binary diff in ignored runtime
storage. No external project is in scope.

T-072 repairs deadline enforcement and observability. Jev request
req_01a14d63b45d728a92f052c5bcdc3348 selected Devin but effort confidence was
0.29. The human explicitly approved swe-2-max for T-072 and its independent
tester in this chat; this is a scoped auditable exception, not Jev certainty
or permission to bypass provider holds. T-072 launches with a 900-second
attempt cap. Preserve all earlier task history; never reset it to conceal a
budget stop. Split remaining T-040 work into independently checked bounded
deliverables before restarting it. Do not blindly relaunch a user stop.

T-072 attempt 1 reached its 900-second cap while the mandatory full suite was
still running (11 focused watchdog tests had passed). Attempt 2 resumes the
same Devin conversation joyous-number via the CLI's --resume flag, with the
preserved draft; do not pay for another full architecture read. Its configured
supervisor ceiling is 1200 seconds for finishing checks and recording the
artifact, not an unlimited extension. This operational adjustment was reported
to the human. Remaining routing delivery is T-074 core -> T-076 direct launch
-> T-078 automatic scheduling/reports, after T-072 and T-080 repair. Original
T-040 is cancelled as superseded, never marked done without its criteria.

## 2026-10-17: Contract-authoring rules learned from two scope rejections

- Allowed files must declare the whole `git diff main...HEAD` file set,
  including the inherited base when a successor branches from an unmerged
  commit - scope verification diffs the branch, not the delta commit.
- One path per bullet: the parser takes the first token of each line, so a
  comma-separated list or a trailing "(note)" becomes a literal path that
  matches nothing.
- `Depends on:` may only point at `done` tasks; when a predecessor is
  rejected, unstarted successors re-point at the accepted successor task.
- A Do-not-touch path that contains an allowed path trips the overlap check;
  exclude other Task Files via the `t-*.md` glob, not the whole tasks/ dir.

## 2026-10-17: 2.12.2 lifecycle trust round 2 - fixes T-029's confirmed defects

Every runtime-state reader now validates the shape it depends on: wrong-shaped
or empty tool-limits/heartbeat/attempt/verify records are diagnosable errors at
read time, never "no limits", "no live orchestrator" or "no evidence"; a
malformed heartbeat blocks an orchestration claim (--force still takes over).
Acceptance is bound: ledger.py set --status done requires a verify record
naming the task, the last attempt number, the current requirements hash and the
full artifact SHA, with that attempt exited - a stale PASS cannot accept;
legacy records bind only what they carry (the file plus the artifact). A live
pid whose start identity is unconfirmed keeps the task locked: --stop refuses
instead of killing a possibly reused pid or freeing the lock, --status reports
blocked, tick surfaces a need; verified stop or verified identity releases.
machine_capacity._alive uses the same pid + recorded start identity rule on
every platform. route._log and tasks.md writes are atomic. Adopted from the
accepted T-050 Result; the round-1 codex+devin reviews found the defects and
the devin round-2 review proved the fixes live.

## 2026-10-17: Mandatory assessed-adequacy routing adopted; task pool extended

New explicit human instruction (runtime file
tasks/.runtime/required-routing-policy-2026-10-17.md) supersedes default-only
worker routing; imported into docs/project-rules.md "Mandatory assessed-
adequacy routing". Created docs/model-options.json (project-owned) from the
pilot's proven schema plus this project's policy and per-family quota_group
fields (agy-gemini vs agy-claude-gpt) matching the machine registry's scoped
holds. TypeSafe key-file variable validated by existence only; first real
route.py call succeeded (jev-1.13.0).
Jev assessments (all persisted in .runtime/T-NNN.route.json): T-028/030/032/034/
036/040/044 -> devin-swe-2 at max effort (swe-2-max), family confidence
0.89-0.97, hard complexity; T-038/042/046/048 -> swe-2-high adequate. Headers
set to the assessed adequate model; T-046/T-048 lowered from a guessed max to
the assessed high (adequacy floor is a minimum, and the policy prefers the
cheaper sufficient tier).
T-028 keeps its running attempt on swe-2-high: it launched before the mandatory
policy (recorded, not retro-fitted), already committed 2c58157 and entered
Result-writing when the policy arrived; per instruction, sufficient in-flight
work is not stopped for paperwork - adequacy is judged by its independent
exact-SHA tester, and any successor runs the assessed model.
New approved contracts: T-040 routing enforcement (depends T-034, inserted
before T-036 so the docs task covers it), T-042 clickable mockup (independent,
parallel-safe), T-044 data layer -> T-046 UI -> T-048 integration (after T-038
and the human's mockup selection; tester IDs reserved odd-after-developer).
Launcher/env verified: Task File Model wins over AGENTFLOW_DEVIN_ARGS via
remove_overridden, so a stronger declared model cannot be silently downgraded
by the swe-2-high machine default; process-level override clearing not needed.

## 2026-10-17: Stage 4 bounded cycle outcome and Stage 5 decomposition

Drift audit (upstream.py --check): every installed project sits at 2.11.8
behind 2.12.0 - version lag only - except Transcript Youtube site\code, which
carries two generalized upstream candidates (tools/limit_detection.py,
tools/quota_groups.py + tests). They address the known tool-wide-limit
conflation and regex-only limitHit false positives; adopted into Stage 5 task
T-030 instead of copying file-by-file, because the plan asks for generalized,
documented mechanisms.
Pilot rollout to WatermarkRemover done inside the authorized cycle
(master@3fa1efb): 2.11.8 -> 2.12.0, dry-run first, local untracked files
preserved, stale env handover files removed per 2.11.11 migration, installed
suite 204 pass. Its conductor was already dead and was not restarted.
Stage 5 decomposed into six serialized developer tasks (T-028/030/032/034/036/
038) mapped 1:1 to improvement-plan sections 1-6, each requiring an independent
tester. Serialization is deliberate: every contract touches CHANGELOG.md and
VERSION, and the human asked for serialized release metadata.
Continuation policy applied to machine config only (never template code):
AGENTFLOW_ORCHESTRATORS=devin, AGENTFLOW_DEVIN_ARGS=--model swe-2-high, worker
timeout 2400s, model probes on; conductor restarted with no active writers.
Rejected: leaving codex first in the orchestrator list (would route background
handover to a conserved tool) and editing conductor.ps1 for machine config.

## 2026-10-17: Runtime baseline accepted and continuation assigned to Devin

T-022 exact 0420265a1e2a5a35136f3b80039adc2bb8a5a177 independently passed T-023
and all four acceptance checks (158 full-suite tests), merged as 2.11.11.
Registry replacement now retries only transient Windows 5/32 within a fixed bound,
preserving atomicity/old state on permanent failure. Conductor handover uses
CurrentUser DPAPI-encrypted in-memory argv; no plaintext env file, legacy file
removed. This avoids pwsh-7.4-only Environment APIs and keeps the 5.1 fallback;
live handover tested on pwsh 7, 5.1 path statically reviewed, not a live claim.
Exact documented rebuild sentinel nothing no longer reserves a shared resource.
T-009 CI configuration was reviewed, but its old-branch acceptance failed a known
test_route baseline case; rejected to merge-only T-026 after repaired main. No
CI semantics are changed or tests waived. T-003/T-010 now depend on T-026.
Delegate the approved mechanical continuation to Devin background Orchestrator
after releasing this root holder; root observes without a second memory writer.
Use Devin-only background platform preference, explicit inference opt-in and
bounded worker attempts. Other platform quota data stays in runtime. No approval
to push, publish, create an unverified release tag or bypass independent checks.

## 2026-10-17: Approved implementation choices for the remaining release pool

These are approved design constraints, not claims that implementation has passed.
T-003 packages generated installer-owned resources from the single .agentflow
source, excludes project memory/settings/tasks, and keeps source/project CLIs
stdlib-only. Built-wheel/sdist checks must work outside the checkout. Distribution
name may be agentflow-sdlc; no PyPI publication is claimed or authorized.
T-005 uses published official mcp 2.3-compatible SDK (PyPI declares Python >=3.10),
optional extra only, no custom JSON-RPC fallback. Mutating acceptance tools are
startup opt-in, not caller authentication. Merge client config without overwrites;
verify Claude/Cursor actual config paths rather than claiming identical discovery.
T-007 uses route_report as the sole metrics provider, honest denominators/history,
unknown missing tokens/cost/context savings, English UI default and marked demo
data. Preserve layout and take snapshot; screenshot must be a real browser capture.
T-010 preserves Russian guide, adds English public docs/Mermaid/dated maintainer
product snapshots and prepared 2.12.0 notes. No invented URLs, unique-user sum,
remote green jobs, published package or verified release tag. T-011 is final LOCAL
preparation review; remote nine-job/macOS proof is a separate release gate after
the human's promised manual push. Do not block local implementation on that gate.
Background Orchestrator may implement/accept this approved scope through existing
gates and write verified facts in handoff/session-log. New design/scope/security
decisions beyond these constraints go to questions.md for the human; no push or
production approval may be inferred. Intermediate patch releases get these dated
design records plus exact task/result evidence; final verification facts remain
explicitly separate from the design approval.

## 2026-10-17: Execute the entire approved public-release pool

Human directs testing and all remaining queued work, then asks to check progress.
Treat this as approval to execute the agreed v2.12.0 scope, not only the previously
registered launcher tasks. Prepare the nine-job CI now and continue all local
features without waiting for macOS; actual remote/macOS results remain an external
release gate and human performs push/publication. Cancel obsolete T-018 placeholder
in favor of T-009 CI and final release evidence. Work on this repository only.
Add T-022 for recurring registry reliability and conductor secret handover, then
T-003 package/CLI, T-005 MCP, T-007 English metrics/dashboard, T-010 public docs;
independent Tester contracts are created for exact result SHAs. Shared release
metadata ownership makes these feature tasks sequential; CI can run independently.
Fresh Devin inference failed solely on untrusted probe cwd; direct read-only/auto
call with explicit respect-workspace-trust false succeeded. T-024 is a narrow
native Codex manual-adapter bootstrap (launcher created worktree/baseline), followed
by independent review, so model checks are retained rather than bypassed. Conserve
Codex; use Devin for the remaining pool. Do not start the old conductor's unsafe
plaintext handover until T-022 repairs it; live Orchestrator coordinates meanwhile.

## 2026-10-16: Verify Windows hardening and hold Unix acceptance

T-015 independently failed T-014 despite 149 green tests: custom catalog/auth
could masquerade as inference, heuristic argv masking missed short secrets and
the worker env JSON reserialized raw config. Rejected to T-016, preserving source.
T-016 produced 1e0bd876a4c3247416f6ccc3dd9c89970a36d695: built-in-only opt-in
model inference, hash-only operator argv evidence, spawn-only worker environment,
probe tree timeouts, hermetic test_route fixtures and nonzero-exit limit detection.
T-017 independently passed local criteria and 151 tests on Windows; overall
unverified solely for real Linux/macOS coverage. Accepted the review via accept.py,
not the product. Per non-pass lifecycle reject T-016 to blocked T-018 for actual
Unix evidence. No source candidate merged or pushed. Human must choose Unix hosts
or CI prepared for manual push; do not silently waive the coverage gate.
The old main launcher falsely set limitHit on successful quota-discussion reports.
Fresh model inference / later successful sessions disproved those observed limits;
corrected through tick.py with explicit administrative one-minute cooldowns, not
raw registry edits. The candidate contains the regression fix; main does not yet.
Conductor's separate plaintext env handover is pre-existing and outside ownership;
record it for a separate bounded security repair before public release.

## 2026-10-16: Record bounded launcher review without accepting missing guarantees

T-012 successor recovered on Devin swe-2-medium after Devin high made no repair
progress and agy Opus exhausted quota. Separate Sonnet and GPT-OSS probes also
returned RESOURCE_EXHAUSTED; Gemini was already unavailable. Keep quota evidence
and reset timing in runtime, not a claim that catalog presence proves resources.
T-012 produced 87de72c: noninteractive agy Tester, streaming, 1200-second enforced
worker timeout/tree termination, PID identity checks and isolated fixtures.
T-013 independently ran all checks: 147 tests pass on Windows 10/Python 3.13.
Its unverified verdict is accepted as a completed review, not code acceptance.
Reject T-012 to prepared T-014: selected-model inference is still unproven by
auth/catalog probes despite the Tester's pass label for AC-06; user requires the
stronger guarantee. Also close secret-bearing probe argv and visible-window rule
gaps. Linux/macOS behavior needs actual host/CI evidence; asked human for route.
Preserve unmerged 06b7e3a and 87de72c worktrees; no push/publication authorized.

## 2026-10-16: T-012 recovery to agy Opus

Devin attempt 1 copied the source port but made no repairs or Result for over
ten minutes. Stopped via launcher; staged draft preserved. Per stale-task recovery,
same scope/task/worktree continues on agy claude-opus-4-6-thinking after a fresh
ACCESS_OK inference probe. Update header only after the first executor stopped.
Current launcher already supports noninteractive developer agy; its broken
interactive Tester path is not used. Independent review can use Devin after repair.

## 2026-10-16: Recover hung agy Tester through a successor

Human authorized repair and continuation. T-002 attempt ran about 15h with no
Result/log; process used -i. Stopped via run-task.ps1 -Stop, preserving artifacts.
Reject T-001 to T-012 rather than change reviewed branch/header; cancel T-002 and
review successor SHA in a new task. T-012 preserves 06b7e3a and requires agy
print/streaming, enforced 20-minute default runtime and process-tree cleanup,
without weakening Tester permissions. Include regression and machine-env isolation
fixtures. Devin remains primary; agy Opus is intended for independent review.

## 2026-10-16: Use non-Gemini models through agy

Human authorizes using agy's Claude and GPT models, rather than excluding the
platform when Gemini is exhausted. T-002 selects claude-opus-4-6-thinking; a short
plan-mode inference returned ACCESS_OK before launch. Catalog also lists
claude-sonnet-4-6 and gpt-oss-120b-medium; probe them when selected for future work.
Do not equate separate Claude CLI availability with Claude-through-agy access.
Machine registry currently scopes the observed Gemini limit to agy:agy-gemini;
Opus remaining quota is unknown. No automatic substitution on exhausted quota.

## 2026-10-15: Authorize T-001 launch on Devin and decouple external projects

Human confirmed authorization to launch worker T-001 via Devin (swe-2-high).
Third-party and client projects (including Gemini to Word) do not influence or block
AgentFlow template tasks; template rollout into client projects will take place only
after changes and testing of AgentFlow are completed in this repository.

## 2026-10-15: Revise public release worker routing

Human directs maximum use of Devin, with agy as a limited secondary platform and
Codex conserved. T-001 now requests Devin swe-2-high. Recommend agy
gemini-3.8-flash-high for independent T-002, subject to fresh model/resource checks;
do not automatically fall back to Claude or Codex. Model catalog queries returned
these identifiers, but do not prove remaining quota or successful inference access.
This supersedes the initial Claude/Codex pairing below. No worker launch authorized
by this routing adjustment; T-001 stays blocked pending start readiness.

## 2026-10-15: Approve public release scope and prepare T-001

Human approved T-001 through T-011 for v2.12.0. Cross-platform scope covers the
Python launcher and CLI; Windows conductor/autostart remains Windows-only. Keep
PowerShell Checks on Windows and sh on Unix, stateful ledger and contract-owned
roles; fail closed for unsupported permission modes. Package template resources
inside the distribution. Use optional official MCP SDK, no custom protocol fallback;
privileged acceptance tools are opt-in and installer merges existing MCP settings.
Reuse routing evidence, mark missing metrics unknown and demo data explicitly;
dashboard defaults to English. Serialize protocol/version/changelog ownership.
Keep real Deployer flow and human-only push/release publication. Product figures
were supplied by the human as October 2026 observations; publication needs direct
source links. T-001 is prepared without authorizing a worker launch; recommended
routes are Claude opus/high for development and Codex gpt-6.1-sol/high for review.
No local model-options.json exists; model entitlement and remaining quotas are
unknown. Before every start check model access, available capacity and resource
observations; CLI presence/help is insufficient. Unknown quota needs an explicitly
approved bounded policy or another checked route; do not invent quota readings.
T-001 uses intermediate 2.11.9 release metadata; final release reserves 2.12.0.

Decisions about the AgentFlow template itself: why, and what was rejected. What changed per version: `CHANGELOG.md`. Add new decisions below; do not delete old ones without a reason.

## 2026-10-10: Human authorizes managed Team Mode

The human explicitly removed an inherited single-agent/no-worktree restriction
from an older project. AgentFlow projects may use orchestrated worker sessions,
parallel independent tasks and isolated task/test checkouts in configured locations.
Keep resource caps, file ownership and independent acceptance; workers do not
recursively delegate. Global Codex instructions and the pilot's project rules were
aligned. This changes local operating policy, not the released template runtime.

## 2026-05-21

### AI Project Memory

Decision: baseline memory files: protocol, handoff, current-step, decisions, known-issues, session-log.

Why: long AI sessions lose context, repeat old errors, and forget why decisions were made. A short handoff is the entry point; details live in specialized files.

## 2026-10-04

### Dashboard is template-owned, in `dashboard/` beside `tools/`

Decision: the human's read-only view (built from the ledger, Task Files, git) ships with the template as `dashboard/`, Russian interface (it is for the human; machine-facing files stay English), statuses mapped from the protocol's ledger words. Only sources are committed; `out/` and `versions/` are git-ignored. Local versioning (`snapshot.py`) stays so the dashboard can be changed and rolled back.

Why: it was crystallized on one real project and the entities and flow are the same in every AgentFlow project. `tools/` is for agents; this is for the human, so a separate folder. Rejected: shipping built pages (they are project data, not template).

## 2026-10-01

### Team roles and single memory writer

Decision: four roles, Task Files in `tasks/`, Task Ledger `state/tasks.md`. In Team Mode only the Orchestrator writes Canonical Memory; workers write only their Result.

Why: several sessions updating handoff and current-step in parallel create conflicting versions of project state. Workers need their role and task, not the whole history.

### One task = one branch + one worktree, mandatory cleanup

Decision: each developer task gets branch `t-NNN-slug` and a worktree outside the repository and cloud sync; the main folder stays on the main branch and belongs to the Orchestrator; after merge the Orchestrator removes the worktree and the branch.

Why: on an earlier project 36 of 37 task branches with worktrees merged; the real problem was 33 merged worktrees left behind. Rejected: a no-worktree rule (loses parallel work).

### Tool routing by fit and budget

Decision: the Orchestrator picks the tool per task from `roles/tool-routing.md` and the limits the human reports; the choice is written in the Task File and ledger.

Why: tools differ in strengths and token cost; spending the most capable tool on mechanical work wastes limits.

## 2026-10-03

Context: an audit against the First Principles Framework (FPF) found rules that the scripts did not enforce, overloaded status words, evidence that was overwritten, and template history mixed into project memory. FPF was used as a reference, not as a target: a principle was applied only where it fixed a concrete defect.

### Enforcement before prose

Decision: prefer code enforcement, then structured fields, then one canonical rule; no rule repeated across files.

Why: every audit defect of the form "the text says X, the tool does Y" came from a rule that existed only as prose. Rejected: more prompt instructions (more tokens, same gap).

### Review isolation instead of "read-only Tester"

Decision: the Tester works in a disposable checkout of the checked commit; the launcher compares the checked branch, worktree, and Task File before and after the attempt. Codex (sandboxed) is the first choice; Claude is a fallback guarded only by the end check.

Why: the Tester needs write access for test runs and its Result, so "read-only" could not be true; what matters is that it cannot change the artifact that is then accepted. Rejected: Tester only on Codex (no fallback when its limit ends).

### Production approval stays in the Deployer session

Decision: the Deployer asks the human in its own designated session and records `source=human target sha at`; the Orchestrator is not in the chain.

Why: an approval relayed by the Orchestrator was a record it could write itself. Rejected: an `approve.ps1` record file (an agent with a shell can write the file as well).

### Acceptance as an event, separate state families

Decision: one owner and one vocabulary per family (Task state, Process state, Outcome, role result, Stage state); acceptance is the ledger transition `review -> done`, allowed by `ledger.py` only after a passing `gate.py verify`. No separate "Decision" status.

Why: `done`, `failed`, `blocked` meant different things in five places. Rejected: a common `Claim` result for all roles (Developer, Tester, and Deployer produce different results).

### Pure logic in Python, side effects in PowerShell

Decision: `tools/gate.py` parses Task Files and runs preflight, end check, verify, and the Stage check; `tools/run-task.ps1` creates worktrees and checkouts and runs processes.

Why: with verify and attempt history the launcher would have become parser, verifier, state machine, and evidence store at once; Python logic is easier to test and is shared with `ledger.py`.

### Template-owned vs project-owned files

Decision: ownership list and install / update procedure in the protocol; `AgentFlow version` in `AGENTS.md`; the template's own `state/` and `docs/project-plan.md` are never copied; project tool notes live in Project rules.

Why: projects inherited template history as their own decisions, and updating `roles/` overwrote project edits in `tool-routing.md`.

### Language

Decision: machine-facing files in English; communication with the human in Russian, generated from the canonical rule, never stored as a second copy.

Why: Russian text costs about twice the tokens of English, and two copies of a rule drift apart.

## 2026-10-07: 2.2.0 - one `.agentflow/` folder, installer, lessons from a real Team Mode run

Why: installing 2.1 into an existing workspace collided with its own `tasks/`, `tools/`, `AGENTS.md`; the Watermark Remover
project ran Team Mode for two days with four tools and surfaced template defects (gate parsing the whole Task File,
undetected Claude session limits, Store-packaged pwsh not passing the environment, the Python Store stub, QuickEdit
pausing workers, manual multi-step acceptance going wrong) and missing guidance (Devin, Antigravity print mode, Codex
desktop-app path, limit-aware routing, merge-only successors, re-tests reusing evidence).
Decided: move everything into `.agentflow/` (the layout Watermark Remover adapted by hand), add `install.py` (marked
blocks, no deletion, dry run) and `accept.py` (stop at the first failure), and fold the fixes into the protocol, roles
and tools. Rejected: keeping the root layout (collisions); rewriting existing entry files (loses project rules);
supporting multi-repo workspaces now (tools assume one repository; recorded as a known limit).

## 2026-10-08: 2.3.0 - workspace mode

Why: the human's AIHomeDesign workspace holds five repositories and is not a repository itself; the human asked for
both a shared mode and the per-repository install. Decided: the workspace root becomes a memory repository that
tracks only AgentFlow files (default-ignore everything else, product repositories ignored); `workspace.json` lists the
repositories; tasks name them in `Repo:`; paths are workspace-relative so Checks read the same in the root and in a
task folder; acceptance does a trial merge everywhere first. Rejected: memory without git (no history, no dashboard);
git submodules (they change the product repositories); per-repository memory copies (two sources of truth).

## 2026-10-08: 2.4.0 - per-task model and TypeSafe routing

Why: the human pays for several tools with different free windows (Devin SWE-2 free until 2026-10-16, unused Codex
capacity) and asked to use TypeSafe AI to pick the model per task. Decided: a `Model:` line per task turned into tool
flags by the launcher; the project lists its options and a policy in `model-options.json`; `route.py` asks Jev one
choice question and only advises (threshold, exit 3 otherwise; `--apply` only before launch). Rejected: letting the
service choose silently at launch (the Orchestrator must see and own the choice); storing the key in the repository.

## 2026-10-08: 2.5.0 - TypeSafe by its official documentation (human)

The human asked to use the official TypeSafe documentation whenever TypeSafe is used. The 2.4 integration had been
built from the API reference, one primitive page and a third-party summary, and differed from the docs (text state,
one broad question, one 0.5 threshold, `jev-latest`, a proxy's variable name). Rebuilt to the docs and recorded the
rules and links in the template-owned `docs/typesafe.md` so every project and session follows them. Rejected: keeping
the single broad question (the docs ask for decomposition into atomic questions combined in code).


## 2026-10-08: 2.6.0 - Orchestration survives the Orchestrator session (human)

Claude Code sessions often end on a usage limit while every other tool still has capacity, and the whole project
stops. The human chose: a background Orchestrator acts only within the approved plan; notifications through Windows;
fallback order Codex, Devin, Antigravity. Built `tick.py` (mechanical steps without a language model, one-holder
heartbeat, remembered tool limits, next free orchestrator tool) and the protocol section with the limits of a
background session and `questions.md`. Rejected: a background session that may extend scope or decide for the human;
two Orchestrators acting at once.

## 2026-10-08: 2.7.0 - The conductor starts background Orchestrator sessions (human)

The human explicitly allowed a watcher that starts background Orchestrator sessions with full access by itself
(Claude Code's safety classifier had refused to write it without that permission). `conductor.ps1` is started and
closed by the human, uses the developer command lines of `run-task.ps1`, and stays inside the 2.6.0 limits: one holder
at a time, the approved plan only, questions to `questions.md`. Rejected: a hidden background process (the window is
how the human sees and stops it); retrying the same needs every round (cooldown, except after a usage limit).

## 2026-10-08: 2.8.0 - Conductor at logon, one instance, a panel and a shortcut (human)

The conductor cannot be started by an Orchestrator that has already hit its limit, so it must run before that. The
human chose autostart at logon through Task Scheduler with a guard against a second instance, a check in the
Orchestrator role, and a visible reminder: a desktop shortcut to a panel that shows and controls it. Rejected: a
Claude Code session-start hook (starts a conductor per session, depends on Claude); a hidden background service (the
human would forget it exists).

## 2026-10-08: 2.9.0 - Planned tasks wait for the human's approval (human)

In Watermark Remover the Orchestrator added two planned tasks as `ready` while the conductor ran; the conductor launches
every `ready` task whose tool is free, so they would have started before the human approved the plan. The human asked
to fix it in the template as a priority. Approval is now state, not memory: `ledger.py add` defaults to `blocked` with
`awaiting approval`, preflight refuses such a task, `ledger.py approve` releases it. Rejected: a separate status (every
tool and the dashboard know the current ones); relying on the heartbeat alone (it goes stale while the human thinks).

## 2026-10-09: 2.9.1 - End check ignores trailing blank lines; -Recheck

In Watermark Remover, Devin finished T-033 with a correct Result, but the attempt became `error`: the Task File had no
`## Result` heading and Devin appended it after an empty line, which changed the hashed header by one trailing newline.
Fixed in the hash (trailing whitespace is not content) and added `-Recheck` so such an attempt is not redone. Rejected:
editing the runtime state by hand (only the launcher writes it); a new attempt (an hour of work repeated for a formality).

## 2026-10-09: 2.9.2 - Result in the worktree copy is an end-check failure

In Watermark Remover, Devin (T-034) wrote its Result into the Task File copy inside its worktree and committed it; the
attempt ended `exited`, and only acceptance would have found an empty Result and a branch past `Change`. The end check
now reports both with the recovery steps, and the worker prompt names the exact file. Rejected: reading the Result from
the worktree copy (two sources of truth; memory would merge through a product branch).

## 2026-10-09: 2.10.0 - Per-tool parallel limit (project rule)

In Watermark Remover two Codex testers ran at once on Windows; their sandboxes kept rewriting the logon of the shared
sandbox account, Windows locked it and the user's own account (lockout policy, error 1909), and both testers lost
their environment. Parallelism is a machine fact, so it is a project Preflight rule `- parallel: <tool>=<n>`, checked
at every launch (also by tick.py and the conductor, which wait for a free slot). The default project rules ship
`codex=1`. Rejected: a global AgentFlow constant (other machines and tools differ).

## 2026-10-10: 2.11.0 - Shared machine capacity, effort routing, upstream sync (human)

Running two AgentFlow projects on one machine showed three gaps. Each project thought a Codex slot was free on its
own; `machine_capacity.py` now keeps an OS-locked lease registry shared per OS account (tool slots, worker PORTs,
limit reset times; pending-claim handoff and dead-PID cleanup). Jev routing picked a tool but not how hard it should
think; a third question plus `efforts`/`model_by_effort` maps a generic tier to the concrete CLI value. And
improvements made inside a project never flowed back to the template: `upstream.py` reports drift in both
directions, `template-source.json` remembers where an install came from, the conductor checks once a day, and a
change is generalized before it enters the template. Rejected: a central service (an OS file lock is enough at this
scale); auto-merging project diffs upstream (generalization is a judgment — the human reviews candidates).

## 2026-10-10: Consolidate instruction ownership (2.11.1)

Human-approved cleanup: platform-independent workflow and communication live in
the protocol; project-owned files hold parameters and engineering constraints.
Root entry points link to role-specific startup. Main-branch naming and ordinary
Orchestrator branches are explicit; historical installation data is not current policy.
The Codex global file holds personal defaults and points AgentFlow projects to their
installed rules. Task evidence and acceptance safeguards remain mandatory.

## 2026-10-10: Adopt structured explanation guidelines (2.11.2)

The human chose to make the reviewed explanation style part of AgentFlow rather than
one tool's global configuration. Communication leads with the conclusion, keeps terms
stable, defines new terms plainly, numbers procedures, and may diagram processes with
more than three parts. Suggested sentence lengths remain soft guidance because strict
limits can damage accuracy. Explicit HTML explanations are delivered as one
self-contained interactive file. Rejected: copying these rules into entry points or
making word counts mandatory.

## 2026-10-10: Launcher reliability

The human authorized lifecycle infrastructure repairs. Version 2.11.3 makes launcher issuance authoritative, omits empty live argv, audits unique commits and merge resolutions, and refuses invalid acceptance states before side effects. Failed handoffs remain issued with an error attempt for explicit recovery.

## 2026-10-12: Observe shared scheduling before changing launches (2.11.5)

Multiple installed projects need fair access to shared CLI capacity, and Jev routing must consider available platforms and primary/backup models. First add a cross-project dispatcher in observation mode: it reads each project's existing dry-run tick, simulates round-robin allocation with the machine registry, and records no grants or worker launches. Keep the current launcher and acceptance gates intact while the observation output is verified. Activation, Jev changes, routing statistics, and rollout to installations follow as separate tested stages.

## 2026-10-12: Keep primary and backup Jev choices (2.11.6)

Jev's choice probabilities provide a ranking among configured model options. Save the selected primary and the highest-ranked eligible option on another CLI platform as backup. Exclude a missing CLI or observed shared usage limit before the Jev call, but keep busy platforms in the ranking so the saved backup can be used when a slot is occupied. Tick changes only an unstarted ready Task File and ledger when the backup flag is enabled; account and model entitlement remain launch-time facts. Keep the flag off by default while the pilot validates routing evidence.

## 2026-10-12: Opt-in cross-project slot grants (2.11.7)

The shared registry owns short-lived ready registrations and grants, not task content. In active mode each project conductor registers its ready work, and the next eligible project in round-robin order receives a grant under the registry lock. The launcher atomically exchanges that grant for its usual lease, so the existing task gate and worker lifecycle remain authoritative. Keep active mode off by default until participating installations have been updated; old versions ignore grants. Rejected: a separate always-running dispatcher process, which adds another service and handover failure point on this single machine.

## 2026-10-12: Measure routing outcomes without claiming causal proof (2.11.8)

Jev needs feedback across comparable tasks. Record the eligible candidate list and provide a read-only report of recommendation, actual platform, backup use, attempts, acceptance, and elapsed attempt time, grouped by role and measured complexity. Planning receives an optional Jev recommendation independent of the user's chat model. Do not invent worker token use or cost, and do not label a one-task outcome as model-selection accuracy. A full goal text is not persisted in the planning route log; a hash and request ID are enough to correlate diagnostics.

## 2026-10-11: Unlink setup junctions before checkout removal (2.11.4)

A `Setup: - link:` line makes the launcher place a junction inside the checkout that points at the main
folder's copy. `git worktree remove` and a recursive PowerShell delete follow the junction and delete the
target's contents; installed projects repeatedly lost the main folder's `node_modules` this way whenever a
tester checkout was re-created or an accepted developer worktree was removed. The launcher and `accept.py`
now delete the reparse point itself before removing a checkout, which leaves the target untouched. Rejected:
copying instead of linking (wasteful per checkout) and documenting manual care (the failure kept recurring).

2026-10-15: Human explicitly confirms AgentFlow is an independently maintained project at vcherstar/AgentFlow. Source-authority rule belongs to this local template repository, not TuScript. Added mandatory rule in root AGENTS.md outside template-owned block: version/update authority is own origin and local development; parent/upstream repository requires explicit per-task request. Do not conflate parent's releases with this project's version. No remote changes or push.

2026-10-17: Human explicitly authorized pushing the completed local release preparation to Git. This supersedes the earlier human-only push restriction for origin/main; it does not authorize tagging, publication, deployment or changing remotes. Remote CI/macOS evidence remains required before public release.

2026-10-17: Human authorized sequential Stages 3-5 and documentation alignment; designated Devin swe-2-high coordinator/default workers with task assessment and fresh concrete agy Gemini/Claude/GPT resource checks before stronger routing. Task decomposition and execution approved within scope; details in project-rules.md.
2026-10-17: Human explicitly restricted further work to AgentFlow. WatermarkRemover must remain unchanged: no rollback of prior update and no further rollout. Supersedes prior pilot-update authorization. Validate installation/migration in disposable AgentFlow fixtures; external rollout remains out of scope.

2026-10-18: Human approved all three roadmap mockups: A (cards), B (journey), C (matrix). Implement a view selector to switch between all three. This resolves the single-variant selection gate for T-044/T-046/T-048; preserve implementation dependencies. Other layout details remain as in the mockups unless separately decided.

## 2026-10-18: Human prefers Devin through the reported unlimited window

Human explicitly prefers Devin for development, testing and orchestration and
reports no usage limits until 2026-11-01 (exact cutoff not supplied). Record
this as qualitative human-provided availability, never a fabricated measured
balance. Independent tests use fresh Devin sessions and exact-SHA checkouts;
this supersedes the generic other-CLI preference, not independence. Mandatory
Jev adequacy, model probes, wall-clock caps and actual provider holds remain.
T-074 is already running on Devin swe-2-high; conductor uses Devin swe-2-high.

## 2026-10-18: Combined urgent recovery accepted and queue resumed

T-080 c7cc37b was independently passed by T-081, then verified, checked on the
trial-merge result and merged as b40c934 (2.15.1). Full suite 372/0/3-skipped;
independent checks 8+14+49 and a real Windows execution-state acquire/release
probe. A new-main 372-test suite passed as well. T-072 was consolidated after
its actual 361-test green output; its gratuitous third full run was stopped,
not allowed to spend another budget. Exact source patches/evidence retained.

The developer used the old Result example; coordinator appended explicit
criterion prefixes before T-081 launch, copying the stated outcomes without
changing code/evidence or manufacturing acceptance. Gate evaluate then had
only the independent-review condition outstanding; independent review and both
acceptance stages subsequently passed. Temporary project rules and unstarted
contracts now use explicit colon/verdict lines; T-036 aligns the old examples.

T-074 final assessment req_01a14d94e7eb7c6db849d72843d5e45a selected swe-2-high
with medium confidence 0.66. Coordinator confirmed the bounded inherited-core
fit/floor match; selected-model probe passed at launch. T-074 now runs with
a recorded 1200s deadline and its own sleep request. Conductor restarted hidden
with one-minute rounds and Devin coordinator; no scheduled-task registration
or global power configuration was changed. Temporary maintenance helper
removed only after confirming the managed worker's own request was active.
