# T-140: Domain 4 Specialized Skill: chrome-extension-mv3 and Manifest V3 Linter

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-143
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

Outcome: completed
Change: b58fe9f on t-140-skill-chrome-extension-mv3
Contract deviation (orchestrator decision needed): the Goal names
`metadata.source` = `michaell/chrome-mv3@main`, but that repository does not
exist (GitHub API 404; user `michaell` has no extension-related repos;
owner-scoped repo search returns 0 hits). Substituted the skills-roadmap
catalog's designated Domain-4 primary source `GoogleChrome/modern-web-guidance@main`
(Apache-2.0, ships `skills/chrome-extensions`, pinned at 65e7edd) alongside the
contract's `google/chrome-extensions-samples@main` (Apache-2.0, pinned 1bdfa5a).
Writing a fabricated pin for a nonexistent repo was not an option; if the
literal contract source is mandatory the task needs a corrected contract.
Files:
- .agentsflower/skills/chrome-extension-mv3/SKILL.md - spec router (<= 500 lines): frontmatter name/description/domain 4/license Apache-2.0, core rules, linter gate, reference links, definition of done
- .agentsflower/skills/chrome-extension-mv3/references/manifest-v3-rules.md - MV3 field contract, permissions audit rules, CSP/inline-code ban, MV2->MV3 migration checklist
- .agentsflower/skills/chrome-extension-mv3/references/service-worker-lifecycle.md - ephemeral lifecycle, chrome.storage.session, message passing, chrome.alarms, offscreen documents
- .agentsflower/skills/chrome-extension-mv3/scripts/mv3_lint.py - zero-pip stdlib-only CLI linter; parses manifest.json + referenced JS/HTML/DNR files; JSON and text output; exit 0/1
- .agentsflower/skills/INDEX.md - registered chrome-extension-mv3 as Active Built-in Skill and marked Built-in in domain 4 row
- .agentsflower/skills/ATTRIBUTION.md - two rows with upstream repo/path, Apache-2.0 license, real commit pins
- .agentsflower/tests/test_skills.py - added ChromeExtensionMv3SkillTests (7 tests: structure, frontmatter, reference links/content, linter pass+fail fixtures, registration)
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_skills.py"` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> fail (542 passed / 1 error, 4 skipped): test_launcher_lifecycle.test_dispatch_grant_becomes_worker_lease hit PermissionError reading a temp fixture JSON - the documented recurring Windows file-lock flake in known-issues.md (AV/indexer locking); rerun standalone -> pass. Unrelated to this change (touches skills/ and test_skills.py only).
Criteria:
- C-01: pass - .agentsflower/skills/chrome-extension-mv3/SKILL.md opens with closed YAML frontmatter (name: chrome-extension-mv3, non-empty description, domain: 4, license: Apache-2.0, two pinned sources), 84-line router linking both existing references/ files; deviation: source list carries the verified real upstreams, not the nonexistent michaell/chrome-mv3 (see Contract deviation above)
- C-02: pass - scripts/mv3_lint.py is stdlib-only; test_mv3_lint_accepts_valid_mv3_manifest exits 0/MV3_COMPLIANT and test_mv3_lint_flags_mv2_antipatterns exits 1 flagging manifest_version, browser_action, service_worker, host_permissions, eval, content_security_policy
- C-03: pass - .agentsflower/skills/INDEX.md and .agentsflower/skills/ATTRIBUTION.md updated; ATTRIBUTION pins real commits 1bdfa5a + 65e7edd with Apache-2.0
- C-04: pass - .agentsflower/tests/test_skills.py ChromeExtensionMv3SkillTests verifies linter behavior and skill package structure
Found, not fixed:
- Task contract upstream `michaell/chrome-mv3@main` is unverifiable/nonexistent; likely a task-authoring typo. Orchestrator should correct the contract source or confirm the substitution.
Proposed memory updates:
- known-issues / orchestrator guidance: when a Task File names an upstream repo for a skill, verify it resolves (GitHub API) before worker launch; a 404 source cannot be pinned honestly.
