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
Outcome: completed
Change: 914f968 on t-139-skill-frontend-art-direction
Files:
- .agentsflower/skills/frontend-art-direction/SKILL.md - spec-compliant router (<=500 lines): YAML frontmatter (name, description, license, metadata.domain=1, metadata.source both upstream ids, metadata.license MIT), core rules, on-demand reference routing table, tester-verifiable Definition of done
- .agentsflower/skills/frontend-art-direction/references/anti-slop-guidelines.md - banned-default signature (centered hero + 3 icon cards + soft gradient), direction-dealing, translucent shadows vs opaque borders, strict typography scale rules
- .agentsflower/skills/frontend-art-direction/references/micro-motion-easing.md - easing direction matrix (ease-out on enter, never ease-in), duration budgets, transform/opacity-only properties, prefers-reduced-motion compliance, no hover-only affordances
- .agentsflower/skills/frontend-art-direction/references/design-tokens-wcag.md - 3-tier token architecture, dark-mode palettes via luminance not borders, WCAG 2.1 AA/AAA contrast table (>=4.5:1 text, >=3:1 large text/UI/focus)
- .agentsflower/skills/INDEX.md - registered as Active Built-in Skill, marked *(Built-in)* in domain 1 row
- .agentsflower/skills/ATTRIBUTION.md - Distilled Skills table with upstream repo, path, MIT license, and real commit pins (taste-skill 6010f91, emilkowalski/skills 2d22863, main @ 2026-10-25)
- .agentsflower/tests/test_skills.py - new FrontendArtDirectionSkillTests: 5 tests covering package structure, spec frontmatter, reference link resolution, concrete-rule content, INDEX/ATTRIBUTION registration
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_skills.py"` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> fail (528 passed / 2 failed / 4 skipped of 530); both failures are test_run_task.py setUp hitting transient WinError 5 in ledger.py _write_atomic os.replace - the documented 2026-10-18 known-issues flake, unrelated to this change (no code touched); isolated rerun `python -m unittest discover -s .agentsflower/tests -p "test_run_task.py"` -> pass (63 passed / 0 failed)
Criteria:
- C-01: pass - .agentsflower/skills/frontend-art-direction/SKILL.md exists with closed YAML frontmatter (name: frontend-art-direction, description, metadata.domain: 1, metadata.source listing Leonxlnx/taste-skill@main and emilkowalski/design-eng@main, metadata.license: MIT) and routes to references/ via links; 56 lines, under the 500 cap; asserted by test_skill_frontmatter_conforms_to_spec and test_skill_routes_to_existing_references
- C-02: pass - all three references/*.md exist with concrete actionable rules (anti-slop ban list + direction-dealing + translucent-shadow/typography rules; ease-out-on-enter matrix + prefers-reduced-motion block; token tiers + dark-mode palette rules + 4.5:1 / 3:1 WCAG ratios); asserted by test_references_provide_concrete_rules
- C-03: pass - .agentsflower/skills/INDEX.md lists frontend-art-direction under Active Built-in Skills and marks it Built-in in the domain-1 row; .agentsflower/skills/ATTRIBUTION.md records both upstream repos, upstream paths, MIT license, and commit pins; asserted by test_registered_in_index_and_attribution
- C-04: pass - .agentsflower/tests/test_skills.py gained 5 integrity tests, all pass (8/8 in the file); full-suite run shows only the documented transient ledger WinError 5 flake, green on isolated rerun
Found, not fixed:
- The Task File's upstream id `emilkowalski/design-eng@main` names no such repository; it resolves to skill `emil-design-eng` inside `emilkowalski/skills` (MIT, main HEAD 2d22863 verified via git ls-remote). metadata.source keeps the task-mandated string; ATTRIBUTION.md records the resolved repo and path.
- test_run_task.py transient WinError 5 on ledger _write_atomic reproduced once in a full-suite run; already documented in known-issues (2026-10-18) - a bounded hardening task may apply the retry pattern used in machine_capacity.
Proposed memory updates:
- known-issues candidate: task-file `metadata.source` ids may name skills, not repos (T-139 `emilkowalski/design-eng` -> `emilkowalski/skills` path `emil-design-eng`); Orchestrator should resolve ids to real repo+path when authoring attribution contracts.
