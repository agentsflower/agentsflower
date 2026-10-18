# T-085: Fast-path re-check of backup-hold carrier

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: T-084
Verifies: T-084 @ fc2c37cc7144d7a5788ac6ee797f4b1020d34025

## Goal

Fast-path independent re-check of the T-084 carrier artifact at
fc2c37cc7144d7a5788ac6ee797f4b1020d34025 - the identical tree already
independently verified PASS by T-083 (its V-01..V-05, live probes and the
negative control). You do not repeat T-083's deep probe work. You confirm,
in a fresh disposable checkout: the artifact identity, the corrected scope
declaration, the green scoped Checks, and that nothing about the carrier
changed the verified content. Fresh session, not the developer conversation.
Same CLI per the human's Devin preference: Codex worker sandbox writes were
environment-blocked on this machine; observed agy holds remain honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-084-backup-hold-carrier.md (contract + Result, not the checkout copy)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-083-verify-backup-hold.md (the deep verification being relied on)
- The candidate diff `git diff main...fc2c37cc7144d7a5788ac6ee797f4b1020d34025` in the disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-084 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- The T-040, T-074 and T-082 worktrees (read only)
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: The disposable checkout HEAD is exactly fc2c37cc7144d7a5788ac6ee797f4b1020d34025, the tree is byte-identical to the one T-083 verified (same SHA), and its parent chain is fc2c37c -> 5a6510c -> shared base with main.
- [ ] V-02: `git diff main...HEAD` touches only files inside T-084's Allowed files (the corrected full inherited scope: the T-074 set plus the T-082 delta). No unexpected file appears vs T-083's record.
- [ ] V-03: Both scoped Checks pass verbatim on the exact SHA. The recorded full-suite evidence is reviewed honestly (T-082: 392 ran / 1 transient test_approval WinError 5 flake / 3 skipped, isolated 5/5; T-075: 391/0/3 on the base); not repeated without cause.
- [ ] V-04: VERSION/AGENTS/CHANGELOG agree at 2.15.2, still API-only with launch enforcement pending T-076; T-040 not claimed complete. Report any real defect as fail/partial/unverified; do not infer from the green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py`
- `python -m unittest discover -s .agentflow/tests -p test_route.py`

## Execution bounds

15-minute cap. This is a fast-path identity/scope check of an already
deep-verified SHA, not a second deep review. Run the two scoped Checks
verbatim; confirm identity, scope and metadata; verdict by evidence. Save
evidence in AGENTFLOW_EVIDENCE with basenames starting `T-085.`; put
`evidence:` markers at line end followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-04 plus `Verdict:`.

## Result
Outcome: completed
Verdict: pass

Checked artifact: fc2c37cc7144d7a5788ac6ee797f4b1020d34025 in the launcher-provided disposable checkout (detached HEAD, clean tree), independently of the developer session. Fast-path identity/scope re-check; T-083's deep probes are relied on, not repeated.

Checks:

- `python -m unittest discover -s .agentflow/tests -p test_routing_core.py` -> pass (20 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-085.evidence/T-085.check-test_routing_core.txt
- `python -m unittest discover -s .agentflow/tests -p test_route.py` -> pass (12 passed / 0 failed, exit 0). evidence: .agentflow/tasks/.runtime/T-085.evidence/T-085.check-test_route.txt

Criteria:

- V-01: pass - HEAD is exactly fc2c37cc7144d7a5788ac6ee797f4b1020d34025 (git rev-parse), the identical SHA T-083 deep-verified PASS, so the tree is byte-identical by definition (tree 14d9c860). Parent chain confirmed: fc2c37c -> 5a6510c -> b40c934, and `git merge-base main HEAD` = b40c9344486ddee304f0c0ff148b8d16d5b3c608 - the shared base with main (52a946d). Working tree clean. evidence: .agentflow/tasks/.runtime/T-085.evidence/T-085.v01-artifact.txt
- V-02: pass - `git diff main...HEAD` touches exactly the 11 files of T-084's corrected Allowed files (the T-074 set plus the T-082 delta): route.py, gate.py, plan_route.py, quota_groups.py, test_route.py, test_routing_core.py, model-options.json, typesafe.md, VERSION, AGENTS.md, CHANGELOG.md - zero unexpected files vs T-083's record; the AGENTS.md delta is the version-block line only (2.15.1 -> 2.15.2). evidence: .agentflow/tasks/.runtime/T-085.evidence/T-085.v02-scope.txt .agentflow/tasks/.runtime/T-085.evidence/T-085.v02-agents-version.diff
- V-03: pass - both scoped Checks pass verbatim on the exact SHA (20/0 and 12/0 above). Recorded full-suite evidence reviewed honestly, not repeated: T-082 logged 392 ran / 1 transient test_approval WinError 5 flake / 3 skipped with isolated rerun 5/5; T-075 recorded 391/0/3 on base 5a6510c; no changed input since. evidence: .agentflow/tasks/.runtime/T-085.evidence/T-085.check-test_routing_core.txt .agentflow/tasks/.runtime/T-085.evidence/T-085.check-test_route.txt
- V-04: pass - .agentflow/VERSION reads 2.15.2, the AGENTS.md version block reads "AgentFlow version: 2.15.2", and the CHANGELOG 2.15.2 entry (2026-10-18) describes the combined artifact: requirements-bound assessment records, requirement-first selection, the launch-side API including backup_ok, "backups and retries ... cannot bypass quota groups"; explicitly API-only, launch enforcement pending T-076, and "T-040 is not complete". No real defect found. evidence: .agentflow/tasks/.runtime/T-085.evidence/T-085.v04-release-metadata.txt .agentflow/tasks/.runtime/T-085.evidence/T-085.v02-agents-version.diff

New defects (outside the task):

- None found. The two disclosures T-083 already evaluated (test_plan_route.py real-registry dependence; ledger.py _write_atomic transient WinError 5) remain inherited issues outside this carrier's scope, unchanged.

Cannot verify, needs:

- Nothing blocked.

Proposed memory updates:

- session-log.md, 2026-10-18: T-085 fast-path re-check of the T-084 carrier at fc2c37c PASS - identity, corrected scope declaration (11 files), green scoped checks (20/0 + 12/0) and 2.15.2 metadata all confirmed; T-084 ready for acceptance.
