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
