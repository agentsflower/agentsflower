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

## 2026-10-18 - T-075 tester launch needs a routing decision (RESOLVED: human approved Option B, Devin swe-2-max; T-075 done 2026-10-18) (RESOLVED)

- Task: T-075 (independent tester for completed T-074 @ 5a6510c).
- Resolution: Human approved Option B on 2026-10-18 - scoped auditable exception
  for Devin swe-2-max (same precedent as T-081).
- What was unblocked: T-075 launch; behind it T-074 acceptance, then the
  T-076 -> T-078 -> T-036 -> T-038 chain and T-066.

## 2026-10-18 - T-092 tester launch needs a routing exception decision

- Task: T-092 (independent tester for T-091 @ 0bf4ac0 - closes the last T-078
  residuals: preferred-CLI independence exemption + full-suite evidence).
- Question: the persisted Jev assessment (req_01a14ea7e1837102b871a4fae80b1749)
  is low confidence (0.34): it demands gpt-6-astra class at xhigh effort
  (complexity 1.96/2). The new admission gate (T-076/T-089, now on main)
  refuses the launch without an explicit auditable human exception - the
  machinery you mandated is working. Which do you approve?
  - A: write Routing exception: <reason> in the T-092 header, launch Devin
    gpt-6-astra-xhigh - adequate Devin option meeting the assessed
    requirement, consistent with your Devin preference.
  - B: write Routing exception: <reason> in the T-092 header, launch Devin
    swe-2-max - the scoped exception you chose for T-075 (precedent T-081).
  - C: Codex gpt-6-astra xhigh (Jev's pick) - but Codex tester writes were
    environment-blocked on this machine, so a fresh attempt may fail again.
  - D: re-scope T-092 to a fast-path re-check (T-085 precedent): the bulk of
    the artifact was already independently verified by T-083/T-086/T-088/
    T-090; a narrower contract lowers the assessed complexity and may pass
    the admission gate without an exception. The Orchestrator rewrites and
    re-assesses; no header needed.
- What waits on it: T-092 launch -> T-091 acceptance -> T-036 -> T-038 ->
  T-044 -> T-046 -> T-048 and T-066.
