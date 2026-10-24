---
name: chrome-extension-mv3
description: Strict Google Chrome Extension Manifest V3 development, service worker lifecycle, declarativeNetRequest rules, CSP security, and permissions auditing. Use for any Chrome/Chromium extension task — new extensions, MV2 to MV3 migration, manifest.json review, service worker debugging, permission scoping — to keep the extension compliant, least-privilege, and store-reviewable.
license: Apache-2.0
metadata:
  domain: 4
  source:
    - google/chrome-extensions-samples@main
    - GoogleChrome/modern-web-guidance@main
  license: Apache-2.0
  version: 1.0.0
---

# Chrome Extension Manifest V3 (`chrome-extension-mv3`)

Use this skill whenever a task authors, migrates, or reviews a Chrome/Chromium
extension: `manifest.json`, background service workers, content scripts,
declarativeNetRequest rulesets, or Web Store readiness. Its job is to replace
the generic LLM default (MV2-era `browser_action`, persistent background pages,
`<all_urls>` in `permissions`, inline event handlers) with a verifiable MV3
contract.

## Core rules (non-negotiable)

1. **`manifest_version: 3`, always.** No MV2 fields: `browser_action`,
   `page_action`, `background.scripts`, `background.page`, `persistent: true`.
   The toolbar entry point is `action` (`chrome.action`), the background unit is
   `background.service_worker`.
2. **Host access lives in `host_permissions`, not `permissions`.** URL match
   patterns (`<all_urls>`, `*://*/*`, `https://...`) in `permissions` are an
   error. API names (`storage`, `alarms`, `scripting`) go in `permissions`;
   every entry must be justifiable.
3. **Zero remotely hosted or inline code.** No `eval()`, `new Function()`,
   remote `<script src="http(s)://...">`, inline `<script>` blocks or `on*=`
   handlers in extension HTML pages. MV3 CSP forbids all of them.
4. **`content_security_policy` is present and uses the MV3 object form** —
   `{"extension_pages": "...", "sandbox": "..."}` — never the MV2 string, and
   never `unsafe-eval` / `unsafe-inline` / remote sources in `script-src`.
5. **Blocking network interception is `declarativeNetRequest`.**
   `webRequestBlocking` does not exist in MV3; port rules to static or dynamic
   DNR rulesets. `tabs.executeScript` becomes `chrome.scripting.executeScript`.
6. **The service worker is ephemeral.** No state in globals, no
   `setInterval`/`setTimeout` for scheduling (use `chrome.alarms`), no DOM /
   `window` / `localStorage` / `XMLHttpRequest` (use `chrome.storage.session`,
   `fetch`, offscreen documents). Listeners register synchronously at top level.

## Deterministic gate

Run the bundled linter against any extension directory or `manifest.json`
before reporting done:

```bash
python .agentsflower/skills/chrome-extension-mv3/scripts/mv3_lint.py <extension-dir-or-manifest.json> [--json]
```

Exit code `0` = `MV3_COMPLIANT` (warnings allowed); `1` = `NON_COMPLIANT` or
unreadable manifest. Fix all `error` findings; warnings require a written
justification (e.g. a genuinely needed high-privilege permission).

## Load references on demand

| Reference | Load when |
|---|---|
| [references/manifest-v3-rules.md](references/manifest-v3-rules.md) | Writing or reviewing `manifest.json` — field-by-field MV2->MV3 map, CSP, permissions, `web_accessible_resources`. |
| [references/service-worker-lifecycle.md](references/service-worker-lifecycle.md) | Writing or debugging `background.service_worker` — ephemeral lifecycle, `chrome.storage.session`, message passing, `chrome.alarms`, offscreen documents. |

## Definition of done (self-check before reporting)

- [ ] `mv3_lint.py` exits `0` with zero `error` findings on the final tree.
- [ ] `manifest_version: 3`; `background.service_worker`; `action` — no
      `browser_action`/`page_action`/`background.scripts` anywhere.
- [ ] URL match patterns only in `host_permissions`; `permissions` is minimal
      and each entry is justified.
- [ ] `content_security_policy` object present; no `unsafe-eval`,
      `unsafe-inline`, or remote script sources.
- [ ] Zero inline `<script>` / `on*=` handlers in extension HTML; zero `eval()`
      / `new Function()` / remote code in JS.
- [ ] `webRequestBlocking` replaced by `declarativeNetRequest`; DOM/timer work
      moved to offscreen documents or `chrome.alarms`.
