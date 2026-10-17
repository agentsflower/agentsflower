# Session Handoff

As of 2026-10-17: main includes accepted T-020 Linux repair and T-024 probe
bootstrap, AgentFlow 2.11.10. User authorized testing plus the entire remaining
v2.12.0 queue. Previous macOS-only stop is superseded; see current-step/ledger.

T-024 exact 183171c19e2e115dfdc6f23af92b42471134e3af fixed required CLI probe
trust/non-Git flags, through narrow native Manual attempts because all automated
CLI starts were blocked. T-025 independently passed 27 focused and 152 full tests,
then a bounded real Devin resource check (first harness cleanup lost its result;
recovery repeated only that missing criterion). accept.py verified/merged/cleaned
T-024; native sessions complete. No probe/security bypass or model permission
escalation; remaining workers are Devin to conserve Codex.

Running T-009 CI and T-022 registry/conductor hardening on separate Devin worktrees.
Approved files/metadata ownership are in their contracts. T-003 package/CLI,
T-005 official-SDK MCP, T-007 English telemetry/dashboard, T-010 docs/release are
ready with dependencies. Independent reviews and screenshot T-008 come at exact
SHAs. Do not create conflicting parallel release-metadata owners.

Conductor was off; keep old plaintext env handover unstarted until T-022 repairs
it, then start with the approved Devin preference and probe opt-in. Real macOS
CI execution requires human push; no agent push, publish or production deployment.
Public product URLs requested asynchronously for README; unresolved links must
be explicit, not invented. Stray nul and rejected worktrees remain untouched.

First reads: current-step.md, tasks.md, decisions.md, active Task Results.
