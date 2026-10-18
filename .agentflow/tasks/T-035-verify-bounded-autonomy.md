# T-035: Independently verify bounded autonomy

Role: tester
Tool: devin
Model: swe-2-max
Stage: 5
Depends on: T-070
Verifies: T-070 @ 52250de

## Goal

Independently evaluate the exact T-070 artifact - the T-034 bounded-autonomy
feature set (recorded model identity, declared quota policy, launch budgets,
delegate rule, Codex Stop-hook prototype, bound check reuse) carried onto
current main by merge commit 52250de - against every H-01..H-04 criterion in
its Task File and the B-01..B-08 requirements it carries, in a disposable
checkout. Probe the load-bearing claims live; report the worst criterion as
the verdict.

## Read first

- .agentflow/roles/tester.md
- .agentflow/docs/ai-handoff-protocol.md (Terms, Standing rules)
- .agentflow/tasks/T-070-bounded-autonomy-carrier.md (contract + Result)
- .agentflow/tasks/T-034-bounded-autonomy.md (carried contract + Result)
- The candidate diff `git diff main...52250de` in the disposable checkout

## Allowed files

- nothing (evidence and Result only)

## Do not touch

- Developer branch/worktree/artifact and the T-034 Task File above your own Result section
- Product code, canonical memory, project settings, other projects

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] W-01: Attempt records carry requested Model:/effort AND the tool-reported effective identity (probe a real attempt record or the recorded fake-tool path); unreported identity is `unknown`, not guessed; pre-field records still parse.
- [ ] W-02: Launch budgets are enforced live: a 9th attempt is refused with records intact; a task exceeding the duration cap refuses; 3 identical failures stop relaunching; a 4th tool switch is refused; a nested launch is refused without `- delegate: on`.
- [ ] W-03: The quota policy mechanism works: quota-policy.json + a stale/missing reading yields `unknown` and never blocks; a policy reading below threshold shows up in tick decide/conductor output - probe through tick.py in a disposable state dir, not only tests.
- [ ] W-04: The Stop-hook adapter is honest: `agentflow hooks` without a valid codex install refuses without writing; the written hook is project-local only; codex-stop inside a managed session is inert. Probe what is safely probeable; do not install anything.
- [ ] W-05: checksHash binding is real: a verify PASS reused only when artifact+requirements+base+checksHash match; a changed check input forces re-measurement - probe with a disposable task.
- [ ] W-06: All claimed checks pass verbatim on the exact SHA (claimed 350/0/3-skipped); VERSION/AGENTS/CHANGELOG 2.15.0 in sync; diff inside Allowed files; safe-form masking actually masks (no prompt/env leakage in the recorded argv).

## Checks

- `python -m unittest discover -s .agentflow/tests -p test_run_task.py` - identity and budget regressions.
- `python -m unittest discover -s .agentflow/tests -p test_tick.py` - quota policy regressions.
- `python -m unittest discover -s .agentflow/tests -p test_done_gate.py` - check-reuse binding.
- `python -m unittest discover -s .agentflow/tests -p test_hooks.py` - hook adapter regressions.
- `python -m unittest discover -s .agentflow/tests` - mandatory full regression suite on the exact SHA.

## Result
