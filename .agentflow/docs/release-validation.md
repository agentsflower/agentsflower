# Release validation evidence

This note records what has actually been verified for the AgentFlow template test
suite and what still needs remote CI evidence. It exists so a green local run is
never presented as a green macOS run.

## What exists

- `.github/workflows/ci.yml` runs `python -m unittest discover -s .agentflow/tests`
  on a matrix of `ubuntu-latest`, `macos-latest`, `windows-latest` crossed with
  Python `3.10`, `3.11`, `3.12` — nine jobs per run.
- Triggers: `push`, `pull_request`, and manual `workflow_dispatch`. The workflow is
  read-only (`permissions: contents: read`, `persist-credentials: false`), calls no
  models, and performs no deployment or publishing.
- `fail-fast: false`, so one failing cell does not hide results from the other eight;
  each job is bounded by `timeout-minutes: 20`.
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
- Remote CI evidence: **not yet obtained**. The nine matrix jobs have never run on
  GitHub-hosted runners; in particular there is no green macOS result. Do not claim
  macOS compatibility from this file or from a local Windows/Linux pass alone.

## How to obtain the remote evidence (human steps)

1. Push a branch containing `.github/workflows/ci.yml` to
   `https://github.com/vcherstar/AgentFlow` (or merge it into `main`):
   `git push origin <branch>`.
2. The `push` trigger starts a run automatically. To run it without pushing, open
   the repository on GitHub -> Actions -> "CI" -> "Run workflow" (manual dispatch).
3. Read results: Actions -> select the run -> the nine jobs appear as
   `tests (<os>, Python <version>)`. A green run is evidence for that OS/Python
   cell; inspect any failed job's "Run unit tests" step log before deciding.
4. Record the outcome (run URL, date, per-cell result) in the release task's Result
   or project memory. Only a completed remote run closes the macOS evidence gap.

Later package/MCP tasks may extend this workflow; ownership of `ci.yml` ends with
this task.
