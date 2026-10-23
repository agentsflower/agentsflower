# T-099: Russian guide parity and public documentation finalization

Role: developer
Tool: devin
Stage: 5
Depends on: T-098
Branch: t-099-guide-ru-parity-release
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-099-guide-ru-parity-release
Independent check: tester
Resume: a80626ac3f4e89fb4aaf11bc0dffbb6d9159fd4d

## Goal

Subtask 3 of re-scoped T-036 (improvement-plan.md section 5): bring
GUIDE.ru.md to section-by-section parity with the post-T-098 GUIDE.md,
preserve the mode/concurrency/commit guarantees across all docs, and finalize
the release metadata for the documentation-alignment train.

## Read first

- .agentflow/docs/improvement-plan.md (section 5)
- GUIDE.md, GUIDE.ru.md, README.md, RELEASE_NOTES.md, .agentflow/README.md
- .agentflow/docs/ai-handoff-protocol.md (Single/Team mode, concurrency and commit rules)
- CHANGELOG.md, .agentflow/VERSION, AGENTS.md

## Allowed files

- GUIDE.ru.md
- GUIDE.md (only edits needed for parity or factual correction)
- README.md
- RELEASE_NOTES.md
- .agentflow/README.md
- .agentflow/docs/release-validation.md (only if parity reveals a drift)
- .agentflow/roles/tool-routing.md (only the stale agy-tester claim below)
- .agentflow/VERSION
- AGENTS.md, CLAUDE.md (AgentFlow version block only)
- CHANGELOG.md
- .agentflow/tests/ (any file - test_layout.py enforces structure and may need updating)

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/commands/
- .claude/commands/
- .agentflow/docs/improvement-plan.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/project-rules.md
- .agentflow/docs/model-options.json
- .agentflow/docs/quota-policy.json
- .agentflow/docs/typesafe.md
- .agentflow/docs/engineering-rules.md
- .agentflow/roles/developer.md
- .agentflow/roles/tester.md
- .agentflow/roles/orchestrator.md
- .agentflow/roles/deployer.md
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

- [ ] G-01: GUIDE.ru.md stays Russian and carries the same factual content as GUIDE.md (section-by-section parity, not a word-for-word translation); README/GUIDE/RELEASE_NOTES honesty rules hold (no invented results, URLs, metrics).
- [ ] G-02: Explicit Single/Team mode choice, user concurrency restrictions and commit rules are preserved in text; nothing automatically relaxes them.
- [ ] G-03: Release metadata agrees with the merged T-097/T-098 state: .agentflow/VERSION, the AGENTS.md/CLAUDE.md version blocks, and CHANGELOG.md migration notes describe the documentation-alignment train as one coherent release step, saying what an installed project must do.
- [ ] G-04: Full suite passes verbatim. Propose dated decisions.md text in the Result.
- [ ] G-05: Leftover from the T-036 re-scope (reported by the T-098 worker): `.agentflow/roles/tool-routing.md` ~line 46 still claims the Antigravity CLI Tester "stays interactive (-i) and needs a human /exit" - stale vs `run_task.py` tool_argv, which launches agy non-interactively (`-p --output-format stream-json`). Correct that line only; the IDE stays -Manual. GUIDE.ru.md carries the same stale wording - fix under G-01.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - template structure and entry-point integrity.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - install/update integrity of changed files.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 4519a63c17ff05b5962cb9452dedcaabaec0ced4 on t-099-guide-ru-parity-release
Files:
- GUIDE.ru.md - rewritten to section-by-section parity with the post-T-098 GUIDE.md (same 20-section structure and factual surface, in Russian): install/update/migrate/package/MCP/machine-resource surface, launch checks and worker bounds, fixed per-tool worker argv, recovery semantics; stale claims corrected (managed workers are detached background processes watched via --status, dashboard UI is English, agy CLI tester non-interactive, 2.1 migration follows the installer refusal path); Russian-only sections the English guide does not carry (machine preparation, TypeSafe setup, per-tool smoke check, day scenario, cheat sheet) dropped - recorded in CHANGELOG
- CHANGELOG.md - 2.15.6 entry now covers the whole documentation-alignment train (T-097+T-098+T-099) with the GUIDE.ru.md parity and tool-routing fix bullets; migration notes extended (install.py --update picks up role files incl. tool-routing.md; GUIDE.ru.md is template-side, not installed)
- RELEASE_NOTES.md - rewritten as the pending 2.15.6 release notes (supersedes the never-published 2.12.0 record): accumulated highlights per shipped version, evidence status and limits preserved (remote run 39026298541 outcome, no green macOS, no PyPI, no tag), publish steps retargeted to v2.15.6
- .agentflow/roles/tool-routing.md - the stale Antigravity CLI line corrected: both managed roles run non-interactive `-p --output-format stream-json` (Developer adds --dangerously-skip-permissions); only the IDE stays -Manual
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (424 passed / 0 failed, 3 skipped)
Criteria:
- G-01: pass - GUIDE.ru.md is Russian and a section-by-section mirror of GUIDE.md (identical 20-heading structure, same line anchors). Facts verified against sources: installer refusal on the 2.1 root layout (install.py:269), the `agentflow` subcommand list, MCP read-only default + `--enable-orchestrator-tools`, machine registry/AGENTFLOW_SHARED_DISPATCHER modes/quota-group holds, worker bounds (AGENTFLOW_WORKER_TIMEOUT 1200 default, attempt/failure/switch budgets, nested-launch refusal, power_guard) and the fixed argv (tool_argv(), run_task.py:339-356). No invented results, URLs or metrics.
- G-02: pass - the "Кто что делает" table keeps the explicit Single Mode vs role-team split and one-task-per-fresh-session concurrency; the one-commit rule (GUIDE.ru.md:173), "no push/merge/deploy - merges belong to accept.py, deploy only after the human's yes" (GUIDE.ru.md:230) and deployer-always-`--manual` (GUIDE.ru.md:168) are preserved verbatim in meaning; nothing relaxes them.
- G-03: pass - .agentflow/VERSION and the AGENTS.md version block both read 2.15.6; CHANGELOG describes T-097/T-098/T-099 as one coherent release step and its migration notes say what an installed project must do (install.py --update; no configuration change; GUIDE.ru.md template-side only - confirmed it is outside install.py OWNED). RELEASE_NOTES.md now documents this same pending 2.15.6 release.
- G-04: pass - full suite green verbatim (see Checks). Proposed decisions.md text below.
- G-05: pass - tool-routing.md now matches tool_argv() exactly (agy tester: `-p --output-format stream-json`, no interactive -i, no /exit; verified run_task.py:351-353); the IDE remains -Manual; the same corrected wording is in GUIDE.ru.md:228.
Found, not fixed:
- `.agentflow/state/known-issues.md` 2026-10-03 entry "Antigravity IDE cannot be automated" is still literally true for the IDE but now reads ambiguously next to the fixed docs; an annotation is proposed below (authored memory, worker cannot write it).
Proposed memory updates:
- decisions.md, dated 2026-10-21: "2.15.6 documentation-alignment train completed (T-099): GUIDE.ru.md rewritten to section-by-section parity with GUIDE.md - one factual surface, so the Russian-only operational sections (machine preparation, TypeSafe setup, per-tool smoke check, day scenario, cheat sheet) were dropped rather than translated forward; RELEASE_NOTES.md rewritten as the pending 2.15.6 release notes superseding the never-published 2.12.0 record; tool-routing.md's stale interactive agy-tester claim corrected to the shipped non-interactive argv. Rejected: bumping VERSION past 2.15.6 - the release is unpublished, so T-099 folds into the same train entry."
- known-issues.md: annotate the 2026-10-03 Antigravity entry: "CLI note (2026-10-21): the `agy` CLI is automated - developer and tester run non-interactive `-p --output-format stream-json`; only the IDE stays `-Manual`."
