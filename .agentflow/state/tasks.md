# Task Ledger

One row per task. Written only by the Orchestrator (or a Single Mode session). Statuses and flow: `docs/ai-handoff-protocol.md`, section "Task lifecycle". How this file relates to `docs/project-plan.md` and `state/current-step.md`: section "Planning levels". Task files: `tasks/`.

| ID | Title | Stage | Role | Tool | Status | Depends on | Commit / artifact | Notes | Updated |
|---|---|---|---|---|---|---|---|---|---|
| T-001 | Cross-platform Python launcher with PowerShell compatibility | 6 | developer | devin | rejected |  |  | Successor T-012: preserved commit 06b7e3a; agy Tester hangs in interactive mode and lacks enforced wall-clock bound | 2026-10-16 18:34 |
| T-002 | Independent verification of cross-platform Python launcher | 6 | tester | agy | cancelled | T-001 |  | Attempt stopped after 15h without output; successor review will verify T-012 fixed artifact | 2026-10-16 18:34 |
| T-012 | Recover Python launcher and bounded agy review | 6 | developer | devin | rejected |  |  | Successor T-014: Windows 147 tests verified; Unix unverified; Orchestrator requires selected-model inference preflight and probe secret hygiene | 2026-10-16 19:11 |
| T-013 | Independent verification of bounded launcher recovery | 6 | tester | devin | done | T-012 | 87de72c4d71992c53fd7d34d6f5c1278580c8a78 | Same tool necessary: agy alternatives quota exhausted; independent fresh session on swe-2-high | 2026-10-16 19:11 |
| T-014 | Close selected-model preflight and probe evidence gaps | 6 | developer | devin | blocked |  |  | Prepared successor; preserve 87de72c; awaiting Unix verification route; no launch yet | 2026-10-16 19:11 |

