# T-123: Specialized Skills Ecosystem: 9-Domain Taxonomy & Packaging

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-113
Branch: t-123-skills-taxonomy-packaging
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-123-skills-taxonomy-packaging
Independent check: tester
Resume: none
Routing exception: human authorized skills ecosystem implementation (2026-10-24)

## Goal

Create template-owned `.agentsflower/skills/` directory structure across 9 specialized agent domains (`INDEX.md`) and register packaging in `install.py`.

## Read first

- .agentsflower/tasks/T-113-skills-ecosystem-research.md

## Allowed files

- `.agentsflower/skills/INDEX.md`
- `.agentsflower/tools/install.py`
- `.agentsflower/tests/test_skills.py`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: 9-domain taxonomy documented in `.agentsflower/skills/INDEX.md`.
- [ ] C-02: `install.py` tracks `.agentsflower/skills/` as template-owned assets.
- [ ] C-03: `test_skills.py` validates skills structure.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"

## Result

Outcome: completed
Change: d123001
Criteria:
- C-01: pass - 9 domains defined with canonical structure and metadata.
- C-02: pass - install.py copies skills directory on template install/update.
- C-03: pass - test_skills.py passes cleanly.
