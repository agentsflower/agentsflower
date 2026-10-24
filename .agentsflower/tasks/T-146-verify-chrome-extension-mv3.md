# T-146: Verify chrome-extension-mv3 skill package and source substitution

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-140 @ b58fe9fa74b94e2e682da122f541bae39f69b4b1
Branch: t-146-verify-chrome-extension-mv3
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-146-verify-chrome-extension-mv3
Independent check: none
Resume: none

## Goal

Independently verify T-140 (Domain 4 specialized skill `chrome-extension-mv3`:
spec-compliant `SKILL.md` router, two references, `scripts/mv3_lint.py` stdlib
linter, INDEX.md/ATTRIBUTION.md registration, `test_skills.py` tests) against
the T-140 contract. The developer disclosed a contract deviation you must
judge: the Goal's `metadata.source` id `michaell/chrome-mv3@main` resolves to
no repository (404); the artifact substitutes the skills-roadmap catalog's
designated Domain-4 primary source `GoogleChrome/modern-web-guidance@main`
plus the contract's `google/chrome-extensions-samples@main`, both Apache-2.0
with real pinned commits. Decide whether the substitution is a faithful,
honestly-attributed fulfillment of the contract intent (a real, verifiable
upstream for a linter/rules skill) or a contract violation needing the human's
corrected contract.

1. Run `test_skills.py` and the full test suite.
2. Inspect `.agentsflower/skills/chrome-extension-mv3/SKILL.md`: closed YAML frontmatter (name, description, `metadata.domain: 4`, `metadata.source` listing the substituted upstreams, `metadata.license: Apache-2.0`); <= 500 lines; routes to references/.
3. Verify `references/manifest-v3-rules.md` and `references/service-worker-lifecycle.md` carry concrete rules; `scripts/mv3_lint.py` is stdlib-only, exits 0 on a valid MV3 manifest and 1 flagging MV2 anti-patterns.
4. Verify INDEX.md registration (Active Built-in, domain-4 row) and ATTRIBUTION.md rows (repo, path, Apache-2.0, real commit pins - spot-check the pins resolve upstream if network permits).
5. Judge the disclosed `michaell/chrome-mv3` -> substituted-sources deviation (unverifiable-contract-id class, same as T-139's `emilkowalski/design-eng`) and the transient WinError 5 note; record verdict in the Result section.

## Read first

- .agentsflower/tasks/T-140-skill-chrome-extension-mv3.md (the contract and the developer Result)
- .agentsflower/docs/skills-implementation-roadmap.md (the catalog's Domain-4 source designation)
- .agentsflower/roles/tester.md

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
- [ ] V-02: Full regression test suite passes without regressions attributable to T-140.
- [ ] V-03: SKILL.md conforms to the spec contract (frontmatter fields, <= 500 lines, reference routing).
- [ ] V-04: Both references carry concrete rules and `mv3_lint.py` behaves per contract (valid MV3 -> 0, MV2 anti-patterns -> 1).
- [ ] V-05: INDEX.md and ATTRIBUTION.md carry correct registration and attribution entries with real pins.
- [ ] V-06: The disclosed source substitution is judged: state whether it faithfully fulfills contract intent; `fail` if it does not.
- [ ] V-07: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->

Outcome: completed
Verdict: pass
Verified on detached HEAD b58fe9fa74b94e2e682da122f541bae39f69b4b1 (== `Verifies` SHA), disposable checkout `agentsflower-t-140-skill-chrome-extension-mv3.t-146`, clean worktree; `git show --stat` confirms the commit touches only T-140 `Allowed files`.
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_skills.py"` -> pass (15 passed / 0 failed) - evidence: .agentsflower/tasks/.runtime/T-146.evidence/T-146.check1-test_skills.txt
- `python -m unittest discover -s .agentsflower/tests` -> pass (543 ran / 0 failed, 4 skipped) - evidence: .agentsflower/tasks/.runtime/T-146.evidence/T-146.check2-full-suite.txt
Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-146.evidence/T-146.check1-test_skills.txt (15 tests incl. ChromeExtensionMv3SkillTests x7, all green)
- V-02: pass - the developer-disclosed test_launcher_lifecycle PermissionError did not reproduce here (543/543 OK) and matches the documented recurring Windows file-lock flake in known-issues.md, not this change. evidence: .agentsflower/tasks/.runtime/T-146.evidence/T-146.check2-full-suite.txt
- V-03: pass - .agentsflower/skills/chrome-extension-mv3/SKILL.md is 79 lines (<= 500), opens/closes YAML frontmatter with `name: chrome-extension-mv3`, non-empty spec-style description, `metadata.domain: 4`, `metadata.source` listing both substituted upstreams, `license: Apache-2.0` (top-level + `metadata.license`); routes to both existing references via a load-when table and a definition-of-done checklist
- V-04: pass - references/manifest-v3-rules.md (103 lines: field contract table, minimal manifest, permissions audit, CSP/inline ban, MV2->MV3 checklist) and references/service-worker-lifecycle.md (67 lines: ephemeral lifecycle, chrome.storage.session, message passing, chrome.alarms, offscreen) carry concrete rules; scripts/mv3_lint.py imports only stdlib (argparse/json/re/sys/pathlib). Manual fixtures: valid MV3 dir -> exit 0 MV3_COMPLIANT 0 errors; MV2 fixture -> exit 1 NON_COMPLIANT, 11 errors flagging manifest_version, browser_action, background.scripts/persistent, host pattern in permissions, webRequestBlocking, MV2 CSP string, unsafe-eval, WAR string form, eval(), chrome.browserAction; missing manifest -> exit 1; manifest.json file target -> exit 0. evidence: .agentsflower/tasks/.runtime/T-146.evidence/T-146.mv3lint-valid.txt .agentsflower/tasks/.runtime/T-146.evidence/T-146.mv3lint-mv2.txt
- V-05: pass - INDEX.md lists `chrome-extension-mv3` under "Active Built-in Skills" and marks it `(Built-in)` in the domain-4 row; ATTRIBUTION.md has two rows (GoogleChrome/chrome-extensions-samples `1bdfa5a730396cc4615d1e32d7c7152a92a6babe`, GoogleChrome/modern-web-guidance `65e7edd67e77420eaf02c5df00fdc0521417d809`, both Apache-2.0). Spot-check: both pins are the current `main` HEADs upstream and both repos carry spdx Apache-2.0 - evidence: .agentsflower/tasks/.runtime/T-146.evidence/T-146.upstream-pins.txt
- V-06: pass - substitution judged faithful to contract intent. `michaell/chrome-mv3` independently re-confirmed unresolvable (GitHub API 404), so the literal contract id could never be pinned honestly; the artifact substitutes the skills catalog's designated Domain-4 distillation source (skills-ecosystem-catalog.md C-15 `GoogleChrome/modern-web-guidance`, "Distill `chrome-extension-mv3`") plus the contract's samples repo, both real, Apache-2.0, pinned at verified commits, and the deviation is disclosed rather than hidden. This is the same unverifiable-contract-id class as T-139's `emilkowalski/design-eng`; the correct remedy is a contract correction, not fabricated attribution
- V-07: pass - worst criterion is pass
New defects (outside the task):
- Task-contract nit (T-140 Goal text, faithfully copied into SKILL.md `metadata.source`): the id `google/chrome-extensions-samples@main` uses a non-resolving org spelling; the canonical org is `GoogleChrome`. ATTRIBUTION.md links the correct `GoogleChrome/chrome-extensions-samples` URL, so attribution is accurate; only the frontmatter id string is imprecise. Recommend a contract-corrected follow-up if literal resolvability of `metadata.source` ids is required.
Cannot verify, needs:
- nothing; all checks ran locally with network available for the pin spot-checks
Proposed memory updates:
- Endorse the developer's proposal: orchestrator pre-flight should verify a Task File's named upstream repos resolve before worker launch (404 sources cannot be pinned honestly); T-139 and T-140 are now two instances of the same contract-authoring defect class.
