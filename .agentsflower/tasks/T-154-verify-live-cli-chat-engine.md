# T-154: Verify Studio Live CLI Chat Execution Engine

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-153
Branch: none
Worktree: none
Independent check: none
Resume: .agentsflower/tasks/.runtime/T-154.evidence
Verifies: T-153 @ 46e11c7f8a65be9077f7aba376e8d7c5318f79a6

## Goal

Independently verify T-153 (Studio live CLI chat execution engine and `/api/chat` integration) against the T-153 contract:

1. Serve Studio from the T-153 candidate worktree.
2. Exercise `POST /api/chat` with mocked CLI runner and verify response shape and error handling.
3. Verify conversational threading in UI with real responses.
4. Verify timeout bounding and safety guards.
5. Run full test suite: `python -m unittest discover -s .agentsflower/tests`.

## Read first

- .agentsflower/tasks/T-153-studio-live-cli-chat-engine.md
- .agentsflower/tools/studio.py
- .agentsflower/studio/studio.js
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

- [ ] V-01: `POST /api/chat` executes prompt against designated tool/model and returns reply payload.
- [ ] V-02: Multi-turn history is preserved and sent in context.
- [ ] V-03: UI displays live assistant replies with thinking indicator.
- [ ] V-04: Full regression suite passes cleanly.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (56 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (560 passed / 4 skipped / 0 failed)
Criteria:
- V-01: pass - evidence: .agentsflower/tasks/.runtime/T-154.evidence/T-154.a2-live-api-chat-checks.txt .agentsflower/tools/studio.py
- V-02: pass - evidence: .agentsflower/tasks/.runtime/T-154.evidence/T-154.a2-live-api-chat-checks.txt .agentsflower/studio/studio.js
- V-03: pass - evidence: .agentsflower/tasks/.runtime/T-154.evidence/T-154.a2-live-api-chat-checks.txt .agentsflower/studio/studio.js .agentsflower/studio/studio.css
- V-04: pass - evidence: .agentsflower/tasks/.runtime/T-154.evidence/T-154.a2-check1-test-studio.txt .agentsflower/tasks/.runtime/T-154.evidence/T-154.a2-check2-full-suite.txt
Findings (attempt 2, independent rerun on the Verifies commit in the disposable checkout):
- V-01: live Studio server (port 8932) dispatched the chat request to a real subprocess (compiled fake CLI binary first on PATH, no mocks): HTTP 200 with ok/reply/tool/model/thread/usage payload; the subprocess argv log proves the prompt flag and both model values passed through as discrete argv items. Error paths live-verified: 400 missing CLI binary, 400 unsupported tool, 400 empty messages, 403 unregistered project, 502 non-zero CLI exit with stderr surfaced.
- V-02: the captured argv shows the formatted prompt containing the conversation-history section with all three prior-turn markers plus the latest turn and the read-only mode line; a task thread id additionally injected task context and task goal; the frontend keeps per-thread message arrays and resends accumulated items each turn.
- V-03: the served frontend bundle posts project/tool/model/thread/messages to the chat endpoint, shows an animated thinking bubble removed in a finally block, aborts after a 30s bound, renders the reply into the assistant bubble and pushes it into the thread; the served stylesheet carries the thinking and error bubble styles and the pulse keyframes. Verified via served-asset and DOM-code inspection; no rendered browser session.
- Goal item 4 (timeout bounding) - evidence: .agentsflower/tasks/.runtime/T-154.evidence/T-154.a2-timeout-check.txt .agentsflower/tasks/.runtime/T-154.evidence/T-154.timeout-check.txt - fake CLI sleeping 90s produced HTTP 504 with the timed_out flag after 30.3s and the child process (PID 37000) was confirmed killed via tasklist; attempt-1 run reproduced the same bound at 30.4s.
- Attempt-1 evidence files (T-154.live-api-chat-checks.txt, T-154.timeout-check.txt, T-154.check1-test-studio.txt, T-154.check2-full-suite.txt) from the same checkout remain in the evidence folder and are consistent with the attempt-2 results; this Result supersedes attempt 1's, which failed gate verify only on evidence-line formatting (path-looking prose tokens claimed after the evidence marker).
New defects (outside the task):
- none observed; Studio's single-threaded HTTP server serializes API calls behind a running chat execution (pre-existing architecture, not a contract violation).
Cannot verify, needs:
- Real provider CLIs were not invoked to avoid consuming quota; dispatch was proven with a real substitute executable. No local Ollama runtime on this host; that path is covered only by mocked unit tests.
Proposed memory updates:
- known-issues candidate: the gate evidence parser treats every path-looking token after an evidence marker on a criterion line as a claim (backticked or not); keep criterion lines in the form "- <id>: <verdict> - evidence: <paths>" and put prose in separate bullets. T-154 attempt 1 lost a verify pass to this formatting alone.
