# T-140: Domain 4 Specialized Skill: chrome-extension-mv3 and Manifest V3 Linter

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-139
Branch: t-140-skill-chrome-extension-mv3
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-140-skill-chrome-extension-mv3
Independent check: tester
Resume: none
Routing exception: human authorized Phase P1 skill implementation (2026-10-25)

## Goal

Implement Domain 4 specialized skill `chrome-extension-mv3` adhering to `agentskills.io` specification and `.agentsflower/docs/skills-implementation-roadmap.md`:

1. **Skill Package Directory:** `.agentsflower/skills/chrome-extension-mv3/`
   - `SKILL.md`: Spec-compliant router (<= 500 lines) with YAML frontmatter:
     - `name`: `chrome-extension-mv3`
     - `description`: Strict Google Chrome Extension Manifest V3 development, service worker lifecycle, declarativeNetRequest rules, CSP security, and permissions auditing.
     - `metadata.domain`: `4`
     - `metadata.source`: `google/chrome-extensions-samples@main` + `michaell/chrome-mv3@main`
     - `metadata.license`: `Apache-2.0`
   - `references/manifest-v3-rules.md`: Concrete MV3 requirements (`manifest_version: 3`, `background.service_worker`, `chrome.action`, separate `host_permissions`, zero inline scripts/handlers).
   - `references/service-worker-lifecycle.md`: Ephemeral service worker persistence, `chrome.storage.session`, message passing, alarm API instead of setInterval.
   - `scripts/mv3_lint.py`: Zero-pip deterministic CLI linter parsing `manifest.json` and checking for MV2 anti-patterns (`browserAction`, `background.scripts`, `eval()`, missing CSP, insecure permissions).

2. **Testing & Registration:**
   - Register in `.agentsflower/skills/INDEX.md` as Active Built-in Skill.
   - Update `.agentsflower/skills/ATTRIBUTION.md` with source pin and Apache-2.0 license.
   - Add unit tests in `.agentsflower/tests/test_skills.py` verifying `mv3_lint.py` against valid/invalid manifests.

## Read first

- .agentsflower/docs/skills-implementation-roadmap.md
- .agentsflower/docs/skills-ecosystem-catalog.md
- .agentsflower/skills/INDEX.md
- .agentsflower/skills/geo-seo-audit/SKILL.md
- .agentsflower/tests/test_skills.py

## Allowed files

- `.agentsflower/skills/chrome-extension-mv3/*`
- `.agentsflower/skills/INDEX.md`
- `.agentsflower/skills/ATTRIBUTION.md`
- `.agentsflower/tests/test_skills.py`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: `.agentsflower/skills/chrome-extension-mv3/SKILL.md` conforms to spec with frontmatter and references.
- [ ] C-02: `scripts/mv3_lint.py` validates `manifest.json` and flags MV2 legacy patterns without external dependencies.
- [ ] C-03: `INDEX.md` and `ATTRIBUTION.md` updated with upstream attribution.
- [ ] C-04: `test_skills.py` verifies linter and skill structure.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
