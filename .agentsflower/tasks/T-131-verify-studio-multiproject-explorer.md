# T-131: Verify Studio multi-project explorer, context sync and authorization gate

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-130 @ 1d2aafed623222e1b4b88d3cea068bc7cee351c4
Branch: t-131-verify-studio-multiproject-explorer
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-131-verify-studio-multiproject-explorer
Independent check: none
Resume: none
Routing exception: human authorized tester verification for Studio multi-project explorer (2026-10-24)

## Goal

Independently verify T-130 (Studio multi-project explorer, context sync and authorization gate):
1. Run `test_studio.py` and the full test suite.
2. Verify path traversal safety on `/api/project/tree` and `/api/file/read`.
3. Verify that project creation/update requires `authorized: true` and is rejected with 403 otherwise.
4. Record verdict in ## Result.

## Read first

- .agentsflower/tasks/T-130-studio-multiproject-explorer-sync.md
- .agentsflower/roles/tester.md

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes (18/18).
- [ ] V-02: Full regression test suite passes without regressions.
- [ ] V-03: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (18 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (510 passed / 0 failed, 4 skipped)
Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-131.evidence/T-131.check1_test_studio.txt ("Ran 18 tests in 2.686s", "OK")
- V-02: pass - evidence: .agentsflower/tasks/.runtime/T-131.evidence/T-131.check2_full_suite.txt ("Ran 510 tests in 396.460s", "OK (skipped=4)")
- V-03: pass - independent probes on detached HEAD 1d2aafe confirm boundary and gate behavior; see Independent verification below and .agentsflower/tasks/.runtime/T-131.evidence/T-131.probe_results.txt
Independent verification (beyond the unit suite, live StudioHandler probes):
- /api/project/tree rejects `..`, `../..`, `..\..`, `.agentsflower/../../..`, `a/../../b`, raw `%2e%2e%2f%2e%2e`, NUL byte and an absolute path outside the project root ("path outside project or not a directory"); an existing but unregistered directory gets HTTP 403.
- /api/file/read rejects `../AGENTS.md`, `../../outside.txt`, `..\..\x`, `.agentsflower/../../CLAUDE.md` and raw `%2e%2e%2f` with HTTP 403; an unregistered project dir gets 403 and no file content leaks.
- A directory junction created inside the repo root pointing at %TEMP% was rejected by both endpoints (resolve() runs before the boundary check in safe_under, studio.py:177-191); no OUTSIDE-MARKER content leaked.
- /api/project/create and /api/project/update return HTTP 403 with requires_authorization:true when `authorized` is missing, false, the string "true", or the int 1; no .agentsflower directory was created and install.py did not run. The gate sits before mkdir/subprocess (studio.py:558-576).
- resolve_known_project (studio.py:152-174) only resolves paths matching the registered workspace set, so the file endpoints cannot be pointed at arbitrary directories.
New defects (outside the task):
- none found
Notes:
- `....`/`...`-style inputs resolve to the project root itself on Windows (trailing-dot stripping) and return the root listing - same exposure as an empty path, not a boundary escape.
- Verified on detached HEAD 1d2aafed623222e1b4b88d3cea068bc7cee351c4 in disposable checkout worktrees/agentsflower-t-130-studio-multiproject-explorer.t-131; worktree left clean (git status empty).
Cannot verify, needs:
- UI-facing criteria (accordion rendering, Explorer layout vs mockup, modal UX) exercised only via HTTP/API level and the developer's own report; no browser-driven check was run - the referenced mockup file is not in the repository. This does not block V-01..V-03, which are API/suite scoped.
Proposed memory updates:
- Studio's file/git/graft endpoints are bound to registered workspaces via resolve_known_project + safe_under; any future file-write or execute endpoint must reuse them.
