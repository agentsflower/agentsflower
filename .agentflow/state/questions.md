# Questions for the human

- Roadmap layout selection RESOLVED by the human on 2026-10-18:
  all three mockups A (cards), B (journey), C (matrix) are approved.
  Implement a view selector allowing navigation between all three layouts.
  Do not gate implementation on choosing a single variant. Stage ordering,
  diagnostics placement, task-table depth and extra filters were not explicitly
  selected; retain mockup behavior unless a further decision is needed.
- Optional public README source input: exact AI Home Design SaaS URL and
  YouTube Transcript Extension listing URL. Never invent missing IDs/URLs.
- External release gate: CI run 39026298541 on 50adf65 FAILED - all
  windows-latest and macos-latest test jobs exit 1 at the unittest step;
  ubuntu tests and both package-integration jobs pass. Logs are not readable
  without repository auth (API 403). Needed from the human: open the run in the
  browser and paste the failing test names/step output, or authenticate `gh`,
  so the runner-specific failure can be fixed; a rerun happens on the next
  authorized push anyway. Tag/release publication remains human-only.

No additional plan approval is needed for the completed local task pool.

## 2026-10-18 - T-075 tester launch needs a routing decision

- Task: T-075 (independent tester for completed T-074 @ 5a6510c).
- Question: the persisted Jev assessment (req_01a14dab3ab875c5b09fa66a87ab71ed)
  is low confidence (0.48): it demands gpt-6-astra class at xhigh effort
  (complexity 1.97/2). Mandatory routing policy blocks the launch without an
  explicit auditable human exception; there is no exception for this tester.
  Which do you approve?
  - A: Devin gpt-6-astra-xhigh - adequate Devin option meeting the assessed
    requirement, consistent with your Devin preference.
  - B: scoped exception for Devin swe-2-max (same precedent as T-081).
  - C: Codex gpt-6-astra xhigh (Jev's pick) - but Codex tester writes were
    environment-blocked on this machine, so a fresh attempt may fail again.
  - D: re-assess or rewrite the task contract first.
- What waits on it: T-075 launch; behind it T-074 acceptance, then the
  T-076 -> T-078 -> T-036 -> T-038 chain and T-066.
