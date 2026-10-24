#!/usr/bin/env python3
"""Deterministic Manifest V3 linter for AgentsFlower's chrome-extension-mv3 skill.
Parses manifest.json (plus the JS/HTML files it references) and flags MV2
legacy patterns: browser_action/page_action, background.scripts, host patterns
inside permissions, missing or MV2-form CSP, unsafe-eval/unsafe-inline,
webRequestBlocking, eval(), remote code, inline scripts/handlers, and
service-worker-incompatible APIs (setInterval, localStorage, XMLHttpRequest).
Zero external dependencies (Python standard library only).
Exit code: 0 = MV3_COMPLIANT (warnings allowed), 1 = NON_COMPLIANT or invalid input.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HOST_PATTERN = re.compile(r"^<all_urls>$|://", re.IGNORECASE)
HIGH_PRIVILEGE_PERMISSIONS = {
    "cookies", "history", "bookmarks", "debugger", "management",
    "nativeMessaging", "clipboardRead", "desktopCapture", "geolocation",
    "privacy", "proxy", "tabCapture", "downloads", "topSites",
}
JS_BANNED_PATTERNS = [
    (re.compile(r"\beval\s*\("), "eval(...) is forbidden by MV3 CSP; remove dynamic code execution"),
    (re.compile(r"\bnew\s+Function\s*\("), "new Function(...) is forbidden by MV3 CSP; remove dynamic code execution"),
    (re.compile(r"\bchrome\.browserAction\b"), "chrome.browserAction is MV2; use chrome.action"),
    (re.compile(r"\bchrome\.pageAction\b"), "chrome.pageAction is MV2; use chrome.action"),
    (re.compile(r"\bchrome\.tabs\.executeScript"), "chrome.tabs.executeScript is MV2; use chrome.scripting.executeScript"),
    (re.compile(r"\bchrome\.tabs\.insertCSS"), "chrome.tabs.insertCSS is MV2; use chrome.scripting.insertCSS"),
    (re.compile(r"chrome\.extension\.getBackgroundPage"), "getBackgroundPage does not exist for service workers; message the worker instead"),
]
WORKER_ONLY_WARNINGS = [
    (re.compile(r"\bsetInterval\s*\("), "setInterval dies with the worker; use chrome.alarms"),
    (re.compile(r"\bsetTimeout\s*\("), "setTimeout dies with the worker; use chrome.alarms"),
    (re.compile(r"\blocalStorage\b"), "no localStorage in service workers; use chrome.storage.session/local"),
    (re.compile(r"\bXMLHttpRequest\b"), "no XMLHttpRequest in service workers; use fetch"),
    (re.compile(r"\bdocument\.(createElement|getElementById|querySelector|body|write)"), "no DOM in service workers; use an offscreen document"),
    (re.compile(r"\bwindow\.(open|alert|confirm|prompt|location)"), "no window in service workers; use an offscreen document"),
]
SCRIPT_TAG = re.compile(r"<script\b[^>]*>", re.IGNORECASE)
SCRIPT_SRC = re.compile(r"\bsrc\s*=\s*[\"']?([^\s\"'>]+)", re.IGNORECASE)
INLINE_HANDLER = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)


def find(key, coll):
    return any(f["rule"] == key for f in coll)


def lint_manifest(manifest_path: Path, text_mode: bool = False) -> dict:
    findings = []

    def add(severity, rule, where, message):
        findings.append({"severity": severity, "rule": rule, "where": where, "message": message})

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        add("error", "manifest.readable", manifest_path.name, f"cannot parse manifest.json: {e}")
        return _report(manifest_path, findings)

    if not isinstance(manifest, dict):
        add("error", "manifest.readable", manifest_path.name, "manifest.json root must be an object")
        return _report(manifest_path, findings)

    root = manifest_path.parent
    where = manifest_path.name

    # 1. manifest_version
    mv = manifest.get("manifest_version")
    if mv is None:
        add("error", "manifest_version", where, "manifest_version missing; MV3 requires manifest_version: 3")
    elif mv != 3:
        add("error", "manifest_version", where, f"manifest_version must be 3, found {mv!r} (MV2 legacy)")
    else:
        add("info", "manifest_version", where, "manifest_version: 3 verified")

    # 2. background
    bg = manifest.get("background")
    worker_files = []
    if isinstance(bg, dict):
        if bg.get("scripts") or bg.get("page"):
            add("error", "background.service_worker", where,
                "background.scripts/background.page is MV2; use background.service_worker")
        if bg.get("persistent"):
            add("error", "background.persistent", where,
                "persistent background is banned in MV3; the service worker is ephemeral")
        sw = bg.get("service_worker")
        if isinstance(sw, str) and sw:
            worker_files.append(sw)
            add("info", "background.service_worker", where, f"background.service_worker verified: {sw}")
        elif isinstance(sw, list):
            worker_files.extend(x for x in sw if isinstance(x, str))
    elif bg is not None:
        add("error", "background.service_worker", where, "background must be an object with service_worker")

    # 3. MV2 toolbar actions
    for key in ("browser_action", "page_action"):
        if key in manifest:
            add("error", key, where, f"{key} is MV2; use action (chrome.action)")

    # 4. permissions vs host_permissions
    for plist_key in ("permissions", "optional_permissions"):
        perms = manifest.get(plist_key) or []
        if not isinstance(perms, list):
            add("error", "permissions", where, f"{plist_key} must be an array")
            continue
        for p in perms:
            if not isinstance(p, str):
                continue
            if HOST_PATTERN.search(p):
                add("error", "host_permissions", where,
                    f"host pattern {p!r} in {plist_key}; host access belongs in host_permissions")
            elif p == "webRequestBlocking":
                add("error", "webRequestBlocking", where,
                    "webRequestBlocking is banned in MV3; use declarativeNetRequest")
            elif p == "tabs":
                add("warning", "permissions.tabs", where, "'tabs' exposes URL/title; prefer 'activeTab'")
            elif p in HIGH_PRIVILEGE_PERMISSIONS:
                add("warning", "permissions.broad", where,
                    f"high-privilege permission {p!r}; ensure it is minimal and justified")
    if "declarativeNetRequest" in (manifest.get("permissions") or []):
        if not manifest.get("host_permissions") and not manifest.get("optional_host_permissions"):
            add("warning", "host_permissions", where,
                "declarativeNetRequest without host_permissions cannot touch host requests; "
                "add host_permissions or declarativeNetRequestWithHostAccess")

    # 5. content_security_policy
    csp = manifest.get("content_security_policy")
    if csp is None:
        add("error", "content_security_policy", where,
            "content_security_policy key missing; set the MV3 object form "
            "{\"extension_pages\": \"script-src 'self'; object-src 'self'\"}")
    elif isinstance(csp, str):
        add("error", "content_security_policy", where,
            "content_security_policy string is the MV2 form; use {\"extension_pages\": ..., \"sandbox\": ...}")
        _check_csp_string(csp, add, where)
    elif isinstance(csp, dict):
        for section in ("extension_pages", "sandbox"):
            value = csp.get(section)
            if isinstance(value, str):
                _check_csp_string(value, add, where)
        add("info", "content_security_policy", where, "content_security_policy object form verified")
    else:
        add("error", "content_security_policy", where, "content_security_policy must be an object (MV3) or string (MV2)")

    # 6. web_accessible_resources object form
    war = manifest.get("web_accessible_resources")
    if isinstance(war, list):
        for i, entry in enumerate(war):
            if isinstance(entry, str):
                add("error", "web_accessible_resources", where,
                    f"web_accessible_resources[{i}] is a bare string; MV3 requires "
                    "{\"resources\": [...], \"matches\": [...]}")
            elif isinstance(entry, dict):
                if not entry.get("resources") or not entry.get("matches"):
                    add("error", "web_accessible_resources", where,
                        f"web_accessible_resources[{i}] requires both 'resources' and 'matches'")

    # 7. content_scripts breadth
    for i, cs in enumerate(manifest.get("content_scripts") or []):
        if isinstance(cs, dict):
            for m in cs.get("matches") or []:
                if m == "<all_urls>":
                    add("warning", "content_scripts.all_urls", where,
                        f"content_scripts[{i}] matches <all_urls>; scope to needed origins")

    # 8. Referenced files: existence + JS/HTML anti-pattern scan
    js_files, html_files, json_files = [], [], []
    worker_set = set()
    for rel in worker_files:
        js_files.append(rel); worker_set.add(rel)
    for cs in manifest.get("content_scripts") or []:
        if isinstance(cs, dict):
            js_files.extend(x for x in cs.get("js") or [] if isinstance(x, str))
    for key in ("default_popup",):
        act = manifest.get("action")
        if isinstance(act, dict) and isinstance(act.get(key), str):
            html_files.append(act[key])
    opt = manifest.get("options_ui")
    if isinstance(opt, dict) and isinstance(opt.get("page"), str):
        html_files.append(opt["page"])
    if isinstance(manifest.get("options_page"), str):
        html_files.append(manifest["options_page"])
    if isinstance(manifest.get("devtools_page"), str):
        html_files.append(manifest["devtools_page"])
    side = manifest.get("side_panel")
    if isinstance(side, dict) and isinstance(side.get("default_path"), str):
        html_files.append(side["default_path"])
    sandbox = manifest.get("sandbox")
    if isinstance(sandbox, dict):
        html_files.extend(x for x in sandbox.get("pages") or [] if isinstance(x, str))
    overrides = manifest.get("chrome_url_overrides")
    if isinstance(overrides, dict):
        html_files.extend(x for x in overrides.values() if isinstance(x, str))
    # background.scripts is MV2 but still scan its JS for forbidden code
    if isinstance(bg, dict):
        js_files.extend(x for x in bg.get("scripts") or [] if isinstance(x, str))
    dnr = manifest.get("declarative_net_request")
    if isinstance(dnr, dict):
        for rs in dnr.get("rule_resources") or []:
            if isinstance(rs, dict) and isinstance(rs.get("path"), str):
                json_files.append(rs["path"])

    for rel in dict.fromkeys(js_files):
        f = root / rel
        if not f.is_file():
            add("warning", "files.missing", rel, f"referenced JS file {rel!r} not found; cannot inspect")
            continue
        code = f.read_text(encoding="utf-8", errors="replace")
        for pattern, msg in JS_BANNED_PATTERNS:
            if pattern.search(code):
                add("error", "js.banned_api", rel, msg)
        if "chrome.webRequest" in code and re.search(r"[\"']blocking[\"']", code):
            add("error", "webRequestBlocking", rel,
                "blocking webRequest extraInfoSpec is banned in MV3; use declarativeNetRequest")
        if rel in worker_set:
            for pattern, msg in WORKER_ONLY_WARNINGS:
                if pattern.search(code):
                    add("warning", "worker.api", rel, msg)
        if re.search(r"fetch\(\s*[\"']javascript:", code) or re.search(r"import\s*\(\s*[\"']https?://", code):
            add("error", "js.remote_code", rel, "remotely hosted code is banned in MV3; bundle all executed code")

    for rel in dict.fromkeys(html_files):
        f = root / rel
        if not f.is_file():
            add("warning", "files.missing", rel, f"referenced HTML file {rel!r} not found; cannot inspect")
            continue
        page = f.read_text(encoding="utf-8", errors="replace")
        for tag in SCRIPT_TAG.findall(page):
            src = SCRIPT_SRC.search(tag)
            if src is None:
                add("error", "html.inline_script", rel,
                    "inline <script> block banned by MV3 CSP; move code to a .js file")
            elif src.group(1).lower().startswith(("http://", "https://", "//")):
                add("error", "html.remote_script", rel,
                    f"remote script {src.group(1)!r} banned in MV3; bundle all executed code")
        if INLINE_HANDLER.search(page):
            add("error", "html.inline_handler", rel,
                "inline on*= handler banned by MV3 CSP; bind via addEventListener")

    for rel in dict.fromkeys(json_files):
        f = root / rel
        if not f.is_file():
            add("warning", "files.missing", rel, f"declarativeNetRequest ruleset {rel!r} not found")
            continue
        try:
            rules = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            if not isinstance(rules, list):
                add("error", "dnr.rules", rel, "declarativeNetRequest ruleset must be a JSON array of rules")
        except json.JSONDecodeError as e:
            add("error", "dnr.rules", rel, f"declarativeNetRequest ruleset is invalid JSON: {e}")

    return _report(manifest_path, findings)


def _check_csp_string(policy: str, add, where):
    lowered = policy.lower()
    for bad in ("unsafe-eval", "unsafe-inline"):
        if bad in lowered:
            add("error", "content_security_policy", where, f"CSP contains {bad}; banned in MV3")
    if re.search(r"https?://", lowered):
        add("error", "content_security_policy", where,
            "CSP allows remote script/connect sources; MV3 bans remotely hosted code")


def _report(manifest_path: Path, findings) -> dict:
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    return {
        "target": str(manifest_path),
        "verdict": "NON_COMPLIANT" if errors else "MV3_COMPLIANT",
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
    }


def main():
    ap = argparse.ArgumentParser(description="AgentsFlower Chrome Extension Manifest V3 linter")
    ap.add_argument("target", nargs="?", default=".",
                    help="Extension directory or path to manifest.json (default: .)")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    ap.add_argument("--out", type=Path, help="Write JSON report to file")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    manifest_path = target / "manifest.json" if target.is_dir() else target
    if not manifest_path.is_file():
        report = {"target": str(manifest_path), "verdict": "NON_COMPLIANT", "errors": 1,
                  "warnings": 0,
                  "findings": [{"severity": "error", "rule": "manifest.readable",
                                "where": str(manifest_path), "message": "manifest.json not found"}]}
    else:
        report = lint_manifest(manifest_path)

    if args.out:
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Lint report saved to {args.out}")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 64)
        print("AgentsFlower Manifest V3 Lint")
        print(f"Target: {report['target']}")
        print(f"Verdict: {report['verdict']}  ({report['errors']} errors, {report['warnings']} warnings)")
        print("=" * 64)
        icon = {"error": "E", "warning": "W", "info": "+"}
        for f in report["findings"]:
            print(f"  [{icon.get(f['severity'], '?')}] ({f['where']}) {f['message']}")
        print("=" * 64)

    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
