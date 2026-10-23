# T-098: Shipped features documentation and tool notes alignment

Role: developer
Tool: devin
Stage: 5
Depends on: T-097
Branch: t-098-shipped-features-docs
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-098-shipped-features-docs
Independent check: tester
Resume: 16b336e647ed937673974a0b71d444b0946e33f0

## Goal

Subtask 2 of re-scoped T-036 (improvement-plan.md section 5): align the
user-facing feature documentation with what the current VERSION actually
ships, and correct stale tool notes against the implementation. Core
instructions, protocol and role guidance are T-097's scope; the Russian guide
and release metadata finalization are T-099's scope.

## Read first

- .agentflow/docs/improvement-plan.md (section 5)
- .agentflow/docs/ai-handoff-protocol.md
- README.md, GUIDE.md, RELEASE_NOTES.md, .agentflow/README.md
- .agentflow/docs/release-validation.md, .agentflow/docs/typesafe.md
- .agentflow/state/known-issues.md (stale tool notes to reconcile: agy interactive tester, Devin permission requirements)
- CHANGELOG.md (what shipped in 2.11.9-2.15.x - the docs must describe the current behavior)

## Allowed files

- README.md
- GUIDE.md
- RELEASE_NOTES.md
- .agentflow/README.md
- .agentflow/docs/release-validation.md
- .agentflow/docs/typesafe.md
- .agentflow/tools/ (only if generated status/handoff facts need a code path - section 5)
- .agentflow/tests/ (any file - test_layout.py enforces structure and may need updating)
- .agentflow/VERSION
- AGENTS.md, CLAUDE.md (AgentFlow version block only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/roles/, .agentflow/commands/, .claude/commands/ (T-097 scope)
- GUIDE.ru.md (T-099 scope)
- .github/
- pyproject.toml, setup.py, MANIFEST.in
- .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] S-01: Every shipped behavior of the current VERSION is truthfully documented: Python launcher with the PowerShell compatibility wrapper, packaged CLI, optional MCP server and its opt-in privileged tools, model probes and their opt-in env vars, worker timeout, machine registry/dispatch modes, quota groups/policy, completion gate, recovery capture. No doc describes removed or never-shipped behavior as current.
- [ ] S-02: Stale tool notes verified against actual implementation and corrected: the agy interactive-tester hang claim vs the current noninteractive Tester path; Devin permission notes vs the current probe/worker argv (`--respect-workspace-trust false`, `--permission-mode` values); Codex sandbox limits on Windows; conductor/autostart marked Windows-only. Each claim is either corrected to match the code or explicitly marked unverified/removed.
- [ ] S-03: Status and handoff facts are generated from task/attempt records where the protocol promises it (or the promise is removed); goals, decisions and explanatory known issues stay authored memory; stale-summary detection exists or the claim is deleted.
- [ ] S-04: release-validation.md and typesafe.md match the shipped tools and current routing/admission behavior.
- [ ] S-05: Full suite passes verbatim; if template-owned files changed, VERSION incremented, AGENTS version block synced, CHANGELOG migration notes say what an installed project must do. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - template structure and entry-point integrity.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - install/update integrity of changed files.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 38f94f6 on t-098-shipped-features-docs
Files:
- README.md - version badge 2.12.0->2.15.6; tools table names all shipped tools (tick, route/plan_route/route_report, quota_groups, machine_capacity, dispatch, hooks, mcp_server); CI row mentions package/MCP jobs; PowerShell note (7 verified, 5.1 unverified) and Windows-only conductor; Verification status records remote run 39026298541 (ubuntu+package green, windows/macos test jobs failed environment-specific, mcp skipped; still no green macOS)
- GUIDE.md - PowerShell requirement line corrected; `agentflow` subcommand list updated to the real CLI (gate verbs task|preflight|endcheck|verify|stage, `done`, `hooks`); F. machine resources rewritten for the shipped registry (AGENTFLOW_MACHINE_STATE_DIR), the three AGENTFLOW_SHARED_DISPATCHER modes, quota-group-scoped holds and the declared quota-policy/quota-samples files; conductor/autostart marked Windows-only; new "Launch checks and worker bounds" section (routing admission via T-NNN.route.json requirementsHash, AGENTFLOW_<TOOL>_PROBE/`off`, opt-in AGENTFLOW_<TOOL>_MODEL_PROBE=on, AGENTFLOW_WORKER_TIMEOUT + --watchdog, autonomy budgets, nested-launch rule, power_guard, gate.py done + Codex Stop-hook adapter); process-control commands corrected to the real argv (`T-NNN --stop/--mark-finished/--recheck`, `--watchdog`); Recovery documents stopReason classes and the bounded recovery record with Resume semantics; Permission boundaries document the fixed per-tool worker argv and the Codex Windows-sandbox limitation
- RELEASE_NOTES.md - 2026-10-21 status update (no v2.12.0 tag/release ever created; repo moved through 2.15.x); remote CI run 39026298541 outcome; thirteen-job count
- .agentflow/README.md - folder map lists every shipped tool (tick, hooks, power_guard, limit_detection, quota_groups, dispatch, conductor helpers marked Windows-only) and the optional quota-policy.json/quota-samples.json
- .agentflow/docs/release-validation.md - thirteen CI jobs (9 matrix + 2 package + 2 mcp), remote run 39026298541 outcome recorded honestly (windows/macos test failures environment-specific and open; no green macOS), updated human steps
- .agentflow/VERSION - 2.15.5 -> 2.15.6
- AGENTS.md - AgentFlow version block synced to 2.15.6
- CHANGELOG.md - 2.15.6 entry (docs-alignment train T-097+T-098) with migration notes: install.py --update picks up changed template files; no workflow/contract change
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (424 passed / 0 failed, 3 skipped)
Criteria:
- S-01: pass - GUIDE.md documents every listed shipped behavior verified against code: Python launcher + run-task.ps1 wrapper (GUIDE.md:7), packaged CLI with the real subcommand set matching cli.py (install/run/gate/accept/ledger/mcp/hooks/done/dashboard), MCP server + --enable-orchestrator-tools opt-in (GUIDE.md:124-142, mcp_server.py), free probe AGENTFLOW_<TOOL>_PROBE and opt-in AGENTFLOW_<TOOL>_MODEL_PROBE=on (run_task.py:162-176), AGENTFLOW_WORKER_TIMEOUT default 1200 + --watchdog (run_task.py:94-99), machine registry + off/shadow/active dispatch (machine_capacity.py, dispatch.py), quota_group holds + quota-policy/samples (quota_groups.py, protocol 3e), gate.py done completion gate + hooks.py adapter, recovery capture (stopReason + recovery record, run_task.py:107-119). No allowed doc describes removed/never-shipped behavior as current (stale "nine jobs never ran", 2.12.0 badge, old CLI list and run_task argv corrected).
- S-02: pass - verified against run_task.py tool_argv()/MODEL_PROBE_ARGS and corrected in GUIDE.md:228: agy tester is non-interactive `-p --output-format stream-json` (no interactive -i, no /exit); Devin workers `-p --permission-mode dangerous --respect-workspace-trust false`, opt-in probe `--permission-mode auto`; Codex Windows-sandbox write denials documented (GUIDE.md:229); conductor/autostart marked Windows-only (GUIDE.md:152, README.md:82). Remaining stale copies live only in do-not-touch files - listed under Found, not fixed.
- S-03: pass - GUIDE.md:200 states status is derived from records (`--status`, `tick.py status`, dashboard read attempt/ledger files) and handoff.md stays an authored note, matching the protocol (Handoff section). Goals/decisions/known-issues stay authored memory per Updating memory; no allowed doc promises generated handoffs. Stale-summary/stale-link detection exists (dashboard flags stale Verifies SHAs; verify rejects a stale unbound PASS - "a still-bound PASS is reused, not re-measured", GUIDE.md:198); no doc claims more.
- S-04: pass - release-validation.md matches .github/workflows/ci.yml (nine matrix jobs + two package + two mcp, 20/30-min bounds) and records the one real remote run; typesafe.md audited line-by-line against route.py (assessment schemaVersion 1 bound to requirementsHash; ok/blocked/low-confidence/failed; floor/recommended/quota_group/model_by_effort; assessment_problems/admission/backup_ok/log_admission; tick + backup-switch path) - no correction needed.
- S-05: pass - full suite green verbatim (see Checks); template-owned files changed so VERSION -> 2.15.6, AGENTS.md block synced, CHANGELOG 2.15.6 entry says an installed project runs install.py --update and needs no configuration change. Proposed decisions.md text below.
Found, not fixed:
- `.agentflow/roles/tool-routing.md` ~line 46 still claims the Antigravity CLI Tester "stays interactive (-i) and needs a human /exit" - stale vs tool_argv() (`-p --output-format stream-json`). roles/ is T-097 scope (do-not-touch here); needs a small template task. Suggested text: "a Tester runs non-interactive print mode `--output-format stream-json`" like the Developer minus `--dangerously-skip-permissions`.
- `GUIDE.ru.md` still carries the stale Antigravity -Manual wording for worker tasks - T-099 scope.
- `.agentflow/state/known-issues.md` "Antigravity IDE cannot be automated: its attempts are -Manual" is still true for the IDE only; the agy CLI runs managed non-interactive workers. Authored memory - clarification proposed below.
Proposed memory updates:
- decisions.md, dated 2026-10-21: "2.15.6 documentation-alignment train (T-097, T-098): user-facing docs now describe shipped 2.15.x behavior (routing admission, probes, worker bounds, dispatch/quota, gate done, recovery capture) instead of the 2.12.0-era surface; the fixed per-tool worker argv is documented in GUIDE.md. Rejected: rewriting RELEASE_NOTES.md into a new release - it stays the 2.12.0 preparation record with a status update; real release notes belong to T-099."
- known-issues.md: annotate the 2026-10-03 Antigravity entry: "CLI note (2026-10-21): the `agy` CLI is automated - developer and tester run non-interactive `-p --output-format stream-json`; only the IDE stays `-Manual`."
