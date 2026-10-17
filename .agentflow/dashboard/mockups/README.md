# Roadmap view — layout mockups (T-042)

Clickable offline mockups of the proposed **Roadmap** dashboard view described in
`.agentflow/tasks/.runtime/dashboard-roadmap-planning/PLAN.md` (sections 1–4).
They exist only so the human can pick a layout before implementation
(UI-RULES A1.2). All data is **synthetic** — `fixtures.json` is invented to
exercise the plan cases; no project files are read and nothing here is real
project evidence. The header carries a MOCKUP badge.

## Variants

Open in a browser (no server needed):

| File | Information architecture |
|---|---|
| `roadmap-a-cards.html` | **Stage-first cards.** Every declared stage is a card in plan source order; each card carries the three facts, blockers, foldable criteria/evidence and a task table. Left rail is a roadmap index + totals; right rail is diagnostics + selection detail. Closest to the existing dashboard vocabulary. |
| `roadmap-b-journey.html` | **Journey stepper.** The plan is a vertical path; stages are nodes coloured by declared status with dated-record spans ("no dated local records" stated when absent). Nodes expand in place. Emphasizes stage order and progression over per-stage density. |
| `roadmap-c-matrix.html` | **Compact matrix.** One row per stage: declared / task counts / evidence / blockers / source, expandable in place. Densest variant; best when there are many stages. |

Shared behavior, identical in all three:

- same header/theme/"Built" chrome as `out/index.html`, with a third nav item
  **Roadmap**; Overview and Gantt & timeline still link to the real built pages;
- the real filter bar (`filterbar.js/css`, inlined unchanged): filters slice
  tasks only — stage existence and declared status never change; the counter
  says "Showing N of M tasks · stage list unaffected";
- three facts shown separately per stage: declared status (plan), local task
  counts (ledger, explicit denominator), exit-criteria evidence (recorded
  pass/fail/stale/pending/unknown with provenance — external evidence marked
  `ext`, stale records labeled, never a current pass);
- recurring stages show cycles separately; a completed cycle never closes the
  stage; unstructured criteria say "coverage unknown";
- tasks whose stage is absent from the plan stay visible in an **Unmapped**
  group; one diagnostics card holds source freshness, warnings and gaps;
- no invented values: missing attempts say "not recorded", unknown is unknown.

## Fixture coverage (PLAN.md acceptance cases exercised)

- zero-task stages (1, 2, 3, 4) incl. a historical closed stage (3) and a
  recurring stage with one recorded cycle (4);
- an active stage with tasks (5) whose declared status ("planned") disagrees
  with the ledger — a mismatch warning, not an auto-rewrite;
- a stage (6) with accepted local tasks plus **failed/pending external**
  release evidence — no fabricated Done badge;
- a stale Verifies link (T-957) and a completed **negative** tester verdict
  (T-956, `fail`) shown as a completed review;
- an unmapped task (T-999, stage "9" not in the plan);
- recorded attempt history on T-951 (incl. unknown effective identity);
  attempts absent everywhere else.

## Open questions for the human

1. **Variant choice:** cards (A), journey (B), or matrix (C)?
2. **Stage ordering:** the plan declares Stage 6 *first* in source order
   (real `project-plan.md` does this). Keep strict source order (faithful,
   surprising) or sort by stage number for readability?
3. **Diagnostics placement:** permanent right-rail card (all variants) vs. a
   collapsible area — how prominent should source mismatch warnings be?
4. **Depth of the task table inside a stage:** full mini-table (A/B) vs.
   counts-only with drill-through to the Overview page (lighter cards)?
5. **New roadmap-specific filters worth adding later:** declared status,
   evidence state, "has mismatch"? (Current mockups reuse task filters only.)

## Proposed common payload fields (implementation contract)

Additive to the existing `build.py` payload; existing task fields are unchanged.

```
schemaVersion: 1
generated, now, project, demo            # as today
stages[]:                                # from docs/project-plan.md, source order
  id, title, ordinal(source position),
  declaredRaw, declared,                 # raw "Status:" text + normalized label
  source, sourceRef,                     # file + section anchor for the source link
  exitCriteria,                          # full text, verbatim
  criteria[] | null:                     # authored IDs only; null = unstructured (coverage unknown)
    id, text,
    evidence: state(pass|fail|stale|pending|unknown), label, provenance,
              recorded, artifact, external(bool), supersededBy
  recurring | null: kind, note, cycles[]{id, recorded, result, ref, note}
  historicalRefs[] | null: label, note   # references shown as text, never resolved remotely
  taskIds[]
tasks[]:                                 # existing contract; task.stage may name a
                                         # stage absent from stages[] -> Unmapped group
diagnostics:
  sources[]{file, mtime, fingerprint, status}   # build-time snapshot, not live monitoring
  warnings[]                                    # mismatches, stale links, unmapped, external
  gaps[]                                        # absent runtime/telemetry, unstructured criteria
  freshnessNote
provenance: plan, ledger, taskFiles, runtime, payload, synthetic(fixture only)
```

## Regenerating

`python .agentflow/dashboard/mockups/build.py` — rebuilds the three pages from
`fixtures.json`, the real `common.css`/`filterbar.*` and the mockup
`chrome.css`/`chrome.js`/`src/*.src.html`. The generated `roadmap-*.html` are
committed; edit sources, then rebuild.
