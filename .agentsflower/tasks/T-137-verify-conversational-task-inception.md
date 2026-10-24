# T-137: Verify conversational task inception, AST blast radius, and task pool synthesis

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-136 @ 1afb577c9c500ad5d250e22c2127c357dde7b551
Branch: t-137-verify-conversational-task-inception
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-137-verify-task-inception
Independent check: none
Resume: none

## Goal

Independently verify T-136 (Studio conversational task inception: Research/Inception chat threads, `/api/task/synthesize` with Graft AST blast radius, interactive Task Pool Card, batch ledger registration, task context threading) against the T-136 contract:

1. Run `test_studio.py` and the full test suite.
2. Serve the Studio from this disposable checkout and verify the markup carries the contract elements: a chat-header thread selector offering `Research & Inception` alongside task threads, and a `Synthesize Tasks from Discussion` action in the composer.
3. Exercise `POST /api/task/synthesize` against the served instance with a discussion payload: the response is a structured pool of task candidates (title, stage, role, effort, allowed files, acceptance criteria) each carrying a complexity/model tier assessment (floor `swe-2-high` vs escalation `gemini-4-argon-high`) and a blast-radius file scope derived from the repository AST (`compute_conversation_blast_radius` / Graft).
4. Exercise `POST /api/task/pool/register` against the served instance: synthesized tasks are registered atomically into the served checkout's `.agentsflower/state/tasks.md` ledger and matching Task Files are generated under `.agentsflower/tasks/`; confirm the writes land only inside the disposable checkout (review isolation: the checked task's branch and worktree in the main repository stay untouched).
5. Exercise `GET /api/task/context`: selecting a task thread returns that task's contract context (allowed files, recent log, diff summary).
6. In `studio.js`, verify the interactive Task Pool Card rendering: task id, title, Stage badge, effort badge, model pill, collapsible Allowed Files and Acceptance Criteria, and the `Approve & Register Pool in Ledger` batch action wired to the register endpoint.
7. Judge the developer's "Found, not fixed" notes (none declared) and record verdict in the Result section.

## Read first

- .agentsflower/tasks/T-136-conversational-task-inception-and-pool.md
- .agentsflower/roles/tester.md

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- PORT=8902

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes.
- [ ] V-02: Full regression test suite passes without regressions.
- [ ] V-03: Served shell markup and `studio.js` carry the contract elements (thread selector with Research & Inception, synthesize action, Task Pool Card with badges/model pill/collapsible scope, batch register button).
- [ ] V-04: `POST /api/task/synthesize` returns structured task candidates with complexity/model assessment and AST blast-radius file scope.
- [ ] V-05: `POST /api/task/pool/register` commits the pool into the served checkout's ledger and generates Task Files; writes stay inside the disposable checkout.
- [ ] V-06: `GET /api/task/context` returns per-task contract context for task threads.
- [ ] V-07: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->
