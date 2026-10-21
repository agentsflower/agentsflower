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
