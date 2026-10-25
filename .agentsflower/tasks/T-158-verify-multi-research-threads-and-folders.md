# T-158: Verify Multi-Research Threads, Folders, and Context Forking

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-157
Branch: none
Worktree: none
Independent check: none
Resume: none
Verifies: T-157 @ 38495f2e3923371c06d19539633ef2533906f9d2

## Goal

Independently verify T-157 (Multi-research threads, folder categorization, and context referencing) against the T-157 contract:

1. Serve Studio from the T-157 candidate worktree.
2. Test creating multiple researches, renaming, and grouping into folders.
3. Verify persistence across page refresh.
4. Verify context cross-referencing between threads.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-157-multi-research-threads-and-folders.md
- .agentsflower/studio/studio.js
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

- [ ] V-01: Multiple research threads can be created and independently switched.
- [ ] V-02: Folder organization works and state persists to disk.
- [ ] V-03: Context referencing accurately pulls in referenced task/research context.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Verified T-157 @ 38495f2e3923371c06d19539633ef2533906f9d2 in the disposable worktree agentsflower-t-157-multi-research-threads-and-folders.t-158 (detached HEAD, exactly the Verifies commit). Served Studio from that checkout (python .agentsflower/tools/studio.py --port 8907) and exercised the same HTTP endpoints the UI calls: created three threads, renamed one, assigned folders, forked one from another, updated refs, fetched threads individually, then restarted the server and re-listed. Ran format_chat_prompt / extract_context_refs / maybe_persist_research_turn directly against the worktree root to prove context injection and chat-turn persistence. Inspected the served studio.js/studio.css for the + button, inline rename, collapsible folder groups, ref chips and fork-from select wiring. Removed the runtime research store afterward; worktree is clean (git status empty).

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (70 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (574 passed / 4 skipped / 0 failed)
Criteria:
- V-01: pass - POST /api/research/create produced research-001..003 with auto-names Task Research - 001..003; each record independently fetchable via GET /api/research/thread; studio.js selectThread() switches the active thread and the '+' button in the Researches section calls addResearchThread -> /api/research/create - evidence: .agentsflower/tasks/.runtime/T-158.evidence/T-158.api_transcript.txt
- V-02: pass - folder values (Architecture, UI Design) stored per record in .agentsflower/state/research/<id>.json and survived a full server restart (names, folders, refs, parent, message history all intact); buildFolderGroup + thread-folder-* classes render collapsible folder headers - evidence: .agentsflower/tasks/.runtime/T-158.evidence/T-158.api_transcript.txt
- V-03: pass - format_chat_prompt emitted a 'Referenced context' section with the real persisted history of research-001, metadata of research-003 and the T-157 task summary; extract_context_refs pulled inline 'Ref: T-157' and 'fork from Research-001' tokens; refs merged into the stored record via chat persist and via /api/research/update - evidence: .agentsflower/tasks/.runtime/T-158.evidence/T-158.api_transcript.txt
- V-04: pass - both check commands green on the verified commit - evidence: .agentsflower/tasks/.runtime/T-158.evidence/T-158.check1_test_studio.txt, .agentsflower/tasks/.runtime/T-158.evidence/T-158.check2_full_suite.txt
New defects (outside the task):
- none new; T-157 already reported that .agentsflower/state/research/ is not gitignored. Robustness note, not a criterion breach: POST /api/research/update on an unknown id upserts a new record (returns 200) instead of 404; the UI only updates existing ids.
Cannot verify, needs:
- Live end-to-end /api/chat turn: claude and codex CLIs are reported non-functional in project rules, and a live devin -p call would spawn an unbounded nested agent with auto permissions against the checked worktree. The prompt-injection and turn-persistence functions that call exercises were verified directly instead, and the endpoint path is covered by test_studio.py with a stubbed CLI.
Proposed memory updates:
- none
