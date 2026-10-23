# T-011: Final local review of v2.12.0 release preparation

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-010
Verifies: T-010 @ 0fcd77398b7d0ce42466c35a4b24d05b8d214762

## Goal

Independently review the local v2.12.0 release preparation at the verified
commit: English public documentation, README, release notes, synchronized
metadata and packaged assets. This is the final LOCAL review before the human's
manual push; remote nine-job CI and macOS results are a separate release gate
and must be recorded as honestly pending, never invented. No product changes.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-010-public-release-docs.md
- README.md
- GUIDE.md
- GUIDE.ru.md
- CHANGELOG.md
- RELEASE_NOTES.md
- AGENTS.md
- .agentflow/README.md
- .agentflow/VERSION
- .agentflow/docs/release-validation.md
- .agentflow/docs/agentflow-production-roadmap.txt
- .agentflow/tests/test_layout.py
- .agentflow/tests/test_install.py
- pyproject.toml
- .agentflow/tools/cli.py
- .agentflow/tools/mcp_server.py
- .agentflow/docs/assets/dashboard.png

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/, .agentflow/tests/, .agentflow/dashboard/
- .agentflow/state/, .agentflow/tasks/
- developer worktree/branch, README.md, GUIDE.md, GUIDE.ru.md, CHANGELOG.md,
  RELEASE_NOTES.md, pyproject.toml, .agentflow/VERSION, AGENTS.md,
  .agentflow/docs/assets/dashboard.png (evidence goes to the task's .runtime
  evidence directory, referenced from Result)

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: GUIDE.md is a complete accurate English guide: source and package
  installation, update preservation, Windows/Linux/macOS paths, optional MCP
  and orchestrator flag, resource opt-in, worker lifecycle, honest metrics and
  demo, recovery, permission boundaries; conductor/autostart marked
  Windows-only; every documented command matches cli.py / run_task.py /
  install.py --help output; every link resolves to an existing file.
  GUIDE.ru.md preserves the previous Russian guide unchanged in content.
- [ ] V-02: README is truthful: clear value proposition; badges make no
  invented green CI result; the Mermaid diagram shows the Orchestrator as
  single memory writer, Task File contracts, isolated Developer/Tester
  artifacts, gate verify and accept; the Deployer consumes an accepted SHA
  with human approval and is not drawn as a developer merge flow or as a
  universal sandbox guarantee.
- [ ] V-03: Production section honesty: dated October 2026 human-attested
  figures are presented as an aggregate snapshot without claiming deduplicated
  unique people or new telemetry; no guessed extension IDs or listing URLs;
  unresolved links are recorded explicitly in RELEASE_NOTES.md rather than
  invented.
- [ ] V-04: Assets and metadata: .agentflow/docs/assets/dashboard.png is the
  real T-008 capture with visible demo/sample attribution in docs; VERSION,
  AGENTS block, CHANGELOG and package metadata are all 2.12.0-consistent;
  RELEASE_NOTES lists final behavior, known evidence limits and the
  human-only push/CI/tag commands including the exact tag line; nothing was
  pushed, published or tagged by the task.
- [ ] V-05: The four verbatim checks pass on the verified commit in a
  disposable checkout; developer worktree, branch and Task File baselines
  unchanged; known evidence limits (remote CI jobs, macOS pass, unresolved
  store URLs) are stated as pending, not claimed.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - links and repository layout.
- `python -m unittest discover -s .agentflow/tests -p test_install.py` - synchronized generated entry points.
- `python .agentflow/tests/check_package.py` - final wheel metadata/resources.
- `python -m unittest discover -s .agentflow/tests` - full regression suite.

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python .agentflow/tests/check_package.py` -> pass (all checks: wheel+sdist build, bundled template, `agentflow --version` prints 2.12.0, install/update on spaced path)
- `python -m unittest discover -s .agentflow/tests` -> pass (204 tests, OK, 3 skipped, 149.7s)
Evidence summary: .agentflow/tasks/.runtime/T-011.evidence/checks.txt
Criteria:
- V-01 GUIDE.md complete accurate English guide - pass - evidence: read in full at 0fcd773; covers source + local package install, update preservation, workspace, Windows/Linux/macOS paths, MCP opt-in with `--enable-orchestrator-tools`, machine-resource opt-in, worker lifecycle, honest metrics/`--demo`, recovery, permission boundaries; conductor/autostart marked Windows-only. Documented `agentflow` subcommands match cli.py parsers (install, run, gate, accept, ledger, mcp, dashboard) and run_task.py/install.py flags match their usage strings. All GUIDE/README links resolve to existing files. GUIDE.ru.md git blob 445608be is byte-identical to pre-T-010 GUIDE.md.
- V-02 README truthful - pass - evidence: badges claim no green result (CI badge links to the workflow itself); Mermaid shows Orchestrator as single memory writer, Task File contracts, isolated Developer worktree / Tester disposable checkout, gate.py verbatim checks, accept.py merge, Deployer consuming an accepted SHA after human approval; text explicitly says isolation is worktree+end-checks, "not a universal sandbox guarantee".
- V-03 production section honesty - pass - evidence: dated October 2026 maintainer-attested figures with explicit "aggregate snapshot across listings, not deduplicated unique people" caveat; only verified https://aisidebar.app linked, no guessed extension IDs; unresolved store links recorded in RELEASE_NOTES.md "Evidence status and limits".
- V-04 assets and metadata - pass - evidence: .agentflow/docs/assets/dashboard.png (92146 bytes) opened and visually confirmed as a real T-008-era dashboard capture of this repository's own task data; README caption says real local capture. VERSION, AGENTS.md block, CHANGELOG 2.12.0 entry and pyproject (dynamic version from VERSION) all read 2.12.0. RELEASE_NOTES lists final behavior, evidence limits and human-only push/CI/tag/release steps including the exact `git tag -a v2.12.0 -m "..."` line. `git tag -l` shows only v2.4.0/v3.0.0; origin/main is 960f892 so nothing was pushed, published or tagged.
- V-05 verbatim checks in disposable checkout - pass - evidence: ran at detached HEAD 0fcd773 in this review worktree; `git status --porcelain` empty before and after; remote nine-job CI, macOS pass and unresolved store URLs are stated as pending in README "Verification status" and RELEASE_NOTES, not claimed.
New defects (outside the task):
- none
Cannot verify, needs:
- Remote nine-job GitHub Actions run and the macOS cell: human-only release gate, correctly recorded as pending; not checkable locally.
- Store listing URLs for "Export Chat from Gemini to Word", "YouTube Transcript", "AI Home Design": maintainer-only knowledge, correctly recorded as unresolved in RELEASE_NOTES.md.
Proposed memory updates:
- session-log: T-011 review of 0fcd773 -> verdict pass; all four checks green (204 tests, check_package ok); docs, metadata and honesty constraints verified; remote CI/macOS/store links remain the explicit human release gate.
