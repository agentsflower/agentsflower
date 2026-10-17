# T-051: Independently verify lifecycle trust round 2

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-050
Verifies: T-050 @ 00852c1698d14ece7dcc56d005ec2eb7f25e803f

## Goal

Independently evaluate the exact T-050 artifact (2.12.2 lifecycle fixes on top
of the preserved T-028 base) against every F-01..F-07 criterion in its Task
File, in a disposable checkout. Never repair the checked artifact; report the
worst criterion as the verdict. The prior reviews (T-029.1.log codex,
T-029 attempt 2 devin) are context - re-verify on this SHA, do not copy them.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules, Task lifecycle)
- .agentflow/tasks/T-050-lifecycle-trust-2.md (the contract and the worker's Result)
- .agentflow/tasks/T-029-verify-lifecycle-trust.md (the first round's independent findings - the original defect list this artifact claims to fix)
- .agentflow/docs/improvement-plan.md section 1
- The candidate diff `git diff main...00852c1698d14ece7dcc56d005ec2eb7f25e803f` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-050 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] W-01: Structural fail-closed proven live: feed wrong-shaped/empty container state (tool-limits.json as `[]`, `null`, `{}`; heartbeat/orchestrator.json; attempt files; verify JSON) to every reader surface and confirm a diagnosable error - never "no limits"/"no live orchestrator"/"no evidence". Include the exact `[]`-and-`null` cases round 1 proved fail-open.
- [ ] W-02: Acceptance binding proven live: a stale PASS verify record (earlier attempt, different artifact SHA, changed header, other task) cannot satisfy `ledger.py set --status done` for the current attempt; a correct record can; `{}` runtime files raise no KeyError anywhere. Reproduce in a disposable repo.
- [ ] W-03: Re-run the round-1 killer scenario: a live worker process whose recorded pidStart is unconfirmed keeps the task locked - `--stop` refuses with a diagnosable block instead of closing the attempt/releasing the lock, a second claim is refused, and a verified-identity stop still releases cleanly. Prove with real sleeper processes.
- [ ] W-04: Per-attempt taskId validation and machine_capacity._alive identity: a reused pid cannot fool a stale lease; POSIX-recorded start honored; unmeasurable/failed identity is not alive. Simulated-platform tests plus static review of the POSIX branch.
- [ ] W-05: Every claimed check command passes on the exact SHA in your checkout (223 green claimed; re-run the full suite and the named files); VERSION 2.12.2 / AGENTS block / CHANGELOG migration notes in sync; diff stays inside Allowed files; every T-028 part the round-1 review verified (approval gate, atomic writes, --live, merge audit) still passes.
- [ ] W-06: Found-not-fixed claims are truthful and correctly scoped; the CHANGELOG fail-closed wording matches observed behavior now (round 1 caught an overstated claim - check the new text the same way). Report anything material missed.

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - locked-stop identity, claim binding.
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` - acceptance binding.
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` - merge-history and baseline audits.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - structural fail-closed readers.
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` - cross-platform pid identity.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
Outcome: completed
Verdict: pass
Checks:
- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (36 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_approval.py` -> pass (5 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_endcheck.py` -> pass (9 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` -> pass (23 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests -p test_machine_capacity.py` -> pass (12 passed / 0 failed)
- `python -m unittest discover -s .agentflow/tests` -> pass (223 passed / 0 failed, 3 skipped: optional mcp SDK not installed)
All six re-run verbatim on the exact SHA 00852c1698d14ece7dcc56d005ec2eb7f25e803f in the detached disposable checkout (clean tree at start and end; Python 3.13.7, git 2.53.0, Windows 11). Logs: check-*.log. Live probes ran against disposable repos and real sleeper processes built from this checkout's tools: t051-probes.json (W-01/W-02), t051-lock-probes.json (W-03/W-04 + fresh-claim and {} runtime cases), t051-regress-probes.json + t051-live-probe.json (approval gate, atomic writes, --live argv). Scripts kept alongside.
Criteria:
- W-01 structural fail-closed at every reader surface - pass - evidence: t051-probes.json, t051-lock-probes.json W01b. tool-limits.json `[]`/`null`/`{"codex":{}}`/`{"codex":[]}`/`{"codex":null}`/`"x"`/non-string-until/unparseable-until -> LaunchError at run_task.limit_until, StateError at tick.limit_end/read_limits, exit 1 at `tick.py status|run|limit|next-orchestrator`; the exact `[]` and `null` cases that were fail-open in round 1 now refuse. `{}` is a valid empty map and `_seen` is tolerated, both explicitly. orchestrator.json `{`/`[]`/`null`/`{}`/missing `at`/bad `at`/non-string or empty holder -> StateError at live_orchestrator; a refused heartbeat leaves the file byte-identical (verified), `--force` takes over, a fresh valid heartbeat refuses a second claim. Attempt files `{`/`[]`/`null`/`{}`/attempts-not-list-or-null/missing or foreign file taskId/per-attempt foreign taskId/bad status/n str/n bool/non-dict attempt -> diagnosable error at `ledger.py set` (claimed->_last_attempt), `run_task.py --status` (per-file `state-error`, scan continues), `run_task.py` launch (live_tasks), `gate.py verify` (exit 2), `tick.py run` (decide need); an attempt without taskId stays tolerated as legacy. Verify JSON `{`/`[non-dict]`/`null`/`{}`/`[{}]`/ok:"false"/ok:1/attempt str-or-float/wrong-typed sha|taskId|headerHash -> ValueError in check_verify, diagnosable sys.exit in ledger.verified (with an exited attempt present), exit 2 in `gate.py verify` - never "no evidence".
- W-02 acceptance binding live - pass - evidence: t051-probes.json W02, t051-lock-probes.json W02b, disposable repo at Temp\t051-disp-1s8elmlb. Real CLI: a stale PASS for attempt 1 cannot accept while attempt 2 runs ("the last attempt is 'running', needs 'exited'") nor after it exits ("none is bound to attempt 2 and the current Task File (stale evidence)"); records for a different artifact SHA, another taskId (T-999), or a stale headerHash all refuse; `ok:"false"` is a diagnosable malformed record, not trusted; a legacy sha-only file-bound record does accept (the documented rule, proven live); a fully-bound record (taskId + last attempt + headerHash + sha) accepts and `set --status done` succeeds; `{}` and minimal-field runtime files exit diagnosably with no KeyError on both claimed() and verified() paths.
- W-03 locked --stop with real sleeper processes - pass - evidence: t051-lock-probes.json. Live python sleepers on Windows: pidStart=null -> `--status` reports "blocked" (not dead); `--stop` exits 1 with a diagnosable refusal naming the pid, leaves the attempt `running` (runtime file unchanged) and the sleeper alive (confirmed); a second claim via `--manual` and via `run_task T-020 codex` is refused before preflight; `tick run --dry-run` surfaces the unconfirmed-pid need; the ledger stays `in progress`. A mismatched recorded start on a live pid behaves identically (refusal, no kill, still locked). With the correct recorded start `--status` shows running and `--stop` kills the sleeper (confirmed dead), closes the attempt as error and releases - the next claim passes the attempt gate (reaches only an unrelated preflight overlap refusal). A dead pid with a recorded start reports "dead" and `--stop` closes+releases cleanly. The round-1 killer scenario cannot recur.
- W-04 per-attempt taskId + machine_capacity._alive identity - pass - evidence: t051-probes.json ("attempt 1 is for T-999, not T-005" diagnosed at ledger/run_task/gate/tick surfaces), t051-lock-probes.json W04. Live: _alive(pid, correct start)=True, wrong start=False, no recorded start=True (legacy pid-only), dead pid=False; a lease whose recorded start mismatches the live pid is cleaned and its slot claimable - a reused pid cannot fool a stale lease - while a correctly-bound lease keeps its slot ("no free machine slot (1/1)"); a patched GetProcessTimes failure -> not alive. Static review: machine_capacity._pid_start/_alive mirrors run_task.pid_start/alive on POSIX (/proc field-22 jiffies -> .NET ticks, `ps lstart` fallback, unmeasurable -> None -> not alive); the same matrix runs in test_machine_capacity.py.
- W-05 verbatim checks + release sync + diff scope + preserved parts - pass - evidence: check-*.log, candidate-files.txt, t051-regress-probes.json, t051-live-probe.json. 223 green matches the claim (named files 36/5/9/23/12); VERSION=2.12.2, AGENTS block line=2.12.2, CHANGELOG 2.12.2 entry with migration notes - in sync. 18 changed files all inside Allowed files; AGENTS.md is the version line only; run-task.ps1 and accept.py unchanged. T-028-verified parts re-proven live: awaiting-approval rows refuse every status transition and prefix-clearing --notes, `approve` allows; `in progress` needs a recorded running attempt; terminal states refuse at the ledger and at preflight launch; atomic writes keep the target intact on an intercepted os.replace failure; `--live` argv carries the live ids and disappears entirely when empty; merge-history audit including the new octopus refusal stays green in test_endcheck.
- W-06 found-not-fixed truthfulness + CHANGELOG wording - pass - evidence: probes above. tick.py run/status exit 1 on malformed heartbeat/limits confirmed (same exit code as "none live", diagnosable stderr naming the file - conductor-retry caveat is real); `tick.py release` cannot remove a non-object heartbeat (StateError, exit 1, file kept) confirmed; gate.write_atomic/run_task.write_rt strand .tmp on replace failure confirmed (target intact) while the two new writers (ledger._write_atomic, route._log) clean theirs; the legacy binding rule confirmed live. The 2.12.2 CHANGELOG wording now matches observed behavior - every enumerated claim was reproduced; the round-1 overstatement is resolved. One enumeration gap found: tick.write (heartbeat/limits/tick.json writer) strands .tmp the same way - the note names gate.write_atomic and run_task.write_rt but not this third same-pattern instance; reported below.
New defects (outside the task):
- tick.write (.agentflow/tools/tick.py:97-101) also strands `<file>.tmp` when os.replace fails - same pre-existing pattern the Result lists for gate.write_atomic and run_task.write_rt; the found-not-fixed list is one instance short. Cosmetic only (target file preserved); belongs to the same follow-up.
Cannot verify, needs:
- Real POSIX/macOS execution of pid_start/_pid_start and alive/_alive: this host is Windows; the POSIX branch is confirmed by static review plus the shared test matrix, not a live run (macOS remains fully unverified, consistent with known-issues).
- Merge-fixture behavior was re-verified through the green test_endcheck suite on this SHA (which builds real repos/merges/octopus commits) rather than separate hand-built fixtures; the merge-audit code itself is unchanged in the diff.
Proposed memory updates:
- Accept T-050: all four T-029 defects are fixed on 00852c1698d14ece7dcc56d005ec2eb7f25e803f with live evidence - structural fail-closed validation at every runtime-state reader (incl. the round-1 `[]`/`null` cases), acceptance bound to task + last exited attempt + headerHash + full artifact SHA, `--stop` locked on unconfirmed pid identity, per-attempt taskId validation, and pid+start machine-lease identity on every platform.
- Add tick.write to the stranded-.tmp follow-up as a third instance of the same pre-existing pattern.
