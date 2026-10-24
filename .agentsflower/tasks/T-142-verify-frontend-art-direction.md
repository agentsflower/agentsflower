# T-142: Verify frontend-art-direction skill package and registry integration

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-139 @ 914f968b27501fc2e57dc7a62fbb958456b84ca3
Branch: t-142-verify-frontend-art-direction
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-142-verify-frontend-art-direction
Independent check: none
Resume: none

## Goal

Independently verify T-139 (Domain 1 specialized skill `frontend-art-direction`: spec-compliant `SKILL.md` router <= 500 lines with YAML frontmatter; three concrete references - anti-slop guidelines, micro-motion easing, design tokens WCAG; registration in `skills/INDEX.md` and `skills/ATTRIBUTION.md`; `test_skills.py` integrity tests) against the T-139 contract:

1. Run `test_skills.py` and the full test suite.
2. In the disposable checkout, inspect `.agentsflower/skills/frontend-art-direction/SKILL.md`: closed YAML frontmatter carrying `name: frontend-art-direction`, an anti-slop/aesthetics description, `metadata.domain: 1`, `metadata.source` listing both upstream ids (`Leonxlnx/taste-skill@main`, `emilkowalski/design-eng@main`), `metadata.license: MIT`; body <= 500 lines and routes to `references/` via links.
3. Verify `references/anti-slop-guidelines.md`, `references/micro-motion-easing.md` and `references/design-tokens-wcag.md` exist and carry concrete actionable rules (banned default patterns, translucent shadows vs opaque borders, typography hierarchy; ease-out on enter / never ease-in, `prefers-reduced-motion`; token tiers, dark-mode palettes, WCAG >= 4.5:1 text / >= 3:1 UI components).
4. Verify `INDEX.md` registers the skill as an Active Built-in Skill (marked Built-in in the domain-1 row) and `ATTRIBUTION.md` records upstream repos, paths, MIT license and commit pins.
5. Judge the developer's "Found, not fixed" notes (task-contract upstream id `emilkowalski/design-eng@main` resolving to skill `emil-design-eng` inside `emilkowalski/skills`; the transient test_run_task.py WinError 5 ledger flake already in known-issues) and record verdict in the Result section.

## Read first

- .agentsflower/tasks/T-139-skill-frontend-art-direction.md
- .agentsflower/roles/tester.md
- .agentsflower/skills/INDEX.md

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

- [ ] V-01: Unit test suite in test_skills.py passes.
- [ ] V-02: Full regression test suite passes without regressions attributable to T-139.
- [ ] V-03: SKILL.md conforms to the spec contract (frontmatter fields, <= 500 lines, reference routing).
- [ ] V-04: All three references exist with concrete actionable rules per the contract.
- [ ] V-05: INDEX.md and ATTRIBUTION.md carry the registration and attribution entries.
- [ ] V-06: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->
Outcome: completed
Verdict: partial
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_skills.py"` -> pass (8 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (526 passed / 0 failed / 4 skipped of 530)
Criteria:
- V-01: pass - 8/8 tests in test_skills.py green on the Verifies SHA, including the 5 new FrontendArtDirectionSkillTests (package structure, spec frontmatter, reference link resolution, concrete-rule content, INDEX/ATTRIBUTION registration). evidence: .agentsflower/tasks/.runtime/T-142.evidence/T-142.check-test_skills.txt
- V-02: pass - full suite green on 914f968b27501fc2e57dc7a62fbb958456b84ca3 (detached HEAD, clean tree): "Ran 530 tests in 363.605s / OK (skipped=4)", zero failures - the WinError 5 ledger flake the developer hit did not reproduce here. `git diff main...HEAD` touches exactly the 7 files in T-139's Allowed files, so no out-of-scope regression surface exists. evidence: .agentsflower/tasks/.runtime/T-142.evidence/T-142.check-full-suite.txt .agentsflower/tasks/.runtime/T-142.evidence/T-142.diff-files.txt .agentsflower/tasks/.runtime/T-142.evidence/T-142.head.txt
- V-03: pass - SKILL.md is a 56-line (<= 500) router with closed YAML frontmatter carrying name: frontend-art-direction, an anti-slop/aesthetics description, metadata.domain: 1, metadata.source listing both upstream ids (Leonxlnx/taste-skill@main, emilkowalski/design-eng@main), metadata.license: MIT; body routes to all three references via markdown links (SKILL.md:42-44). evidence: .agentsflower/tasks/.runtime/T-142.evidence/T-142.skill-frontmatter.txt .agentsflower/tasks/.runtime/T-142.evidence/T-142.skill-linecounts.txt
- V-04: pass - all three references exist with concrete actionable rules per the contract: anti-slop-guidelines.md (4-element banned-default signature, direction-dealing, layered translucent-shadow CSS values vs opaque borders, modular type scale / two-family cap / measure and tracking rules), micro-motion-easing.md (enter=ease-out / never ease-in matrix, 100-500 ms duration budgets, transform/opacity-only, prefers-reduced-motion CSS block + JS fallback), design-tokens-wcag.md (3-tier token architecture, dark-mode luminance elevation, WCAG 2.1 table: >= 4.5:1 normal text, >= 3:1 large text / UI components / focus). evidence: .agentsflower/skills/frontend-art-direction/references/
- V-05: partial - INDEX.md registers frontend-art-direction under "Active Built-in Skills" and marks it *(Built-in)* in the domain-1 row (INDEX.md:7,22); ATTRIBUTION.md records both upstream repos, MIT licenses and commit pins, all verified live (taste-skill main = 6010f91a9935f1c167dfc500fb1a475681892e6b, emilkowalski/skills main = 2d228630ba1446365f614a108cb8252f1feda202; both licenses MIT). Defect: the taste-skill row's "Upstream path" cell contains `design-taste-frontend`, which is the upstream skill's `name:` field (and the catalog's skill label), not a path in the repo - GET /repos/Leonxlnx/taste-skill/contents/design-taste-frontend at the pinned commit returns "Not Found"; the real path is `skills/taste-skill`. Fix is one cell: `skills/taste-skill` (optionally noting the skill name `design-taste-frontend`, mirroring the emilkowalski row's parenthetical). evidence: .agentsflower/tasks/.runtime/T-142.evidence/T-142.taste-skill-path-check.txt .agentsflower/tasks/.runtime/T-142.evidence/T-142.upstream-pins.txt .agentsflower/tasks/.runtime/T-142.evidence/T-142.emilkowalski-path-check.txt
- V-06: partial - the verdict is partial (V-05 upstream-path defect), so "Verdict is pass" is not satisfied.
Developer "Found, not fixed" notes evaluated:
- `emilkowalski/design-eng@main` naming no repo: CONFIRMED - git ls-remote returns "Repository not found"; the id resolves to skill `emil-design-eng` at `skills/emil-design-eng` inside `emilkowalski/skills` (repo LICENSE is MIT, main HEAD 2d228630, both verified live; consistent with catalog entry C-09). The resolved repo + path + parenthetical recorded in ATTRIBUTION.md is accurate, and keeping the task-mandated string in metadata.source is correct contract compliance.
- test_run_task.py transient WinError 5 in ledger _write_atomic: CONFIRMED already documented - known-issues.md 2026-10-18 entry names the same os.replace flake and the machine_capacity._replace_retry fix pattern. Unrelated to T-139's file set; did not reproduce in this run.
- Undisclosed counterpart found by this check: the same id-vs-path class on the taste-skill ATTRIBUTION row (V-05) - the developer resolved the emilkowalski path correctly but recorded the taste-skill skill `name` in the path column.
New defects (outside the task):
- none
Cannot verify, needs:
- none
Proposed memory updates:
- known-issues.md candidate: task-contract `metadata.source` ids may name upstream skills, not repos (T-139 `emilkowalski/design-eng` -> `emilkowalski/skills` path `skills/emil-design-eng`), and ATTRIBUTION.md "Upstream path" must hold the repo path (`skills/taste-skill`), not the upstream skill's `name:` (`design-taste-frontend`) - the latter discrepancy was undisclosed and caught by T-142 verification.
