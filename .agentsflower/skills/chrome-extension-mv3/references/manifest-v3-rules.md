# Manifest V3 rules — `manifest.json` field contract

Concrete requirements for a Manifest V3 (MV3) extension. Anything in the
"banned" column fails store review and the `mv3_lint.py` gate.

## Required keys

| Key | MV3 value | Banned MV2 form |
|---|---|---|
| `manifest_version` | `3` (integer) | `2`, missing |
| `background` | `{"service_worker": "sw.js"}`; `"type": "module"` optional for ES modules | `"scripts": [...]`, `"page": "bg.html"`, `"persistent": true` |
| toolbar entry | `"action": {...}` → `chrome.action` API | `"browser_action"`, `"page_action"` |
| host access | `"host_permissions": ["https://api.example.com/*"]` | URL patterns inside `permissions` |
| `content_security_policy` | object: `{"extension_pages": "script-src 'self'; object-src 'self'", "sandbox": "..."}` | single string (MV2), `unsafe-eval`, `unsafe-inline`, `http:`/`https:` script sources |
| `web_accessible_resources` | `[{"resources": [...], "matches": [...]}]` objects | flat string array `["img.png"]` |
| network interception | `"declarative_net_request"` + `declarativeNetRequest` permission | `webRequestBlocking`, `chrome.webRequest` blocking |
| script injection | `chrome.scripting.executeScript` + `scripting` permission | `chrome.tabs.executeScript` |

## Minimal valid manifest

```json
{
  "manifest_version": 3,
  "name": "Example",
  "version": "1.0.0",
  "description": "One sentence, <= 132 chars.",
  "action": { "default_popup": "popup.html", "default_icon": "icon.png" },
  "background": { "service_worker": "sw.js" },
  "permissions": ["storage", "alarms"],
  "host_permissions": ["https://api.example.com/*"],
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'"
  },
  "web_accessible_resources": [
    { "resources": ["icon.png"], "matches": ["https://example.com/*"] }
  ]
}
```

## Permissions audit rules

- `permissions` holds API names only: `storage`, `alarms`, `scripting`,
  `activeTab`, `declarativeNetRequest`, `notifications`, `contextMenus`,
  `offscreen`, `sidePanel`, etc. Every entry needs a one-line justification;
  remove anything unused — Web Store review rejects unjustified breadth.
- Prefer `activeTab` over `tabs`; `tabs` exposes URL/title of every tab.
- Treat as high-privilege (justify explicitly): `cookies`, `history`,
  `bookmarks`, `debugger`, `management`, `nativeMessaging`, `clipboardRead`,
  `desktopCapture`, `geolocation`, `privacy`, `proxy`, `tabCapture`.
- `declarativeNetRequest` alone only covers static rulesets on
  extension-owned resources; modifying requests on hosts needs
  `declarativeNetRequestWithHostAccess` (or `declarativeNetRequestFeedback`)
  plus matching `host_permissions`.
- Host match patterns go to `host_permissions` (or `optional_host_permissions`
  for runtime-requested access). `<all_urls>` demands written justification;
  prefer explicit origins.
- `optional_permissions` + `chrome.permissions.request` is the
  least-privilege path for capabilities only some users need.

## Inline-code and remote-code ban (CSP)

MV3 extension pages default to `script-src 'self'`. Forbidden everywhere
(extension pages, popups, options, sandbox escapes):

- `<script>...</script>` blocks inside HTML files — move to `.js` files with
  `<script src="...">`.
- Inline handlers: `onclick=`, `onload=`, any `on*=` HTML attribute — bind via
  `addEventListener`.
- `eval(...)`, `new Function(...)`, `setTimeout("string", ...)`.
- Remote code: `<script src="https://...">`, dynamically injected remote
  scripts, WASM `unsafe-eval`. Bundle every byte the extension executes.
- Relaxing CSP to allow any of the above (`unsafe-eval`, `unsafe-inline`,
  remote origins in `script-src`) is a hard failure.

## Other MV3-only forms worth checking

- `commands` → `chrome.commands` + `suggested_key`; unchanged key name, but the
  action it triggers is `action`, not `browser_action`.
- `declarative_net_request`: `{"rule_resources": [{"id": "ruleset_1",
  "enabled": true, "path": "rules.json"}]}` — rules files must be valid DNR
  JSON at packaged paths.
- `options_page` still works; prefer `options_ui` (`"open_in_tab": true`) for
  new extensions. MV2-only `options_ui.chrome_style`/`browser_style` are gone.
- `side_panel`, `offscreen` documents and `chrome_url_overrides` are MV3 forms;
  `chrome_url_overrides` may override exactly one page.
- `minimum_chrome_version` should be set when using post-88 APIs
  (`sidePanel` needs 114+, `chrome.storage.session` needs 102+).

## Migration checklist (MV2 -> MV3)

1. `manifest_version` 2 -> 3; delete `persistent`.
2. `background.scripts`/`background.page` -> `background.service_worker`
   (concatenate scripts or use `"type": "module"` + `import`).
3. `browser_action`/`page_action` -> `action`; `chrome.browserAction.*` ->
   `chrome.action.*`.
4. Move URL patterns from `permissions` to `host_permissions`.
5. Convert `content_security_policy` string to `{"extension_pages": ...}`;
   strip `unsafe-eval`/`unsafe-inline`/remote sources.
6. Replace `webRequestBlocking` handlers with declarativeNetRequest rules.
7. Replace `tabs.executeScript`/`tabs.insertCSS` with `chrome.scripting`.
8. Convert `web_accessible_resources` strings to `{resources, matches}`.
9. Remove every inline `<script>`/`on*=` handler and `eval`/`new Function`.
10. Re-run `scripts/mv3_lint.py`; it must exit 0.
