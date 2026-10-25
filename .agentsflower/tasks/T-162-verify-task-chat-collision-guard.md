# T-162: Verify Task-Level Chat and DAG Stage Move Collision Checker

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-161
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-161 @ 9d2089697b7a257d64666cea990b9a7502e571c9

## Goal

Independently verify T-161 (Task-level chat context, Implementations creation guard, and DAG stage move collision checking) against the T-161 contract:

1. Serve Studio from the T-161 candidate worktree.
2. Confirm UI prevents manual task creation in Implementations.
3. Test task thread discussion.
4. Test moving tasks between stages: verify cycle and dependency inversion rejections, verify valid moves update ledger.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-161-task-level-chat-and-stage-collision-guard.md
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Allowed files

none

## Do not touch

- *

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Manual task creation in Implementations is prevented.
- [ ] V-02: Task-level chat functions with task context preserved.
- [ ] V-03: Cyclic or inversion stage moves are rejected with descriptive errors.
- [ ] V-04: Valid stage moves mutate ledger safely.
- [ ] V-05: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes its outcome below this block -->
Outcome: completed
Verdict: pass

Verified T-161 @ 9d2089697b7a257d64666cea990b9a7502e571c9 in a detached disposable checkout; `git status --porcelain` was empty before and after all checks, and the developer worktree was only probed read-only via `inspect_worktree_status`. Studio was served live from the candidate worktree on 127.0.0.1:8911 for UI assets and non-mutating endpoints; mutating move-stage scenarios ran through the same `move_task_stage` code path against a temp copy of the real ledger and Task Files so the checkout stayed clean.

Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (79 passed / 0 failed; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.checks.txt)
- `python -m unittest discover -s .agentsflower/tests` -> pass (583 passed / 0 failed / 4 skipped; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.checks-full.txt)
Criteria:
- V-01: pass - manual task creation is prevented in UI and API: served studio.js renders Implementations via `buildThreadSection('implementations', ...)` with `sectionKey !== 'implementations'` gating, `data-manual-create="disabled"`, and no add button, while `POST /api/task/create` returns HTTP 403 `{"guard":"implementations_synthesis_only"}` both without `synthesis_approved` and with it set false; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.live-api.txt, .agentsflower/studio/studio.js, .agentsflower/tools/studio.py
- V-02: pass - task-level chat preserves task context: `GET /api/task/context?id=T-161` returns the contract file, goal, allowed files, criteria C-01..C-06, checks, `depends_on`, and live `worktree_status` {exists: true, status: "active (clean)", branch: t-161-...}; `format_chat_prompt` for thread `T-161` injects Task Context, Contract File, Worktree status, Depends on, Goal, Allowed Files and Acceptance Criteria into the dispatched prompt, and a non-task thread stays generic. The live CLI round-trip itself was not exercised (external binary, quota); the mocked end-to-end `/api/chat` path and the pre-existing dispatch mechanics are covered by the accepted suite; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.live-api.txt, .agentsflower/tasks/.runtime/T-162.evidence/T-162.move-stage.txt
- V-03: pass - cyclic and inversion moves are rejected with descriptive errors: upstream inversion `T-161 -> Stage 06` fails with "Cannot move T-161 to Stage 06: depends on T-160 in Stage 07 (dependency inversion)", downstream inversion `T-160 -> Stage 08` fails naming dependent T-161 in Stage 07, and a depends-override cycle is rejected with `collision_type: "cycle"` and path `T-160 -> T-161 -> T-160`; the inversion rejection was reproduced on the live server over HTTP and on the standalone code path; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.move-stage.txt, .agentsflower/tasks/.runtime/T-162.evidence/T-162.live-api.txt
- V-04: pass - valid moves mutate the ledger safely: `T-167 Stage 7 -> 6` returned 200 and atomically updated both the `Stage:` header in `.agentsflower/tasks/T-167-*.md` and the Stage column in `state/tasks.md` with stage-grouped row re-ordering; all three rejected moves left the fixture byte-identical (sha256 digest unchanged), so rejection happens before any mutation; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.move-stage.txt
- V-05: pass - full regression suite is clean: 583 tests ran, 0 failed, 4 skipped; evidence: .agentsflower/tasks/.runtime/T-162.evidence/T-162.checks-full.txt
New defects (outside the task):
- none
Cannot verify, needs:
- A real agent-CLI chat round-trip (installed CLI plus quota); prompt construction, context injection and API wiring were verified instead.
Proposed memory updates:
- none
