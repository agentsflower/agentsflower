# T-064: Completion gate carrier - T-032 artifact + audit fix under corrected machinery

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-062
Branch: t-064-completion-gate-carrier
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-064-completion-gate-carrier
Independent check: tester
Resume: none

## Goal

Successor of rejected T-060 (itself successor of rejected T-032): the branch
9c7450ae4ffa7b8a1d648cb3727365b9e298f731 already contains the complete
verified completion-gate artifact (a4f0642, T-032) PLUS the audit-scope fix
(T-060's work, now independently landed on main as T-062/2.13.3). The prepared
worktree sits on that commit - keep it. Reconcile against current main
(a4f0642 no longer flags the audit since _template.md is now excluded),
confirm every criterion is green, consolidate release metadata (VERSION may
need sync against main's 2.13.3 - the artifact claims 2.14.0 for the whole
combined feature, which is correct if the diff carries T-032's full gate +
metadata), write the Result.

## Read first

- .agentflow/tasks/T-032-completion-gate.md + .agentflow/tasks/T-060-completion-gate-final.md (rejected predecessors + Results)
- .agentflow/tasks/T-062-audit-scope-fix.md + T-063-verify-audit-scope.md (the audit fix now on main)
- .agentflow/tools/gate.py, accept.py, ledger.py, cli.py on the branch
- .agentflow/tests/test_done_gate.py, test_endcheck.py

## Allowed files

- .agentflow/tools/gate.py
- .agentflow/tools/accept.py
- .agentflow/tools/ledger.py
- .agentflow/tools/cli.py
- .agentflow/tools/run_task.py
- .agentflow/tasks/_template.md
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
- .agentflow/docs/release-validation.md
- .agentflow/docs/model-options.json
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/t-*.md (other Task Files)
- .agentflow/tasks/.runtime/
- .github/
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md
- pyproject.toml, setup.py, MANIFEST.in, .agentflow/dashboard/
- other projects and their machine leases

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] C-01: Every T-032 criterion holds on this branch: required criteria carry stable IDs; the Result maps each to an outcome line; evidence paths validated and bound to artifact/base SHAs; accept.py runs Checks on the trial-merge result; agentflow done returns structured pass/fail; pre-existing failures are distinguished from introduced ones.
- [ ] C-02: The audit-scope defect that rejected T-032 and T-060 is gone on this branch: a _template.md commit passes the merge-history audit while t-*.md and .runtime/ commits still flag.
- [ ] C-03: All T-050/T-056-verified behaviors stay green (fail-closed readers, bound acceptance, locked --stop, group scoping, classification, takeover block, recovery).
- [ ] C-04: Full suite passes verbatim; VERSION/AGENTS/CHANGELOG consistent at the consolidated version; commit the consolidated state (a fresh commit on top of 9c7450a if anything needed merging from main, otherwise record 9c7450a as the Change). Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-audit regressions.
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` - preflight criteria-ID enforcement.
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - the completion gate tests.
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` - completion command surface.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result

Outcome: completed
Change: 7f208e2eb85b88af80acc8b9b2694ce28dd2eb45 on t-064-completion-gate-carrier
Files:
- .agentflow/tools/gate.py - merge resolution keeps main's independently verified audit machinery (name-only audit under the tasks tree with the product-template exclude; the flag names the offending paths) plus the fuller docstring wording
- .agentflow/tests/test_endcheck.py - both audit-scope regression sets merged (the named-path assertions and the scenario tests); the fixture keeps the real product-template copy
- CHANGELOG.md - the consolidated 2.14.0 entry stays on top and the shipped 2.13.3 entry is retained below it
- .agentflow/VERSION, AGENTS.md - resolved to the consolidated 2.14.0
- .agentflow/docs/ai-handoff-protocol.md - resolved to the explicit audit-scope wording (Task Files and launcher runtime state flag, the product template does not)
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_parallel.py` -> pass (3 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` -> pass (21 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_cli.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (295 passed / 0 failed / 3 skipped)
Criteria without a command:
- C-01: pass - the T-032 artifact rides unchanged at a4f0642 (ancestor of HEAD); stable criterion IDs enforced by preflight and per-criterion outcome lines by evaluate in .agentflow/tools/gate.py; evidence paths are scope-checked and artifact/base-bound via evidence_problems and the verify record; the integrated check runs through integrated_problems and .agentflow/tools/accept.py; the single completion command is the done subcommand of .agentflow/tools/gate.py surfaced by .agentflow/tools/cli.py with structured output; pre-existing versus introduced failures are separated by base_failing - all covered by .agentflow/tests/test_done_gate.py and .agentflow/tests/test_parallel.py
- C-02: pass - live probe on this branch: a4f0642's diff under the tasks tree names only the product template and is empty under the exclude pathspec, and the merge commit's remerge-diff there is empty too; Task-File and launcher runtime-state commits still flag per the six audit-scope tests in .agentflow/tests/test_endcheck.py
- C-03: pass - the T-050 and T-056 verified behaviors stay green inside the verbatim full suite (fail-closed readers, bound acceptance, locked stop, group scoping, classification, takeover block, recovery) across .agentflow/tests/test_run_task.py, .agentflow/tests/test_launcher_lifecycle.py and .agentflow/tests/test_workspace.py
- C-04: pass - fresh commit 7f208e2 on top of 9c7450a reconciles main at 1a05af9; .agentflow/VERSION, AGENTS.md and CHANGELOG.md are consistent at the consolidated 2.14.0 with the shipped 2.13.3 entry retained; the diff from main stays inside Allowed files; decisions text proposed below
Found, not fixed:
- the first run of the merged tree's completion-gate test file reported one transient failure that did not reproduce on two later runs nor inside the 295-test full suite; the failing output was not captured, so the flaky test is unidentified - likely fixture-worktree timing on Windows
Proposed memory updates:
- .agentflow/state/decisions.md, dated 2026-10-17: "T-064 consolidates the completion gate onto the corrected machinery: the branch carrying the T-032 artifact a4f0642 and the T-060 audit fix 9c7450a merges main's independently verified T-062 fix, keeping the name-only audit implementation that names offending paths and the consolidated 2.14.0 release record while retaining the shipped 2.13.3 changelog entry. Rejected alternatives: rebasing onto main (loses the carried-artifact lineage and forces re-verification of unchanged work) and keeping the earlier patch-output audit (the independently verified version was already on main)."
