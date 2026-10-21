# T-048: Dashboard integration - packaged assets, installer preservation, docs and release metadata

Role: developer
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-110
Branch: t-048-dashboard-integration
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-048-dashboard-integration
Independent check: tester
Resume: none

## Goal

Complete the roadmap dashboard rollout inside the template: the packaged
distribution carries the new dashboard assets, install.py --update delivers
them while preserving project-owned plans/state, and every document describes
the shipped behavior.

## Read first

- .agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md (section 7)
- .agentflow/dashboard/README.md, UI-RULES.md (documentation deltas from T-044/T-046)
- .agentflow/tools/install.py, cli.py, upstream.py (asset delivery surface)
- pyproject.toml, setup.py, MANIFEST.in
- .agentflow/tests/check_package.py, test_install.py, test_layout.py, test_dashboard*.py
- README.md, GUIDE.md, GUIDE.ru.md, RELEASE_NOTES.md, .agentflow/docs/ai-handoff-protocol.md (dashboard section), .agentflow/docs/release-validation.md

## Allowed files

- pyproject.toml
- setup.py
- MANIFEST.in
- .agentflow/tools/install.py (only if packaged asset delivery requires it)
- .agentflow/tools/cli.py (dashboard command surface only if changed)
- .agentflow/dashboard/README.md
- .agentflow/dashboard/UI-RULES.md (data-contract/rule deltas only)
- .agentflow/docs/ai-handoff-protocol.md (dashboard/data-contract section only)
- .agentflow/docs/release-validation.md
- README.md
- GUIDE.md
- GUIDE.ru.md
- RELEASE_NOTES.md
- .agentflow/tests/ (any file)
- .agentflow/VERSION
- AGENTS.md (AgentFlow block version line only)
- CHANGELOG.md

## Do not touch

- .agentflow/state/, .agentflow/tasks/ (other Task Files), .agentflow/docs/project-plan.md
- .agentflow/dashboard/build.py, templates, common.*, filterbar.*, roadmap page assets (T-046 owns them; report defects found, do not patch)
- .github/
- other projects and their machine leases

## Setup

- python .agentflow/dashboard/snapshot.py save "pre-roadmap-integration" (record output in Result)

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] I-01: The wheel/sdist carry every new dashboard asset (roadmap page, mockups excluded or explicitly justified); a package built from the sdist reproduces them outside the source checkout; zero new runtime dependencies.
- [ ] I-02: install.py --update delivers the new dashboard files to a disposable fixture project (a scratch directory under temp, never a real installed project - repository-only scope) and preserves project-owned plans, state, Task Files and settings; legacy project-plan syntax needs no migration; new optional metadata never overwrites project-owned content. Tested against a disposable fixture carrying an old-format plan.
- [ ] I-03: Documentation synchronized and truthful: dashboard README data contract and UI-RULES deltas, protocol dashboard section, root README/GUIDE.md/GUIDE.ru.md (roadmap view, the build/open command, snapshot rollback), RELEASE_NOTES and release-validation.md reflect exact verification status; no invented CI results, screenshots or listings.
- [ ] I-04: `python .agentflow/dashboard/build.py` on a fresh disposable fixture install produces the full page set offline; the dashboard command (cli.py) exposes the roadmap page where applicable.
- [ ] I-05: VERSION/AGENTS block/CHANGELOG aligned as the Stage 5 dashboard release with honest migration notes for installed projects. Propose dated decisions.md text in the Result.
- [ ] I-06: Full suite passes verbatim plus check_package.py.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_install.py` - installer preservation and asset delivery.
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` - template structure.
- `python .agentflow/tests/check_package.py` - packaged assets outside the checkout.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite.

## Result
