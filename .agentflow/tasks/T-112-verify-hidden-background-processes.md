# T-112: Independently verify hidden background process consoles

Role: tester
Tool: devin
Model: swe-2-high
Stage: 5
Depends on: none
Verifies: T-066 @ 3c8d9e6db30f2da718acbfca524650f4360977ee

## Goal

Independently evaluate the exact T-066 artifact (3c8d9e6db30f2da718acbfca524650f4360977ee)
against every A-01..A-05 criterion in its Task File, in a disposable checkout.
The artifact configures Windows background processes (conductor, automatic Orchestrator,
worker CLI, panel starts and Task Scheduler registration) to run on hidden consoles
without taskbar entries or focus theft, sets stdin to an EOF'd pipe to prevent prompts
from hanging unattended sessions, updates docs/guides, and aligns version metadata to 2.15.11.
Fresh independent session per protocol.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md
- E:\Projects\AgentFlow\code\.agentflow\tasks\T-066-hidden-background-processes.md
- The candidate diff `git diff main...3c8d9e6db30f2da718acbfca524650f4360977ee` in disposable checkout

## Allowed files

- nothing (Result and evidence only)

## Do not touch

- Developer branch/worktree/artifact and the T-066 Task File above your own Result section
- Product code, tests, configuration, canonical memory, other Task Files, attempt history
- Other repositories

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: (A-01) Background conductor, automatic Orchestrator, worker CLI and managed helpers create no visible console or focus theft on Windows. Audit scheduled-task registration and manual panel start.
- [ ] V-02: (A-02) Process creation controls at the parent launch boundary (-WindowStyle Hidden, CREATE_NO_WINDOW); POSIX behavior and PowerShell 5.1/pwsh compatibility preserved.
- [ ] V-03: (A-03) Logs and panel status available; exit codes, PID identity, leases, stop and timeout tree cleanup retain behavior; stdin EOF prevents unattended hangs.
- [ ] V-04: (A-04) Targeted regressions pass and cover all changed launch paths; verify on a real Windows desktop and record observed window/focus behavior.
- [ ] V-05: (A-05) VERSION 2.15.11, AGENTS block, CHANGELOG and affected guides aligned with honest migration notes.
- [ ] V-06: Full regression suite passes verbatim; map all A-01..A-05 to concrete evidence/outcomes.

## Checks

- `python -m unittest discover -s .agentflow/tests`

## Execution bounds

Run the scoped checks verbatim on the checked SHA. Save evidence in AGENTFLOW_EVIDENCE with basenames starting `T-112.`.
Use the current gate format in Result: one `- V-01: pass - <evidence>` line for each V-01..V-06 plus `Verdict:`.

## Result
Outcome: not-started
Verdict: unverified
Checks:
Criteria:
- V-01: unverified - pending
- V-02: unverified - pending
- V-03: unverified - pending
- V-04: unverified - pending
- V-05: unverified - pending
- V-06: unverified - pending
