# .agentsflower

Everything AgentsFlower needs lives in this folder, so it never collides with a project's own `docs/`, `tasks/`,
`tools/` or `state/`. Git and product commands still run from the repository root.

| Path | Owner | What |
|---|---|---|
| `VERSION` | template | installed AgentsFlower version |
| `docs/ai-handoff-protocol.md` | template | the protocol: terms, states, rules, session steps |
| `docs/typesafe.md` | template | TypeSafe AI: official documentation links and the rules `route.py` follows |
| `docs/project-rules.md`, `docs/project-plan.md` | project | Project rules (worktrees, Preflight, Tool routing) and the roadmap |
| `roles/` | template | one file per role; `tool-routing.md`: which tool takes which task |
| `commands/` | template | slash-command texts; `.claude/commands/` holds one-line pointers here |
| `tasks/_template.md` | template | Task File template; `tasks/T-NNN-*.md` are the project's Task Files |
| `tasks/.runtime/` | local | attempt history, logs, evidence (git-ignored) |
| `state/` | project | handoff, current step, decisions, known issues, session log, Task Ledger |
| `workspace.json` | project | workspace only: the product repositories under the workspace root |
| `docs/model-options.json` | project | tools, model families, effort variants, availability windows and `quota_group`s for `route.py` |
| `docs/quota-policy.json`, `docs/quota-samples.json` | project | optional declared quota expectations and their readings (`tick.py`; `AGENTFLOW_QUOTA_POLICY`/`AGENTFLOW_QUOTA_SAMPLES` override) |
| `template-source.json` | project | where this install came from (written by `install.py`); `upstream.py` reads it |
| `tools/` | template | `run_task.py` launcher (`run-task.ps1` Windows wrapper), `cli.py` unified `agentsflower` entry, `studio.py` local web cockpit, `gate.py` preflight/verify/`done`, `accept.py`, `ledger.py`, `install.py`, `paths.py`, `tick.py` scheduler, `mcp_server.py` optional MCP server, `machine_capacity.py` shared machine slots and limits, `dispatch.py` shared scheduling preview and grants, `route.py`/`plan_route.py`/`route_report.py` (Jev routing), `quota_groups.py`, `limit_detection.py`, `hooks.py` Codex Stop-hook adapter, `power_guard.py` Windows idle-sleep guard, `conductor.ps1`/`conductor-panel.ps1` Windows-only helpers, `upstream.py` template drift report |
| `studio/` | template | local web UI cockpit files (HTML/CSS/JS, zero runtime dependencies) |
| `dashboard/` | template | read-only view for the human (`python .agentsflower/dashboard/build.py`) |
| `skills/` | template | specialized skills ecosystem (UI/UX, algorithms, architecture, browser, backend, frontend, devops, product, geo-seo-audit) |
| `tests/` | template | checks of the tools themselves (`python -m unittest discover -s .agentsflower/tests`) |

Template-owned files are replaced by `install.py --update`; project-owned files are never overwritten.
Rules: `docs/ai-handoff-protocol.md`, section "Installing or updating AgentsFlower".
