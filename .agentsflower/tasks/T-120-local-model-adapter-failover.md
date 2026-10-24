# T-120: Local Model Protocol & Adaptive Failover Architecture

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-121
Branch: t-120-local-model-failover
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-120-local-model-failover
Independent check: tester
Resume: none
Routing exception: human authorized via AgentsFlower Studio (2026-10-24)

## Goal

Implement zero-cost local model adapter and automated multi-tier failover protocol for AgentsFlower:
1. Create `.agentsflower/tools/local_adapter.py` probing local inference runtimes (Ollama on `11434`, LM Studio / LocalAI / vLLM on `1234` / `8000`).
2. Implement auto-detection of local coding models (`deepseek-r1`, `qwen2.5-coder`, `llama3.3`).
3. Implement adaptive failover engine (`.agentsflower/tools/failover.py`) that handles token exhaustion (detected by `limit_detection.py`), switches sessions across tiers (Tier 1 Cloud -> Tier 2 Backup Cloud -> Tier 3 Zero-Token Local), preserving conversation context.
4. Expose CLI commands (`agentsflower local probe`, `agentsflower failover status`) and Studio API endpoints (`/api/local/probe`, `/api/failover/status`).
5. Provide comprehensive unit tests in `.agentsflower/tests/test_local_adapter.py`.

## Read first

- .agentsflower/docs/ai-handoff-protocol.md
- .agentsflower/tools/limit_detection.py
- .agentsflower/tools/route.py

## Allowed files

- .agentsflower/tools/local_adapter.py
- .agentsflower/tools/failover.py
- .agentsflower/tools/cli.py
- .agentsflower/tools/studio.py
- .agentsflower/studio/index.html
- .agentsflower/studio/studio.js
- .agentsflower/studio/studio.css
- .agentsflower/docs/model-options.json
- .agentsflower/tests/test_local_adapter.py
- .agentsflower/tools/install.py
- .agentsflower/state/tasks.md
- .agentsflower/state/current-step.md

## Do not touch

- All other files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] C-01: `.agentsflower/tools/local_adapter.py` probes Ollama and LM Studio endpoints, returning structured reachability and model list.
- [ ] C-02: `.agentsflower/tools/failover.py` defines ordered tier fallback (Tier 1 Cloud -> Tier 2 Cloud -> Tier 3 Local) and context-preserving session transfer.
- [ ] C-03: `agentsflower local probe` and `agentsflower failover` CLI subcommands work cleanly.
- [ ] C-04: Studio `Model Quota Hub` visually displays the failover chain and local model status.
- [ ] C-05: All unit tests in `test_local_adapter.py` pass without external network dependencies (mocked sockets/HTTP).

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_local_adapter.py"

## Result

<!-- Worker writes its outcome below this block -->
