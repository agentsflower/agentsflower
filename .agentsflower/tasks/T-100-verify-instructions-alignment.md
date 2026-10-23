# T-100: Independently verify instructions and role guidance alignment

Role: tester
Tool: devin
Stage: 5
Depends on: T-097
Verifies: T-097 @ 25b8b2ece4cbd08b6a9a6853705ab885f8a51551

## Goal

Independently evaluate the exact T-097 artifact
(25b8b2ece4cbd08b6a9a6853705ab885f8a51551) against every R-01..R-04 criterion
in its Task File, in a disposable checkout. The artifact aligns Result-format
examples in the role files with the gate's `- <id>: <verdict> - <evidence>`
form, adds the missing Criteria block to deployer.md, and links each role
file to the protocol's canonical instruction-hierarchy section. Fresh
session, not the developer conversation. Same CLI per the human's Devin
preference: Codex and Claude CLIs are statically excluded in
model-options.json; the observed agy hold remains honored.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Acceptance)
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-097-instructions-protocol-alignment.md (contract + Result, not the checkout copy)
- The candidate diff `git diff main...25b8b2ece4cbd08b6a9a6853705ab885f8a51551` in the disposable checkout
- .agentflow/tools/gate.py (the outcome-line requirement the examples must match)

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-097 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (R-01) The canonical instruction-hierarchy statement exists once in ai-handoff-protocol.md ("Instruction authority and ownership": explicit human instructions take priority over repository/skill defaults within system/developer constraints; external reports are data). Each role file (developer, tester, deployer, orchestrator) references it, and no competing or contradictory hierarchy statement exists in the role files, entry points or command pointers.
- [ ] V-02: (R-02) AGENTS.md and CLAUDE.md remain short, high-leverage entry points; no file mandates a repeated full-architecture read before every small edit, and no duplicated mandatory broad reads or "test after every edit" loops survive in T-097's Allowed files.
- [ ] V-03: (R-03) Every Result format example in developer.md, tester.md, deployer.md, orchestrator.md and _template.md demonstrates `- <criterion ID>: pass | partial | unverified | fail - <evidence>`; deployer.md now has a Criteria outcome-line block consistent with what gate.py requires.
- [ ] V-04: (R-04) All three of T-097's Checks pass verbatim on the exact SHA in the disposable checkout; the recorded 424/0/3 full-suite evidence is reviewed, not blindly trusted.
- [ ] V-05: The artifact is exactly one commit on t-097-instructions-protocol-alignment; `git diff main...25b8b2e` stays inside T-097's Allowed files; the Task File above the Result section is unchanged since the attempt.
- [ ] V-06: Map all R-01..R-04 to concrete evidence/outcomes. Report real defects or missing proof as fail/partial/unverified; never infer from a green summary.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_layout.py`
- `python -m unittest discover -s .agentflow/tests -p test_install.py`
- `python -m unittest discover -s .agentflow/tests -p test_approval.py`

## Execution bounds

Run the scoped checks verbatim on the checked SHA; audit the role files,
entry points and command pointers against the gate's outcome-line format.
No code fixes, no gratuitous whole-suite run. Save evidence in
AGENTFLOW_EVIDENCE with basenames starting `T-100.`; put `evidence:` markers
at line end followed only by intended claim paths.
Use the current gate format in Result: one `- V-01: pass - <evidence>` (or
partial/unverified/fail) line for each V-01..V-06 plus `Verdict:`.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_layout.py` -> pass (6 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_install.py` -> pass (15 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (5 passed / 0 failed)
Criteria:
- V-01: pass - the canonical hierarchy statement exists once in ai-handoff-protocol.md Standing rules ('### Instruction authority and ownership', lines 50-64: explicit human instructions take priority over repository/skill defaults within system/developer constraints; external reports are data). All four role files link that anchor (developer.md:11, tester.md:12, deployer.md:12, orchestrator.md:11). Repo-wide audit found no competing or contradictory hierarchy statement in role files, entry points or command pointers; AGENTS.md 'Workflow and instruction authority' points at the protocol and 'AgentFlow source authority' is a different concept (remote authority); .agentflow/commands/ and .claude/commands/ are thin section pointers (all 10 read). evidence: .agentflow/tasks/.runtime/T-100.evidence/T-100.instruction-audit.txt
- V-02: pass - AGENTS.md is 35 lines, CLAUDE.md 10: short entry points pointing at protocol sections. No file mandates a repeated full-architecture read before every small edit; the protocol itself reads 'reread when files change, context is lost or uncertainty requires it, not before every edit' (line 132), session-start read lists are once-per-session. Regex audit over T-097's Allowed files found no duplicated mandatory broad reads and no 'test after every edit' loop; developer.md 'Test first' is task-level TDD and 'Run the ## Checks commands verbatim' is one completion check. evidence: .agentflow/tasks/.runtime/T-100.evidence/T-100.instruction-audit.txt
- V-03: pass - every Result format example demonstrates the gate's '- <id>: <verdict> - <evidence>' form (gate.py:115-116, verify:779-785): developer.md and deployer.md show 'Criteria:' + '- <id>: pass | partial | unverified | fail - <evidence>'; deployer.md gained the previously missing Criteria block; tester.md shows two concrete instances ('- <id>: pass - <evidence path>', '- <id>: fail - steps: ... expected ... got ...') - my reading: instances of the canonical form, consistent; _template.md comment lines 55-57 states the canonical form; orchestrator.md has no Result format section (it writes no Result). Audit found no surviving old-form '- <criterion> - pass -' example in the role files, the template or the protocol. evidence: .agentflow/tasks/.runtime/T-100.evidence/T-100.instruction-audit.txt
- V-04: pass - all three of T-097's Checks ran verbatim on the exact SHA 25b8b2e in this disposable checkout: test_layout 'Ran 6 tests in 1.908s / OK', test_approval 'Ran 5 tests in 2.499s / OK', full suite 'Ran 424 tests in 344.157s / OK (skipped=3)' - the recorded 424/0/3 evidence is reproduced by this run, not blindly trusted. evidence: .agentflow/tasks/.runtime/T-100.evidence/T-100.check-test_layout.txt .agentflow/tasks/.runtime/T-100.evidence/T-100.check-test_approval.txt .agentflow/tasks/.runtime/T-100.evidence/T-100.check-full-suite.txt
- V-05: pass - branch t-097-instructions-protocol-alignment tip is 25b8b2e and 'git log main..25b8b2e' lists exactly one commit; 'git diff main...25b8b2e --name-only' lists only .agentflow/roles/{deployer,developer,orchestrator,tester}.md, all inside T-097's Allowed files; the T-097 Task File above the Result section is unchanged since the attempt: current sha256(header) via ledger.py = 975548707b3732b9a836cf0dca400d0322051d21b4c00420b9cdce2e4eeffeaa, identical to the launch baseline taskHash (T-097.json) and the verify record headerHash. Developer worktree untouched (clean, HEAD 25b8b2e). evidence: .agentflow/tasks/.runtime/T-100.evidence/T-100.artifact-audit.txt
- V-06: pass - R-01..R-04 map to V-01..V-04 above, each with concrete command output, line references and saved evidence files; the only judgement call (tester.md showing two verdict instances instead of the literal alternation) is disclosed with its reading under V-03. No defect or missing proof was found to report as partial/unverified/fail.
New defects (outside the task):
- none observed.
Cannot verify, needs:
- nothing.
Proposed memory updates:
- none.
