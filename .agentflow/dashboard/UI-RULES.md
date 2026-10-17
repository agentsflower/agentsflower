# Interface development rules (from the AgentFlow dashboard experience)

Source: every owner request about the `.agentflow/dashboard/` and how it is implemented (`build.py`, `template.html`, `graph_template.html`, `common.js/css`, `filterbar.js/css`, `snapshot.py`). Section A — what the owner asked for. Section B — practices that emerged in the work. Section C — how to apply them to a new interface.

---

## A. Owner requirements and methods

### A1. Working process
1. **Discuss and assess feasibility first, change nothing.** For big ideas (graph, Gantt, timing) — a "can it be done" assessment first, then implementation.
2. **Clickable mockup before porting.** Layout variants are shown as a clickable mockup, the owner picks one, then implementation.
3. **Version before changes.** "Keep the previous version": before every noticeable edit take a snapshot (`snapshot.py save`), roll back with one command (`restore vN`).
4. **Collect feedback as a list and estimate before editing.** When the owner gives many remarks, consolidate, estimate, answer, then do.
5. **Do not break process or data.** The dashboard only reads the ledger, Task Files and git. Statuses, acceptance rules and templates are never changed for looks.
6. **Dashboard sources are part of the template and are committed**; only `.agentflow/dashboard/out/` (built pages) and `.agentflow/dashboard/versions/` (local versions) are git-ignored. The interface is English (human-approved default); status, role and outcome vocabulary comes from `.agentflow/docs/ai-handoff-protocol.md`, never invented.
7. **Decide within your authority.** The owner said "use your judgement, I'll review". Ask only when the decision is his.

### A2. Data and honesty
8. **Never invent a value.** No data — empty or "not set", not a guess. Estimated fields are marked as estimates ("Set by — … (estimate)"). Metrics come only from recorded evidence: missing history, runtime, cost or token telemetry is N/A, never zero or an invented saving.
9. **Do not merge different entities under one word.** Ledger status, worker outcome (worker report) and independent-check verdict are three separate fields with separate names. "Completed by worker" ≠ "Done"; a `fail` verdict is a completed negative report, not a worker failure.
10. **Show the source.** Next to a normalized value — the original report line; for commits, a note on where it came from and what it does not mean.
11. **Full text as-is, no paraphrase.** No auto-summary, no LLM compression, no bolding. Short — the title, full — a collapsible block with the original text.
12. **Empty blocks are hidden** (no text — no block). Exception: "Status history" is always expanded.
13. **Ambiguity is not guessed.** The worker commit is taken only from an explicit `Commit:`/`Change:` line and only when there is exactly one hash; otherwise empty. Tester links come from the declared `Verifies:` field and its SHA, never from a title regex; a stale link is flagged, not silently used.

### A3. Layout and screen
14. **Use the whole screen.** Side blocks fit rather than scroll; exactly one central block scrolls (table, Gantt).
15. **Same column widths across pages**, same grid: header / filters / chosen / three columns.
16. **No horizontal scroll**, including 4K and narrow screens (extra columns hide by width).
17. **Page scale does not jump.** Switching pages does not change element sizes or header position at 100%.
18. **No stray scrollbars.** Long fields are collapsible with bounded inner height.
19. **Identical headers:** "Tasks <project>" title (project = folder name), "Overview / Gantt & timeline" switch, "Built …" top right, theme as a ☀/🌙 icon (not a word). A demo build carries a clearly visible DEMO DATA badge.
20. **Rarely needed is removed** (legend on the Timing tab) when not needed for understanding.

### A4. Filters
21. **One filter set on both pages, all working.** Remove a filter only if selecting it changes nothing on that page.
22. **Maximum slice.** Filters on every axis: status, set-by, stage, role, agent, outcome, check, size, links, created/closed dates.
23. **Per-filter reset and "Reset all".** The selection is visible as chips in a separate row; the "Showing N of M" counter comes first.
24. **A count on every value** (how many tasks a choice yields). Zero counts are dimmed but selectable.
25. **Search by id/title/notes plus an "in task text" option**; a text hit is shown as a snippet in the card.
26. **Filters do not jump.** The ": N" counter appearing or disappearing does not move neighbours (space is reserved).
27. **Same height and look** of the filter bar on both pages.

### A5. Task card
28. **One card on both pages** (shared component), same data.
29. **Inter-task links are clickable** and work on both pages (jump, highlight).
30. **Long fields collapse** (Goal, Result, Notes); the rest is shown in full.
31. **Split the worker into agent and role** (the same session can be a deployer while Codex or Claude did the work).

### A6. Time, graph, links
32. **Real wall-clock time.** An "active only" option (threshold activity model over git pings). The active-only mode is owner-approved.
33. **Time-scale units** (hours/days/weeks/months), MS Project style, separate from zoom. Shows how development accelerated.
34. **Gantt order — by finality**: cancelled on the left … accepted on the right; grouped by stage by default, switchable.
35. **Links of different kinds** (depends, rework-successor, check) — different styles, **one legend shared by Gantt and board** (one style table).
36. **Links are not muted without reason**; background links are a separate toggle, hover/click highlights. Link settings are shared by Gantt and board; grouping and zoom are Gantt-only.
37. **Layers:** background lines under cards, never overlapping them; highlighted ones on top.
38. **Show "how big the change is"** per task (git change size) and "depends on a rejected/cancelled task" (a toggle).
39. **Sticky right panel next to the Gantt:** the selected task's description stays visible without leaving the chart.

---

## B. Best practices (developed in the work)

### B1. Architecture
1. **Single data source shared by the pages.** One JSON payload is embedded in both pages; pages differ only in rendering.
2. **Shared layer in separate files:** `common.css` (tokens, grid, header, card), `common.js` (`C` namespace: constants, `prep`, `makeDims`, `matchDims`, `taskCard`, `initHeader`), `filterbar.js/css`. A page template only includes and draws its own view. Duplicated page logic is a defect.
3. **Build one self-contained HTML** with no server: `build.py` substitutes markers (`__DATA__`, `/*COMMON_JS*/` etc.). Python is stdlib only.
4. **One style/vocabulary table for everything:** `EDGE_STYLE`, `ST`, `RESULT_EN` — legend, Gantt and board all take from it.
5. **Filter dimensions described once** (`makeDims`); both screens build filters and matching from it. Check: per-filter counts match on both pages.

### B2. Data
6. **Source of truth — project files and git**, not manual edits. Status over time — replaying history (`git log --reverse`, `git show hash:file`).
7. **Normalization + source.** A "raw → English label" map plus the preserved raw string (machine keys travel as `statusKey`, `roleKey`, `verdict`).
8. **Strip service markup:** template HTML comments are cut before display.
9. **Extraction rules — strict and explainable:** anchor on a label (`Commit:`), single value, regex-checked. "Not determined" cases are enumerated and shown honestly.
10. **Verify on real edge tasks**, not only typical ones: empty report, rejected, multiple hashes, replacement, chain.

### B3. Markup and UX
11. **Colour tokens on `:root`, dark/light themes** (`prefers-color-scheme` plus explicit `data-theme`), the toggle persists to `localStorage`.
12. **Fixed `.app` grid on screen** (`100vh`, rows `auto auto 26px 1fr`), exactly one container scrolls; a narrow screen falls back to normal flow.
13. **Reserve space for appearing elements.** Dynamic counters, badges, the "Selected" row have reserved size; selection is marked by colour and outline, not bold (bold changes width).
14. **Align heights of related blocks** across pages (search field, filter bar), verify with a screenshot.
15. **Dropdowns:** close on outside click via `composedPath().includes(bar)`; re-render must not detach the target element.
16. **Do not wipe classes** with `className=` — use `classList.add`.
17. **SVG layers:** background under cards; highlight is cloned into the top layers (`hlclone`), not repainted in place.
18. **Compact left panel:** compression + thin scroll instead of overflow; narrow screens hide columns rather than collapsing everything.
19. **Labels in the owner's domain language** ("Outcome", "Independent check"), not implementation terms.

### B4. Verification and change safety
20. **Version snapshot before and after** (`snapshot.py save|list|restore`), including sources and built pages.
21. **Verify in a real browser** (playwright on a temporary `http.server`; `file://` is blocked): filters, page switches, collapsing blocks, links, console clean, no horizontal scroll at 1920×1080 and other sizes.
22. **Counter regression:** all filters give identical numbers on both pages.
23. **Screenshots and test servers are removed** after verification.
24. **Complex edits — a patch script** (`rep(old, new)` with `assert`), not long shell heredocs: it fails loudly when an anchor disappears.
25. **Hidden characters:** after escaping a regex in a patch, check the file for control characters (once \x08 instead of `\b`).
26. **Final answer to the owner, briefly:** what changed, where each disputed field comes from, which cases are intentionally empty, how to roll back.

---

## C. Checklist for a new interface (before starting and before delivering)

Before starting
- [ ] One data source? One description of dimensions/vocabularies? Shared layer extracted?
- [ ] Mockup variants shown to the owner if the layout is new?
- [ ] Version saved before edits?
- [ ] Which entities are easy to confuse? Each gets its own field and name.

Before delivering
- [ ] No invented values; estimates marked; source visible.
- [ ] Empty not shown, ambiguous not guessed.
- [ ] One filter set, all working, per-filter and global reset, counts present.
- [ ] No jumps on state changes (counters, chips, page switches).
- [ ] No horizontal scroll on 4K, 1920, narrow; no stray scrollbars.
- [ ] Same header, grid, theme, "Built" on every page.
- [ ] Verified in a browser, console clean, numbers match across pages.
- [ ] Snapshot taken after; temp files removed; owner report brief.
