# Current Step

2026-10-17: human requests all approved v2.12.0 work. Do not stop local work on
missing macOS evidence. Push/publication remain human-only.

T-024 bootstrap is accepted/merged (VERSION 2.11.10): Devin probe has explicit
workspace-trust false + auto permissions; Codex read-only probe skips Git check.
T-025 independently passed focused 27/full 152 and a real bounded Devin check
(recovery reused suite evidence after a harness-only cleanup failure).

Running on Devin medium: T-009 CI and T-022 runtime reliability. T-022 owns
shared version/changelog/protocol files. CI owns only workflow/release-validation.
Queue: T-003 package/CLI depends on both; T-005 MCP -> T-007 English metrics ->
T-008 visual review/screenshot -> T-010 docs/release -> T-011 final local review.
Create independent Tester contracts for exact feature SHAs (T-004/T-006/T-008
reserved for those reviews). All feature scope approved; no repeated approval.

Use AGENTFLOW_DEVIN_MODEL_PROBE=on for real launch checks. Bound long implementation
attempts via AGENTFLOW_WORKER_TIMEOUT; preserve drafts on a stop. Other tool quota
observations live in runtime. Do not launch the old conductor plaintext env path
until T-022 repairs it; root Orchestrator currently coordinates live.

MacOS actual remote runs stay an external release gate after human push. CI is
prepared early in T-009; do not invent green remote jobs or block other local work.
Untracked nul is foreign. Preserve rejected worktrees pending cleanup agreement.
