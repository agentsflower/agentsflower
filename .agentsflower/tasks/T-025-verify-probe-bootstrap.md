# T-025: Verify the narrow probe bootstrap

Role: tester
Tool: codex
Stage: 6
Depends on: T-024
Verifies: T-024 @ 183171c19e2e115dfdc6f23af92b42471134e3af
Resume: .agentflow/tasks/.runtime/T-025.evidence - repeat only B-03 harness failure

## Goal

Recovery attempt 2: prior attempt independently passed focused 27 and full 152
tests on this exact unchanged SHA. Reuse those evidence files per Recovery/re-test
rules. Only B-03 is missing: the outer harness cleanup failed before serializing
its record. Permit exactly one additional bounded Devin call in this recovery,
record result before cleanup and restore cwd before removing any temp directory.
No more real calls after that; no repeat of already passed suites is needed.

Independently check the small probe argv repair so automatic Devin work can
resume. Native manual adapter is necessary until CLI bootstrap is accepted;
same tool is currently the available independent native session. No code edits.

## Read first

- .agentflow/roles/tester.md
- .agentflow/tasks/T-024-probe-bootstrap.md
- .agentflow/tools/run_task.py (MODEL_PROBE_ARGS/resource_check ranges)
- .agentflow/tests/test_run_task.py (new argv test)

## Allowed files

- nothing

## Do not touch

- .agentflow/tools/
- .agentflow/tests/
- .agentflow/state/
- .agentflow/docs/
- other tasks and developer artifacts

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] B-01: Explicit Devin trust flag and auto/read-only tool policy allow the bounded selected-model probe in an empty untrusted directory without dangerous permissions. Existing opt-in, selected model, timeout and no-secret evidence remain. Codex probe keeps read-only sandbox and correct non-Git flag per local help.
- [ ] B-02: Focused fake tests and full suite run verbatim; record all failures/skips and any known baseline conductor/registry flake, not just a narrow rerun pass. No product changes, clean developer worktree and unchanged baseline.
- [ ] B-03: One bounded real Devin resource probe is authorized by the human's pre-start availability/testing instruction: use swe-2-medium, explicit MODEL_PROBE=on, isolated temporary machine registry and empty cwd, no repo tools/writes. Invoke the checked resource_check API from a test harness under your AGENTFLOW_EVIDENCE; report metadata/exit only, no account/credential output. Do not call a real Codex/Claude/agy model, do not launch workers. If environment blocks the single check, mark unverified.

## Checks

- `python E:/Projects/AgentFlow/code/.agentflow/tasks/.runtime/T-025.evidence/live_probe_recovery.py` - prepare this evidence-only harness first; record the single missing live probe before cleanup, no product edits. Preserve prior focused/full-suite outputs and reference them in Result.

## Result

Outcome: completed
Verdict: pass
Checks:
- `python E:/Projects/AgentFlow/code/.agentflow/tasks/.runtime/T-025.evidence/live_probe_recovery.py` -> pass (exit 0; 12.623s). Evidence: `.agentflow/tasks/.runtime/T-025.evidence/recovery-real-probe.json`, `recovery-harness-exit.json`, `live_probe_recovery.py`.
- Prior attempt, reused per Resume: `python -m unittest discover -s .agentflow/tests -p test_run_task.py` -> pass (27 passed / 0 failed; 37.789s), evidence: `focused.log` in the same directory.
- Prior attempt, reused per Resume: `python -m unittest discover -s .agentflow/tests` -> pass (152 passed / 0 failed / 0 skipped; 132.106s), evidence: `full.log` in the same directory.
Criteria:
- B-01 - pass: installed help, narrow diff and fake argv/denial regressions confirm Devin explicit trust false with auto read-only tool policy; Codex read-only sandbox and skip-git-repo-check; opt-in, selected model, bounds and no-secret evidence remain. Recovery real probe passed with exactly those Devin arguments. Evidence: `devin-help-flags.txt`, `codex-help-flags.txt`, `focused.log`, `recovery-real-probe.json`.
- B-02 - pass: prior verbatim focused/full Checks passed independently on unchanged 183171c19e2e115dfdc6f23af92b42471134e3af; no independent failures/skips. Developer's earlier 151/152 conductor session-2 timeout and passing targeted rerun remain recorded, not replaced by the independent pass; known registry/conductor flakiness stays outside scope. Checked checkout and developer worktree remain clean at that exact SHA. Evidence: prior logs plus `recovery-checked-status.txt`, `recovery-developer-status.txt`.
- B-03 - pass in authorized recovery attempt 2: exactly one additional bounded real checked resource_check('devin', 'swe-2-medium') call; builtin account auth/status and selected-model inference both returned 0, modelProbe.result=ok. Explicit MODEL_PROBE=on, 60s inference / 45s account bounds, isolated temporary machine registry and empty cwd; no other real models or workers. Harness saved safe metadata before cleanup; exit 0 confirms completed cleanup, unchanged and still-empty cwd. No provider/account output serialized. Evidence: `recovery-real-probe.json`, `recovery-harness-exit.json`, `live_probe_recovery.py`.
New defects (outside the task):
- Prior attempt's tester-only harness failed Windows cleanup before serializing result; its model result remains unknown. Preserved evidence: `probe_harness.py`, `probe-traceback.txt`, `real-probe-unverified.txt`. Recovery evidence resolves only the missing B-03; no product defect found.
Cannot verify, needs:
- Nothing within this task.
Proposed memory updates:
- T-025 independently verified unchanged T-024 commit: focused 27/27, full Windows 152/152 and authorized recovery real Devin swe-2-medium bounded resource probe pass. Prior harness failure remains documented; no worker/model calls beyond the two explicitly authorized attempts.
