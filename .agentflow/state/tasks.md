# Task Ledger

One row per task. Written only by the Orchestrator (or a Single Mode session). Statuses and flow: `docs/ai-handoff-protocol.md`, section "Task lifecycle". How this file relates to `docs/project-plan.md` and `state/current-step.md`: section "Planning levels". Task files: `tasks/`.

| ID | Title | Stage | Role | Tool | Status | Depends on | Commit / artifact | Notes | Updated |
|---|---|---|---|---|---|---|---|---|---|
| T-001 | Cross-platform Python launcher with PowerShell compatibility | 6 | developer | devin | rejected |  |  | Successor T-012: preserved commit 06b7e3a; agy Tester hangs in interactive mode and lacks enforced wall-clock bound | 2026-10-16 18:34 |
| T-002 | Independent verification of cross-platform Python launcher | 6 | tester | agy | cancelled | T-001 |  | Attempt stopped after 15h without output; successor review will verify T-012 fixed artifact | 2026-10-16 18:34 |
| T-012 | Recover Python launcher and bounded agy review | 6 | developer | devin | rejected |  |  | Successor T-014: Windows 147 tests verified; Unix unverified; Orchestrator requires selected-model inference preflight and probe secret hygiene | 2026-10-16 19:11 |
| T-013 | Independent verification of bounded launcher recovery | 6 | tester | devin | done | T-012 | 87de72c4d71992c53fd7d34d6f5c1278580c8a78 | Same tool necessary: agy alternatives quota exhausted; independent fresh session on swe-2-high | 2026-10-16 19:11 |
| T-014 | Close selected-model preflight and probe evidence gaps | 6 | developer | devin | rejected |  |  | Successor T-016: T-015 fail reproduced custom catalog model-proof bypass and secrets in env handover/argv | 2026-10-16 19:39 |
| T-015 | Verify selected-model access and safe probe evidence | 6 | tester | devin | done | T-014 | 549245f758dfa10419b119a86e2cb720b489e4c6 | Same tool necessary; focus new delta and retained Unix external gate; do not infer pass from tests alone | 2026-10-16 19:39 |
| T-016 | Make model preflight and runtime handover fail closed | 6 | developer | devin | rejected |  |  | Successor T-018: T-017 local checks and 151 tests pass; overall unverified solely until actual Linux/macOS evidence | 2026-10-16 20:04 |
| T-017 | Verify fail-closed probes and secret-free handover | 6 | tester | devin | done | T-016 | 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 | Same tool necessary; replay T-015 findings; Unix remains external gate | 2026-10-16 20:03 |
| T-018 | Complete real Unix verification of launcher candidate | 6 | developer | devin | cancelled |  |  | Mac evidence moved to T-009 CI and final release gate; Linux repair already accepted in T-020. All remaining local work authorized 2026-10-17 | 2026-10-17 06:21 |
| T-019 | Verify launcher on a real Linux kernel in Docker | 6 | tester | devin | done | T-016 | 1e0bd876a4c3247416f6ccc3dd9c89970a36d695 | User steers to virtualization; existing Linux Docker and python:3.12-slim found; same worker tool necessary | 2026-10-16 20:47 |
| T-020 | Repair POSIX worker-timeout kill and Linux git portability | 6 | developer | devin | done | none | bafc2a02060146c0cf880e27bd66e4217d878399 | Successor T-016: repairs T-019 Linux defects (killpg self-kill, merge-tree --quiet on git 2.47, endcheck git identity); Docker Linux gate | 2026-10-16 21:22 |
| T-021 | Verify Linux defect repairs on a real kernel | 6 | tester | devin | done | T-020 | bafc2a02060146c0cf880e27bd66e4217d878399 | Same tool necessary: Codex conserved per human routing, agy/claude limited; replays T-019 Docker method on T-020 SHA | 2026-10-16 21:18 |
| T-022 | Harden registry writes and conductor environment handover | 6 | developer | devin | done | T-024 | 0420265a1e2a5a35136f3b80039adc2bb8a5a177 | 0420265 exact artifact; developer 158 tests pass; T-023 independent review required | 2026-10-17 07:01 |
| T-009 | Prepare multi-OS public CI | 6 | developer | devin | rejected | T-024 |  | Successor T-026: integrate preserved 6fe56f3 after accepted T-022 baseline repair; no CI config defect found | 2026-10-17 06:51 |
| T-003 | Build distributable template package and unified CLI | 6 | developer | devin | done | T-022,T-026 | 1849b2bfd292f2d1fb3e19054f4029c5f42049e7 |  | 2026-10-17 07:42 |
| T-024 | Repair noninteractive probe trust flags | 6 | developer | codex | done |  | 183171c19e2e115dfdc6f23af92b42471134e3af | 183171c exact probe-argv repair; native manual adapter; full-suite conductor timing flake disclosed | 2026-10-17 06:39 |
| T-005 | Optional official-SDK MCP server and safe installer configuration | 6 | developer | devin | in progress | T-003 |  |  | 2026-10-17 07:43 |
| T-007 | Honest telemetry and English dashboard | 6 | developer | devin | ready | T-005 |  |  | 2026-10-17 06:27 |
| T-010 | English public documentation and prepared v2.12.0 release | 6 | developer | devin | ready | T-007,T-008,T-026 |  |  | 2026-10-17 06:51 |
| T-025 | Verify the narrow probe bootstrap | 6 | tester | codex | done | T-024 | 183171c19e2e115dfdc6f23af92b42471134e3af | Attempt 2: exact same artifact; reuse 27/152 pass evidence, one bounded B03 recovery call only | 2026-10-17 06:36 |
| T-026 | Integrate CI after runtime baseline repair | 6 | developer | devin | done | T-022 | a0b9c697a36e9d6bc5b0f94eaeb61fef96d1798c | Approved recovery successor of T-009 | 2026-10-17 07:12 |
| T-023 | Independently verify runtime reliability repair | 6 | tester | devin | done | T-022 | 0420265a1e2a5a35136f3b80039adc2bb8a5a177 | Fresh independent Devin session; other tools limited/conserved | 2026-10-17 06:58 |
| T-027 | Independently verify package and unified CLI | 6 | tester | devin | cancelled | T-003 |  | Wrong ID: tester for T-003 is reserved as T-004 per approved plan; recreated there before any work | 2026-10-17 07:33 |
| T-004 | Independently verify package and unified CLI | 6 | tester | devin | done | T-003 | 1849b2bfd292f2d1fb3e19054f4029c5f42049e7 | Tester for T-003 @ 1849b2bf; same tool per resource policy (agy/claude limited, codex conserved); replaces misnumbered T-027 | 2026-10-17 07:40 |
| T-006 | Independently verify optional MCP server and installer config | 6 | tester | devin | in progress | T-005 |  | Tester for T-005 @ 1665318; same tool per resource policy (agy/claude limited, codex conserved); ID reserved in approved plan | 2026-10-17 07:59 |

