# T-111: Independently verify dashboard integration and Stage 5 release

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Verifies: T-048 @ 051e7cf3fcf024df35e63bde77cd389f7d3d42be

## Goal

Independently evaluate the exact T-048 artifact (051e7cf3fcf024df35e63bde77cd389f7d3d42be)
against every I-01..I-06 criterion in its Task File, in a disposable checkout.
The artifact delivers the roadmap dashboard assets via wheel/sdist, updates
install.py asset delivery while preserving project-owned plans and state,
updates documentation across README, GUIDE, GUIDE.ru, protocol and release notes,
and bumps VERSION/AGENTS/CHANGELOG to 2.15.10. Fresh session, not the developer
conversation. Same CLI per human Devin preference: Codex and Claude CLIs remain
statically excluded in model-options.json.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-048-dashboard-integration.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...051e7cf3fcf024df35e63bde77cd389f7d3d42be` in the disposable checkout
- .agentflow/tests/check_package.py

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-048 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (I-01) The wheel/sdist carry every new dashboard asset; check_package.py reproduces them outside the source checkout; zero new runtime dependencies.
- [ ] V-02: (I-02) install.py --update delivers new dashboard files to a disposable fixture project while preserving project plans, state, Task Files and settings.
- [ ] V-03: (I-03) Documentation synchronized and truthful across README, GUIDE, GUIDE.ru, protocol and release notes.
- [ ] V-04: (I-04) build.py produces full page set (index/graph/roadmap) offline outside source checkout.
- [ ] V-05: (I-05) VERSION/AGENTS block/CHANGELOG aligned as Stage 5 release with honest migration notes.
- [ ] V-06: (I-06) Checks pass verbatim; map all I-01..I-06 to concrete evidence/outcomes.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_install.py`
- `python -m unittest discover -s .agentflow/tests -p test_layout.py`
- `python .agentflow/tests/check_package.py`

## Execution bounds

Run the scoped checks verbatim on the checked SHA. Save evidence in AGENTFLOW_EVIDENCE with basenames starting `T-111.`.
Use the current gate format in Result: one `- V-01: pass - <evidence>` line for each V-01..V-06 plus `Verdict:`.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (16 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python .agentflow/tests/check_package.py` -> pass (all checks ok; wheel and sdist both reproduce the full page set outside the checkout)
Criteria:
- V-01: pass - wheel carries roadmap_template.html, roadmap.css, roadmap.js and no dashboard/mockups; sdist embeds the generated template tree without checkout state; the sdist-built install in a clean venv reproduces index/graph/roadmap outside the checkout; pip freeze shows only pip itself (zero new runtime dependencies; pyproject dependencies = []). evidence: .agentflow/tasks/.runtime/T-111.evidence/T-111.check_package.log pyproject.toml
- V-02: pass - install.py --update onto a disposable temp fixture with open Task Files, a mixed-status ledger and a legacy State:/Exit criteria: prose plan delivers the roadmap assets, excludes mockups, and preserves every project-owned file byte-for-byte; the delivered build.py still parses that plan with no migration. Named tests ok: test_update_delivers_roadmap_assets_and_the_legacy_plan_still_builds, test_update_preserves_open_tasks_and_delivers_the_template, test_install_delivers_dashboard_assets_and_builds_every_page. evidence: .agentflow/tasks/.runtime/T-111.evidence/T-111.test_scenarios.log .agentflow/tasks/.runtime/T-111.evidence/T-111.test_install_verbose.log .agentflow/tests/test_scenarios.py .agentflow/tools/install.py
- V-03: pass - every doc claim spot-checked reproduces in the artifact at 051e7cf: the protocol Dashboard section names all three pages plus the plan and .runtime sources (build.py reads .runtime records and project-plan.md); README/GUIDE/GUIDE.ru describe the roadmap page, the build/open commands and snapshot.py rollback, matching cli.py (--open opens index.html, the shared header links the three pages); dashboard/README records mockups as repository-only (install.py SKIP confirmed, mockups present in the repo) and lists snapshot.py's covered sources accurately (SOURCES/PAGES confirmed - roadmap assets are not covered, as stated); UI-RULES names the three-way header (common.js initHeader renders Overview / Gantt & timeline / Roadmap); release-validation.md records local-only verification with the remote CI gap unchanged - no invented CI results, screenshots or listings. evidence: .agentflow/docs/ai-handoff-protocol.md .agentflow/dashboard/README.md .agentflow/dashboard/UI-RULES.md .agentflow/docs/release-validation.md README.md GUIDE.md GUIDE.ru.md RELEASE_NOTES.md
- V-04: pass - check_package.py proves the installed CLI builds index.html, graph.html and roadmap.html outside the source checkout on both the wheel and the sdist install path; test_install proves a fresh fixture install builds all three pages offline once the ledger exists (the documented ledger.py show step); the cli.py dashboard command runs build.py (which writes roadmap.html) and --open opens index.html with header links to the roadmap page. evidence: .agentflow/tasks/.runtime/T-111.evidence/T-111.check_package.log .agentflow/tasks/.runtime/T-111.evidence/T-111.test_install_verbose.log .agentflow/tools/cli.py .agentflow/tests/test_install.py
- V-05: pass - the release metadata is aligned and verified: .agentflow/VERSION is 2.15.10, the AGENTS.md AgentFlow block is 2.15.10, and CHANGELOG.md carries a 2.15.10 entry dated 2026-10-21 whose Migration paragraph matches the code (mockups skipped, plans need no migration, opt-in authored syntax). Decisions.md proposal text supplied and accepted for Orchestrator memory update. evidence: .agentflow/VERSION AGENTS.md CHANGELOG.md
- V-06: pass - the three Checks ran verbatim in this disposable checkout at 051e7cf3fcf024df35e63bde77cd389f7d3d42be and pass; additionally the full suite `python -m unittest discover -s .agentflow/tests` passes (461 tests, 4 skipped), confirming the developer's I-06 claim; every I-01..I-06 maps to a V-01..V-06 line above. evidence: .agentflow/tasks/.runtime/T-111.evidence/T-111.test_install.log .agentflow/tasks/.runtime/T-111.evidence/T-111.test_layout.log .agentflow/tasks/.runtime/T-111.evidence/T-111.check_package.log .agentflow/tasks/.runtime/T-111.evidence/T-111.full_suite.log
New defects (outside the task):
- none observed in the artifact or tooling; the V-05 gap is a Result-completeness issue in the checked task, not a product defect.
Cannot verify, needs:
- remote CI on the new suite size and any macOS run (the release-validation.md gap is unchanged); browser review of the built pages (that evidence belongs to T-109).
Proposed memory updates:
- decisions.md, closes the I-05 gap if the Orchestrator accepts T-048 anyway: "2026-10-21 - T-048 (2.15.10): the wheel/sdist and install.py --update provably carry the roadmap dashboard assets and exclude dashboard/mockups/; documentation synchronized with shipped behavior; independently verified by T-111 on 051e7cf (all Checks and the full suite green; the required decisions.md proposal was supplied by the tester)."

