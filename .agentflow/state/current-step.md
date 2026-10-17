# Current Step

2026-10-17: main is 2.11.11, accepted T-024 bootstrap and T-022 reliability fixes.
T-023 independent and acceptance full suite 158 pass. No active workers now.
Human explicitly authorizes all remaining v2.12.0 local implementation/testing.

NEXT: T-026 ready merges preserved CI-only 6fe56f3 onto repaired main; run checks,
accept via accept.py. Then T-003 package/CLI -> T-004 independent review -> accept;
T-005 optional official SDK MCP -> T-006 independent review -> accept;
T-007 English metrics/dashboard -> T-008 visual review + real demo screenshot ->
accept; T-010 English/Russian docs + prepared 2.12.0 -> T-011 final LOCAL review.
Create Tester contracts with exact actual SHAs as developer Results arrive.

T-008 canonical filename MUST be T-008-dashboard-visual-review.md because T-010
reads it. Save screenshot under Tester evidence; T-010 copies it to product asset.
Use real headless browser capture, not image synthesis. Do not fabricate URLs.

All feature contracts are approved with explicit ownership. Shared release
metadata remains serial. Intermediate 2.11 patches; final 2.12.0 in T-010. Keep
published SDK compatible with Python 3.10 (mcp 2.3.0 metadata), not unreleased main.
Set AGENTFLOW_DEVIN_MODEL_PROBE=on for launches; bounded long workers 2400 seconds.
Use existing tick/run-task/gate/accept/ledger, independent reviews and no bypasses.

Remote nine-job/macOS results are a separate RELEASE gate after human manual
push; T-011 reviews LOCAL preparation and honestly records this gap. Do not block
other local work, tag/publish or invent a green remote run. No agent push.
Keep rejected worktrees/foreign nul untouched. Human product URLs are optional
missing input: ask/record unresolved sources, never guess extension IDs.
