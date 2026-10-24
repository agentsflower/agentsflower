# Service worker lifecycle — ephemeral MV3 background

The MV3 `background.service_worker` is an event-driven worker Chrome starts on
demand and kills after ~30 s of idleness (hard cap ~5 min even while busy).
Everything that assumed a persistent background page must be redesigned.

## Consequences of the ephemeral lifecycle

- **Globals die.** `let state = ...` at top level is wiped on termination.
  Persist across restarts in `chrome.storage.local`; keep per-session secrets
  and scratch state in `chrome.storage.session` (RAM-only, cleared when the
  browser session ends; Chrome 102+). Large/binary data: IndexedDB.
- **Register listeners synchronously at top level.** `chrome.runtime.onMessage
  .addListener(fn)` must run during the first evaluation of the worker —
  never inside `async`, a callback, or after `await`. A listener registered
  late silently misses the event that woke the worker.
- **Rehydrate on start.** Boot work belongs in `chrome.runtime.onInstalled`
  (first install/update) and `chrome.runtime.onStartup` (browser start), not
  a "run once at load" assumption.
- **Module workers:** `"background": {"service_worker": "sw.js",
  "type": "module"}` enables static `import`; `importScripts()` is the classic
  alternative for bundling multiple files into one worker.

## API substitutions inside the worker

| Not available in a service worker | Use instead |
|---|---|
| `setInterval`, `setTimeout` (unreliable; worker dies) | `chrome.alarms` (`alarms` permission; min ~30 s delay, 30 s min period for `periodInMinutes`) |
| `window`, `document`, DOM, `<canvas>` 2D UI | `chrome.offscreen.createDocument` (`offscreen` permission) — a hidden page that owns DOM APIs and reports back via `chrome.runtime.sendMessage` |
| `localStorage` / `sessionStorage` | `chrome.storage.local` / `chrome.storage.session` (async, promise-based) |
| `XMLHttpRequest` | `fetch` |
| `alert`, `confirm`, `prompt` | notifications API or offscreen document |
| Audio playback, clipboard DOM APIs, `URL.createObjectURL` on media | offscreen document |

## Message passing contract

- `chrome.runtime.onMessage` handlers: return `true` synchronously when the
  response is sent asynchronously, otherwise the channel closes and
  `sendMessage` rejects with "message port closed". Promise-returning handlers
  are supported — `async msg => {...}` resolves as the response.
- `chrome.runtime.sendMessage` (worker <-> offscreen/popup/options),
  `chrome.tabs.sendMessage` (worker -> content script),
  `chrome.runtime.connect`/`Port` for long-lived channels. Note: an open Port
  does not guarantee keep-alive; use `chrome.alarms` for scheduled work.
- Content script -> page context: `window.postMessage` only; the two worlds
  share no JS scope.

## Patterns to reject in review

- `setInterval(keepAlive, ...)` / pinging `chrome.runtime.getPlatformInfo` to
  defeat termination — it throttles the worker and fails review; model the
  task with `chrome.alarms` or event listeners.
- Polling loops that assume continuous execution; MV3 rewards event-driven
  design (`onAlarm`, `onMessage`, `webNavigation`, `declarativeNetRequest`).
- Reading DOM state at worker start to "restore" the background page —
  persist what matters in storage and read it on demand.
- One worker listening for another extension-internal wakeup chain; collapse
  to direct listeners.

## Quick self-test

1. Load the extension, open `chrome://extensions` -> "service worker"
   inspector; let it go idle past 30 s.
2. Trigger each registered event (alarm fires, message arrives, install).
   Each must wake the worker and hit a top-level listener.
3. Restart Chrome; state needed across sessions must come back from
   `chrome.storage.local`, never from globals.
