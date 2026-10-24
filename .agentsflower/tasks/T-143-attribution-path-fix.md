# T-143: ATTRIBUTION upstream-path repair - T-139 artifact successor

Role: developer
Tool: devin
Model: swe-2-high
Backup Tool: agy
Backup Model: gemini-3.8-flash-high
Stage: 7
Depends on: T-142
Branch: t-143-attribution-path-fix
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-143-attribution-path-fix
Independent check: tester
Resume: none

## Goal

Successor of rejected T-139: the independent check (T-142, `Verdict: partial`,
V-05) found that `.agentsflower/skills/ATTRIBUTION.md`'s taste-skill row records
`design-taste-frontend` in the "Upstream path" column - that is the upstream
skill's `name:` field, not a repository path (upstream
`GET /repos/Leonxlnx/taste-skill/contents/design-taste-frontend` -> 404 at the
pinned commit; the real path is `skills/taste-skill`). The rest of the artifact
at commit `914f968b27501fc2e57dc7a62fbb958456b84ca3` on branch
`t-139-skill-frontend-art-direction` passed every other criterion.

Branch this task's branch onto that preserved commit (git reset --hard from the
launcher-created start, clean tree), then repair exactly that one cell:

- taste-skill row, "Upstream path" column: `design-taste-frontend` ->
  `` `skills/taste-skill` (skill name `design-taste-frontend`) ``, mirroring the
  emilkowalski row's parenthetical style.
- Nothing else changes: no content, test, INDEX.md, or metadata edits.

## Read first

- .agentsflower/tasks/T-139-skill-frontend-art-direction.md (rejected contract; its artifact is your base)
- .agentsflower/tasks/T-142-verify-frontend-art-direction.md (the independent verdict and the defect evidence)

## Allowed files

- `.agentsflower/skills/frontend-art-direction/*`
- `.agentsflower/skills/INDEX.md`
- `.agentsflower/skills/ATTRIBUTION.md`
- `.agentsflower/tests/test_skills.py`

## Do not touch

- All other files.

## Setup

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] D-01: The branch is moved onto `914f968b27501fc2e57dc7a62fbb958456b84ca3` once; the delta vs that commit is only the ATTRIBUTION.md cell repair and `git diff main...HEAD` stays inside this contract's Allowed files.
- [ ] D-02: ATTRIBUTION.md's taste-skill row records the real upstream repository path `skills/taste-skill` (skill name `design-taste-frontend` noted parenthetically); the row keeps repo link, MIT license and commit pin unchanged.
- [ ] D-03: Both Checks pass verbatim on the branch HEAD.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->
Outcome: completed
Change: 63e03281ecd45a83826932fccde39f64fa5e03af on t-143-attribution-path-fix
Files:
- .agentsflower/skills/ATTRIBUTION.md - taste-skill row "Upstream path" cell repaired: `design-taste-frontend` -> `skills/taste-skill` (skill name `design-taste-frontend`); one insertion / one deletion, nothing else touched
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_skills.py"` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (526 passed / 0 failed / 4 skipped of 530)
Criteria:
- D-01: pass - branch reset --hard onto 914f968b27501fc2e57dc7a62fbb958456b84ca3 once (parent of HEAD commit verified by git rev-parse HEAD^); `git diff 914f968..HEAD` is exactly ATTRIBUTION.md, 1 insertion / 1 deletion (the cell repair); `git diff main...HEAD` names exactly the 7 T-139 artifact files plus ATTRIBUTION.md, all inside this contract's Allowed files (skills/frontend-art-direction/*, INDEX.md, ATTRIBUTION.md, test_skills.py). evidence: .agentsflower/skills/ATTRIBUTION.md
- D-02: pass - taste-skill row now records the real repository path `skills/taste-skill` with the upstream skill name `design-taste-frontend` noted parenthetically, mirroring the emilkowalski row; repo link, MIT license and commit pin `6010f91a9935f1c167dfc500fb1a475681892e6b` unchanged. Path verified live: GET /repos/Leonxlnx/taste-skill/contents/skills/taste-skill?ref=6010f91a -> 200, /contents/design-taste-frontend?ref=6010f91a -> 404. evidence: .agentsflower/skills/ATTRIBUTION.md
- D-03: pass - both Checks pass verbatim on branch HEAD 63e0328: test_skills.py "Ran 8 tests / OK"; full suite "Ran 530 tests in 374.306s / OK (skipped=4)".
Found, not fixed:
- First verbatim full-suite run (pre-commit tree, identical content) showed 2 transient PermissionError [WinError 5] failures in disposable-fixture ledger.py _write_atomic os.replace (test_hooks.CodexStopTests.test_a_blocked_task_is_never_a_reason_to_continue, test_run_task.RunTaskTests.test_stop_with_a_confirmed_identity_kills_the_worker) - the flake already documented in known-issues.md (2026-10-18) and noted in T-142's verdict; both files green on isolated re-run (13/13 and 63/63) and the verbatim full suite green on re-run on HEAD.
Proposed memory updates:
- none; the id-vs-path ATTRIBUTION lesson is already covered by T-142's proposed known-issues candidate.
