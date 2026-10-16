# T-021: Verify Linux defect repairs on a real kernel

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-020
Verifies: T-020 @ bafc2a02060146c0cf880e27bd66e4217d878399

## Goal

Independently verify that T-020's commit repairs the three defects T-019 found
on a real Linux kernel (Docker, python:3.12-slim) and regresses nothing on
Windows. Replay T-019's method on the exact Verifies commit, not a description
of it. Do not restart Docker/WSL or affect other containers. macOS remains a
separate external gate. Same worker tool is necessary: Codex is conserved by
human routing and agy/Claude are limited.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-019-linux-container-verification.md
- .agentflow/tasks/T-020-linux-defect-repair.md
- .agentflow/tasks/.runtime/T-019.evidence/

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/
- .agentflow/tests/
- .agentflow/state/
- .agentflow/docs/
- other projects, containers, images and volumes

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Execute the exact Verifies commit on Docker's real Linux kernel in a container-local clone. Source `.git` mount is read-only; only AGENTFLOW_TARGET=local is passed. Record uname/Python/git SHA and command output in AGENTFLOW_EVIDENCE.
- [ ] V-02: Full unittest suite on Linux passes: specifically test_wall_clock_timeout_kills_the_tree_and_records_an_error (worker survives its own killpg and records the error attempt), test_launch_status_and_stop descendant termination (a tool leading its own session is still fully killed), the test_workspace/test_accept merge-tree path on git 2.47.x, and test_endcheck's merge fixture without a global git identity. Record counts, failures and skip reasons; investigate failures without modifying product code.
- [ ] V-03: The same full suite in the disposable checkout on Windows passes, or the Result reports the failures plainly (including any recurrence of T-020's reported test_route flake).
- [ ] V-04: The disposable container is removed; no other container/daemon/WSL service is restarted/stopped; checked branch, worktree and baselines remain unchanged.
- [ ] V-05: Distinguish Linux evidence from macOS: Darwin `ps`-based identity and `tree_pgroups` fallback were written for POSIX but never exercised on a real Mac; never infer a macOS pass.

## Checks

- `docker info --format '{{.OSType}} {{.ServerVersion}}'` - existing daemon is Linux.
- `docker run --rm --name agentflow-t021-linux --mount "type=bind,source=E:\Projects\AgentFlow\code\.git,target=/src.git,readonly" --env AGENTFLOW_TARGET=local python:3.12-slim sh -ec "apt-get update -qq && apt-get install -y -qq git >/tmp/apt-install.log 2>&1 && git clone --quiet --no-hardlinks /src.git /tmp/agentflow-check && cd /tmp/agentflow-check && git checkout --quiet --detach bafc2a02060146c0cf880e27bd66e4217d878399 && uname -a && python --version && git rev-parse HEAD && python .agentflow/tools/run_task.py --help && python -m unittest discover -s .agentflow/tests"` - exact-artifact suite on Linux with disposable dependencies; save output including failures.
- `python -m unittest discover -s .agentflow/tests` - verbatim suite in the disposable Windows checkout.

## Result

Outcome: completed
Verdict: pass
Checks:
- `docker info --format '{{.OSType}} {{.ServerVersion}}'` -> pass (output: `linux 29.8.0`; evidence check1-docker-info.txt)
- `docker run --rm --name agentflow-t021-linux --mount "type=bind,source=E:\Projects\AgentFlow\code\.git,target=/src.git,readonly" --env AGENTFLOW_TARGET=local python:3.12-slim sh -ec "apt-get update -qq && apt-get install -y -qq git >/tmp/apt-install.log 2>&1 && git clone --quiet --no-hardlinks /src.git /tmp/agentflow-check && cd /tmp/agentflow-check && git checkout --quiet --detach bafc2a02060146c0cf880e27bd66e4217d878399 && uname -a && python --version && git rev-parse HEAD && python .agentflow/tools/run_task.py --help && python -m unittest discover -s .agentflow/tests"` -> pass (151 ran / 0 failed / 0 errors / 18 skipped, ~34s, exit 0; evidence check2-linux-suite.txt, check2-exit.txt)
- `python -m unittest discover -s .agentflow/tests` -> fail on both verbatim runs in the disposable Windows checkout, each with exactly one error (151 ran / 1 error): run 1 `test_tick.test_disabled_subscription_access_temporarily_skips_the_tool`, run 2 `test_dispatch.test_grants_round_robin_and_convert_to_worker_leases`. Identical signature: `PermissionError [WinError 5]` in `machine_capacity._locked` at `os.replace(temp, registry.json)` (machine_capacity.py:97). Both tests pass standalone and together (check7-flaky-tests-standalone.txt). Evidence check4/check6 + exit files.

Environment recorded in the Linux suite log: `Linux b9c85d8c9f90 6.6.114.1-microsoft-standard-WSL2 x86_64 GNU/Linux`, Python 3.12.14, HEAD bafc2a02060146c0cf880e27bd66e4217d878399 (exact Verifies commit), git 2.47.3 in the container (check3-git-version-and-skips.txt). The `.git` mount was read-only; only AGENTFLOW_TARGET=local was passed.

Criteria:
- V-01 - pass - evidence: check2-linux-suite.txt shows uname/Python/`git rev-parse HEAD` = the Verifies commit on a container-local clone; read-only bind mount; only AGENTFLOW_TARGET=local in the environment; run_task.py --help printed on Linux.
- V-02 - pass - full suite green on real Linux: 151 ran, 0 failed, 18 skipped. `test_wall_clock_timeout_kills_the_tree_and_records_an_error`, the `test_launch_status_and_stop` descendant-termination tests, the test_workspace/test_accept merge-tree path (git 2.47.3, no `--quiet`), and the test_endcheck merge fixture (container has no global git identity) all ran and passed - none appears in the skip list (check3-git-version-and-skips.txt). The 18 skips are identical to T-019's: PowerShell/pwsh conductor tests (10), launcher-lifecycle pwsh/PowerShell tests (6), the run-task.ps1 wrapper, the Windows junction test and the Windows PID start-time guard - Windows/PowerShell-only by design.
- V-03 - pass - reported plainly per the criterion: the verbatim Windows suite did NOT pass on either of two runs; each failed with one `os.replace` PermissionError inside `machine_capacity._locked` (different test each run), a transient file-lock race on this Windows host. Both failing tests pass standalone. This is not T-020's reported test_route flake - test_route passed both runs. See "New defects".
- V-04 - pass - both disposable containers used `--rm` and are absent (`docker ps -a --filter name=agentflow-t021` empty); containers-after.txt is byte-identical to containers-before.txt; no daemon/WSL restart issued. Checked worktree remains clean at bafc2a0; the T-020 branch and the main checkout are untouched; only this Result and the T-021.evidence files were added (a pre-existing untracked `nul` file was already present at the first baseline status and is unrelated).
- V-05 - pass - this is Linux (WSL2 kernel) plus Windows evidence only. Darwin `ps`-based `pid_start`/`tree_pgroups` fallback was never exercised on a real Mac; nothing here implies a macOS pass and the external macOS gate stays open.

New defects (outside the task):
- `machine_capacity._locked` (.agentflow/tools/machine_capacity.py ~line 97): `os.replace(temp, path)` can raise `PermissionError [WinError 5]` on Windows when a background scanner/AV briefly holds `registry.json`. Intermittent: 1 error per full-suite run, in different tests (test_tick, test_dispatch), both green standalone; never seen on Linux. `machine_capacity.py` was outside T-020's allowed files and unchanged by the checked commit, but a retry-with-backoff on `os.replace` would harden it. Likely also explains T-020's reported test_route flake (same subprocess registry path).

Cannot verify, needs:
- A real macOS host for the Darwin `ps`-based identity and `tree_pgroups` fallback paths (unchanged external gate).

Proposed memory updates:
- known-issues.md: record the Windows `machine_capacity._locked` `os.replace` PermissionError flake (signature above; 2 occurrences in 2 full-suite runs on 2026-10-17); the T-019 Linux defects are confirmed repaired at bafc2a0 on a real Linux kernel (git 2.47.3); macOS remains unverified.
