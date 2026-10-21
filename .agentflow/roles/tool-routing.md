# Tool routing

Which tool takes which task. Read by the [Orchestrator](orchestrator.md) only. The choice goes to `Tool:` in the Task File and to the ledger `Tool` column.

This file is shared by all projects and replaced on template update: notes from one project go to its Project rules, `## Tool routing`. As of 2026-10; the strengths below are defaults, not measurements: confirm them on your own tasks.

## How to choose

0. If the project has `.agentflow/docs/model-options.json` and a TypeSafe key: `python .agentflow/tools/route.py T-NNN` first. Jev ranks the configured usable CLI/model options and reasoning effort; the highest eligible choice is primary and the highest eligible option on another CLI is backup. Exit 0 (confidence >= 0.9): take it (`--apply`); exit 4 (0.5-0.9): review its evidence; exit 3: decide from the task and available tools. Rules and links: [../docs/typesafe.md](../docs/typesafe.md). Keep the options file current: models, efforts, availability windows, and project policy.
1. Fit: evaluate the task's required capabilities and model characteristics. No platform has a standing first-choice priority.
2. Remaining limit: at session start the human says what is left per tool. Not said: ask in one line. Do not write limits to memory.
3. Expensive tools only where a mistake is expensive: mechanical edits, renames, simple tests go to the cheapest fitting tool or a smaller model.
4. Tester on a different tool than the Developer when possible: another model has other blind spots. Codex's [review isolation](../docs/ai-handoff-protocol.md#terms) uses a sandbox; other tools rely on the end check.
5. Plan for limits, not only fit. Observed: Claude Code worker sessions can end after minutes when several run at once; an Antigravity quota can be gone for days; a Codex sandbox on Windows can refuse to start processes. Give long tasks to the tool that has proved steady on this machine, keep a second tool ready, and move a task at once when its tool is out ([Recovery](../docs/ai-handoff-protocol.md#recovery-stale-task)).
6. Multiple projects on one machine share AgentFlow's tool slots, declared ports, and observed usage-limit reset times through `machine_capacity.py`. A busy slot waits and is retried; it does not mark a task failed. Keep each project's repository and worktree paths distinct.

## Tools

| Tool | Strong | Weak |
|---|---|---|
| Claude Code | complex multi-file work and architecture; long action chains; project memory (`CLAUDE.md`, commands) | more tokens per task; limits per time window |
| Codex CLI | fewer tokens per task; sandbox modes; small models for simple tasks; reads `AGENTS.md` | large multi-file changes |
| Antigravity (IDE) | built-in browser agent: sites, screen widths, screenshots | not automatable: `-Manual` only |
| Antigravity CLI | context up to 1M tokens: large code, logs, dumps; fast models; free quota | young; quotas can run out for days; soft confirmations: never production |
| Devin CLI | independent model for development and testing; follows Task Files well | needs `--permission-mode dangerous` in print mode; no Windows sandbox (the end check guards a Tester) |

## Task types

- Planning and acceptance: the available Orchestrator session prepares tasks and decides from gate evidence. The chat's manually selected model does not determine a worker's model.
- Development: route every scoped Developer Task File through Jev when available; launch independent tasks in parallel within shared capacity.
- Code review and automated tests: Tester Task Files use narrow checks covering the changed behavior and an independent model when one is available.
- Interface verification: a browser-capable Tester checks changed UI states after code and targeted tests. Antigravity IDE is manual; another browser-capable tool may be used.
- Reading large code or logs is work inside one of these tasks, not a separate routing category.
- Deployment uses a tool with configured server access and the runbook; production still requires the human's approval.

## Backup and limits

An unstarted ready task with a saved backup may switch automatically when `AGENTFLOW_BACKUP_ROUTING=on` and the primary platform is limited or full. A started task follows [Recovery](../docs/ai-handoff-protocol.md#recovery-stale-task); after its attempt ends, use the saved backup if still eligible and record the handover. If Jev made no decision or no backup is usable, the Orchestrator decides or leaves the task waiting. No fixed vendor-to-vendor fallback order applies.

## Tool notes

- Launch: `.agentflow/tools/run-task.ps1 T-NNN <codex|claude|agy|devin>`. Machine settings are environment variables, not script edits: `AGENTFLOW_CODEX` (codex path, `*` allowed, the newest match wins), `AGENTFLOW_CODEX_ARGS` (for example `-m <model>`), `AGENTFLOW_CLAUDE`, `AGENTFLOW_AGY`, `AGENTFLOW_DEVIN`, `AGENTFLOW_PYTHON`. Set them as user variables: the worker window gets them from the launcher (protocol, Launching workers, Machine setup).
- Codex installed with the Codex desktop app: the CLI is not on PATH; use `%USERPROFILE%\.codex\plugins\.plugin-appserver\codex.exe` (the copy in `.codex\.sandbox-bin` lacks its helper and cannot run commands). Its tester sandbox may fail with EPERM on the npm prefix or cache, or `CreateProcessWithLogonW` error 1909: give that test to another tool.
- Models: `Model: <model>[, effort=<level>]` in the Task File. Codex uses `-m` and `-c model_reasoning_effort=<level>`; Claude uses `--model` / `--effort`; Devin uses `--model` with the effort encoded in the model id (`swe-2-high`, `gpt-6-astra-medium`; inspect with `devin models list`). The installed Antigravity CLI likewise exposes effort-specific model ids (`agy models`), so routing writes the concrete id. Machine-wide extra flags: `AGENTFLOW_<TOOL>_ARGS`.
- Devin CLI: `-p` print mode; `smart` permissions refuse every tool call without a person, and a new worktree is an untrusted folder, so the launcher passes `--permission-mode dangerous --respect-workspace-trust false`. Login: `devin auth login`.
- Antigravity CLI: a Developer runs in print mode with `--dangerously-skip-permissions` and `--output-format stream-json`, a Tester the same print mode without `--dangerously-skip-permissions` — both non-interactive, so progress reaches the log and the process exits by itself. Login: run `agy` once.
- Antigravity: the worktree must be in its trusted folders before the first run; the first run passes the setup wizard by hand once. Error 500: retry, not a task failure.
- Antigravity (IDE): `.agentflow/tools/run-task.ps1 T-NNN -Manual`, the human starts the task, then `-MarkFinished`.
- Prompt for tools without slash commands (they read `AGENTS.md` themselves): `Your role: .agentflow/roles/<role>.md. Your task: .agentflow/tasks/T-NNN-slug.md. Follow .agentflow/docs/ai-handoff-protocol.md, section "Starting a role session".` Claude Code: `/start-role <role> .agentflow/tasks/T-NNN-slug.md`.
