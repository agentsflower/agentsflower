# T-068: Evidence-path validator - only repo-path claims count as evidence

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-064
Branch: t-068-evidence-scope-fix
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-068-evidence-scope-fix
Independent check: tester
Resume: none

## Goal

Fix the evidence validator exposed by T-034's rejection: it treats arbitrary
path-like prose tokens in Result outcome lines (`verify/done`,
`launch.argv`, `records/checkpoints`, `decisions.md`, `debugging/risky`) as
declared evidence files and fails the criterion. Only tokens that plausibly
are repository-relative file references should be validated - and even then,
the check must distinguish "declared evidence outside the task scope" from
descriptive prose about where a schema/setting lives. Keep the real
protections: an actual declared evidence file outside the task scope or a
nonexistent claimed path must still fail. This unblocks T-034's verified
artifact (ccd74ba) for its carrier.

## Read first

- .agentflow/tools/gate.py (the evidence-problems path added by the completion gate)
- .agentflow/tasks/T-034-bounded-autonomy.md (the flagged Result - your reproduction case)
- .agentflow/tests/test_done_gate.py (evidence-binding coverage)
- .agentflow/docs/ai-handoff-protocol.md (evidence rule wording)

## Allowed files

- .agentflow/tools/gate.py
- .agentflow/tests/ (any file)
- .agentflow/docs/ai-handoff-protocol.md (only where behavior actually changed)
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

- [ ] V-01: Prose tokens are not evidence: bare filename-ish words without a repo-path shape (no leading `./`, no known top-level dir, no existing file on disk in the checkout) are not flagged. T-034's exact flagged lines (`verify/done`, `launch.argv`, `init/config`, `decisions.md`, `decide/next-orchestrator/status/run`) pass clean.
- [ ] V-02: Real evidence still binds: a declared `.agentflow/tasks/.runtime/...` evidence file missing on disk or outside the task's allowed scope still fails; a declared file that exists inside scope passes.
- [ ] V-03: The schema/prose distinction: a result text that describes where a config file lives or will live (e.g. `.agentflow/docs/quota-policy.json`) is not treated as claimed evidence when the line does not present it as produced evidence - the flag requires an evidence claim, not mere mention.
- [ ] V-04: Full suite passes verbatim; increment VERSION (patch), sync AGENTS block, CHANGELOG migration notes. Propose dated decisions.md text in the Result.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - evidence-binding regressions.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - baseline regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
Outcome: completed
Change: 0193c0a on t-068-evidence-scope-fix
Files:
- .agentflow/tools/gate.py - evidence_tokens now yields claims only: path-looking tokens after an evidence marker (evidence: / evidence=), or a bare repository path list (first segment a top-level folder or an on-disk path, and/or connectors); prose mentions are skipped and the scope/existence checks for claimed evidence are unchanged
- .agentflow/tests/test_done_gate.py - four new EvidenceTests: prose tokens clean, described repository path not a claim, bare path list still claims, missing own runtime evidence rejected
- .agentflow/docs/ai-handoff-protocol.md - Terms Result entry documents the claim rule
- .agentflow/VERSION, AGENTS.md - 2.14.0 to 2.14.1
- CHANGELOG.md - 2.14.1 entry with migration notes
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` -> pass (25 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (299 passed / 0 failed, 3 skipped)
Criteria without a command:
- V-01: pass - evidence: .agentflow/tests/test_done_gate.py - the seven flagged T-034 prose tokens pass clean; reproduced live against its real Result (evidence_problems now returns zero problems) and pinned verbatim by test_prose_path_tokens_are_not_evidence
- V-02: pass - evidence: .agentflow/tools/gate.py - declared evidence still binds: a missing own runtime file and a missing declared file fail while an existing in-scope file passes (test_missing_runtime_evidence_of_this_task_is_rejected, test_bare_path_list_is_still_an_evidence_claim, plus the preexisting EvidenceTests)
- V-03: pass - evidence: .agentflow/tests/test_done_gate.py - test_described_paths_are_not_evidence_claims: a line describing where a schema lives is no claim even when the named path is repository shaped
- V-04: pass - full suite green verbatim; version bumped patch, AGENTS block synced, changelog migration notes written; decisions text proposed below
Found, not fixed:
- First full-suite run hit one transient WinError 5 on os.replace of a disposable registry file in test_run_task (the recurring Windows flake already in known-issues); green standalone and on the rerun.
Proposed memory updates:
- decisions.md (date 2026-10-18): "T-068 (2.14.1): the evidence gate validates only claimed evidence - paths after an evidence marker, or a bare repository path list - so path-looking Result prose (the T-034 flagged tokens, schema locations) no longer fails scope checks; declared evidence outside the task scope or missing on disk still fails."