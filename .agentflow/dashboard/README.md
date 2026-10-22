# Dashboard

Local layout: `file` is the repository-relative Task File path;
`fileHref` is the link relative to generated HTML in `out/`.
Workflow storage lives in `.agentflow/`; Git history is read from the repository root.

A read-only view of the project for the human (English interface): task table and filters (`out/index.html`), Gantt, timeline, links and evidence metrics (`out/graph.html`), and the roadmap (`out/roadmap.html`): every `### Stage` of `docs/project-plan.md` with declared status, local task counts and exit-criteria evidence as three separate facts, plus safe attempt/routing/gate records in the task drill-down. It never changes the project; it reads `.agentflow/state/tasks.md` (Task Ledger), `.agentflow/tasks/T-*.md` (Task Files), `.agentflow/tasks/.runtime/` (attempt and gate evidence, via `tools/route_report.py`), `.agentflow/docs/project-plan.md` and git history. Template-owned: see `.agentflow/docs/ai-handoff-protocol.md`, section "Dashboard".

## Use

```
python .agentflow/dashboard/build.py                          # build out/index.html, out/graph.html and out/roadmap.html, open any in a browser
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
| `template.html`, `graph_template.html`, `roadmap_template.html` | the three pages; `__DATA__` and `__PROJECT__` are replaced by `build.py` |
| `roadmap.css`, `roadmap.js` | roadmap-only styles and stage renderers (inlined into `roadmap.html`); the roadmap page renders the roadmap data below as three switchable layouts (cards, journey, matrix) |
| `common.css`, `common.js` | header, task card, shared helpers (inlined into both pages) |
| `filterbar.css`, `filterbar.js` | the filter panel (inlined into both pages) |
| `snapshot.py` | local versions of the dashboard sources, rollback |
| `UI-RULES.md` | interface rules this dashboard follows; read before changing it |
| `mockups/` | the T-042 layout studies (synthetic data): committed here as the design record, but never installed into projects or packaged - `install.py` skips it |

`snapshot.py` covers the sources listed in its own `SOURCES`/`PAGES` (`build.py`, `template.html`, `graph_template.html`, `common.*`, `filterbar.*` and the built `index.html`/`graph.html`); it does not cover the roadmap assets (`roadmap_template.html`, `roadmap.css`, `roadmap.js`).

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

## Roadmap data (payload `schemaVersion: 1`)

Additive fields for the roadmap view; every field above is unchanged. All strings from project files are untrusted data: pages must escape them, and the build never fetches anything.

| Field | Source | Values shown |
|---|---|---|
| `schemaVersion` | build.py | integer, `1`; absent in older payloads |
| `stages[]` | `docs/project-plan.md` | one record per `### Stage <id>` heading, in source order (not sorted) |
| `stages[].id`, `.title`, `.ordinal`, `.line` | plan heading | id text; title or `null`; 0-based source position; source line |
| `stages[].declaredRaw`, `.declared`, `.declaredKey` | `Status:` block | raw text verbatim; normalized `Planned`/`Current`/`Closed` or `null` when unrecognized (raw still shown, warning issued) |
| `stages[].source`, `.sourceRef`, `.sourceHref` | plan path | repo-relative file, anchor label, link relative to `out/` |
| `stages[].exitCriteria` | `Exit criteria:` block | full block text verbatim, `null` when absent |
| `stages[].criteria` | authored bullets | `null` = unstructured criteria (coverage unknown); else `[{id, text, evidence}]` |
| `stages[].criteria[].evidence` | authored `evidence:` line | `{state: pass|fail|stale|pending|unknown, label, provenance, recorded, artifact, external, supersededBy, ref, refKind: file|url|invalid, refExists, refHref}` — absent keys stay absent |
| `stages[].recurring` | `Recurring:` block | `{kind, note, cycles[]: {id, result, recorded, note, ref, refKind, refExists, refHref}}` — a completed cycle never closes the stage |
| `stages[].historicalRefs` | `References:` block | `[{label, note}]`, display text only, never resolved |
| `stages[].taskIds`, `.counts` | ledger join | linked task ids; `{accepted, active, review, blocked, ready, rejected, cancelled, other{}, total}` — the denominator is `total`; no percentage is computed, a zero-task stage has `total: 0`, not 0%/100% |
| `stages[].coverage` | criteria states | `{kind: "authored", total, states{state: n}}` or `{kind: "unstructured"}` |
| `stages[].duplicate`, `.diagnostics[]` | parser | duplicate stage ids are never resolved silently: both records are flagged and their tasks stay unmapped |
| `tasks[].attempts` | `.runtime/T-NNN.json` | allowlisted fields only (n, tool, role, manual, status, exitCode, startedAt/finishedAt, requestedModel/requestedEffort, effectiveModel/effectiveEffort, toolVersion, limitHit, stopReason, workerTimeout, deadline, target, note, logRef); `null` = not recorded. Never argv/env/pid/paths/quota |
| `tasks[].routing` | `.runtime/T-NNN.route.json` | `{assessments[], events[]}` allowlisted the same way (`usage`, `jev`, `probabilities`, `requestId`, `candidates`, `backup` internals are never exported); `null` = not recorded |
| `tasks[].verifications` | `.runtime/T-NNN.verify.json` | allowlisted gate records; `checks[]` reduced to `{cmd, exit}` (no output text); `stale: true` when the record SHA does not match the task's current artifact; `null` = not recorded |
| `diagnostics` | build | `{sources[]: {file, status: read|missing|unreadable|absent|synthetic, mtime, fingerprint}, warnings[], gaps[], unmappedTaskIds[], freshnessNote}` |
| `provenance` | build | `{plan, ledger, taskFiles, runtime, git, payload, synthetic}` — `synthetic: true` marks the demo fixture |

Three facts per stage stay independent: `declared` (what the plan says), `counts` (what the ledger did), `coverage` (what authored evidence says). A mismatch is a warning, never a rewrite. Tasks whose `stage` value is absent from the plan — or ambiguous because the id is duplicated — stay visible under `diagnostics.unmappedTaskIds`; bad stage data never hides task data.

`roadmap.html` renders this payload: every declared stage regardless of task filters (filters slice only the task slice, with filtered-vs-total counts shown), a Cards/Journey/Matrix view switch (the human approved all three mockups on 2026-10-18), drill-down into the shared task card plus the allowlisted `attempts`/`routing`/`verifications` records, and a diagnostics area labeled as a build snapshot, not live monitoring.

### Optional authored syntax in project-plan.md

Not required — a plan with plain `Status:`/`Exit criteria:` paragraphs parses unchanged. To get per-criterion coverage, author inside a stage's `Exit criteria:` block:

```markdown
Exit criteria:
- S5-E1: scenario suite passes            # - <ID>: <text>; the ID needs a digit or -/_
  evidence: state=pass; label="recorded pass"; provenance="gate verify"; recorded=2026-10-20; artifact=abc1234; ref=.agentflow/state/x.md
- S5-E2: external CI green
  evidence: state=pending; external=true; ref=https://ci.example/run/1
```

- `evidence:` line indent under its criterion; `;`-separated `key=value` pairs (quote values containing `;`). Keys: `state` (pass/fail/stale/pending/unknown), `label`, `provenance`, `recorded`, `artifact`, `ref`, `external`, `supersededBy`.
- `ref=` is checked at build: a path must resolve under the project root (traversal and symlink escapes are rejected, a missing target is shown as text with a warning); only `http(s)` URLs are treated as external references — `javascript:`/`data:` and other schemes are rejected. Nothing is ever fetched.
- `Recurring: <kind>` block: note lines, then `- <cycle-id>: <result>; recorded=...; ref=...; note=...` bullets. A completed cycle does not close the stage.
- `References:` block: `- <label>; note=...` bullets for historical evidence outside the repository — display text only.
- A stage block ends at the next level-1..3 heading; deeper headings and fenced code blocks are opaque (a `### Stage` line inside a fence is ignored).
