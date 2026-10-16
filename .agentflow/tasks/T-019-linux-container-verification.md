# T-019: Verify launcher on a real Linux kernel in Docker

Role: tester
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: T-016
Verifies: T-016 @ 1e0bd876a4c3247416f6ccc3dd9c89970a36d695

## Goal

Resolve the Linux execution evidence gap using the existing local Docker Linux
daemon and python:3.12-slim image. Human asked to use virtual execution. Test the
exact artifact in an isolated Linux filesystem, not mocked os.name or /mnt paths.
Do not restart Docker/WSL or affect other containers. macOS remains a separate gate.
Same worker tool is necessary: other providers are unavailable/conserved.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-016-probe-hardening.md
- .agentflow/tasks/T-017-verify-probe-hardening.md
- .agentflow/tests/test_run_task.py

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

- [ ] L-01: Execute the exact Verifies commit on Docker's real Linux kernel, Python 3.12, in a container-local clone. Source Git metadata mount is read-only; no host project files or credentials are passed. Record uname/Python/Git SHA and command output in AGENTFLOW_EVIDENCE.
- [ ] L-02: Full unittest suite executes on Linux. Record counts, failures and skip reasons. Confirm actual POSIX spawn/process-group timeout/descendant termination, /proc identity and symlink Setup paths were exercised; simulations alone cannot establish these cases. Investigate failed checks without modifying product code.
- [ ] L-03: The one disposable named container is removed on completion; no other container/daemon/WSL service is restarted/stopped. Source branch, developer worktree and Task baselines remain unchanged.
- [ ] L-04: Distinguish Linux evidence from macOS: this task cannot certify Darwin ps-based identity or macOS behavior. If a Linux defect is found, give reproducible steps and worst-criterion Verdict. Never infer macOS pass from a Linux kernel.

## Checks

- `docker info --format '{{.OSType}} {{.ServerVersion}}'` - existing daemon is Linux.
- `docker run --rm --name agentflow-t019-linux --mount "type=bind,source=E:\Projects\AgentFlow\code\.git,target=/src.git,readonly" --env AGENTFLOW_TARGET=local python:3.12-slim sh -ec "apt-get update -qq && apt-get install -y -qq git >/tmp/apt-install.log 2>&1 && git clone --quiet --no-hardlinks /src.git /tmp/agentflow-check && cd /tmp/agentflow-check && git checkout --quiet --detach 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 && uname -a && python --version && git rev-parse HEAD && python .agentflow/tools/run_task.py --help && python -m unittest discover -s .agentflow/tests"` - exact-artifact suite on Linux with disposable dependencies; save output including failures.

## Result

Outcome: completed
Verdict: fail
Checks:
- `docker info --format '{{.OSType}} {{.ServerVersion}}'` -> pass (output: `linux 29.8.0`; evidence check1-docker-info.txt)
- `docker run --rm --name agentflow-t019-linux --mount "type=bind,source=E:\Projects\AgentFlow\code\.git,target=/src.git,readonly" --env AGENTFLOW_TARGET=local python:3.12-slim sh -ec "apt-get update -qq && apt-get install -y -qq git >/tmp/apt-install.log 2>&1 && git clone --quiet --no-hardlinks /src.git /tmp/agentflow-check && cd /tmp/agentflow-check && git checkout --quiet --detach 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 && uname -a && python --version && git rev-parse HEAD && python .agentflow/tools/run_task.py --help && python -m unittest discover -s .agentflow/tests"` -> fail (151 ran / 3 failed / 1 error / 18 skipped, ~73s, exit 1; evidence check2-linux-suite.txt)

Environment recorded in the suite log: `Linux b262774f4afa 6.6.114.1-microsoft-standard-WSL2 x86_64 GNU/Linux`, Python 3.12.14, HEAD 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 (exact Verifies commit), git 2.47.3 installed inside the disposable container. The `.git` mount was read-only; no project files or credentials were passed (only AGENTFLOW_TARGET=local).

Criteria:
- L-01 - pass - evidence: check2-linux-suite.txt shows uname/Python/git SHA on a container-local clone at the exact commit; `python .agentflow/tools/run_task.py --help` printed usage on Linux.
- L-02 - fail - the suite executed on a real Linux kernel but did not pass: 3 failures + 1 error (check2-linux-suite.txt, check2b-verbose-merge-repro.txt). All 18 skips are Windows/PowerShell-only tests (conductor, pwsh wrapper, Windows PID guard, junctions; check4-skip-reasons.txt), expected on Linux. POSIX paths WERE exercised for real: the probe-timeout killpg path passed (test_probe_timeouts_kill_the_probe_tree), /proc-based pid_start passed (test_recorded_pid_identity), POSIX --stop descendant termination passed (test_launch_status_and_stop), symlink Setup tests ran unskipped. Investigated failures below; nothing was modified.
- L-03 - pass - evidence: containers-after.txt equals the pre-run container list; the named container is absent (--rm removed it); no daemon/WSL restart was issued. Source branch (main, unchanged), developer worktree (clean at 1e0bd87) and task baselines untouched; only this Result was appended.
- L-04 - pass - this is Linux (WSL2 kernel) evidence only. It says nothing about Darwin `ps -o lstart=` identity or any macOS behavior; the macOS gate stays open. Two Linux defects were found, reproduced below; worst-criterion Verdict applied.

Linux defects found in the checked artifact (T-016 scope, run_task.py / accept.py):

1. run_task.py - worker wall-clock timeout kills the launcher's own worker process on POSIX. `run_logged` (~line 731) spawns the tool WITHOUT `start_new_session`, so on Linux the tool shares the worker's process group. On `AGENTFLOW_WORKER_TIMEOUT` expiry `kill_tree` runs `os.killpg(os.getpgid(tool_pid), 15)`, which SIGTERMs the worker python itself before it can write the error state. Symptom: test_wall_clock_timeout_kills_the_tree_and_records_an_error fails - the attempt stays `running` forever (pid recorded, never finalized; observed 45s+ against a 5s bound). Reproduced minimally (check3-merge-and-killtree-repro.txt): `run_task.kill_tree()` on a plain child in the same group terminates the caller (`Terminated`, no `SURVIVED` output). On Windows this passed because taskkill /T targets the tree, not the caller's group. Real production impact: a worker that hits its timeout dies silently with a permanently `running` attempt instead of a recorded error.
2. accept.py - `git merge-tree --write-tree --quiet` (line ~151) uses a `--quiet` option that stock Debian/trixie git 2.47.3 does not support (`error: unknown option 'quiet'`, exit 129). Both test_workspace accept-path tests fail, so the accept flow is unusable on a stock Linux git. The Windows dev machine's newer git masks this.
3. test_endcheck.py line ~115 - `git(self.wt, "merge", "--no-ff", "--no-commit", "main")` omits the `-c user.name/-c user.email` used by every neighboring git call; on a host without global git identity it exits 128 (`fatal: unable to auto-detect email address`, reproduced in check3-merge-and-killtree-repro.txt: MERGE_EXIT=128). Fixture defect, environment-dependent, not a launcher bug.

New defects (outside the task):
- none beyond the three above (all inside the checked artifact's files)

Cannot verify, needs:
- A real macOS host for Darwin ps-based identity and macOS-only behavior (unchanged external gate).
- The wall-clock/accept defects above preclude a Linux pass until fixed and re-verified.

Proposed memory updates:
- known-issues.md: update the "real Linux/macOS ... unverified" entry - real Linux evidence now exists at 1e0bd87 and it found two defects (worker-timeout killpg self-kill in run_logged; merge-tree --quiet unsupported by Debian git 2.47) plus one env-dependent test fixture (missing git identity in test_endcheck). macOS remains fully unverified. The T-014 env.json entry stays resolved per T-017.

