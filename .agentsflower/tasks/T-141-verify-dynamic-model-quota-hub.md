# T-141: Verify dynamic model quota hub, real CLI probing, and default model persistence

Role: tester
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: none
Verifies: T-138 @ 4f611e6b75e0567e9025fc04f993acc489412109
Branch: t-141-verify-dynamic-model-quota-hub
Worktree: E:\Projects\AgentFlow\worktrees\agentsflower-t-141-verify-model-quota-hub
Independent check: none
Resume: none

## Goal

Independently verify T-138 (Studio Dynamic Model Quota Hub: `/api/capacity/probe` real CLI scanning with bounded timeouts and 60s TTL cache, live platform cards in `#view-capacity`, dedicated Free & Local Offline Models section, `/api/capacity/default-model` persistence into `docs/model-options.json`, probe-fed chat composer model list) against the T-138 contract:

1. Run `test_studio.py` and the full test suite.
2. Serve the Studio from this disposable checkout on PORT and verify `#view-capacity` carries the contract elements: live hub header/scan meta, a platform grid rendered from probe data (Devin, Claude Code, Antigravity, Ollama/Local), status badges (active/limited/missing), collapsible model listings, and a dedicated `Free & Local Offline Models` section; confirm no hardcoded static platform cards or `/api/quotas` mock remain.
3. Exercise `GET /api/capacity/probe` against the served instance: the response is structured per-platform probe data with status and model lists (model ids, context length and pricing where available); confirm results are cached (second call served from the 60s TTL cache) and a missing tool reports `Not Installed` rather than failing the whole probe.
4. Exercise `POST /api/capacity/default-model` against the served instance: a valid model persists `default_worker_model` into the served checkout's `.agentsflower/docs/model-options.json`; invalid/empty input is rejected; confirm the writes land only inside the disposable checkout (review isolation: the main repository's model-options.json and the T-138 worktree stay untouched).
5. In `studio.js`, verify the dynamic wiring: `loadCapacity`/`renderCapacityHub` render from the probe endpoint, per-model `Set default` actions call the endpoint, and the chat composer model list/default pill are fed by probe results plus the persisted default.
6. Judge the developer's "Found, not fixed" notes (static `/api/failover/status`; claude.exe auth reporting loggedIn while OAuth calls fail) and record verdict in the Result section.

## Read first

- .agentsflower/tasks/T-138-dynamic-model-quota-hub.md
- .agentsflower/roles/tester.md

## Allowed files

- none (read-only verification)

## Do not touch

- All project files.

## Setup

- nothing

## Port

- PORT=8903

## Rebuild together

- nothing

## Acceptance criteria

- [ ] V-01: Unit test suite in test_studio.py passes.
- [ ] V-02: Full regression test suite passes without regressions attributable to T-138.
- [ ] V-03: Served `#view-capacity` markup and `studio.js` carry the contract elements (live platform cards with status badges, collapsible model listings, Free & Local Offline Models section); no hardcoded static cards or `/api/quotas` mock.
- [ ] V-04: `GET /api/capacity/probe` returns structured per-platform live probe data with bounded subprocess timeouts and 60s TTL caching; a missing platform degrades to `Not Installed` without failing the endpoint.
- [ ] V-05: `POST /api/capacity/default-model` validates input and persists `default_worker_model` into the served checkout's `docs/model-options.json`; writes stay inside the disposable checkout.
- [ ] V-06: `studio.js` wires the probe into the UI: live card rendering, Set default actions, and a chat composer model list/default pill driven by probe + persisted default.
- [ ] V-07: Verdict is pass.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_studio.py"
- python -m unittest discover -s .agentsflower/tests

## Result

<!-- Filled by the worker below this heading only. Format: its role file. Nothing above this heading may change, and the header never repeats this heading text. -->
