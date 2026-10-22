# Release notes — AgentFlow 2.15.10

Prepared locally on 2026-10-21. **Not yet published.** Push, CI verification,
tagging and the GitHub Release are human steps; see *Publish (human steps)*.
These notes supersede the never-published 2.12.0 preparation record: no tag or
GitHub Release has ever been created, so the first published release carries
everything that landed through 2.15.10 — details per version in
[CHANGELOG.md](CHANGELOG.md).

## What is in this release

Highlights of the accumulated release; every item is summarized from the
changelog entry of the version that shipped it:

- Project memory and four roles (2.x line): Orchestrator, Developer, Tester,
  Deployer over `.agentflow/`, with Task Files, one branch/worktree per task,
  ledger-driven acceptance and an evidence-bound `## Result`.
- Shared machine scheduling (2.11.x): `machine_capacity.py` registry for tool
  slots and PORT leases across projects on one machine, machine-wide observed
  limits, `AGENTFLOW_SHARED_DISPATCHER` `shadow`/`active` modes, and
  `upstream.py` template-drift reports (the conductor runs `--check` daily).
- Cross-platform surface (2.12.0): `run_task.py` Python launcher
  (`run-task.ps1` is the Windows compatibility wrapper; managed workers run as
  detached background processes, no console windows), packaged `agentflow-sdlc`
  CLI (source install, not on PyPI), optional MCP server with read-only tools
  by default and `agentflow_accept_task` behind
  `--enable-orchestrator-tools`, the English dashboard with evidence metrics
  and a marked `--demo` mode, the CI workflow, and the rewritten
  `README.md`/`GUIDE.md`.
- Trustworthy lifecycle (2.12.1–2.13.3): ledger transitions enforce verified
  state and awaiting-approval blocks, malformed runtime records fail closed,
  acceptance binds to the verified attempt/artifact/base, and recoverable
  handover keeps a classified `stopReason` plus a bounded `recovery` record so
  a successor continues the preserved draft; `limit_detection.py` is the single
  judge of provider limits, scoped to quota groups.
- Artifact-bound completion gate (2.14.x): required criteria carry stable IDs,
  evidence paths are validated against task scope, and `gate.py done` runs the
  task's Checks on the artifact and on a trial merge onto the current base.
- Bounded autonomy and enforced routing (2.15.x): launcher-enforced worker
  wall clock (`AGENTFLOW_WORKER_TIMEOUT`) plus `--watchdog`, budgets for
  attempts, task duration, identical failures and platform switches, a Windows
  idle-sleep guard (`power_guard.py`), the persisted routing assessment
  (`T-NNN.route.json`, enforced on every launch with an auditable
  `Routing exception:` override), declared quota-policy/sample files, an
  opt-in Codex Stop-hook adapter (`hooks.py`), and Jev-ranked model selection
  with `recommended` tie-breaks.
- Documentation-alignment train (2.15.6): role Result examples match the
  gate's outcome-line format; `GUIDE.md`, `README.md`, `.agentflow/README.md`
  and `release-validation.md` describe the shipped 2.15.x behavior;
  `GUIDE.ru.md` reaches section-by-section parity with `GUIDE.md` in Russian;
  the `tool-routing.md` Antigravity CLI note matches the non-interactive
  worker argv.
- Roadmap dashboard (2.15.8–2.15.10): a third dashboard page
  (`out/roadmap.html`) renders every `### Stage` of `project-plan.md` in
  source order — declared status, local task counts and exit-criteria
  evidence as three separate facts — with allowlisted
  attempt/routing/verify drill-down and build diagnostics, in cards,
  journey and matrix layouts. Optional authored plan syntax (`evidence:`,
  `Recurring:`, `References:`) stays opt-in — existing plans need no
  migration. The packaged distribution and `install.py --update` carry the
  assets; `dashboard/mockups/` stays repository-only.

## Evidence status and limits

- Local evidence: Windows development machine and Linux (Docker,
  python:3.12-slim) full-suite runs; recorded in
  `.agentflow/docs/release-validation.md` and `.agentflow/state/known-issues.md`.
- Remote CI: one run has executed (run `39026298541`, 2026-10-17, `main@50adf65`).
  The `ubuntu-latest` test jobs and both `package` jobs were green; the
  `windows-latest` and `macos-latest` test jobs failed (the unit-test command
  exited 1 — environment-specific, under investigation); the `mcp` jobs were
  skipped by dependency. There is still no green macOS result, and the macOS
  (Darwin) `ps`-based process-tree fallback remains unverified.
- Production figures in README are maintainer-attested (October 2026):
  NotebookLM AI Sidebar 80k+ users, 4.7/5 (111 ratings, Featured);
  Export Chat from Gemini to Word 4k+, 4.8/5 (38 ratings, Featured);
  YouTube Transcript 1.6k+; AI Home Design production SaaS. The ~85,600
  total is an aggregate snapshot across listings, not deduplicated uniques.
- Unresolved listing evidence (recorded explicitly, not guessed):
  Chrome Web Store / product URLs for "Export Chat from Gemini to Word",
  "YouTube Transcript" and "AI Home Design" are not yet verified links —
  only https://aisidebar.app is linked. The maintainer should add the store
  URLs to the README production table before or after publication.
- No package is published on PyPI; `agentflow-sdlc` is a local distribution
  name only. No `v2.x` tag or GitHub Release exists yet.

## Verify locally

```bash
python -m unittest discover -s .agentflow/tests      # full suite, stdlib-only, offline
python .agentflow/tests/check_package.py             # wheel/sdist build + installed CLI (needs network for build tooling)
python .agentflow/tests/check_mcp.py                 # optional: real stdio MCP session (provisions mcp SDK)
```

## Publish (human steps)

After final review and acceptance of the release tasks:

1. Push the merge / main:
   `git push origin main`
2. Confirm the thirteen-job CI run is green: repository → Actions → "CI"
   (also runnable manually via "Run workflow"). Record results in
   `.agentflow/docs/release-validation.md` — only a completed remote run
   closes the macOS evidence gap.
3. Tag (only after the remote run is verified — do not tag a state that
   still lacks CI evidence if the tag is meant to represent a verified
   release):
   `git tag -a v2.15.10 -m "AgentFlow 2.15.10: project-memory template, cross-platform CLI, optional MCP, evidence and roadmap dashboard, trustworthy lifecycle and enforced routing"`
   `git push origin v2.15.10`
4. Create the GitHub Release for `v2.15.10`, using this file's *What is in
   this release* and *Evidence status and limits* sections as the notes.
