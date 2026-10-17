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
