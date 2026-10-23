# T-110: Roadmap UI carrier - T-046 artifact under corrected scope declaration

Role: developer
Tool: devin
Stage: 5
Depends on: none
Branch: t-110-dashboard-ui-carrier
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-110-dashboard-ui-carrier
Independent check: none - the artifact at 822c3ec is byte-identical to what T-109 verified (real-browser render at 390/1280/1920/3840, allowlist audit, scope/integrity); the recorded checks on that exact SHA are the proof (T-046 contract, corrected scope declaration only)
Resume: none

## Goal

Mechanical carrier task, identical to the T-095 precedent: T-046 was
rejected for an authoring defect in its contract - the Allowed bullet
`.agentflow/dashboard/roadmap*.{html,css,js}` splits at the comma inside the
braces (paths() takes only the first token per bullet, and glob_match does
no brace expansion), so the artifact's own files are outside the parseable
scope and verify can never pass. The artifact itself is complete and
independently verified at commit
822c3ecff773e40427197d16098d8531703f0d95 on branch t-046-dashboard-ui.

Move this task's new branch onto that commit (git reset --hard from the
launcher-created start, clean tree), run the three Checks verbatim, write
the Result section. No code edits.

Result authoring - the evidence rule that has now tripped four times: put
`evidence:` markers at line END followed only by the intended claim paths;
every path-looking token after a marker is parsed as a claim (so
`DATA.stages`, `title/id`, `pass/fail/stale/pending/unknown` etc. all
become claimed paths). Keep prose free of slash/dotted tokens after the
marker; mention them before it or in plain words.

## Read first

- .agentflow/tasks/T-046-dashboard-ui.md (the artifact and its Result section)
- .agentflow/tasks/T-109-verify-dashboard-ui.md (the independent verification - verdict pass)

## Allowed files

- .agentflow/dashboard/template.html
- .agentflow/dashboard/graph_template.html
- .agentflow/dashboard/common.css
- .agentflow/dashboard/common.js
- .agentflow/dashboard/filterbar.js
- .agentflow/dashboard/filterbar.css
- .agentflow/dashboard/roadmap_template.html
- .agentflow/dashboard/roadmap.css
- .agentflow/dashboard/roadmap.js
- .agentflow/dashboard/build.py
- .agentflow/dashboard/README.md
- .agentflow/tests/test_dashboard.py
- .agentflow/VERSION
- AGENTS.md
- CHANGELOG.md

## Do not touch

- .agentflow/state/
- .agentflow/tasks/ (other Task Files)
- .agentflow/tools/
- .github/
- .agentflow/dashboard/out/ and versions/ (generated/local)
- other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] C-01: The branch tip is exactly 822c3ecff773e40427197d16098d8531703f0d95 - the T-109-verified artifact, byte-identical (git reset --hard; no new edits).
- [ ] C-02: All three Checks pass verbatim on that SHA.
- [ ] C-03: The Result records the carried artifact honestly: `Change: 822c3ecff773e40427197d16098d8531703f0d95`, the T-109 verification basis, and no new unverified claims.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py`
- `python .agentflow/dashboard/build.py`
- `python .agentflow/dashboard/build.py --demo`

## Result
Outcome: completed
Change: 822c3ecff773e40427197d16098d8531703f0d95 on t-110-dashboard-ui-carrier

Carrier note: mechanical carry per the Goal. `git reset --hard` moved this
branch from the launcher-created start (8c927718) onto the exact T-046
artifact commit; no code edits, no new commit, worktree clean. The
byte-identical tree was independently verified by T-109 (Verdict: pass -
real-browser render at 390/1280/1920/3840, payload allowlist audit, scope
and integrity), recorded in that task's own Result; this carry adds no new
verification of its own.

Files:
- none edited by this task - the branch tip is the carried commit itself;
  per-file contents are listed in the T-046 Result

Checks:
- `python -m unittest discover -s .agentflow/tests -p test_dashboard.py` -> pass (36 passed / 0 failed)
- `python .agentflow/dashboard/build.py` -> pass (92 tasks, 6 stages, 93 dependencies, 21 successors, 216 commits -> out)
- `python .agentflow/dashboard/build.py --demo` -> pass (8 tasks, 7 stages, 2 dependencies, 1 successors, 24 commits -> out [DEMO DATA])

Criteria:
- C-01: pass - `git rev-parse HEAD` returns exactly the target commit; tree clean after reset and after the build checks; the roadmap page sources carried byte-identical evidence: .agentflow/dashboard/roadmap_template.html, .agentflow/dashboard/roadmap.js, .agentflow/dashboard/roadmap.css
- C-02: pass - all three Checks run verbatim on this SHA in this worktree; outputs above
- C-03: pass - this Result names the carried SHA, states the T-109 verification basis, and makes no new unverified claims

Found, not fixed:
- carried from T-109, pre-existing and unchanged by this carry: the shared header title overflows narrow widths when the project folder name is long; snapshot.py does not version the new roadmap sources (documented in the 2.15.9 migration notes)

Proposed memory updates:
- none - the T-109 verdict already stands as the verification record; a decisions entry belongs to the acceptance step, not this carrier
