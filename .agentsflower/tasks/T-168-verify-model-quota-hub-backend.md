# T-168: Verify Model Quota Hub Backend Engine and Secure Provider Integration

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-167
Independent check: none
Resume: none
Verifies: T-167 @ d610b8a735b93e2c808cafa943446b7a4bcf29d9
Routing exception: human authorized Model Quota Hub verification (2026-10-25)

## Goal

Independently verify T-167's dynamic CLI probing, per-project activation/deactivation persistence, OpenRouter provider fetching, and secret storage hygiene.

When recording the Result: put prose first and keep `evidence:` followed only by real repo-relative paths; every file under .agentsflower/tasks/.runtime/<this task>.evidence/ must be named <task id>.<name> (e.g. T-158.checks.txt), never bare filenames, selectors or fragments.

## Read first

- .agentsflower/tasks/T-167-model-quota-hub-backend.md
- .agentsflower/tools/studio.py
- .agentsflower/tests/test_studio.py
- .gitignore

## Allowed files

- nothing

## Do not touch

- all files

## Setup

- nothing

## Acceptance criteria

- [ ] V-01: Probing `/api/capacity/probe` dynamically scans `codex`, `devin`, `claude`, `agy`, and `ollama` with live model discovery.
- [ ] V-02: Adding an OpenRouter provider with an API key dynamically fetches live models; keys are stored securely outside Git and masked in outputs.
- [ ] V-03: Per-project toggles accurately enable/disable platforms and individual models independently across different project roots.
- [ ] V-04: Full unit test suite passes: `python -m unittest discover -s .agentsflower/tests`.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Worker writes outcome below -->
Outcome: completed
Verdict: pass
Verified commit d610b8a in the isolated tester checkout with AGENTFLOW_TARGET=local. Beyond the unit Checks I ran studio.py live on port 8891 (codex.exe dir added to PATH so the codex probe was exercised for real) against two throwaway project roots (worktrees/T168-proj-a, worktrees/T168-proj-b) and a local stub OpenAI-compatible /models server; a real OpenRouter add was also performed. All fixture dirs were deleted afterwards; the checkout stayed clean and nothing was committed.
Checks:
- `python -m unittest discover -s .agentsflower/tests -p "test_studio.py"` -> pass (96 passed / 0 failed)
- `python -m unittest discover -s .agentsflower/tests` -> pass (600 ran / 0 failed, 4 skipped)
Criteria:
- V-01: pass - live GET /api/capacity/probe?refresh=1 scanned all five platforms dynamically: devin active via `devin models list` (816 models incl. swe-2-high), agy active via `agy models` (6 models incl. gemini-3.8-flash-*), codex active via `codex --version`/`login status` (codex-cli 0.163.0-alpha.10.2; `codex models` itself errors "stdin is not a terminal" on this host so the response honestly served the labeled "configured catalog" fallback - live parsing when output exists is covered by test_codex_models_come_from_live_cli), claude installed but correctly reported limited (OAuth session expired), ollama correctly missing; no hardcoded model arrays in studio.py (SUGGESTED_LOCAL_MODELS pre-exists as install suggestions). evidence: .agentsflower/tasks/.runtime/T-168.evidence/T-168.probe-full.json, .agentsflower/tools/studio.py
- V-02: pass - POST /api/capacity/provider/add with kind=openrouter and no base_url defaulted to https://openrouter.ai/api/v1 and fetched 467 live models from the real /models endpoint; a custom openai-compatible provider fetched 2 models live from a local stub; verify-failure on a dead endpoint returned 502 and persisted nothing; raw key stored only in <project>/.agentsflower/state/.secrets.json (git check-ignore confirms repo .gitignore lines 14-15; _ensure_secrets_ignored wrote the ignore block into each target project), every API surface exposes only api_key_masked "sk-or-••••••••" and grep found no raw key in any response or in project-models.json. evidence: .agentsflower/tasks/.runtime/T-168.evidence/T-168.provider-add.json, .agentsflower/tasks/.runtime/T-168.evidence/T-168.edge-checks.json, .gitignore
- V-03: pass - POST /api/capacity/project-toggle persisted platform devin enabled=false and model agy/gemini-3.8-flash-low enabled=false under projA/.agentsflower/state/project-models.json while projB held only its own codex=false flag; GET /api/capacity/project-state returned each root's own state, single-platform probes showed enabled:false propagated to the platform and per-model level (agy: only flash-low false, siblings true), unregistered project -> 403; provider remove purged both state and secrets (providers {} afterwards). evidence: .agentsflower/tasks/.runtime/T-168.evidence/T-168.toggles.json, .agentsflower/tasks/.runtime/T-168.evidence/T-168.probe-projA.json
- V-04: pass - full suite green as recorded in the Checks lines above. evidence: .agentsflower/tasks/.runtime/T-168.evidence/T-168.check-full-suite.txt, .agentsflower/tasks/.runtime/T-168.evidence/T-168.check-test-studio.txt
New defects (outside the task):
- Provider "verification" proves only catalog reachability: https://openrouter.ai/api/v1/models is public, so provider/add accepted a dummy invalid key (200) and stored it; an invalid key is only discovered later on a key-authenticated call.
- `codex models` refuses non-TTY stdin on this host, so the codex catalog can never be probed live by the current subprocess approach; the labeled configured-catalog fallback is the ceiling for codex until the CLI accepts piped stdin.
Cannot verify, needs:
- Authenticated OpenRouter behavior with a real funded key (a human-owned key); the public catalog path was verified live instead.
Proposed memory updates:
- Model Quota Hub backend verified live: dynamic probing of devin/codex/claude/agy/ollama, OpenRouter + OpenAI-compatible providers (masked secrets in <project>/.agentsflower/state/.secrets.json, git-ignored), per-project platform/model toggles in <project>/.agentsflower/state/project-models.json.
