# T-020: Repair POSIX worker-timeout kill and Linux git portability

Role: developer
Tool: devin
Model: swe-2-medium
Stage: 6
Depends on: none
Branch: t-020-linux-defect-repair
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-020-linux-defect-repair
Independent check: tester
Resume: none

## Goal

Successor of rejected T-016 at 1e0bd876a4c3247416f6ccc3dd9c89970a36d695.
Preserve its complete port with `git diff` of that commit against its parent
2b4366eeee334a4af0106937d1dd19c7299a6ce2, then repair the concrete Linux
defects found by T-019 in one final task commit. Read T-019 Result and its
evidence files. Do not edit predecessors or their worktrees. macOS coverage
remains an external release gate, never claimed here.

## Read first

- .agentflow/tasks/T-016-probe-hardening.md
- .agentflow/tasks/T-019-linux-container-verification.md
- .agentflow/tasks/.runtime/T-019.evidence/check2-linux-suite.txt
- .agentflow/tasks/.runtime/T-019.evidence/check3-merge-and-killtree-repro.txt
- .agentflow/tools/run_task.py
- .agentflow/tools/accept.py
- .agentflow/tests/test_run_task.py
- .agentflow/tests/test_endcheck.py
- AGENTS.md
- .agentflow/docs/project-rules.md

## Allowed files

- .agentflow/tools/run_task.py
- .agentflow/tools/run-task.ps1
- .agentflow/tools/accept.py
- .agentflow/tests/test_run_task.py
- .agentflow/tests/test_launcher_lifecycle.py
- .agentflow/tests/test_launcher_args.py
- .agentflow/tests/test_endcheck.py
- .agentflow/tests/test_accept.py
- .agentflow/tests/test_workspace.py
- .agentflow/tests/test_parallel.py
- .agentflow/tests/test_dispatch.py
- .agentflow/tests/test_conductor.py
- .agentflow/tests/test_tick.py
- .agentflow/tests/test_machine_capacity.py
- .agentflow/tests/test_route.py
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/VERSION
- CHANGELOG.md
- AGENTS.md

## Do not touch

- .agentflow/tools/gate.py
- .agentflow/tools/ledger.py
- .agentflow/tools/machine_capacity.py
- .agentflow/tools/tick.py
- .agentflow/tools/paths.py
- .agentflow/tools/conductor.ps1
- .agentflow/tools/conductor-panel.ps1
- .agentflow/tools/dispatch.py
- .agentflow/tools/install.py
- .agentflow/tools/plan_route.py
- .agentflow/tools/route.py
- .agentflow/tools/route_report.py
- .agentflow/tools/upstream.py
- .agentflow/tests/test_approval.py
- .agentflow/tests/test_install.py
- .agentflow/tests/test_layout.py
- .agentflow/tests/test_plan_route.py
- .agentflow/tests/test_route_report.py
- .agentflow/tests/test_upstream.py
- .agentflow/state/
- .agentflow/dashboard/
- .agentflow/docs/project-rules.md
- .agentflow/docs/project-plan.md
- .agentflow/docs/agentflow-production-roadmap.txt
- README.md
- GUIDE.md
- pyproject.toml

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] L-10: The complete diff `git diff 2b4366eeee334a4af0106937d1dd19c7299a6ce2 1e0bd876a4c3247416f6ccc3dd9c89970a36d695` is applied onto main; ported paths carry the candidate content. One commit `[T-020] <type>: <what>` holds port plus repairs.
- [ ] L-11: On POSIX the tool process spawned by `run_logged` runs in its own session/process group, so a worker wall-clock timeout kills only the tool's tree and the worker survives to record the error attempt (T-019 defect 1: `os.killpg` currently SIGTERMs the worker's own group). Windows behavior unchanged (taskkill /T). `test_wall_clock_timeout_kills_the_tree_and_records_an_error` passes on real Linux.
- [ ] L-12: `accept.py`'s trial merge works on stock git 2.47.x: `git merge-tree --write-tree` without the unsupported `--quiet` option, still detecting conflicts and writing nothing to the repository (T-019 defect 2). The accept-path tests in test_accept.py and test_workspace.py pass on Linux.
- [ ] L-13: The `git merge` call in test_endcheck.py (~line 115) carries `-c user.name` / `-c user.email` like every neighboring git call, so fixtures do not depend on a host-global git identity (T-019 defect 3).
- [ ] L-14: Full `python -m unittest discover -s .agentflow/tests` passes verbatim on Windows and on real Linux in the Docker check below. Remaining Linux skips are Windows/PowerShell-only and named in the Result. Any other Linux failure is reported, not hidden.
- [ ] L-15: Release record: extend the ported 2.11.9 CHANGELOG entry with the defect repairs; VERSION stays at the ported value (no extra bump). Propose any `decisions.md` line in the Result; do not write state files.

## Checks

- `python .agentflow/tools/run_task.py --help` - portable entry point on Windows.
- `python -m unittest discover -s .agentflow/tests` - full suite on Windows.
- `docker info --format '{{.OSType}} {{.ServerVersion}}'` - existing daemon is Linux.
- `docker run --rm --name agentflow-t020-linux --mount "type=bind,source=E:\Projects\AgentFlow\code\.git,target=/src.git,readonly" --env AGENTFLOW_TARGET=local python:3.12-slim sh -ec "apt-get update -qq && apt-get install -y -qq git >/tmp/apt-install.log 2>&1 && git clone --quiet --no-hardlinks /src.git /tmp/agentflow-check && cd /tmp/agentflow-check && git checkout --quiet --detach origin/t-020-linux-defect-repair && uname -a && python --version && git rev-parse HEAD && python .agentflow/tools/run_task.py --help && python -m unittest discover -s .agentflow/tests"` - exact committed artifact on a real Linux kernel, disposable container; requires the branch's final commit to exist before the run.

## Result

Outcome: completed
Change: bafc2a02060146c0cf880e27bd66e4217d878399 on t-020-linux-defect-repair
Files:
- .agentflow/tools/run_task.py - ported from 1e0bd87; repaired: `run_logged` spawns the tool with `start_new_session=True` on POSIX (own session/group) so a worker wall-clock timeout kills only the managed tree, and `kill_tree` now signals the process groups of the whole tree via new `tree_pgroups` (`/proc` scan on Linux, `ps -eo pid=,ppid=,pgid=` fallback) so `--stop` still reaches a tool that leads its own session. Windows `taskkill /T` path unchanged.
- .agentflow/tools/accept.py - `git merge-tree --write-tree` no longer passes `--quiet` (unsupported by stock git 2.47.x); a nonzero exit still stops the accept before any merge.
- .agentflow/tests/test_endcheck.py - the merge fixture (~line 115) now passes `-c user.name`/`-c user.email` like every neighboring git call.
- CHANGELOG.md - ported 2.11.9 entry extended with the three defect repairs.
- Ported unchanged from 1e0bd87: .agentflow/VERSION (2.11.9), .agentflow/docs/ai-handoff-protocol.md, .agentflow/tools/run-task.ps1, .agentflow/tests/{test_run_task,test_launcher_args,test_launcher_lifecycle,test_machine_capacity,test_parallel,test_route,test_tick,test_conductor,test_dispatch}.py, AGENTS.md.
Checks:
- `python .agentflow/tools/run_task.py --help` -> pass (usage printed on Windows)
- `python -m unittest discover -s .agentflow/tests` -> pass (151 ran / 0 failed; ~106s). One flaky `test_route.test_medium_band_is_shown_not_applied` failure (exit 1 != 4) appeared on the first full-suite run only; it passed standalone, module-only, and on the verbatim rerun of the final commit. Reported, not hidden.
- `docker info --format '{{.OSType}} {{.ServerVersion}}'` -> pass (`linux 29.8.0`)
- `docker run --rm --name agentflow-t020-linux --mount "type=bind,source=E:\Projects\AgentFlow\code\.git,target=/src.git,readonly" --env AGENTFLOW_TARGET=local python:3.12-slim sh -ec "... && git checkout --quiet --detach origin/t-020-linux-defect-repair && ... && python -m unittest discover -s .agentflow/tests"` -> pass (151 ran / 0 failed / 18 skipped, ~40s). `Linux cdd20f4fb5da 6.6.114.1-microsoft-standard-WSL2 x86_64`, Python 3.12.14, HEAD bafc2a02060146c0cf880e27bd66e4217d878399 (exact committed artifact). The command resolves `origin/t-020-linux-defect-repair` inside the mounted `.git`; that remote-tracking ref was pointed at the commit locally with `git update-ref` - nothing was pushed and no remote was contacted. An earlier container run at 27bbdb0 (same tree minus the `/proc` scan) surfaced that python:3.12-slim ships no `ps`, so `tree_pgroups` now reads `/proc/<pid>/stat` first and keeps `ps` only for non-/proc POSIX.
Criteria without a command:
- L-10 - checked: `git diff 1e0bd87..HEAD` contains only the three repairs plus the changelog bullets; all other ported paths are byte-identical to the candidate. One commit holds port plus repairs; the worktree is clean.
- L-11 - checked on real Linux in the Docker run: `test_wall_clock_timeout_kills_the_tree_and_records_an_error` passes (attempt recorded as `error` with "wall-clock timeout", descendant killed, lease released); `test_launch_status_and_stop_kills_the_tree` passes too, so `--stop` still kills the tool's own-session tree.
- L-12 - checked on real Linux: both `test_workspace` accept-path tests and `test_accept` pass with git 2.47.x in the container; `merge-tree --write-tree` writes no refs/index/worktree changes, only the (unused) trial tree object.
- L-13 - checked: the fixture carries `-c user.name=t -c user.email=t@t`; `test_task_edit_introduced_in_merge_rejected` passes in the container which has no global git identity.
- L-14 - checked: verbatim suite green on Windows and on real Linux. The 18 Linux skips are identical to T-019's: PowerShell/pwsh-dependent conductor and launcher-lifecycle tests, the run-task.ps1 wrapper test, the Windows junction test and the Windows PID start-time guard - all Windows/PowerShell-only by design.
- L-15 - checked: CHANGELOG 2.11.9 entry extended; VERSION stays at the ported 2.11.9.
Found, not fixed:
- `test_route.test_medium_band_is_shown_not_applied` flaked once during a full-suite run on Windows (route.py subprocess exited 1 instead of 4); not reproducible standalone, per-module or on the rerun. Possible cross-test timing/environment interaction worth a look if it recurs.
- macOS coverage remains an external release gate: `ps`-based `pid_start`/`tree_pgroups` fallback is written for POSIX but never exercised on a real Darwin host.
Proposed memory updates:
- decisions.md, dated 2026-10-16: "T-020 ported T-016 (2b4366e..1e0bd87) onto main and repaired the T-019 Linux defects: the tool process now leads its own POSIX session so a worker wall-clock timeout cannot kill the worker, `kill_tree` signals the groups of the whole tree (`/proc` first, `ps` fallback - slim containers ship no `ps`), accept.py's trial merge drops `merge-tree --quiet` (unsupported by git 2.47.x), and the test_endcheck merge fixture carries an explicit git identity. VERSION stays 2.11.9; macOS verification remains an external gate."
- known-issues.md: the T-019 Linux defects (killpg self-kill, `merge-tree --quiet`, git-identity fixture) are fixed at bafc2a0 and re-verified on a real Linux kernel; the "real Linux unverified" entry can be updated.
