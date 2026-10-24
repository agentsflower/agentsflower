# T-139: Domain 1 Specialized Skill: frontend-art-direction and UI Polish

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Branch: t-139-skill-frontend-art-direction
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-139-skill-frontend-art-direction
Independent check: tester
Resume: none
Routing exception: human authorized Phase P1 skill implementation (2026-10-25)

## Goal

Implement Domain 1 specialized skill `frontend-art-direction` adhering to `agentskills.io` specification and `.agentsflower/docs/skills-implementation-roadmap.md`:

1. **Skill Package Directory:** `.agentsflower/skills/frontend-art-direction/`
   - `SKILL.md`: Spec-compliant router (<= 500 lines) with YAML frontmatter:
     - `name`: `frontend-art-direction`
     - `description`: Anti-slop UI design system, modern aesthetics, typography scales, micro-motion easing rules, and accessible contrast guidelines.
     - `metadata.domain`: `1`
     - `metadata.source`: `Leonxlnx/taste-skill@main` + `emilkowalski/design-eng@main`
     - `metadata.license`: `MIT`
   - `references/anti-slop-guidelines.md`: The concrete anti-slop rules (never centered hero + 3 icon cards as entire design; translucent shadows instead of opaque borders; strict typography hierarchy).
   - `references/micro-motion-easing.md`: Transition rules (only `ease-out` / decelerating curves on enter, never `ease-in` on enter; `prefers-reduced-motion` compliance).
   - `references/design-tokens-wcag.md`: Color token systems, dark mode palettes, WCAG 2.1 AA/AAA contrast ratios (>= 4.5:1 text, >= 3:1 UI components).

2. **Testing & Registration:**
   - Register in `.agentsflower/skills/INDEX.md` as Active Built-in Skill.
   - Update `.agentsflower/skills/ATTRIBUTION.md` with source pin and MIT license.
   - Add unit tests in `.agentsflower/tests/test_skills.py` asserting structure, frontmatter, references, and validation rules.

## Read first

- .agentsflower/docs/skills-implementation-roadmap.md
- .agentsflower/docs/skills-ecosystem-catalog.md
- .agentsflower/skills/INDEX.md
- .agentsflower/skills/geo-seo-audit/SKILL.md
- .agentsflower/tests/test_skills.py

## Allowed files

- `.agentsflower/skills/frontend-art-direction/*`
- `.agentsflower/skills/INDEX.md`
- `.agentsflower/skills/ATTRIBUTION.md`
- `.agentsflower/tests/test_skills.py`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: `.agentsflower/skills/frontend-art-direction/SKILL.md` conforms to spec with frontmatter and references.
- [ ] C-02: `references/anti-slop-guidelines.md`, `references/micro-motion-easing.md`, and `references/design-tokens-wcag.md` exist and provide concrete actionable rules.
- [ ] C-03: `INDEX.md` and `ATTRIBUTION.md` updated with upstream attribution.
- [ ] C-04: `test_skills.py` verifies skill integrity and all tests pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
