# AgentsFlower

[![CI](https://github.com/agentsflower/agentsflower/actions/workflows/ci.yml/badge.svg)](https://github.com/agentsflower/agentsflower/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.15.11-blue.svg)](CHANGELOG.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![MCP ready](https://img.shields.io/badge/MCP-optional%20server-green.svg)](#mcp-server-optional)

Project memory and four agent roles for running one software project with several AI coding sessions (Claude Code, Codex CLI, Antigravity, Devin) without losing state or overwriting each other's work.

## Why

Multi-agent coding fails in predictable ways: context drifts between sessions, parallel workers collide on the same files, and "done" gets reported without evidence. AgentsFlower answers each failure with a small mechanism instead of a big framework:

- **Context drift** → one canonical project memory with a single writer. All rules live in one file, [.agentflow/docs/ai-handoff-protocol.md](.agentflow/docs/ai-handoff-protocol.md); everything else points there.
- **File collisions** → each task is one Task File, one branch, one isolated git worktree, one fresh session.
- **Hallucinated done** → acceptance runs the task's own `## Checks` verbatim through `gate.py`; only then does `accept.py` merge and update the Task Ledger.

Everything AgentsFlower puts into a project lives in one folder, `.agentflow/`, so it never collides with the project's own `docs/`, `tasks/` or `tools/`. The project root gets only small entry points (`AGENTS.md`, `CLAUDE.md`, `.claude/commands/`) and a marked block in `.gitignore`; existing files keep their content. The core is Python 3.10+ stdlib only — no third-party runtime dependencies.

## How it works

```mermaid
flowchart LR
    O[Orchestrator<br/>only writer of<br/>project memory] -->|writes| TF[Task File<br/>contract: role, files,<br/>checks, criteria]
    TF -->|run_task.py / agentflow run| D[Developer<br/>fresh session,<br/>isolated worktree]
    TF -->|Verifies: SHA| T[Tester<br/>disposable checkout,<br/>changes nothing]
    D -->|Result + one commit| G[gate.py<br/>preflight / verify:<br/>checks run verbatim]
    T -->|Verdict| G
    G -->|pass| A[accept.py<br/>merge + Task Ledger<br/>worktree cleanup]
    A -->|accepted SHA| DP[Deployer<br/>manual launch,<br/>deploys after the<br/>human's yes]
    O -->|reads evidence| A
```

The Orchestrator splits the goal into task contracts, launches workers and accepts results on evidence; it is the only writer of project memory. Developers and Testers each work on an isolated artifact (worktree / disposable checkout); the Deployer consumes only an accepted SHA and starts manually after human approval. Isolation is by git worktree plus post-attempt checks — not a universal sandbox guarantee for every tool.

## Dashboard

```bash
python .agentflow/dashboard/build.py          # real view -> .agentflow/dashboard/out/
python .agentflow/dashboard/build.py --demo   # deterministic fixture, marked DEMO DATA
agentflow dashboard --open                    # packaged CLI: build and open in a browser
```

A read-only view for the human: task table, filters, Gantt, timeline, a roadmap page showing every `### Stage` of `docs/project-plan.md` (declared status, local task counts and exit-criteria evidence kept as three separate facts), and evidence metrics (first-pass gate rate, lead time, verdict counts). Missing telemetry is shown as N/A — never a zero or an invented saving. Local source snapshots: `python .agentflow/dashboard/snapshot.py save <what>` / `restore vN`.

![AgentsFlower dashboard](.agentflow/docs/assets/dashboard.png)

*Screenshot: this repository's own development dashboard — real task data, captured locally.*

## Contents

| Path | What |
|---|---|
| `.agentflow/docs/ai-handoff-protocol.md` | the protocol: terms, states, rules, session steps |
| `.agentflow/roles/` | one instruction file per role; `tool-routing.md`: which tool takes which task |
| `.agentflow/commands/` | slash-command texts (`.claude/commands/` holds one-line pointers) |
| `.agentflow/tasks/_template.md` | Task File template |
| `.agentflow/tools/` | `install.py` installer/updater, `run_task.py` launcher (`run-task.ps1` Windows wrapper), `cli.py` unified CLI, `gate.py` preflight/verify/`done`, `accept.py` acceptance, `ledger.py` Task Ledger, `tick.py` scheduler, routing (`route.py`, `plan_route.py`, `route_report.py`, `quota_groups.py`), machine sharing (`machine_capacity.py`, `dispatch.py`), `hooks.py` Codex adapter, `mcp_server.py` optional MCP server |
| `.agentflow/dashboard/` | read-only view for the human (`python .agentflow/dashboard/build.py`) |
| `.agentflow/tests/` | tests of the tools (`python -m unittest discover -s .agentflow/tests`) |
| `.agentflow/VERSION`, `.agentflow/README.md` | version and folder map |
| `AGENTS.md`, `CLAUDE.md`, `.claude/commands/` | entry points for the tools |
| `GUIDE.md` | step-by-step guide: install, update, machine setup, daily use ([Russian version](GUIDE.ru.md)) |
| `CHANGELOG.md`, `RELEASE_NOTES.md` | what changed in each version; latest release notes |
| `.github/workflows/ci.yml` | CI matrix: ubuntu/macos/windows × Python 3.10–3.12, plus package and MCP integration jobs |

The template's own memory (`.agentflow/state/`, `.agentflow/docs/project-plan.md`) describes the development of AgentsFlower itself and is never copied into a project.

Requirements: git, Python 3.10+, and the CLIs of the tools you use. PowerShell is needed only on Windows, for the compatibility wrapper and the optional conductor (7 verified; 5.1 unverified). The conductor/autostart helpers are Windows-only.

## Quick start

```bash
python <AgentsFlower>/.agentflow/tools/install.py <project> --dry-run   # see what would change
python <AgentsFlower>/.agentflow/tools/install.py <project>             # install (later: --update)
```

Or build the local package for the `agentflow` command (source install, not on PyPI):

```bash
python -m pip install build && python -m build
python -m pip install dist/agentflow_sdlc-*.whl
agentflow install <project>
```

Then follow [GUIDE.md](GUIDE.md). In Claude Code the Orchestrator starts with `/start-role orchestrator` and your goal; a session without a role uses `/start-session`.

## MCP server (optional)

Expose project state to Claude Code, Cursor or any MCP client over stdio:

```bash
python -m pip install "agentflow-sdlc[mcp]"   # official SDK, opt-in extra
python .agentflow/tools/install.py <project> --update --mcp
```

Read-only tools by default; `agentflow_accept_task` only behind the explicit operator flag `--enable-orchestrator-tools`. The core tools never need the SDK.

## Verification status

Local evidence: Windows and Linux test-suite runs are recorded in [.agentflow/docs/release-validation.md](.agentflow/docs/release-validation.md). One remote CI run has executed (2026-10-17): the ubuntu test jobs and both package jobs were green; the windows-latest and macos-latest test jobs failed (the unit-test command exited 1) — an environment-specific failure still open — and the mcp jobs were skipped by dependency. There is still no green macOS result, and none is claimed here.

License: MIT.
