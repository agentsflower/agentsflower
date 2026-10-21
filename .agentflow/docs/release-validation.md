# Release validation evidence

This note records what has actually been verified for the AgentFlow template test
suite and what still needs remote CI evidence. It exists so a green local run is
never presented as a green macOS run.

## What exists

- `.github/workflows/ci.yml` runs `python -m unittest discover -s .agentflow/tests`
  on a matrix of `ubuntu-latest`, `macos-latest`, `windows-latest` crossed with
  Python `3.10`, `3.11`, `3.12` — nine test jobs, plus the `package` and `mcp`
  jobs below (thirteen jobs per run).
- Triggers: `push`, `pull_request`, and manual `workflow_dispatch`. The workflow is
  read-only (`permissions: contents: read`, `persist-credentials: false`), calls no
  models, and performs no deployment or publishing.
- `fail-fast: false`, so one failing cell does not hide results from the others;
  each job is bounded by `timeout-minutes: 20` (30 for the integration jobs).
- A second job `package` runs `python .agentflow/tests/check_package.py` on
  `ubuntu-latest` and `windows-latest` (Python 3.12): it provisions `build`/`setuptools`
  into disposable venvs, builds the `agentflow-sdlc` wheel and sdist, and exercises the
  installed CLI outside the source tree. The unit-test job stays stdlib-only and offline.
- A third job `mcp` (`needs: tests`) runs `python .agentflow/tests/check_mcp.py` on
  `ubuntu-latest` and `windows-latest` (Python 3.12): it provisions the released `mcp` SDK
  (`>=2.3,<3`) and the packaged wheel into disposable venvs and drives a real stdio MCP
  session against an installed project. The core unit-test job stays stdlib-only and offline.
- `AGENTFLOW_MACHINE_STATE_DIR` is pointed into `${{ runner.temp }}`, so the machine
  registry is isolated per job and no real AgentFlow credentials or host machine
  state are touched. Platform-specific tests keep their existing skips
  (`@unittest.skipUnless` guards in `.agentflow/tests/`); a skip is reported as a
  skip, not as a pass or a masked failure.

## Evidence status

- Local evidence so far: Windows (this development machine) and Linux (Docker),
  recorded in the task results and `known-issues.md`.
- Remote CI evidence: one run has executed — run `39026298541` on `main@50adf65`
  (2026-10-17). Result: all three `ubuntu-latest` test jobs and both
  `package` jobs passed; all three `windows-latest` and all three
  `macos-latest` test jobs exited 1 at `python -m unittest discover`; both
  `mcp` jobs were skipped by dependency (`needs: tests`). The failure is
  specific to the GitHub windows-2025/macos-arm64 runner environments — a
  local Windows 10 / Python 3.13 run reproduces green (204 tests) even with
  the CI environment — and the failing step logs need authenticated access to
  read. No green macOS result exists: do not claim macOS compatibility from
  this file or from a local Windows/Linux pass alone.

## Stage 5 evaluation evidence (2.12.1-2.15.7)

Improvement-plan section 6 asks for reproducible scenarios and a migration
proof. What that work actually verified, and what it did not:

- **Locally verified (this machine, Windows 10 / Python 3.13):**
  `.agentflow/tests/test_scenarios.py` drives the real `run_task.py`,
  `gate.py`, `accept.py`, `tick.py` and `ledger.py` in disposable git
  repositories through four named cases — a bug-fix task, a contract-change
  task (a passed verify does not carry to a moved artifact or a moved base),
  a quota/limit recovery and an interrupted-merge recovery — plus an
  `install.py --update` fixture proving open Task Files, ledger statuses and
  project-owned docs/settings survive an update byte-for-byte and stay
  operable under the new tools. The full suite
  (`python -m unittest discover -s .agentflow/tests`) passes including these.
- **Simulation-only:** every worker in the scenario fixtures is a fake CLI
  script; no real model, account or provider is contacted. The provider-limit
  line, the hold expiry and the accept crash are simulated (marked `_simulated`
  in the test names). A real-platform launch variant exists but is skipped
  unless `AGENTFLOW_REAL_PLATFORM=1` — it is never faked. The migration proof
  covers a disposable fixture, not a production project; no external rollout
  has happened since the 2026-10-17 repository-only scope was set, and none
  is claimed.
- **Still needs remote CI:** a green `tests (windows-latest, ...)` and
  `tests (macos-latest, ...)` job on the new suite size. The recorded failure
  above (run `39026298541`) is an open evidence gap, unchanged by the local
  additions — local green never substitutes for those cells.

## How to obtain a green remote run (human steps)

1. Push a branch containing `.github/workflows/ci.yml` to
   `https://github.com/vcherstar/AgentFlow` (or merge it into `main`):
   `git push origin <branch>`.
2. The `push` trigger starts a run automatically. To run it without pushing, open
   the repository on GitHub -> Actions -> "CI" -> "Run workflow" (manual dispatch).
3. Read results: Actions -> select the run -> the jobs appear as
   `tests (<os>, Python <version>)`, `package integration (<os>)` and
   `mcp integration (<os>)`. A green run is evidence for that OS/Python
   cell; inspect any failed job's "Run unit tests" step log before deciding
   (log download needs repository access — anonymous API reads return 403).
4. Record the outcome (run URL, date, per-cell result) in the release task's Result
   or project memory. Only a green remote `tests (macos-latest, ...)` job closes
   the macOS evidence gap.
