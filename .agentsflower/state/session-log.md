# Session Log

## 2026-10-17: Accept runtime baseline and enable the rest of the pool

T-022 and independent T-023 passed 158 full-suite tests plus focused checks;
accept.py verified, merged and cleaned T-022 (main 2.11.11). T-009 produced correct
CI files/152-test developer pass, but old-branch acceptance failed an intermittent
test_route case; preserved and rejected to T-026 integration after runtime repair.
Queue dependencies updated. No test or release gate waived. Prepared a complete
handoff for Devin background continuation to conserve Codex; root will release
writer ownership before starting the coordinator. No push or publication.

## 2026-10-17: Resume the full approved release queue

Read current repository: background Devin had completed T-020/T-021 and merged
2.11.9 Linux fixes. Human now explicitly authorizes all remaining pool tasks.
Created/approved CI, reliability, package CLI, MCP, English metrics and final docs
contracts with serialized shared metadata. Cancelled obsolete T-018 placeholder.
Live pre-start check reproduced Devin untrusted-temp-cwd refusal. T-024 repaired
only built-in probe argv using narrow native Manual adapter; T-025 independently
passed 27 focused, 152 full and a real Devin probe after harness-only recovery.
accept.py verified and merged bootstrap to 2.11.10; no source/code changes by the
Orchestrator. Started ordinary Devin T-022 and T-009 after real inference checks.
No push/publication. Current queue and actual evidence references are in ledger.

Checkpoint validation after all workers exited: main 2.11.8 full suite ran
124 tests, one WinError 5 error in test_tick via machine_capacity._locked/os.replace.
Recorded as recurring baseline registry reliability issue. Product candidate
1e0bd87 independently passed 151 tests in T-017; no product merge performed.

## 2026-10-16: Linux defect repair merged via Docker evidence (background devin)

Decided T-019's fail Verdict: T-016 stays rejected; T-019 verified and done.
Created successor T-020 (developer, devin): ported 1e0bd87 onto main and repaired
the three T-019 defects - run_logged tool spawn now leads its own POSIX session
(no killpg self-kill), kill_tree signals the tree's process groups via /proc
with ps fallback, accept.py drops `merge-tree --quiet` (git 2.47), test_endcheck
merge fixture carries git identity. Commit bafc2a0. T-021 (tester, devin -
Codex conserved per human routing, agy/claude limited) independently re-ran the
Docker Linux gate on the exact SHA: 151 tests, 0 failed, 18 Windows-only skips;
Verdict pass. Windows verbatim suite hit the known registry os.replace WinError 5
flake twice (different tests, green standalone) - reported, not T-020's code.
T-020 accepted and merged to main (eb59c7c). T-018 stays blocked: its question
now reduces to the macOS route (questions.md). No push or release.

## 2026-10-16: Complete local launcher hardening; hold real Unix gate

T-015 found concrete defects despite 149 tests: accepted the failing review,
rejected T-014 to T-016. T-016 on Devin medium produced exact SHA
1e0bd876a4c3247416f6ccc3dd9c89970a36d695; developer 151 tests green twice.
T-017 separately repeated probes/secret/timeout/routing checks and full suite:
151/0/0, all local criteria pass, overall unverified only for actual Linux/macOS.
Accepted T-017 as a completed review via accept.py; no code merge. T-016 rejected
to prepared blocked T-018 under the protocol's non-pass successor rule. All worker
processes exited, no new worker launched. Human question asks Unix hosts vs CI
branch for human push. Conductor env-file risk logged separately. No push/release.

## 2026-10-16: Launcher recovery and independent review completed

T-012 attempt 1 Devin high copied port but made no repairs; stopped safely.
Attempt 2 agy Opus read sources then quota failure; Sonnet/GPT-OSS also exhausted.
Attempt 3 Devin medium completed 87de72c, 147 tests green. T-013 on separate Devin
high session repeated 147 tests green and verified Windows timeout/noninteractive
behavior; unverified for actual Unix. Accepted review via accept.py, rejected
artifact to T-014 because required selected-model inference preflight is still
missing. Prepared T-014 but did not launch; awaiting human Unix/CI verification
route. No product commit merged and no push. Evidence in T-013.evidence runtime.

## 2026-10-16: Recover agy interactive hang

Observed T-002 process alive for 15h with no Result/log; stopped using launcher.
Human authorized execution. Prepared T-012 successor for Python port plus bounded
noninteractive agy review, rejected T-001 with preserved artifact, cancelled T-002.

## 2026-10-15: Launch T-001 via Devin

Human authorized launch of T-001 on Devin (swe-2-high) and confirmed that external
projects do not block AgentFlow template work. Template rollout into client projects
will occur only after AgentFlow changes and tests are complete. Ledger T-001 set to
ready, then launched via launcher.

## 2026-10-15: Prefer Devin for release work

Human changed resource routing. Queried Devin/agy model catalogs, assigned
T-001 to Devin swe-2-high and proposed agy gemini-3.8-flash-high for T-002.
No inference probes or workers launched; model access/quotas are not inferred
from catalog listings.

## 2026-10-15: Public release planning

Read the production roadmap and implementation. Human approved T-001 through
T-011 and scope decisions recorded in decisions.md. Prepared only T-001; no
workers launched. CLI executables found for Claude, Codex, Devin and agy; model
access and quotas remain unknown. Added mandatory pre-start resource checks.

Chronological log of work on the AgentFlow template.

## 2026-05-21

- Base AI Project Memory: protocol, handoff, current-step, decisions, known-issues, session-log.

## 2026-10-01

- Team layer: roles, Task Files, Task Ledger, `/start-role`, protocol sections "Roles and memory ownership", "Starting a role session", "Task lifecycle", "Planning levels", "Git rules", `AGENTS.md`, `roles/tool-routing.md`.

## 2026-10-02

- Launcher and ledger defects from migrating a live project fixed; preflight, `## Checks`, production opt-in added.

## 2026-10-03

- FPF audit of all files; refactor to 2.0.0 in five commits: P0 enforcement, P1 state and evidence, P2 rule order and contradictions, P3 template vs project, P4 English machine-facing text. Details: `CHANGELOG.md`, `state/decisions.md`.

## 2026-10-07: 2.2.0

- Moved the template into `.agentflow/` with `git mv`; ported the Watermark Remover adaptation (`paths.py`, relocated
  paths, dashboard history and links, layout tests) and its fixes; added `install.py`, `accept.py`, VERSION, tests.
- Protocol, roles, tool routing, Task File template, README, GUIDE, CHANGELOG updated. 19 tests pass.


## 2026-10-10: Launcher reliability

Implemented 2.11.3 launcher, end-check and acceptance repairs with regression tests in disposable repositories; deployment to the pilot follows the installer workflow.

Final validation: 105/105 tests pass (including PowerShell 5.1/7 and fake-worker
tick launch). Pilot full suite: 105/105; focused lifecycle rerun: 7/7. Pilot
update committed as 66deac8 on master; no template drift or product changes.
Conductor restarted hidden and reports zero needs/waits, with autostart enabled.
A test-only temporary-directory cleanup race was fixed by waiting for worker exit.

## 2026-10-12: Shared resource scheduling and Jev evidence

- Completed and merged the prepared 2.11.4 junction-cleanup release separately. Its 107 tests passed with the legacy Codex machine limit fixed at 1 for that historical test run.
- Released 2.11.5 dispatcher observation, 2.11.6 Jev primary/backup routing, 2.11.7 opt-in shared grants, and 2.11.8 planning advice and read-only routing reports. The final template suite passed 124 tests, including real PowerShell grant-to-lease launch with a fake worker; no real worker model was called by tests.
- Installed 2.11.8 in Transcript Youtube (master@e6c088d) and Watermark Remover (master@c512c70); each installation passed 124 tests. Upstream drift is clean for both. Transcript's real Jev planning probe returned a medium-confidence recommendation with request ID; the machine remains in dispatcher `shadow` mode and backup auto-switching is off.
- Gemini to Word remains at 2.11.3 with manual tester T-009 running and uncommitted template-owned `accept.py`/`run-task.ps1`; do not update it or activate shared grants until that work is resolved. No push or production deployment was made.

2026-10-15: Human corrected rule ownership: AgentFlow repository, not TuScript. Root AGENTS.md now pins source authority to vcherstar/AgentFlow; decisions record instruction. Misplaced TuScript rule reverted in its own history. Required precommit unittest run: 124 tests, errors=2 in test_launcher_lifecycle.test_dispatch_grant_becomes_worker_lease due PermissionError/WinError32 on temporary runtime file and teardown directory held by process. Documentation-only change; no framework code changed, no claim of green suite. Existing untracked nul untouched.

2026-10-17 (devin-background): T-003 developer completed at 1849b2bf. Wrote Tester contract T-004-verify-package-cli.md (Verifies T-003 @ 1849b2bf, tool devin, swe-2-medium), ledger ready, attempt 1 launched (log .agentflow/tasks/.runtime/T-004.1.log). Initially misfiled as T-027; cancelled unused and recreated under the reserved ID T-004.

2026-10-17 (devin-background): T-005 developer completed at 1665318 (optional MCP server, installer --mcp/--mcp-client, VERSION 2.11.13, CI mcp job). Wrote Tester contract T-006-verify-mcp-server.md (Verifies T-005 @ 1665318, tool devin, swe-2-medium), ledger ready, attempt 1 launched (log .agentflow/tasks/.runtime/T-006.1.log).

## 2026-10-17: T-010 result in, T-011 final local review launched

T-010 developer completed at 0fcd773 (English GUIDE, README, RELEASE_NOTES,
real T-008 dashboard.png, 2.12.0 metadata sync; 204 tests + check_package pass).
Orchestrator wrote the reserved T-011 Task File (tester, devin, swe-2-medium),
ledger ready, attempt 1 launched. Verdict pass -> tick auto-accepts T-010. Any
other verdict -> Orchestrator decides; remote CI/macOS push remains the human's
separate release gate.

2026-10-17: Foreground Orchestrator confirmed all approved Stage 6 contracts terminal, T-011 pass at 0fcd773 (204 tests OK, 3 skipped, package integration passed). Updated stale continuation memory and T-010 note. Human explicitly authorized origin/main push; tag/release remain separate. Final regression rerun before checkpoint commit.
Final pre-push regression on 2026-10-17: 204 tests in 138.107s, OK (3 skipped); git diff --check passed.

2026-10-17: Prepared handover for human-delegated Devin swe-2-high foreground orchestration of sequential Stages 3-5. Built-in bounded selected-model inference passed; agy family resource probes pending. Local v2.12.0 scope already accepted; no new publication authorization.
Fresh bounded checks: Devin swe-2-high inference OK; agy Gemini Flash inference OK, remaining quota unknown; agy Sonnet/Opus/GPT-OSS denied RESOURCE_EXHAUSTED. Existing tool-wide agy limit must not be bypassed; evaluate scoped repair if needed.

## 2026-10-17: Foreground orchestration - handover checkpoint, CI triage, Stage 4 cycle, Stage 5 launched (devin swe-2-high)

Claimed heartbeat as devin. Committed pending handover memory on
chore/memory-handover-2026-10-17 after a 204-test green suite, merged to main
(5f613e8). Configured continuation: user env AGENTFLOW_ORCHESTRATORS=devin,
AGENTFLOW_DEVIN_ARGS=--model swe-2-high, probe opt-ins and WORKER_TIMEOUT=2400
persisted; conductor restarted with no active writers (all attempts exited);
next-orchestrator resolves devin.
CI run 39026298541 triaged: ubuntu tests and both package jobs pass; all
windows-latest and macos-latest test jobs fail at the unittest step; logs not
publicly readable; recorded in known-issues.
Stage 3 evidence verified: pilot at 2.11.8 via install.py --update
(template-source.json), 49-ledger task cycle (37 done / 12 rejected), findings
recorded.
Stage 4 bounded cycle: upstream.py --check over all machine-registry projects -
all at 2.11.8 behind 2.12.0 (version lag only) except one real upstream
candidate set in Transcript Youtube site\code (tools/limit_detection.py,
tools/quota_groups.py + tests; folded into T-030). Pilot rollout: installer
dry-run clean (42 actions); applied install.py --update to WatermarkRemover
2.11.8 -> 2.12.0, deleted stale plaintext env handover files per 2.11.11
migration, kept launch.ps1/settings.local.json untracked, decisions entry added,
committed master@3fa1efb; installed suite 204 pass (3 skipped); conductor was
not running and was not restarted.
Stage 5 decomposed into six serialized developer contracts (T-028 lifecycle
trust -> T-030 recovery + upstream generalization -> T-032 completion gate ->
T-034 bounded autonomy -> T-036 instructions/docs alignment -> T-038 evaluation/
migration/release record), each with an independent tester contract written at
result time. Approved under the dated human authorization. T-028 attempt 1
launched on devin swe-2-high. No push, tag, publication or deployment.

## 2026-10-17: New mandatory routing policy imported; pool extended to dashboard

Human delivered required-routing-policy-2026-10-17.md + dashboard PLAN/
DEVELOPER-CONTRACT/TESTER-CONTRACT drafts and ordered them queued and executed.
Session resumed with T-028 still running (verified launcher pid 23604 + devin
child, attempt alive; worker had committed 2c58157 and was writing its Result).
Created project-owned docs/model-options.json (floor swe-2-high, Devin-first,
group-scoped agy holds); key-file validated by existence; live Jev calls
succeeded. Assessed all pending tasks via route.py and set headers to assessed
adequate models (swe-2-max for T-030/32/34/36/40/44; swe-2-high for
T-038/42/46/48). Imported durable requirements into project-rules.md and
decisions.md. Created/approved T-040 (routing enforcement, depends T-034;
T-036 re-pointed to T-040) and T-042 (mockup, independent), T-044/T-046/T-048
(dashboard data/UI/integration, serialized after T-038 + mockup selection).
Launched T-042 attempt 1 on devin (pid 68712). AGENTFLOW_DEVIN_ARGS verified
non-downgrading for declared task models; no process override clearing needed.
2026-10-17: Recorded AgentFlow-only scope and no WatermarkRemover rollback. Restarted only foreground Devin coordinator to deliver the boundary; preserved active Tester T-053 and worker artifacts.

## 2026-10-18: Urgent standby/worker-control diagnosis and bounded recovery

Human requested diagnosis and correction of stalled T-040, then forward queue
progress. Windows System events confirm idle standby 04:49:19-07:45:24 Moscow;
read-only Devin session records identify the background coordinator as the
07:48 --stop caller. Separately reproduced invalid/zero worker-timeout values
falling through to a 4h task budget. Conductor had no external deadline check
while a background coordinator was alive. Conductor/coordinator stopped for
controlled repair, drafts preserved, scoped temporary system-execution request
held without power-plan/display changes.

T-072 draft passed 11 focused tests and a 361-test full suite (3 skipped).
Its first 15m attempt cap interrupted a full suite; same native session was
resumed. A redundant third whole-suite run after green was stopped, and the
draft consolidated into T-080 rather than repeating acceptance/release loops.
Exact patch, new test file, green actual tool output and hashes are in ignored
runtime storage. Baseline main passed 350 tests / 0 failures / 3 skipped.

T-080 adds process-scoped idle-sleep guard, deadline watchdog, locked external
stops, bounded kill waits, honest CLI stop attribution and fixes a test fixture
that mistook its parent worker markers for a nested launch. It is now running
the final full suite. Human explicitly approved conservative swe-2-max for
repairs and their independent testers despite low effort confidence; original
Jev records remain unchanged. T-040 is cancelled with all drafts preserved;
bounded successors T-074 -> T-076 -> T-078 precede T-036 -> T-038. Stage plan
labels reconciled: Stage 4 bounded cycle closed with external rollout deferred,
Stage 5 current. Concurrent questions.md changes preserved and excluded.

Completion: T-080 accepted/merged as b40c934 (2.15.1), T-081 done/pass; 372
full tests (3 skipped), 71 scoped independent tests/live Windows probe and
standard verify/integration passed. Main regression repeated before the memory
checkpoint: 372/0/3-skipped. T-074 launched at 06:02:30Z on Devin swe-2-high
with recorded 1200s deadline and actual sleep-request log. Conductor restarted
hidden at one-minute rounds, Devin coordinator; temporary helper removed.
Human's latest Devin preference/unlimited-until-November report persisted with
provenance and actual-hold/adequacy safeguards. Foreign questions.md preserved.

2026-10-18 background orchestrator (devin-background): T-074 developer attempt exited completed at 5a6510c (R-01..R-05 all claimed pass; focused 12+19 and full 391 tests green per its Result). Ledger: T-074 -> review. Wrote tester task T-075 (exact-SHA verify of R-01..R-05), added ready, ran mandatory route.py: persisted assessment req_01a14dab3ab875c5b09fa66a87ab71ed is low confidence 0.48 demanding gpt-6-astra xhigh (complexity 1.97/2); per mandatory routing policy launch blocked pending explicit human exception. T-075 -> blocked; question with options (devin gpt-6-astra-xhigh / scoped swe-2-max exception / codex / re-assess) appended to state/questions.md. Worker's proposed decisions.md update left pending - background orchestrator may not write decisions.md. Chain T-076->T-078->T-036->T-038 and T-066 wait on T-074 acceptance.

## 2026-10-18 - Background devin orchestration: routing chain landed on main

- T-075 (tester, devin swe-2-max per human Option B) verified T-074 @ 5a6510c:
  Verdict partial - backup_ok ignored live quota-group holds at call time.
  Mechanical Result normalization first (evidence-marker placement + T-075.*
  basename prefixes; T-080-prefix precedent), then verify+accepted.
- T-074 rejected -> T-082 repaired backup_ok at fc2c37c (live
  machine_capacity.limit_until consult for tool+quota_group) -> T-083
  deep-verified PASS -> T-082 rejected for an Orchestrator scope-authoring
  defect (inherited base missing from Allowed files) -> T-084 carrier under
  corrected contract -> T-085 fast-path PASS -> T-084 merged at fc2c37c.
- T-076 launch-admission integration: attempt 1 timed out after a heavy
  survey (10-file draft preserved); attempt 2 resumed and completed
  07fbeed (398/0/3). T-086 tester verdict FAIL (D-01: codex
  --config effort alias bypassed env_selected). T-087 repaired at f6bc519
  (alias spellings parsed) -> T-088 verdict FAIL (F-01: repeated config
  keys first-vs-last wins; new cross-tool --config parsing hazard).
  T-089 repaired at 52b06aa (last-wins + codex-only scoping) -> T-090
  PASS (19 probes, negative control, argv parity; one disclosed flake).
  T-089 merged into main at 52b06aa = the combined T-076 line (2.15.3).
- T-076/T-087 rejected branches/worktrees kept as preserved drafts for the
  human's cleanup decision. test_plan_route.py env-dependence and
  ledger.py WinError 5 recorded in known-issues as latent follow-ups.
- T-078 (scheduler/report integration) ready and assessed (swe-2-high):
  first launch refused on machine capacity - sibling project
  E:/Projects/AgentFlow/site holds the 2nd devin slot (its own T-001
  worker, cap 2). Launch waits for a free slot; retry on later ticks.

- T-078 launched on the freed slot: decide()/use_backup() admission gates +
  route_report metadata landed at 0ba5d37 (2.15.4) but rejected on its own
  honest partials (S-05 route.py preferred-CLI exclusion, S-03 suite never
  recorded). T-091 closed both at 0bf4ac0 (prefer-scoped exemption, fixture
  repairs the base owed the suite, 424 tests green) - tester T-092 blocked:
  the new admission gate itself refuses the low-confidence (0.34)
  assessment; human Routing exception decision pending in questions.md.

- 2026-10-18 foreground devin (human-facing): human resolved the T-092
  routing question with Option D (re-scope to fast-path re-check, T-085
  precedent, no exception header) and reported Codex+Claude CLIs out of
  resources - statically excluded via "until" 2026-10-17 in
  docs/model-options.json (devin-hosted families unaffected). Recorded in
  questions.md/current-step.md/decisions.md and committed 20ca4aa.
  Human then explicitly requested a push: origin/main 50adf65..20ca4aa.
  GitHub reports the repository moved/renamed to
  https://github.com/vcherstar/agentflow.git (old URL still redirects;
  remote not re-pointed - remote changes stay human-authorized). The push
  triggers the pending multi-OS CI rerun; windows/macos log access still
  needs the human (API 403) or authenticated gh.

- 2026-10-18 foreground devin (orchestrator acting): T-092 contract rewritten
  to a fast-path re-check (T-085 precedent) per the human's Option D; fresh
  route.py assessment req_01a150e72dd47e2796b8e12c907f730c on the new
  contract selected devin swe-2-high (option conf 0.95, overall medium 0.60 -
  orchestrator-confirmed floor fit), all codex/claude options recorded as
  excluded. Ledger T-092 -> ready; header applied. Launch refused at the
  fail-closed selected-model inference probe: the devin CLI is not
  authenticated ("Not logged in"; `auth status` exits 0 vacuously - the
  inference probe caught it). Recovery: human runs `devin auth login`, then
  re-run run-task.ps1 T-092 devin; assessment stays valid while the contract
  is unchanged. This also blocks every future devin launch until fixed.

- 2026-10-18 background devin (devin-background): T-092 manual tester attempt
  (human-facing session) exited completed; verify PASS, accepted - verdict
  FAIL is a correct tester result (V-03). T-091 rejected -> T-093: the
  artifact at 0bf4ac0 carries a deterministic time bomb -
  test_routing_scheduler.py AT constant leaves the recorded "live" hold
  expired after 13:00Z. T-093 successor (fixed-clock repair on the 0bf4ac0
  base) created, assessed ok (req_01a150e, swe-2-high floor) and launched
  -Manual by the human's session; attempt running. T-036/T-066 Depends on
  repointed T-091 -> T-093 so the approved chain survives the rejection.
  devin CLI is authenticated again (`devin auth status`: logged in) - the
  earlier launch block is resolved.

## 2026-10-20: Jev-led model selection + Devin Argon pool (2.15.5)

Human instruction (in this chat): update the Devin model pool, record
recommended options per assessed tier, and let Jev's values drive the
model/effort decision while platform availability stays honored. Single Mode
change on branch chore/jev-recommended-routing, merged to main 890ff21:
devin-gemini-4-argon (low/medium/high, 1M context, devin group) added capped
at <= high requirements; new `recommended` map (tier -> ordered options)
shown to Jev as recommended_for and applied by admission_order only for
probability ties/unranked candidates; ordering is prefer group -> Jev
probability -> recommended -> name (floor lost its dedicated first rank,
still lifts the requirement). plan_route uses the same ordering; typesafe.md
rule 8 updated; test_routing_core ordering test rewritten; argon assertion
in test_quota_groups replaced with a devin-group resolution check. 409 tests
pass (3 skipped). Pending: human will paste `devin models list` to verify
the concrete model ids (CLI was unauthenticated at change time); 2.15.4 from
the T-093 line lands after this - merge keeps both CHANGELOG sections,
VERSION stays 2.15.5.

## 2026-10-21: T-093 decided; successor T-094 launched (background devin)

Tick need "T-093 developer Outcome missing (attempt error): decide".
Findings: manual attempt 1 was --stop'ed at 07:44Z with no Result and no
draft; a managed attempt 2 (launched 07:48:32Z, most likely human-side)
raced the review and committed the contract repair 0b82f61 (2-line hold fix
on base 0bf4ac0) before being stopped; the worktree was deleted during the
overlap and the ledger row was already rejected (final), so the Result path
closed. Preserved 0b82f61 on branch t-093-fixed-clock-test-repair. Successor
T-094 authored with the identical contract plus a carry note, assessed ok
(Jev req_01a15d7, devin-swe-2 swe-2-high, medium band), launched as managed
devin attempt 1 (pid 64840, deadline ~08:3xZ). T-036/T-066 Depends on moved
to T-094 in ledger and Task File headers (headers still read T-091 - the
2026-10-18 repoint had touched the ledger only; preflight reads headers).
Recorded gate.py endcheck crash-on-deleted-worktree defect in known-issues.
Note for the human: the T-093 attempt-2 launch was not mine - if it was
yours, the concurrent launch raced the rejection; the fix commit survived
and is being carried forward.

## 2026-10-21 (2): T-094 verify-fail is an Orchestrator authoring defect; carrier T-095 launched

Background session devin (devin-background). tick need: T-094 accept stopped at
`gate.py verify` - five inherited-base files flagged "outside Allowed files".
Root cause is the contract, not the product: T-094's `Allowed files` listed
several paths comma-separated per bullet, but gate.py `paths()` keeps only the
first whitespace token of each bullet (a trailing comma breaks the match and
the rest of the line never registers). The artifact at 0477331 on
t-094-fixed-clock-test-repair is complete and green (R-01..R-04, scoped checks
52+11+25, full suite 424/0/3 on that SHA). Per the T-052->T-056 / T-082->T-084
precedent: rejected T-094, authored carrier T-095 with Allowed files one path
per line over the full inherited set. Jev assessed ok (req_01a15d82, band
medium 0.81 after a leaner contract; devin-swe-2 0.95, floor resolves effort
to swe-2-high) - Orchestrator confirmed. Launched managed devin attempt 1
(pid 29976, log .runtime/T-095.1.log). T-036/T-066 still wait on the carrier.

## 2026-10-21 (3): T-095 carrier verified, stale-branch merge successor T-096 launched

Background session devin (devin-background), continued. T-095 carrier completed
in ~3 min: branch reset onto 0477331, scoped checks 52+11+25 green, Result
completed -> `gate.py verify` PASS. `accept.py` then stopped at the trial
merge: VERSION/AGENTS.md/CHANGELOG.md conflict (branch 2.15.4 vs main 2.15.5)
- the anticipated stale-branch case. Rejected T-095 -> T-096 merge-only
successor: branch from main, merge t-095-fixed-clock-carrier, resolution
pinned line-by-line (VERSION/AGENTS block = 2.15.5; CHANGELOG = verbatim
2.15.5 entry then verbatim 2.15.4 entry), full suite required on the merge
SHA (route.py/typesafe.md/test_quota_groups.py auto-merged = changed input).
Jev assessed ok after a leaner contract wording (req_01a15d89a, band medium
0.86; devin-swe-2 0.88, floor resolves effort to swe-2-high) - Orchestrator
confirmed. Launched managed devin attempt 1 (pid 3092, deadline ~08:4xZ, log
.runtime/T-096.1.log). Lesson recorded: comma-separated `Allowed files`
bullets silently fail the scope gate - one path per line (known-issues).

## 2026-10-21 (4): routing stack merged via T-096; T-036/T-066 gated on human routing call

Background session devin (devin-background), final. T-096 merge commit 6754959
accepted and merged (main 8b588f9): the full T-078+T-091+T-094 routing stack is
on main at 2.15.5 with both changelog entries verbatim; verify PASS, integrated
check green, suite 424/0/3 on the merge SHA. Ledger T-096 done; worktree+branch
cleaned. T-036/T-066 `Depends on` repointed T-094 -> T-096 (headers+ledger).
Fresh Jev assessments for both heavy tasks land stable low-confidence
(devin-swe-2 -> swe-2-max selected; effort-xhigh confidence ~0.42-0.45) - the
admission gate refuses, a human `Routing exception:` or re-scope decision is
recorded in questions.md 2026-10-21; both set `blocked`. Whole remaining chain
(T-038->T-044->T-046->T-048, then T-066) waits on that answer.

## 2026-10-21 (5): docs-alignment train landed at 2.15.6; rotation routing committed; T-038 running

Background session devin (devin-background). Executed the human's Option-C
re-scope end to end: wrote T-098/T-099 Task Files, launched/accepted
T-097 (25b8b2e -> T-100 pass), T-098 (38f94f6 -> T-101 pass) and
T-099 (4519a63 -> T-102 pass) - the documentation-alignment train is merged
at VERSION 2.15.6. Two attempts (T-098.1, T-099.1/.2) hit the 2400s wall
clock mid-suite and were resumed on preserved drafts via Resume:<sha> -
worked as designed. One transient WinError-5 os.replace flake seen in
verify (temp fixture, unrelated to the diff). Surgical Result-section fix
on T-100: a quoted `evidence:` marker produced false path claims; reworded,
verdict and evidence unchanged. Committed the human-attended session's
uncommitted rotation work (route.py low-confidence candidate rotation,
AGENTFLOW_BACKUP_ROUTING default on, gate.py paths() comma support,
decisions.md entry) - tests 26/26 green. T-066 re-assessed `ok` (swe-2-max,
medium) and set ready; queued behind the docs chain by file overlap. T-038
repointed Depends T-036 -> T-099 and launched. known-issues annotated:
agy CLI automation note, paths() marked resolved, install.py:269 section
name nit, evidence:-marker quoting rule. decisions.md train entry proposed
by T-098/T-099 workers - left for the human's session (background limit).

## 2026-10-24: T-131 evidence rename repair -> accept; T-130 merged (main 3d89d3c)

Background session devin (devin-background). Opened on one need: T-131 accept
had stopped at `gate.py verify` - evidence files existed under
`.runtime/T-131.evidence/` but lacked the required `T-131.` basename prefix
("belongs to another task"). Mechanical repair per the T-100 surgical-fix
precedent: renamed the three evidence files to `T-131.*` and corrected the
two claimed evidence paths plus one mention in the Result; verdict, criteria
outcomes and evidence content untouched. verify #2/#3 PASS -> accept.py
accepted T-131 (tester, nothing to merge; worktree cleaned). tick then
mechanically accepted T-130 (its tester done): merged to main 3d89d3c,
branch t-130-studio-multiproject-explorer deleted, ledger T-130/T-131 done.
Ledger fully clean - no open tasks. Ran `gate.py stage 7` read-only: FAIL,
seven done rows (T-121, T-123, T-124, T-126..T-129) have no Task File in the
repository - recorded in known-issues and questions.md for the human.

## 2026-10-24: T-134 verified and merged; Stage 7 closed (16 tasks done)

Background session devin (devin-background). Opened on one tick need: T-134
developer completed, tester task required. Wrote T-135 (tester, devin
swe-2-high, `Verifies: T-134 @ f5355b5`), ledger `ready` (tester within the
approved goal), Jev assessment confirmed devin-swe-2 (0.89, medium band;
recorded, not auto-applied). Launched attempt 1; exited `completed`,
`Verdict: pass` (26/26 test_studio, suite 518/1-fail documented
test_run_task fixture flake, served-markup checks, jsdom harness 30/30
interactive assertions; real-browser pixels unverified, recorded). accept.py
accepted T-135 (tester, nothing to merge), then T-134 (verify PASS, merge
db7e22f, worktree+branch cleaned). Ledger fully clean. `gate.py stage 7`
PASS (16 tasks); recorded the human-declared Stage 7 closure (b3b9bd2,
questions.md 2026-10-24) in project-plan.md and current-step.md. Stage 8
remains new scope awaiting human approval.

## 2026-10-24: T-138/T-139 workers running; T-140 serialized on T-139

Background session devin-background. Opened on the tick need "T-138 launch
refused on launch.lock" - already stale: T-138 attempt 1 had launched at
21:52:26Z (devin, pid 25632, deadline 22:32:26Z) seconds after the refusal.
Ledger: T-136/T-137 done. The human had just formalized T-139/T-140 Phase P1
skill contracts (ee71a9c) as `ready` with `Routing exception` headers.
T-139/T-140 share INDEX.md/ATTRIBUTION.md/test_skills.py, so only one may
run: launched T-139 attempt 1 on devin (pid 94900, human-exception
admission) and set T-140 `Depends on: T-139` (ledger note explains) so tick
launches it automatically at T-139 done instead of recording a doomed
overlap refusal. Tick clean: no needs; waits T-138, T-139, T-140(dep).

What waits: T-138 and T-139 outcomes (both `Independent check: tester`).
On each `completed`: write the tester task (devin preferred) and proceed to
acceptance. Committed T-137's pending Result, the T-140 Depends-on edit and
memory.

2026-10-24 ~22:11Z
Background session devin-background. Claimed the heartbeat for the tick
need "T-138 developer completed: write its tester task". T-138 attempt 1
had exited `completed` at 22:08:06Z: Result written, all 5 criteria pass,
Change 4f611e6 on t-138-dynamic-model-quota-hub (test_studio 39/39, full
suite 531/0/4). Wrote T-141 tester task (Verifies: T-138 @ 4f611e6,
devin/swe-2-high per human Devin preference, PORT=8903), ledger row added
`ready`, Jev assessment ok (devin-swe-2 primary, 0.81 medium confirmed,
backup agy-gemini-3.8-flash) and launched attempt 1 on devin (pid 101876);
worker verified review isolation on the Verifies commit.

What waits: T-141 verdict and T-139 outcome. T-141 `pass` -> mechanical
accept of T-141, then T-138 acceptance (gate verify on 4f611e6, merge).
T-139 `completed` -> write its tester task the same way; T-140 stays
`Depends on: T-139`. Committed Task Files, Result and ledger; released.

## 2026-10-24 ~23:50Z - Background orchestrator session (devin-background)

Resolved the tick need (T-139 completed without a tester) and ran the full
downstream chain to a clean ledger:

- Wrote and launched tester T-142 for T-139 @ 914f968 (Jev medium 0.53
  confirmed after one low-confidence re-assessment). Verdict: partial -
  ATTRIBUTION.md taste-skill "Upstream path" held the skill name
  `design-taste-frontend`, not the repo path `skills/taste-skill`.
- Accepted T-142; rejected T-139; successor T-143 (one-cell repair on the
  preserved artifact) verified by T-145 (pass) and merged.
- T-138's tester T-141 came back `pass`; accepted both (T-138 merged).
- T-140 (chrome-extension-mv3) completed with a disclosed contract deviation
  (`michaell/chrome-mv3@main` 404 -> catalog-designated sources, real pins);
  tester T-146 judged the substitution faithful (pass); T-140 merged.
- Human-added T-144 (Studio analytics pixel-perfect) completed; T-147 verified
  it pass end-to-end but flagged that the contract's Allowed files omitted
  `dashboard/common.css`. Accepted T-147, rejected T-144, carrier T-148
  (byte-identical artifact, corrected scope) merged.
- Mechanical normalizations applied twice: T-141/T-147 evidence basenames
  lacking the `T-NNN.` prefix and mid-line `evidence:` markers turned into
  claims (T-075/T-080 precedent).
- Repointed T-140's dependency T-139 -> T-143 after the rejection.
- Recorded worker-proposed known-issues entries (upstream-id authoring rule,
  carrier-defect class third instance).

Ended: ledger fully clean, tick.json no needs/waits. Rejected worktrees and
branches of T-139 and T-144 left for human-agreed cleanup.

2026-10-25 background orchestrator (devin-background), ~00:14-08:40Z: ran the full T-149..T-172 batch to a clean ledger (24 tasks, all done, `gate.py stage 7` PASS at 51 tasks).

- Completed the serial chain T-149->T-166: UI strict cleanup, dynamic platform/model selector, live /api/chat engine, hierarchical thread switcher, multi-research threads + folders + forking, stage-aware pool synthesis + skills mapping, task-level chat + DAG stage-move guard, Jev token/budget estimator, telemetry Cost & ROI dashboard. Then the Model Quota Hub branch T-167->T-172: backend provider engine (OpenRouter, masked secrets, per-project toggles), hub UI reconstruction, end-to-end project model filtering.
- Mechanical gaps fixed in the batch Task Files: missing Setup/Port/Rebuild together/Checks/Result sections added (template-conformant), tester `Verifies: T-xxx @ <SHA>` filled per accepted Change SHA, T-166's ledger row restored after a silent drop from tasks.md (cause unknown - a stale-snapshot rewrite is suspected; worth watching).
- T-154 attempt 1: verdict pass but Result evidence lines failed the gate (bare tokens/selectors as path claims) - re-attempt with `Resume: .runtime/T-154.evidence` rewrote the Result gate-clean, verify PASS. T-156 same class: fixed surgically (renamed evidence files to T-156.* prefix, prose moved ahead of `evidence:` markers; verdicts/evidence unchanged, T-075/T-080/T-100 precedent). Prevention: added an evidence-format hint line to all remaining tester Task Files.
- T-165 attempt 1 hit the 2400s watchdog timeout after implementing everything uncommitted; attempt 2 on the preserved draft finished `completed` in ~7 min.
- T-169 attempt 1 was a dead tool exit (exit 0, ~90s, no Result, clean worktree); attempt 2 completed normally.
- Routing: T-155 and T-163 rolled stable Jev low-confidence (~0.46-0.48) on the effort-tier sub-question only (option confidence 0.97/0.99 for devin). Applied the recorded human standing policy (2026-10-21: evaluate catalog on low confidence; devin swe-2-high is the mandated floor) via `Routing exception:` header lines - logged as human-exception admissions. T-167/T-169/T-171 already carried the human's own exception lines.
- Merges: d72d033 (T-149), 2b8e9f3 (T-151), 46e11c7 (T-153), 772f321 (T-155), 38495f2 (T-157), 9d208969 (T-161), a5889f2 (T-163), 30bd454 (T-165), d610b8a (T-167), 83e28f2 (T-169), a95f84e (T-171).

Ended: ledger fully clean, tick.json no needs/waits, stage 7 gate PASS. What waits: nothing mechanical - new scope needs the human.

2026-10-25 background orchestrator (devin-background), ~09:10-09:55Z: closed the last open tick need - T-173/T-174.

- tick.json named one need: T-173 launch refused at preflight ("## Checks empty") - already fixed by commit 0035d60; a stale 09:10Z launch.lock had also self-expired (>300s rule). tick launched T-173 attempt 1 on devin; worker completed in ~17 min, `Outcome: completed`, Change 3f28f31, all C-01..C-05 pass (test_studio 106/106; full suite 609/610 with the known Windows temp-fixture PermissionError flake, passes isolated).
- Set T-173 `review`; filled T-174's `Verifies: T-173 @ 3f28f31f80ad29509e7d6e5a16a614c706e53095` header and set it `ready`. Tick's mechanical decide() does not model the pre-merge tester exception (checked task in review satisfies its Depends), so T-174 was launched directly via run-task.ps1 - the launcher's admission gate handled it correctly.
- T-174 exited `completed`, `Verdict: pass` with live headless-Chrome DOM evidence (card collision checks at 1366/480/320px, 3-subtab analytics, project disambiguation, flat searchable thread dropdown; 106 + 610 test runs clean on rerun). tick accepted T-174, then T-173; merged at 6a059a4, worktree/branch cleaned.
- Recorded tester-proposed known-issues: test_scenarios PermissionError flake (second observation) + pre-existing <=600px sidebar clipping limitation (candidate future task, human's call).

Ended: ledger fully clean, tick.json no needs/waits, main@6a059a4.
