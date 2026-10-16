# Task Ledger

One row per task. Written only by the Orchestrator (or a Single Mode session). Statuses and flow: `docs/ai-handoff-protocol.md`, section "Task lifecycle". How this file relates to `docs/project-plan.md` and `state/current-step.md`: section "Planning levels". Task files: `tasks/`.

| ID | Title | Stage | Role | Tool | Status | Depends on | Commit / artifact | Notes | Updated |
|---|---|---|---|---|---|---|---|---|---|
| T-001 | Cross-platform Python launcher with PowerShell compatibility | 6 | developer | devin | rejected |  |  | Successor T-012: preserved commit 06b7e3a; agy Tester hangs in interactive mode and lacks enforced wall-clock bound | 2026-10-16 18:34 |
| T-002 | Independent verification of cross-platform Python launcher | 6 | tester | agy | cancelled | T-001 |  | Attempt stopped after 15h without output; successor review will verify T-012 fixed artifact | 2026-10-16 18:34 |
| T-012 | Recover Python launcher and bounded agy review | 6 | developer | agy | blocked |  |  | Recovery: Devin stopped after 10min without repair progress; staged port preserved; agy Opus access probe passed; prepare retry | 2026-10-16 18:47 |

