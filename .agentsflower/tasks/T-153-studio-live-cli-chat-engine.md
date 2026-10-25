# T-153: Studio Live CLI Chat Execution Engine (/api/chat)

Role: developer
Tool: devin
Model: gemini-4-argon-high
Stage: 7
Depends on: T-152
Branch: t-153-studio-live-cli-chat-engine
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-153-studio-live-cli-chat-engine
Independent check: tester
Resume: none

## Goal

Replace the static mock response in Studio Chat with a fully functional conversational backend executing real queries against selected CLI platforms or local runtimes:

1. **Backend Chat Endpoint (`POST /api/chat`)**:
   - In `.agentsflower/tools/studio.py`: implement `POST /api/chat` accepting `{ project, tool, model, thread, messages }`.
   - Dispatch query to the chosen engine:
     - `devin`: execute `devin -p "<prompt>"` in read-only / bounded mode.
     - `claude`: execute `claude -p "<prompt>"`.
     - `codex`: execute `codex exec "<prompt>"`.
     - `agy`: execute `agy -p "<prompt>" --output-format stream-json`.
     - `ollama`: call `local_adapter.py` chat completion endpoint.
   - Format thread context and previous messages into conversation prompt.
   - Capture stdout and return JSON `{ ok: true, reply: "...", model: "...", usage: {...} }`.
2. **Frontend Reactive Chat Integration**:
   - In `.agentsflower/studio/studio.js`: update `sendChatMessage()` to call `POST /api/chat`.
   - Show an animated typing / thinking indicator while CLI executes.
   - Render the real model response in the assistant bubble.
   - Handle timeouts (30s bound) and display clean error messages on failure.
3. **Automated Tests**:
   - Add unit tests in `.agentsflower/tests/test_studio.py` testing `POST /api/chat` dispatch, mock CLI runner, error handling, and timeout behavior.

## Read first

- .agentsflower/studio/studio.js
- .agentsflower/tools/studio.py
- .agentsflower/tools/local_adapter.py
- .agentsflower/tools/run_task.py
- .agentsflower/tests/test_studio.py

## Allowed files

- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py

## Do not touch

- .agentsflower/tools/gate.py
- .agentsflower/state/tasks.md

## Setup

- none

## Port

- 8903 (Studio dev port)

## Rebuild together

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"

## Acceptance criteria

- [ ] C-01: Endpoint `POST /api/chat` dispatches prompts to the designated tool CLI or local runtime.
- [ ] C-02: Previous conversation history in the active thread is packaged into the prompt context.
- [ ] C-03: Chat UI displays an animated waiting state and renders the real CLI response in the assistant bubble.
- [ ] C-04: Subprocess execution is strictly bounded by a 30s timeout with process termination on expiration.
- [ ] C-05: Unit tests in `test_studio.py` pass without external network dependencies.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

Outcome: completed
Change: 46e11c7f8a65be9077f7aba376e8d7c5318f79a6 on t-153-studio-live-cli-chat-engine
Files:
- .agentsflower/tools/studio.py - added POST /api/chat route, execute_chat_query, format_chat_prompt, _build_chat_argv, _chat_run (30s timeout with process tree termination), _parse_chat_output, and local_adapter integration
- .agentsflower/studio/studio.js - updated sendChatMessage() to call POST /api/chat with 30s AbortController timeout, animated thinking indicator, and error bubble rendering
- .agentsflower/studio/studio.css - added styles and keyframe animation for .chat-bubble.assistant.thinking, .thinking-dots, and .chat-bubble.assistant.error
- .agentsflower/tests/test_studio.py - added TestStudioChatEngine covering CLI/local dispatch, prompt history packaging, 30s timeout termination, error handling, and UI markers
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (56 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (556 passed / 4 skipped / 0 failed)
Criteria:
- C-01: pass - evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-02: pass - evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-03: pass - evidence: .agentsflower/studio/studio.js, .agentsflower/studio/studio.css
- C-04: pass - evidence: .agentsflower/tools/studio.py, .agentsflower/tests/test_studio.py
- C-05: pass - evidence: .agentsflower/tests/test_studio.py
Found, not fixed:
- Windows Defender occasionally locks `tasks.md.tmp` during `os.replace` in `ledger.py` `_write_atomic` inside `%TEMP%` during full-suite runs (`PermissionError: [WinError 5]`); `ledger.py` is outside Allowed files.
Proposed memory updates:
- none
