# T-030: Recoverable handover - failure classification, draft capture, upstream limit-detection/quota-group generalization

Role: developer
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-050
Branch: t-030-recoverable-handover
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-030-recoverable-handover
Independent check: tester
Resume: none

## Goal

Implement improvement-plan.md section 2 and generalize two audited upstream
candidates found in the Transcript Youtube installed project: shared
provider-limit detection and per-model quota groups. After this task a stalled
or limited worker hands its task to a successor without losing drafts, and an
agy Gemini hold does not also block agy Claude/GPT (or vice versa).

## Read first

- .agentflow/docs/improvement-plan.md (section 2)
- .agentflow/docs/ai-handoff-protocol.md (Recovery, Autonomous orchestration, Launching workers)
- .agentflow/state/known-issues.md (limitHit false positives, agy tool-wide limit)
- E:\Projects\Google Chrome Extensions\Transcript Youtube\Transcript Youtube\site\code\.agentflow\tools\limit_detection.py (upstream candidate - read as reference)
- E:\Projects\Google Chrome Extensions\Transcript Youtube\Transcript Youtube\site\code\.agentflow\tools\quota_groups.py (upstream candidate - read as reference)
- E:\Projects\Google Chrome Extensions\Transcript Youtube\Transcript Youtube\site\code\.agentflow\tests\test_limit_detection.py and test_quota_groups.py (reference)
- .agentflow/tools/run_task.py, .agentflow/tools/tick.py, .agentflow/tools/conductor.ps1, .agentflow/tools/machine_capacity.py, .agentflow/tools/ledger.py, .agentflow/tools/gate.py
- .agentflow/tests/test_run_task.py, test_tick.py, test_conductor.py, test_machine_capacity.py

## Allowed files

- .agentflow/tools/limit_detection.py (new)
- .agentflow/tools/quota_groups.py (new)
- .agentflow/tools/run_task.py
- .agentflow/tools/tick.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/conductor-panel.ps1
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/ledger.py
- .agentflow/tools/gate.py
- .agentflow/tools/cli.py
- .agentflow/tests/ (any file)
- .agentflow/docs/model-options.json stub handling inside install.py if a schema field is added (keep it optional)
- .agentflow/tools/install.py (only if a new stub/template-owned file must be delivered)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- the Transcript Youtube project itself (read-only reference; do not modify it)
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] H-01: Shared limit detection in `.agentflow/tools/limit_detection.py` replaces the regex-only limitHit logic in run_task.py, conductor.ps1 and tick.py: strong provider-directed phrases count at any exit code; weak quota/status phrases count only with tool-failure evidence (nonzero exit, error-prefixed line, outer error event in stream-json); quoted subject-matter content is skipped; retryable transport failures never match. Preserve the transcript project's audited semantics and adapt naming to this template's conventions.
- [ ] H-02: `.agentflow/tools/quota_groups.py` scopes observed holds per model quota group: model-options.json gains an optional `quota_group` field; a hold on `<tool>:<group>` blocks only that group, holds on the bare tool key stay tool-wide, account/access failures are always tool-wide; the option named after the tool defines the default group's model. The current tool-wide agy record keeps blocking the exhausted families while a fresh agy Gemini probe remains possible. Launches, tick run and conductor next-orchestrator honor group-scoped holds.
- [ ] H-03: Attempt records classify the stop reason: quota/access limit, environment failure, implementation failure, verification failure, completed, killed/stopped, timeout. Classification is derived from exit code + limit detection + end-check, not from free text alone.
- [ ] H-04: Before a takeover or a new attempt, the launcher confirms the previous executor and its managed children stopped (pid+pidStart identity check); uncertain process ownership blocks concurrent writing with a diagnosable error instead of launching alongside a live worker.
- [ ] H-05: A new bounded recovery-capture step records branch, HEAD, tracked modifications, untracked files, stop reason and remaining work for a failed/dead attempt, including when the worker left no commit and no Result; captured drafts are preserved and never silently discarded for quota loss alone. Secret-bearing file contents stay out of the record (paths/status only).
- [ ] H-06: `Resume:` continuation works from the captured state: a new attempt on the same Task File/branch/worktree sees the preserved draft; `Resume: start fresh` discards only that worktree's draft.
- [ ] H-07: Full suite passes verbatim; increment VERSION (next minor or patch per change weight), sync AGENTS block and CHANGELOG migration notes (installed projects receive the two new tools via install.py --update; existing tool-wide holds keep working). Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` - strong/weak/quoted/transport signal classes.
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` - group scoping and tool-wide fallback.
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - classification, takeover safety, draft capture.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - limited-tool and group-aware needs.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: f6d746bec79dc703df4b57f15c7b982b44c5fdc5 on t-030-recoverable-handover
Files:
- .agentflow/tools/limit_detection.py (new) - shared provider/account limit detector: strong phrases count at any exit code, weak quota words need failure evidence, quoted subject matter skipped; CLI `--exit-code` for conductor.ps1; `detect_detail` returns (phrase, "account"|"quota")
- .agentflow/tools/quota_groups.py (new) - `quota_group` resolution from model-options.json: `group_for(tool, model)`, `default_group(tool)` (the option named after the tool), CLI for conductor.ps1
- .agentflow/tools/run_task.py - shared detector for `limitHit`/`limitKind`/`limitPhrase`; `stopReason` classification; `quotaGroup` on attempts; leftover-children takeover block (parent chain + POSIX tool session + Windows job object); bounded `recovery` capture; `Resume:` handling; one-line handover in worker prompt and `--manual` output
- .agentflow/tools/tick.py - shared detector replaces LIMIT_RE; group-scoped `record_limit`/`limit_end`/`limited`, `limit --group`, `limit-migrate`; `active_limits`; group-aware `decide`/`learn_limits`/`use_backup`/`next_orchestrator`/`run`; dead-attempt need reports leftover managed processes
- .agentflow/tools/machine_capacity.py - `_limit_key`/`_limit_end` scoping, `claim --group`, `record_limit`/`limit_until`/`has_capacity` group params, `move-limit`
- .agentflow/tools/gate.py - parses `Tool`/`Resume` fields, computes task `quotaGroup`, launch-tool override in preflight
- .agentflow/tools/conductor.ps1 - `Test-LimitLog` via the shared detector; `Start-Orchestrator` claims with `--group` of the tool default group
- .agentflow/docs/model-options.json - `agy` option (CLI default model) defining the `agy-gemini` default group
- .agentflow/docs/ai-handoff-protocol.md - Terms (quota group), Runtime state (new attempt fields), Recovery (classification, recovery record, leftover block, Resume semantics), orchestration item 3 and 3a, Launching workers 6
- .agentflow/tests/test_limit_detection.py (new), test_quota_groups.py (new), test_run_task.py (stopReason assertions + 5 recovery tests), test_tick.py (shared-detector call), test_conductor.py (fixture copies the new shared tools)
- .agentflow/VERSION 2.13.0, AGENTS.md version line, CHANGELOG.md entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_limit_detection.py` -> pass (14 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_quota_groups.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (41 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (263 passed / 0 failed, 3 skipped - platform-specific)
Criteria without a command:
- H-01: covered by test_limit_detection.py plus run_task/conductor integration tests; the regex LIMIT_RE copies are deleted from run_task.py and tick.py, and conductor.ps1 calls the shared CLI.
- H-02: covered by test_quota_groups.py (group scoping, tool-wide fallback, legacy-hold migration, next-orchestrator) and test_run_task.test_group_scoped_limit_blocks_and_quota_group_is_recorded; the `agy` option gives unmodelled agy the `agy-gemini` group, and `limit-migrate` rescopes the recorded tool-wide agy hold so a Gemini probe stays possible.
- H-03: `classify_stop` uses only launcher facts (hint from the stop path, `limitHit`, "launch error:" prefix, end-check violations, exit code); asserted in test_run_task for stopped/timeout/limit/verification/implementation/completed.
- H-04: covered by test_orphaned_descendant_blocks_the_next_launch plus the existing unconfirmed-pid tests; `--stop` and a new launch both refuse with a diagnosable error while a managed process still runs.
- H-05: covered by test_failed_attempt_captures_drafts_and_hands_over and test_a_dead_workers_attempt_recovers_and_the_successor_is_told; `capture_recovery` records paths/status only (RECOVERY_MAX_FILES=200 bound), never file contents, and runs even with no commit and no Result.
- H-06: covered by test_resume_sha_keeps_drafts_bad_sha_refuses_and_start_fresh_resets: `Resume: <sha>` requires ancestry of the worktree HEAD and keeps drafts; `start fresh` resets/cleans only that worktree; the successor's record and prompt carry the handover.
- H-07: VERSION 2.13.0, AGENTS.md block synced, CHANGELOG migration notes written (install.py --update ships the two new tools via the template-owned tools/ dir; existing tool-wide holds keep working). decisions.md text proposed below.
Found, not fixed:
- .agentflow/tools/dispatch.py (not in Allowed files) still views holds tool-wide: it may issue a grant for a group-held tool, which the scoped `claim` then refuses and tick.run releases - a wait, never a blocked launch. Pinned by test_quota_groups.DispatchGroupTests.
- .agentflow/tools/conductor-panel.ps1 displays scoped `tool:group` keys verbatim (generic iteration); no functional change needed.
- install.py's model-options.json stub deliberately omits `quota_group` (optional field; absent = tool-wide semantics), matching upstream practice.
- Attempt 1 of this task hit the 2400 s AGENTFLOW_WORKER_TIMEOUT mid-documentation; this attempt (2) reviewed, completed and verified its draft. The worktree draft was preserved under the task's own recovery rules.
Proposed memory updates:
- decisions.md: "2026-10-17 - T-030 (2.13.0): one shared provider-limit detector (limit_detection.py) now judges worker, tick and conductor logs - two signal classes (strong provider-directed phrasing at any exit code, weak quota words only with failure evidence) replaced three diverging regex copies that misread reports about product quotas. Observed holds are scoped to model quota groups (optional quota_group in model-options.json, hold key '<tool>:<group>'); account/access failures stay tool-wide. Attempts carry a classified stopReason and a bounded paths-only recovery record; `Resume: <sha>` continues the preserved draft, `start fresh` discards only that worktree; a successor is refused while managed children of the previous worker still run. Rejected: per-caller regexes (already diverged); teaching dispatch.py quota groups (out of scope - its tool-wide grant degrades to a wait at the scoped claim, pinned by tests)."
- known-issues.md: the 2026-10-03 entry ("`limitHit` is a text match... Reopen if a tool reports limits in a structured way") is superseded by limit_detection.py at 2.13.0 - worth annotating when the Orchestrator next updates it.
