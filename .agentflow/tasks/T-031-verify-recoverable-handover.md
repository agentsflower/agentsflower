# T-031: Independently verify recoverable handover and quota groups

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-030
Verifies: T-030 @ f6d746bec79dc703df4b57f15c7b982b44c5fdc5

## Goal

Independently evaluate the exact T-030 artifact (2.13.0 recoverable handover)
against every H-01..H-07 criterion in its Task File, in a disposable checkout.
Never repair the checked artifact; report the worst criterion as the verdict.
This is the task whose own domain is recovery - test it adversarially with real
kill/stop scenarios, not only the suite.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Recovery, Runtime state, Task lifecycle)
- .agentflow/tasks/T-030-recoverable-handover.md (the contract and the worker's Result)
- .agentflow/docs/improvement-plan.md section 2
- .agentflow/docs/model-options.json (the quota_group schema this uses)
- The candidate diff `git diff main...f6d746bec79dc703df4b57f15c7b982b44c5fdc5` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-030 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Shared limit detection proves stronger than the old regexes: a log merely *mentioning* quota (a worker reporting about a product quota feature, quoted subject matter) does not trip limitHit; a provider-directed limit phrase trips it even at exit 0; a weak quota word at exit 0 does not; transport failures never match. Reproduce each class with real captured-worker-log fixtures.
- [ ] R-02: Group-scoped holds proven live in a disposable repo: a recorded `agy:agy-gemini` hold blocks gemini launches while an agy claude launch refuses on the tool-wide hold - and a tool-wide hold on agy blocks every agy model; account failures stay tool-wide; `limit-migrate` rescopes the real recorded tool-wide agy record so agy-gemini is probeable again (use a disposable machine registry, never the live one).
- [ ] R-03: Stop classification proven live: run real miniature worker scripts through the launcher paths (or the documented test entry points) for quota-limit, timeout, verification-failure, stopped, and clean-exit cases and confirm stopReason names each correctly.
- [ ] R-04: Takeover safety proven live: a worker spawning a background child then dying leaves a live descendant - the next launch or --stop must refuse while it runs (Job Object on Windows or ppid scan on POSIX); after the child is gone the launch proceeds. Reproduce the orphan process, not only the test.
- [ ] R-05: Recovery capture proven live: kill a worker mid-work with uncommitted tracked + untracked changes and no Result; the recovery record carries branch, HEAD, file statuses, stop reason and remaining work - paths only, no file contents, bounded. A successor attempt receives the handover and sees the draft; `Resume: start fresh` clears only that worktree.
- [ ] R-06: Every claimed check command passes on the exact SHA in your checkout (263 green claimed; re-run); VERSION 2.13.0 / AGENTS block / CHANGELOG migration notes in sync; diff stays inside Allowed files; nothing T-050 verified (fail-closed readers, bound acceptance, locked --stop) regressed.
- [ ] R-07: Found-not-fixed claims (dispatch.py tool-wide grant, conductor-panel display, model-options stub) are truthful and correctly scoped; report anything material missed.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` - signal classes.
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` - group scoping and tool-wide fallback.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - classification, takeover, draft capture.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - group-aware needs.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: partial
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (41 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (263 ran / 0 failed, 3 skipped platform-specific; matches the claimed count)
Evidence root: `.agentflow/tasks/.runtime/T-031.evidence/` (all paths below live inside it; checked SHA f6d746bec79dc703df4b57f15c7b982b44c5fdc5, clean disposable checkout, suite output in check*.txt)
Criteria:
- R-01 - partial - every named class reproduced live through the shipped CLI `limit_detection.py <log> --exit-code N` on captured-worker-style fixtures (fixtures/, r01-cli-results.txt, r01-kinds.txt): a worker report about the product's own quota feature (QUOTA_EXCEEDED / rate-limit / usage-limit prose) -> `no limit` @exit0; a provider-directed phrase -> `limit` @exit0; a bare weak word `quota exceeded` -> `no limit` @exit0 and `limit` @exit1; transport failures (UNAVAILABLE/connection refused/503/timeout) -> `no limit` at BOTH exit codes; stream-json assistant/tool/success-result events containing limit phrases -> `no limit` even @exit1; an `error:`-prefixed weak line -> `limit` @exit0; an outer stream-json error event -> `limit` @exit0; kind split verified (account-disabled -> kind `account` = tool-wide, quota phrases -> kind `quota`). What is wrong: plain-line quoted subject matter is skipped only when a listed frame verb precedes the match or the quote char directly abuts it - `the banner shows "you've hit your usage limit"` and `the banner prints "you've hit your usage limit"` still produce `limit: hit your usage limit` @exit0 (fixtures/r01-isolate-shows.log, r01-isolate-banner.log): `_quoted()` inspects only the prefix before the match and the `hit your X limit` pattern starts mid-quote after `you've`, while `shows`/`prints` are not in _QUOTE_FRAME. So a worker quoting provider phrasing verbatim can still get a false limitHit at exit 0 -> false group-scoped hold. The file is byte-identical to the audited upstream except one docstring line, so this is a preserved upstream semantic, not a porting regression; strictly stronger than the old regexes but the quoted-subject-matter guarantee is leaky.
- R-02 - pass - live in a disposable repo with AGENTFLOW_MACHINE_STATE_DIR pointed at a disposable machine registry (never the live one), fake agy CLI (r02_quota_groups_live.out.txt): `tick limit agy .. --group agy-gemini` recorded `agy:agy-gemini` in BOTH the project file and the machine registry; gemini launches (unmodelled default + Model: gemini-3.8-flash-medium) refused `agy group agy-gemini is limited`, a claude-opus-4-6-thinking launch proceeded and exited. An account-disabled message without --group recorded the tool-wide `agy` key and every agy model was then refused; a quota message without --group auto-scoped to `agy:agy-gemini`. The REAL recorded tool-wide agy record (copied verbatim from the live project tool-limits.json, seeded into the disposable registry too) blocked gemini; `tick limit-migrate agy agy-claude-gpt` rescoped it in both stores preserving until=2026-10-21T22:09:21Z and its reason; afterwards the gemini launch ran to completion (quotaGroup=agy-gemini, stopReason=completed) while the claude launch refused `agy group agy-claude-gpt is limited until 2026-10-21T22:09:21Z`. `tick next-orchestrator` live (r02b_next_orchestrator.out.txt): no holds -> agy; `agy:agy-claude-gpt` held -> agy (its default group gemini free); `agy:agy-gemini` held -> devin; tool-wide `agy` -> devin.
- R-03 - pass - real miniature workers launched through run_task.py in a disposable repo (r03_stop_classification_live.out.txt): strong phrase + exit 1 -> stopReason=limit with limitHit=true; sleeping worker under AGENTFLOW_WORKER_TIMEOUT=5 -> timeout with the wall-clock note; worker committing a Task File inside its worktree branch -> verification (end check: "branch commits Task Files"); clean exit 0 -> completed; exit 2 -> implementation; sleeping worker + `--stop` -> stopped. All names classified by launcher facts.
- R-04 - pass - real orphan reproduced on Windows (r04_r05_takeover_recovery_live.out.txt): a fake worker spawned a background sleeper and exited; the next launch refused `managed processes of the previous worker still run` (attempt count stayed 1) and proceeded after the child was taskkilled. Second variant: the worker python was killed directly, leaving the tool tree plus a stray sleeper - `--stop` refused (the attempt stayed `running`, lock kept) and a relaunch refused the same way; once the strays were gone, `--stop` released the lock and the dead attempt closed correctly.
- R-05 - pass - worker killed mid-work (taskkill /T on the recorded worker pid) with a modified tracked file, an untracked draft and no Result: the attempt closed stopReason=dead and its recovery record carries capturedAt, stopReason, hasResult=false, and per-repo branch + HEAD + modified + untracked paths (r04_r05_takeover_recovery_live.out.txt). Bound verified live with 211 untracked files: the record holds 200 untracked + 1 modified with truncated=true; no file contents enter the runtime JSON (the SECRET-BODY marker is absent) (r05_bound_live.out.txt). The successor attempt's `handover` names 'dead' plus 'N modified + M untracked', the drafts still sat in the worktree, and `Resume: start fresh` reset+cleaned only that worktree (drafts gone, `git status` clean, the main repo's files untouched).
- R-06 - pass - all five checks ran verbatim green on f6d746b (check1..check5 .txt; the full suite ran 263 tests, 0 failed, 3 skipped). VERSION=2.13.0, AGENTS.md block=2.13.0, CHANGELOG has a 2.13.0 entry with migration notes (install --update ships the new tools via template-owned tools/, existing tool-wide holds keep working, limit-migrate documented). Diff main...f6d746b = 17 files, all inside Allowed files - note: `.agentflow/docs/model-options.json` matches its Allowed-files entry literally, though the entry's prose speaks of install.py stub handling while the actual edit added the `agy` default-group option to the live project config (required by H-02; quota_group fields on other options already existed in main via 57de1e9). T-050-verified behaviors all exercised green inside the suite: fail-closed runtime/verify/limits readers, acceptance bound to attempt+header hash+SHA, locked --stop on unconfirmed pid identity.
- R-07 - pass - all three found-not-fixed claims verified truthful and correctly scoped: dispatch.py reads only the bare tool key (`state["limits"].get(tool)` at lines 70/123) - a group hold is invisible to it, the scoped `machine_capacity.claim(tool,...,group)` refuses the issued grant (`<tool> is group '<g>' limited`) so active dispatch degrades to a wait, pinned by test_quota_groups.DispatchGroupTests; conductor-panel.ps1 iterates tool-limits keys generically so `agy:agy-claude-gpt` displays verbatim (confirmed live via `tick status`); install.py's model-options.json stub omits quota_group (optional field, absent = tool-wide semantics) while `tools/` is template-owned so --update ships both new tools. Sweep for missed readers: dashboard reads no limit state; route.py `cli_usable` reads tool-wide only (unlisted) - acceptable first-pass semantics since a group hold must not exclude the whole tool, group enforcement lands at the launch resource_check.
New defects (outside the task):
- limit_detection.py residual false positive: a verbatim strong provider phrase embedded mid-quote after an unlisted verb (`shows`, `prints`, `displays`, `writes`, `echoes`) still trips at exit 0, e.g. `the banner shows "you've hit your usage limit"` -> `limit: hit your usage limit`. A false limitHit at exit 0 records a ~1h hold on the attempt's quota group. Same gap exists in the audited upstream file; fix candidate: extend _QUOTE_FRAME verbs or let a quote char anywhere before the match count when the line is prose.
- run_task.py resource_check: under a *tool-wide* hold the refusal message reads `agy group agy-gemini is limited` - it attributes the block to the session's own group scope although the blocker is the bare `agy` key. Cosmetic mislabel only; the block itself is correct.
Cannot verify, needs:
- The POSIX descendant-detection path (tool-session sid scan): this machine is Windows, so R-04 was proven on the Job Object + parent-chain paths; the POSIX session-scan branch is covered only by unit-level code review on this platform.
Proposed memory updates:
- known-issues.md: annotate the 2026-10-03 `limitHit` entry as superseded by limit_detection.py at 2.13.0, and record the residual gap: a verbatim strong provider phrase embedded mid-quote after an unlisted verb still produces a false limitHit at exit 0 - reopen candidate if quoting-in-report false positives recur.
- decisions.md (if the Orchestrator accepts): the checker's note that dispatch.py and route.py both read holds tool-wide only is consistent with scoped-claim enforcement - a group hold never hard-blocks a launch, it degrades to a wait/refusal at the scoped claim and at resource_check.
