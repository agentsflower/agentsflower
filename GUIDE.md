# Guide: how to use AgentFlow

A project-memory template with a team of agent roles: Orchestrator, Developer, Tester, Deployer. How it works inside: [README](README.md) and the [protocol](.agentflow/docs/ai-handoff-protocol.md). This file is only "what to type and where to click". A Russian version of this guide: [GUIDE.ru.md](GUIDE.ru.md).

The *template* is the folder where you cloned this repository, written below as `<AgentFlow>` — substitute your own path. Everything AgentFlow puts into a project lives in one folder, `.agentflow/`; the project root gets only small entry points (`AGENTS.md`, `CLAUDE.md`, `.claude/commands/`) and a marked block in `.gitignore`. A project's own `docs/`, `tasks/`, `tools/` are never touched.

Requirements on the machine: git, Python 3.10+ (stdlib only — no third-party runtime dependencies), and the CLIs of the tools your workers will use (`claude`, `codex`, `agy`, `devin`). PowerShell 7 is needed only on Windows for the compatibility wrapper `run-task.ps1` and the optional conductor; the launcher itself is `run_task.py` (pure Python, cross-platform).

---

# Part 1. Installation

| Your project folder | Path |
|---|---|
| Empty, a fork, or existing code without AgentFlow (its own `AGENTS.md`, `tasks/`, `tools/` are fine) | [A. Install](#a-install) |
| One folder holding several repositories (a workspace, e.g. `code/` with `backend/`, `web/`…) | [A2. Workspace](#a2-workspace) |
| `.agentflow/` already installed | [B. Update](#b-update) |
| Old 2.1 layout: `docs/ai-handoff-protocol.md`, `tools/gate.py` at the root | [C. Migrate the old layout](#c-migrate-the-old-layout) |
| You want the `agentflow` command | [D. Install from a package](#d-install-from-a-package) |
| You want the MCP server in your IDE | [E. MCP server](#e-mcp-server-optional) |

## A. Install

### Step 1. Git

The agents need git with a main branch and at least one commit, and the installer writes the template only into the **root** of a git repository. For a folder with several repositories see [A2](#a2-workspace).

Empty folder:

```bash
cd /path/to/project          # Windows: cd D:\path\to\project
git init -b main
git commit --allow-empty -m "init"
```

Existing repository: commit everything (`git status`), then make an install branch: `git switch -c chore/agentflow`.

### Step 2. Preview what will change

```bash
python <AgentFlow>/.agentflow/tools/install.py /path/to/project --dry-run
```

Expected result: a list of actions; nothing is written. The installer deletes nothing; if `AGENTS.md`, `CLAUDE.md` or `.gitignore` already exist, their content stays and the managed block goes between `agentflow:begin` and `agentflow:end`. One-line pointers appear under `.claude/commands/`; files that already exist are kept.

If the project folder is inside a repository rather than at its root, add `--inside-repo`.

### Step 3. Install and finish the setup

```bash
python <AgentFlow>/.agentflow/tools/install.py /path/to/project
```

Then start a session in the project (Claude Code, VS Code, any tool) and ask it to finish the install — pick a worktrees folder outside cloud sync, e.g. `D:\tmp` or `~/worktrees`:

```text
AgentFlow is installed in .agentflow/. Finish the install:
.agentflow/docs/ai-handoff-protocol.md, section "Installing or updating AgentFlow", "Install".
Worktrees folder: <your worktrees folder>.
```

The session fills in `.agentflow/docs/project-rules.md` (main branch, worktrees folder, `## Preflight`, `## Tool routing`) and `.agentflow/docs/project-plan.md` for your project; `python .agentflow/tools/ledger.py show` creates the Task Ledger; one commit. If a tool reports that a test config reaches staging or production by default, that is a decision for you — the installer does not change it.

## A2. Workspace

A workspace is one folder holding several product repositories (for example `code/` with `backend/` and `web/`). AgentFlow installs into the workspace root, which is itself a small git repository tracking only AgentFlow files and the root entry points; product repositories stay untouched.

```bash
python <AgentFlow>/.agentflow/tools/install.py /path/to/code --workspace --git-init --dry-run
python <AgentFlow>/.agentflow/tools/install.py /path/to/code --workspace --git-init
```

Afterwards check: the root has `.git` (the memory repository), `.agentflow/workspace.json` lists the product repositories (default: child folders with `.git`; override with `--repos a,b`), and `.gitignore` does not exclude folders AgentFlow needs (a `!/<folder>` negation is added where required). Commit `git add -A && git commit -m "chore: install AgentFlow"` in the memory repository and finish step 3 of [A](#a-install).

Task Files in a workspace name `Repo:` (which repositories the task may change), and paths in `Allowed files`, `Do not touch` and `## Checks` start with the repository folder: `web/src/...`. Each task gets one worktree folder holding one worktree per repository it touches. Acceptance merges the same branch name into the main branch of every affected repository.

## B. Update

```bash
python <AgentFlow>/.agentflow/tools/install.py /path/to/project --update --dry-run
python <AgentFlow>/.agentflow/tools/install.py /path/to/project --update
```

The update replaces template-owned files and refuses to run while they have uncommitted changes; files the project added inside `.agentflow/` are reported and kept. Memory (`.agentflow/state/`, Task Files, Project rules, the runbook) is never overwritten. In a Claude Code session:

```text
AgentFlow was updated in .agentflow/. Finish the update:
.agentflow/docs/ai-handoff-protocol.md, section "Installing or updating AgentFlow", "Update".
```

Afterwards: `.agentflow/VERSION` is new, migration notes of the in-between CHANGELOG entries were applied to open Task Files and the ledger, a dated entry went into `decisions.md`, one commit.

## C. Migrate the old layout

Version 2.1 kept `docs/ai-handoff-protocol.md`, `tools/gate.py` and `tasks/` at the repository root. The installer refuses that layout and asks you to move your own files into `.agentflow/` first, then runs a normal install. The 2.1 memory layout maps to `.agentflow/state/` and `.agentflow/docs/`; version 2.1 had no `roles/`, `commands/` or `dashboard/`.

## D. Install from a package

The repository also builds a local distribution `agentflow-sdlc` (source install — it is not published on PyPI under this name):

```bash
python -m pip install build          # development tooling, one time
python -m build                      # writes dist/agentflow_sdlc-<ver>-py3-none-any.whl and a .tar.gz
python -m pip install dist/agentflow_sdlc-*.whl
agentflow --version                  # equals .agentflow/VERSION
```

The wheel bundles the whole installer-owned template under `agentflow/template/`, so the `agentflow` command works from any directory:

```bash
agentflow install <project> [--update] [--dry-run] [--inside-repo] [--workspace] [--repos a,b] [--git-init] [--mcp [--mcp-client claude|cursor]]
agentflow run T-NNN --role <developer|tester|deployer> [--project <dir>]
agentflow gate <verify|preflight|endcheck|task> <T-NNN> [--project <dir>]
agentflow accept T-NNN [--project <dir>]
agentflow ledger <add|set|approve|show> [--project <dir>]
agentflow mcp [--enable-orchestrator-tools] [--project <dir>]
agentflow dashboard [--open] [--project <dir>]
```

`--project` may be any directory inside the project; project commands walk up to the installed `.agentflow` and run that project's own tool scripts. Without the package, every subcommand has a direct equivalent: `python .agentflow/tools/<tool>.py` from the project root.

## E. MCP server (optional)

`.agentflow/tools/mcp_server.py` exposes project state over the Model Context Protocol on stdio. It needs the official SDK — an opt-in extra, never required by the core tools:

```bash
python -m pip install "agentflow-sdlc[mcp]"   # or: python -m pip install "mcp>=2.3,<3"
python .agentflow/tools/mcp_server.py         # or: agentflow mcp
```

Tools exposed by default (read-only): `agentflow_status`, `agentflow_get_task`, `agentflow_query_ledger`, plus `agentflow_run_gate` which runs the real `gate.py`. `agentflow_accept_task` exists only behind the explicit operator flag `--enable-orchestrator-tools`. The flag controls the server's surface; it is not proof of the caller's role — anything that can reach the server can call what it exposes.

To wire a client into the project config, re-run the installer with the explicit opt-in flag:

```bash
python .agentflow/tools/install.py <project> --update --mcp                    # Claude Code: .mcp.json
python .agentflow/tools/install.py <project> --update --mcp --mcp-client cursor  # Cursor: .cursor/mcp.json
```

`--mcp` merges an `agentflow` entry without touching unrelated keys or other servers, points at the project's own installed server with privileged tools off, and refuses a malformed file or an unmanaged conflicting `agentflow` entry before writing anything.

## F. Machine resources (opt-in)

Shared machine scheduling — how many tool slots this machine offers to AgentFlow projects — is opt-in per machine. `machine_capacity.py` keeps a registry of projects that claimed a slot; `dispatch.py` previews shared scheduling and issues grants a launcher can exchange (`run_task.py --dispatch-grant <token>`). If you never configure it, every command above works unchanged: launching a worker does not require a grant.

The `conductor.ps1` / `conductor-panel.ps1` helpers (scheduled orchestrator ticks and autostart subscription on this machine) are **Windows-only** — they use PowerShell, `conductor.env.json` and Task Scheduler. They are not part of the core workflow and are never required on Linux or macOS.

TypeSafe AI users: `.agentflow/docs/typesafe.md` holds the official documentation links and the rules `route.py` follows when picking tool/model options.

---

# Part 2. Daily work

## Who does what

| Session | Started by | Does |
|---|---|---|
| Orchestrator | `/start-role orchestrator` | splits the goal into Task Files, launches workers, accepts on evidence; the only writer of project memory |
| Developer / Tester / Deployer | `python .agentflow/tools/run_task.py T-NNN <tool>` (usually launched by the Orchestrator) | one task each in a fresh session; writes only `## Result` |
| No role (Single Mode) | `/start-session` | does everything itself, including memory updates |

The Orchestrator can also launch through the CLI: `agentflow run T-NNN --role developer` reads the `Tool:` field from the Task File and refuses if `--role` does not match the file. Deployer tasks always launch with `--manual`: the launcher prepares the attempt, a human starts the tool — a deployer never runs unattended.

## A worker's lifecycle

1. `run_task.py T-NNN <tool>` creates the worktree `worktrees/<repo>-t-NNN-slug` and branch `t-NNN-slug`, runs the gate's preflight (deny rules, file ownership, ledger state), records the attempt and starts the tool with the task prompt.
2. The worker does the task, runs its `## Checks` verbatim, makes one commit `[T-NNN] <type>: <what>` and fills `## Result` in the Task File — in the main folder, never the copy inside the worktree.
3. When the attempt exits, the end check verifies the worktree is clean and the Task File in the main folder gained a Result.
4. The Orchestrator runs `python .agentflow/tools/gate.py verify T-NNN` — the `## Checks` commands run verbatim — and on a pass accepts with `python .agentflow/tools/accept.py T-NNN` (verify, merge, ledger `done`, worktree and branch cleanup).

Process control for a stuck or manual attempt:

```bash
python .agentflow/tools/run_task.py --status          # state of the last attempt of every task
python .agentflow/tools/run_task.py --stop            # kill a hung worker's whole process tree
python .agentflow/tools/run_task.py --mark-finished   # a --manual attempt has finished
python .agentflow/tools/run_task.py --recheck         # rerun the end check after fixing its cause
```

## Watching progress

```bash
python .agentflow/dashboard/build.py          # writes .agentflow/dashboard/out/index.html and graph.html
python .agentflow/dashboard/build.py --demo   # same pages from a deterministic fixture, marked DEMO DATA
agentflow dashboard --open                    # build and open in a browser
```

The dashboard is read-only for the human and invents nothing: statuses, roles and verdicts come from the ledger and Task Files; the metrics panel (first-pass gate rate, lead time, verdict counts) is computed only from recorded evidence — missing history, runtime or cost is shown as N/A, never zero or an invented saving. `--demo` exists for screenshots and layout review: it reads no project memory and writes only into `out/`.

## Recovery

- A dead or errored attempt is recorded per task in `.agentflow/tasks/.runtime/T-NNN.json`; the ledger stays `in progress` until the Orchestrator decides. Do not repeat a failed path recorded in `.agentflow/state/known-issues.md`.
- `gate.py verify` failing on a `completed` Result means the task is rejected: the Orchestrator writes a successor Task File with the findings — it never edits the worker's code itself.
- A `blocked` Result goes back to the Orchestrator with the worker's question.
- Review isolation: a Tester works in a disposable checkout of the `Verifies` commit and changes nothing; after its attempt the launcher checks that branch, worktree and Task File are untouched.

## Permission boundaries (what is supported)

- Workers change only files listed in `Allowed files`; Preflight deny rules in `.agentflow/docs/project-rules.md` (`## Preflight`) are enforced by `gate.py` before a launch.
- For Claude Code, allow only the launcher — not the whole project:

  ```json
  { "permissions": { "allow": [ "PowerShell(.\\.agentflow\\tools\\run-task.ps1:*)", "Bash(python .agentflow/tools/run_task.py:*)" ] } }
  ```

- Isolation is by git worktree and by post-attempt checks, not by a universal sandbox: Codex runs sandboxed, Claude on Windows is checked after the attempt. Do not rely on the launcher alone to prevent writes outside `Allowed files` — verify with the end check.
- No tool may push, merge to main, or deploy: merges belong to the Orchestrator's `accept.py`, deployment to a Deployer session that starts only after the human's explicit yes.

## If something goes wrong

- The ledger row for a task is the source of truth for its state: `python .agentflow/tools/ledger.py show`.
- The full test suite of the template: `python -m unittest discover -s .agentflow/tests` (stdlib only, offline). Packaging and MCP integrations run explicitly: `python .agentflow/tests/check_package.py`, `python .agentflow/tests/check_mcp.py`.
- Platform evidence: `.agentflow/docs/release-validation.md` records which OS/Python cells are actually verified; a local green run is never a green macOS run.
