# Dashboard

Local layout: `file` is the repository-relative Task File path;
`fileHref` is the link relative to generated HTML in `out/`.
Workflow storage lives in `.agentflow/`; Git history is read from the repository root.

A read-only view of the project for the human (English interface): task table and filters (`out/index.html`), Gantt, timeline, links and evidence metrics (`out/graph.html`). It never changes the project; it reads `.agentflow/state/tasks.md` (Task Ledger), `.agentflow/tasks/T-*.md` (Task Files), `.agentflow/tasks/.runtime/` (attempt and gate evidence, via `tools/route_report.py`) and git history. Template-owned: see `.agentflow/docs/ai-handoff-protocol.md`, section "Dashboard".

## Use

```
python .agentflow/dashboard/build.py                          # build out/index.html and out/graph.html, open either in a browser
python .agentflow/dashboard/build.py --demo                   # same pages from a deterministic DEMO DATA fixture: no project reads or memory writes, clearly marked
python .agentflow/dashboard/snapshot.py save "what changed"   # keep the current dashboard sources as version vN
python .agentflow/dashboard/snapshot.py list
python .agentflow/dashboard/snapshot.py restore vN            # roll the sources back (the current state is saved first)
```

Needs Python 3 and git. Run it after the Orchestrator updates the ledger, or whenever you want a fresh view. `out/` and `versions/` are local and git-ignored; everything else here is part of the template.

## Files

| File | Role |
|---|---|
| `build.py` | reads ledger, Task Files, git, `route_report.metrics()`; writes `out/*.html`; owns the data contract below |
| `template.html`, `graph_template.html` | the two pages; `__DATA__` and `__PROJECT__` are replaced by `build.py` |
| `common.css`, `common.js` | header, task card, shared helpers (inlined into both pages) |
| `filterbar.css`, `filterbar.js` | the filter panel (inlined into both pages) |
| `snapshot.py` | local versions of the dashboard sources, rollback |
| `UI-RULES.md` | interface rules this dashboard follows; read before changing it |

## Data contract (`build.py` -> pages)

The pages compare against these exact strings; change both sides together. Display labels are English; the machine values travel next to them as `statusKey`, `roleKey`, `verdict`, `ind`.

| Field | Source | Values shown |
|---|---|---|
| `status` | ledger `Status` | `ready` → Ready, `in progress` → In progress, `review` → In review, `done` → Done, `rejected` → Rejected, `blocked` → Blocked, `cancelled` → Cancelled (1.x words are mapped) |
| `statusKey`, `roleKey` | ledger `Status`, `Role` | the raw machine values, untranslated |
| `role` | ledger `Role` | Developer, Tester, Deployer |
| `tool` | ledger `Tool` | agent that did the work: Claude Code, Codex, Antigravity, or the raw value / "not set" |
| `result` | Result `Outcome` (1.x: `Status`) | Completed by worker, Partially done, Worker blocked, Worker failed, Deploy rolled back, "No report". This is the worker's report, not acceptance |
| `check` | `Independent check` and tester `Verdict` + `Verifies` | Tester: pass / partial / fail, " (stale link)" when the `Verifies` SHA no longer matches the checked task's current commit, Tester assigned, Tester required no report, No independent check, Not set (legacy task), `—` for non-developer tasks |
| `checkedBy` | tester Task File `Verifies:` | per check: `{id, verdict, status, sha, stale}` — the link is the declared `Verifies`, never a title regex |
| `origin` | estimated from text | Owner, Orchestrator, Tester, Deployer (labeled as an estimate) |
| `sizeCls` | commits `[T-NNN] ...` | docs, S, M, L, XL, `—` |
| `metrics` | `tools/route_report.py metrics()` | first-pass gate rate (first `gate.py verify` record per task, denominator = tasks with that evidence), lead time from attempt timestamps, tester verdict counts; missing evidence is N/A, never zero; cost/tokens are N/A (not recorded) |
| `demo` | `--demo` flag | `true` marks the deterministic fixture; the header shows a DEMO DATA badge |

Three different questions, three different fields: ledger `status` (is it accepted), `result` (what the worker reported), `check` (what the independent review found). "Completed by worker" is not "Done", and a `fail` verdict is a completed negative report, not a worker failure.

The page header shows the name of the repository folder containing `.agentflow/` (or `demo-project` in demo mode).
