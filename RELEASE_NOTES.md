# Release notes — AgentFlow 2.12.0

Prepared locally on 2026-10-17. **Not yet published.** Push, CI verification,
tagging and the GitHub Release are human steps; see *Publish (human steps)*.

## What is in this release

- Cross-platform Python launcher `.agentflow/tools/run_task.py` (stdlib only);
  `.agentflow/tools/run-task.ps1` stays as a thin Windows compatibility wrapper.
- Distributable package `agentflow-sdlc` (`python -m build`; source/local install —
  not published on PyPI) with the unified `agentflow` CLI: `install`, `run`,
  `gate`, `accept`, `ledger`, `mcp`, `dashboard`. Zero third-party runtime
  dependencies.
- Optional MCP server `.agentflow/tools/mcp_server.py` on the official `mcp`
  SDK (`pip install "agentflow-sdlc[mcp]"`); read-only tools by default,
  `agentflow_accept_task` only behind `--enable-orchestrator-tools`;
  `install.py --mcp [--mcp-client cursor]` wires the client config on explicit
  opt-in.
- English dashboard with evidence metrics (first-pass gate rate, lead time,
  verdict counts — N/A where telemetry is missing) and an isolated,
  visibly marked `--demo` mode.
- CI workflow `.github/workflows/ci.yml`: unit tests on ubuntu/macos/windows ×
  Python 3.10–3.12 plus `package` and `mcp` jobs; read-only, offline core.
- English `GUIDE.md` (Russian preserved as `GUIDE.ru.md`), rewritten
  `README.md` with badges, Mermaid architecture diagram, production
  references and the real dashboard screenshot
  (`.agentflow/docs/assets/dashboard.png`, from this repository's own
  development dashboard — real task data captured by T-008).

Details per version: [CHANGELOG.md](CHANGELOG.md).

## Evidence status and limits

- Local evidence: Windows development machine and Linux (Docker,
  python:3.12-slim) full-suite runs; recorded in
  `.agentflow/docs/release-validation.md` and `.agentflow/state/known-issues.md`.
- **No remote CI run yet**: the nine-job matrix has never executed on
  GitHub-hosted runners; there is no green macOS result. The macOS
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
  name only. No `v2.12.0` tag or GitHub Release exists yet.

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
2. Confirm the nine-job CI run is green: repository → Actions → "CI"
   (also runnable manually via "Run workflow"). Record results in
   `.agentflow/docs/release-validation.md` — only a completed remote run
   closes the macOS evidence gap.
3. Tag (only after the remote run is verified — do not tag a state that
   still lacks CI evidence if the tag is meant to represent a verified
   release):
   `git tag -a v2.12.0 -m "AgentFlow 2.12.0: public release docs, cross-platform CLI, optional MCP, evidence dashboard"`
   `git push origin v2.12.0`
4. Create the GitHub Release for `v2.12.0`, using this file's *What is in
   this release* and *Evidence status and limits* sections as the notes.
