"""Assess the tool, model and reasoning effort for one task with TypeSafe AI (Jev), and enforce the
recorded assessment at every worker launch.

  python .agentflow/tools/route.py T-007              # print the recommendation, persist the assessment
  python .agentflow/tools/route.py T-007 --apply      # write Tool: / Model: into a task that has not started (high band)

Built to the TypeSafe documentation (https://docs.typesafe.ai, summary in .agentflow/docs/typesafe.md); read it
before changing this file:
- state is an object with named fields, only what the decision needs, clipped well under the 32k-token state budget;
- one request asks three atomic questions in parallel - choices "option" (tool/model family) and "effort", plus a
  3-level score "complexity" - and code combines them deterministically;
- options are object criteria (`what`, `not_for`, `examples`), the project policy goes into the instructions;
- confidence bands: >= 0.9 act (`--apply` writes the task), 0.5-0.9 recommendation for the Orchestrator to confirm,
  < 0.5 no decision (decide by tool-routing.md); the Jev version is pinned (`jev_model` in the options file).

Options: `.agentflow/docs/model-options.json` (project-owned):

  {"policy": "how to choose, in words (cost, free windows, independence)",
   "jev_model": "jev-1.13.0",
   "floor": {"option": "devin-swe-2", "effort": "high"},   # minimum permitted default, never a downgrade
   "prefer": ["devin"],                                   # CLI preference among adequate options only
   "options": {"<id>": {"tool": "codex|claude|agy|devin", "model": "...",
                        "efforts": ["low", "medium", "high"],
                        "model_by_effort": {"low": "model-low", "high": "model-high"},
                        "tier": "high",                   # effort-less models only: declared capability tier
                        "what": "what it is good at", "not_for": "what to keep away from it", "examples": ["..."],
                        "roles": ["developer", "tester"], "from": "YYYY-MM-DD", "until": "YYYY-MM-DD",
                        "max_complexity": 0|1|2, "escalate_to": "<id>", "quota_group": "..."}}}

An option outside its from/until window or not meant for the task's role is left out; a tester never gets the tool
of the developer task it checks while another option remains (protocol: Tool Routing, independence).

Enforcement (the routing policy): every call persists an assessment record - schemaVersion 1, event
"assessment" - in .agentflow/tasks/.runtime/T-NNN.route.json, bound to the task's requirementsHash
(header minus the routing fields Tool/Model/Backup/Routing exception/Resume). Its `status` is
  ok              an adequate option was selected under the ordering: the floor option first when it can
                  meet the requirement, then preferred CLIs, then everything else - each by Jev ranking;
  blocked         nothing adequate is usable (the record names why per option) - the launch waits;
  low-confidence  Jev answered below the low band - never admission evidence;
  failed          the assessment could not complete (no key, API error, no options file) - never evidence.
Launch admission (run_task.py, and tick.py's automatic launches): the latest assessment must exist, match
the current requirementsHash and be status ok, and the resolved identity after env/CLI overrides
(AGENTFLOW_<TOOL>_ARGS filtered by the task's Model line) must still meet the recorded requirement - the
same rule binds backups, retries and resumed attempts. Only a `Routing exception: <reason>` header line
overrides a failed or missing assessment, and it is recorded as a human exception, never as Jev evidence.

Key: TYPESAFE_API_KEY, or a file named by AGENTFLOW_TYPESAFE_KEY_FILE (outside the repository); never printed or
stored. Base URL: TYPESAFE_BASE_URL (default https://api.typesafe.ai). Exit: 0 high band, 4 medium band (printed, not
applied), 3 no decision, 5 blocked. Every call prints and logs Jev's version, token usage and request id.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT  # noqa: E402
import gate  # noqa: E402
import machine_capacity  # noqa: E402
import quota_groups  # noqa: E402

API = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai").rstrip("/") + "/v1/systemone"
OPTIONS = FLOW_ROOT / "docs" / "model-options.json"
JEV_MODEL = "jev-1.13.0"  # pinned: the bands below are set for this version (docs: Models)
HIGH, LOW = 0.9, 0.5      # docs: Confidence - act above 0.9, confirm 0.5-0.9, a person decides below 0.5
OK, NO_DECISION, MEDIUM, BLOCKED = 0, 3, 4, 5
CLI_TOOLS = ("codex", "claude", "agy", "devin")  # the launcher's managed CLIs (as run_task.TOOLS)
COMPLEXITY = [
    {"summary": "Small", "signals": "one area, clear steps, mechanical or well-trodden change, little risk"},
    {"summary": "Moderate", "signals": "several files within one feature, ordinary tests, known patterns"},
    {"summary": "Hard", "signals": "cross-cutting or architectural change, unfamiliar APIs, concurrency, security, "
                                   "subtle edge cases, or many interacting parts"},
]
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max", "ultra"]
EFFORT = {
    "low": {"what": "Light reasoning for quick, mechanical, low-risk work with clear steps",
            "examples": ["rename a field", "adjust one setting", "run a known check"]},
    "medium": {"what": "Normal reasoning for a clear, scoped implementation using familiar patterns",
               "examples": ["fix a contained bug", "add a small feature with tests"]},
    "high": {"what": "Deep reasoning for non-trivial debugging, several interacting files, or careful testing",
             "examples": ["trace a state bug", "change a feature across UI and backend"]},
    "xhigh": {"what": "Extra-high reasoning for ambiguous, cross-cutting, risky, or unfamiliar work",
              "examples": ["redesign a subsystem", "debug a subtle integration failure"]},
    "max": {"what": "Maximum reasoning for the hardest long-horizon work, security, or concurrency",
            "examples": ["resolve a systemic race", "plan and implement a risky migration"]},
    "ultra": {"what": "Ultra-high reasoning for exceptional tasks where exhaustive analysis is worth the cost",
              "examples": ["investigate a critical failure with several plausible root causes"]},
}


class NoDecision(Exception):
    pass


def api_key():
    if k := os.environ.get("TYPESAFE_API_KEY", "").strip():
        return k
    f = os.environ.get("AGENTFLOW_TYPESAFE_KEY_FILE", "").strip()
    if f and Path(f).exists():
        return Path(f).read_text(encoding="utf-8-sig").strip()
    raise NoDecision("no TypeSafe key: set TYPESAFE_API_KEY or AGENTFLOW_TYPESAFE_KEY_FILE")


def static_reason(o, role, avoid_tool, today):
    """Why an option is out regardless of the machine: role, tester independence or the from/until window."""
    if o.get("roles") and role not in o["roles"]:
        return f"not for role {role}"
    if avoid_tool and o.get("tool") == avoid_tool:
        return f"kept off {avoid_tool}: the checked task ran on it (tester independence)"
    if o.get("from", "0000") > today:
        return f"available from {o['from']}"
    if o.get("until", "9999") < today:
        return f"until {o['until']} has passed"
    return None


def cli_usable(tool, group=None):
    """Known CLI and quota state; account access may still fail at launch. A hold on the bare tool key
    stays tool-wide; a hold on '<tool>:<group>' blocks only that quota group."""
    if machine_capacity.limit_until(tool, group):
        return False
    if os.environ.get("AGENTFLOW_ROUTE_ASSUME_CLI_AVAILABLE") == "1":  # local API stand-in tests
        return True
    configured = os.environ.get(f"AGENTFLOW_{tool.upper()}", "").strip()
    if configured:
        return bool(glob.glob(configured)) if "*" in configured else (Path(configured).is_file() or shutil.which(configured) is not None)
    return shutil.which(tool) is not None


def live_reason(o):
    """Why the option is unusable right now (observed hold on its quota group, or no executable)."""
    end = machine_capacity.limit_until(o["tool"], o.get("quota_group"))
    if end:
        return f"limited until {end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    return None if cli_usable(o["tool"], o.get("quota_group")) else f"no {o['tool']} executable"


def eligibility(options, role, avoid_tool, today):
    """(eligible, reasons): options offered to Jev now, plus why each remaining option is out. When the
    independence filter would leave a tester nothing, the avoided tool stays (as available() did)."""
    eligible, reasons = {}, {}
    for name, o in options.items():
        r = static_reason(o, role, avoid_tool, today) or live_reason(o)
        (reasons if r else eligible).__setitem__(name, r or o)
    if avoid_tool and not any(o.get("tool") != avoid_tool for o in eligible.values()):
        for name, o in options.items():
            if name in eligible:
                continue
            r = static_reason(o, role, None, today) or live_reason(o)
            if r is None:
                eligible[name] = o
                reasons.pop(name, None)
    return eligible, reasons


def available(options, role, avoid_tool=None, today=None):
    """Options usable for the role right now - role, availability window, machine state, tester
    independence. Kept for the callers that need the bare dict; eligibility() also gives the reasons."""
    return eligibility(options, role, avoid_tool, today or date.today().isoformat())[0]


def option_ceiling(o):
    """The highest effort tier the option can express; effort-less models sit at their declared 'tier'
    (or default_effort), else medium."""
    supported = [x for x in supported_efforts(o) if x in EFFORT_ORDER]
    if supported:
        return max(EFFORT_ORDER.index(x) for x in supported)
    declared = o.get("tier") or o.get("default_effort") or "medium"
    return EFFORT_ORDER.index(declared) if declared in EFFORT_ORDER else -1


def adequate_reason(o, required):
    """Why an option cannot meet the requirement, or None. Capability is capability/effort based -
    no universal ranking: the option qualifies when it can express a tier at or above the required
    effort and its complexity cap covers the assessed complexity."""
    cx, cap = (required or {}).get("complexity"), o.get("max_complexity")
    if cap is not None and cx is not None and float(cx) > float(cap) + 0.5:
        return f"complexity {cx:.2f} exceeds its cap {cap}"
    need = (required or {}).get("effort")
    if need and need in EFFORT_ORDER and option_ceiling(o) < EFFORT_ORDER.index(need):
        return f"needs effort >= {need}; this option reaches only {EFFORT_ORDER[option_ceiling(o)]}"
    return None


def resolve_requirement(o, required_effort):
    """(model, effort_flag, tier) this option must run to MEET the requirement, or (None, None, None)
    when it cannot reach it. Unlike nearest_effort this never resolves below the requirement."""
    supported = supported_efforts(o)
    if not supported:
        return o.get("model"), o.get("effort"), o.get("tier") or o.get("default_effort") or "medium"
    need = required_effort if required_effort in EFFORT_ORDER else \
        o.get("default_effort") if o.get("default_effort") in EFFORT_ORDER else "medium"
    higher = [x for x in supported if x in EFFORT_ORDER and EFFORT_ORDER.index(x) >= EFFORT_ORDER.index(need)]
    if not higher:
        return None, None, None
    tier = higher[0]
    by_effort = o.get("model_by_effort") or {}
    model = by_effort.get(tier, o.get("model"))
    effort = None if by_effort or o.get("effort_in_model") else tier
    return model, effort, tier


def admission_order(candidates, cfg, probabilities):
    """The policy order over adequate+usable options: the configured floor option first, then the
    preferred CLIs, then the rest - inside each group by Jev probability. CLI preference never ranks an
    inadequate option: this sorts only options that already meet the requirement."""
    floor_option = (cfg.get("floor") or {}).get("option")
    prefer = cfg.get("prefer") or []

    def key(name):
        o = candidates[name]
        rank = 0 if name == floor_option else 1 if o.get("tool") in prefer else 2
        return (rank, -probabilities.get(name, 0), name)
    return sorted(candidates, key=key)


def criterion(o):
    """Object-form choice criterion (docs: Advanced structure): what / not_for / examples, plus the facts."""
    c = {"what": o.get("what") or o.get("describe", "")}
    if o.get("not_for"):
        c["not_for"] = o["not_for"]
    if o.get("examples"):
        c["examples"] = o["examples"]
    models = o.get("model_by_effort") or {}
    c["runs_on"] = o.get("tool") + (f" with model {o['model']}" if o.get("model") else "")
    if models:
        c["model_family"] = models
    efforts = supported_efforts(o)
    if efforts:
        c["supported_efforts"] = efforts
    for fact in ("cost", "latency", "context"):
        if o.get(fact):
            c[fact] = o[fact]
    if o.get("until"):
        c["available_until"] = o["until"]
    return c


def clip(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[:n - 1] + "…"


def task_state(t, text, routing_date=None):
    """Only what the decision needs, as named fields (docs: State)."""
    title = text.splitlines()[0].lstrip("# ").strip() if text else t["id"]
    task = {"id": t["id"], "title": clip(title, 200), "role": t["role"],
            "goal": clip(gate.section(text, "Goal"), 2000),
            "acceptance_criteria": [clip(a, 400) for a in t["acceptance"][:30]],
            "allowed_files": t["allowed"][:40], "checks": [clip(c, 200) for c in t["checks"][:20]]}
    if t.get("repos") and t["repos"] != [""]:
        task["repositories"] = t["repos"]
    return {"routing_date": routing_date or date.today().isoformat(), "task": task}


def questions(options, policy):
    return {
        "option": {"type": "choice",
                   "instructions": {"question": "Which option should take this task?",
                                    "project_policy": policy or "none",
                                    "note": "Options are alternatives; weigh the task against what each is for."},
                   "criteria": {k: criterion(v) for k, v in options.items()}},
        "complexity": {"type": "score",
                       "instructions": "How hard is this task for a capable software engineer?",
                       "criteria": COMPLEXITY},
        "effort": {"type": "choice",
                   "instructions": {"question": "How much reasoning effort does this task require?",
                                    "note": "Judge the task itself. Code maps this tier to the selected model's "
                                            "supported effort; prefer the cheaper tier when two are sufficient."},
                   "criteria": EFFORT},
    }


def ask(state, qs, key, jev_model, opener=urllib.request.urlopen, tries=3):
    data = json.dumps({"state": state, "model": jev_model, "questions": qs}).encode("utf-8")
    for i in range(tries):
        req = urllib.request.Request(API, data=data, method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with opener(req, timeout=30) as r:
                d = json.loads(r.read())
                return d["answers"], {"model": d.get("model"), "usage": d.get("usage"),
                                      "requestId": r.headers.get("x-typesafe-request-id")}
        except urllib.error.HTTPError as e:
            rid = e.headers.get("x-typesafe-request-id") if e.headers else None
            if e.code in (429, 529) and i + 1 < tries:  # docs: back off and retry on rate limit / overload
                time.sleep(2 * (i + 1))
                continue
            raise NoDecision(f"TypeSafe answered HTTP {e.code}" + (" (invalid key)" if e.code == 401 else "")
                             + (" (request rejected: see docs/typesafe.md)" if e.code == 422 else "")
                             + (f", request {rid}" if rid else ""))
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
            raise NoDecision(f"TypeSafe call failed: {type(e).__name__}")
    raise NoDecision("TypeSafe is busy (429/529)")


def supported_efforts(option):
    """Return effort tiers in canonical order; model_by_effort keys are concrete CLI variants."""
    values = option.get("efforts") or list((option.get("model_by_effort") or {}).keys())
    return [x for x in EFFORT_ORDER if x in values] + [x for x in values if x not in EFFORT_ORDER]


def band(conf):
    return "high" if conf >= HIGH else "medium" if conf >= LOW else "low"


def set_header(path, tool, model, effort, backup=None):
    text = Path(path).read_text(encoding="utf-8")
    head, sep, rest = text.partition("\n## Result")
    head = re.sub(r"(?m)^Tool:[^\n]*$", f"Tool: {tool}", head, count=1)
    model_line = f"Model: {model}" + (f", effort={effort}" if effort else "") if model else None
    if re.search(r"(?m)^Model:", head):
        head = re.sub(r"(?m)^Model:[^\n]*\n?", (model_line + "\n") if model_line else "", head, count=1)
    elif model_line:
        head = re.sub(r"(?m)^(Tool:[^\n]*\n)", rf"\1{model_line}\n", head, count=1)
    head = re.sub(r"(?m)^Backup Tool:[^\n]*\n?|^Backup Model:[^\n]*\n?", "", head)
    if backup:
        backup_tool, backup_model, backup_effort = backup
        backup_line = f"Backup Tool: {backup_tool}\n"
        if backup_model:
            backup_line += f"Backup Model: {backup_model}" + (f", effort={backup_effort}" if backup_effort else "") + "\n"
        head = re.sub(r"(?m)^(Stage:[^\n]*\n)", backup_line + r"\1", head, count=1)
    Path(path).write_text(head + sep + rest, encoding="utf-8", newline="\n")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _config():
    if not OPTIONS.exists():
        raise NoDecision(f"no {OPTIONS.relative_to(FLOW_ROOT.parent).as_posix()}")
    try:
        cfg = json.loads(OPTIONS.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        raise NoDecision(f"cannot read {OPTIONS.name}: {e}")
    return cfg


def _required(jev_effort, complexity, cfg):
    """The launch-binding requirement: Jev's effort is a floor-adjusted minimum - the project floor
    lifts it, never lowers it."""
    need = None
    floor_eff = (cfg.get("floor") or {}).get("effort")
    for e in (jev_effort, floor_eff):
        if e in EFFORT_ORDER and (need is None or EFFORT_ORDER.index(e) > EFFORT_ORDER.index(need)):
            need = e
    return {"effort": need, "complexity": complexity}


def _floor_record(cfg):
    spec = cfg.get("floor") or {}
    name = spec.get("option")
    o = (cfg.get("options") or {}).get(name or "", {})
    model, _effort, tier = resolve_requirement(o, spec.get("effort")) if o else (None, None, None)
    return {"option": name, "tool": o.get("tool"), "model": model, "effort": spec.get("effort"),
            "resolvedModel": model, "resolvedTier": tier} if name else None


def route(tid, apply=False, opener=urllib.request.urlopen, today=None):
    """Assess the task and persist the record a launch is admitted on. The assessment is written
    whenever the Task File parses - including failed and blocked outcomes - because silence here
    would read as 'not assessed', which is itself a refusal."""
    t = gate.parse(tid)
    text = Path(t["file"]).read_text(encoding="utf-8-sig")
    today = today or date.today().isoformat()
    rec = {"event": "assessment", "schemaVersion": 1, "task": tid, "at": now_iso(), "source": "jev",
           "requirementsHash": gate.requirements_hash(text), "role": t["role"],
           "status": "failed", "error": None, "applied": False}
    try:
        cfg = _config()
        avoid = None
        if t["role"] == "tester":
            avoid = gate.field(gate.header(Path(t["checked"]["file"]).read_text(encoding="utf-8-sig")), "Tool")
        all_options = cfg.get("options", {})
        eligible, excluded = eligibility(all_options, t["role"], avoid, today)
        rec["excluded"] = excluded
        rec["eligibleOptions"] = sorted(eligible)
        if not eligible:
            rec["status"] = "blocked"
            rec["required"] = _required(None, None, cfg)
            rec["blocked"] = f"no option is eligible or usable today for a {t['role']} task"
            _log(tid, rec)
            print(f"{tid}: blocked - {rec['blocked']}: " +
                  "; ".join(f"{k}: {v}" for k, v in list(excluded.items())[:6]))
            return BLOCKED
        answers, meta = ask(task_state(t, text, today), questions(eligible, cfg.get("policy", "")),
                            api_key(), cfg.get("jev_model", JEV_MODEL), opener)
    except NoDecision as e:
        rec["error"] = str(e)
        _log(tid, rec)
        print(f"{tid}: assessment failed: {e}")
        return NO_DECISION
    rec["jev"] = meta
    rec["requestId"] = meta.get("requestId")
    opt, cx = answers["option"], answers.get("complexity", {})
    effort_answer = answers.get("effort", {})
    option_conf = float(opt.get("confidence", 0))
    effort_conf = float(effort_answer.get("confidence", 0)) if effort_answer else None
    probs = dict(sorted(opt.get("probabilities", {}).items(), key=lambda kv: -kv[1]))
    margin = sorted(probs.values(), reverse=True)
    margin = margin[0] / margin[1] if len(margin) > 1 and margin[1] else None
    cx_score = float(cx.get("score", 0)) if cx else None
    required = _required(effort_answer.get("choice"), cx_score, cfg)
    inadequate, candidates = {}, {}
    for name, o in eligible.items():
        r = adequate_reason(o, required)
        (inadequate if r else candidates).__setitem__(name, r or o)
    order = admission_order(candidates, cfg, probs)
    # Options that meet the requirement but cannot run now: the resource reason a blocked launch waits on.
    held = {}
    for name, o in all_options.items():
        if name in candidates or name in inadequate:
            continue
        if static_reason(o, t["role"], avoid, today) or adequate_reason(o, required):
            continue
        if live_reason(o):
            held[name] = live_reason(o)
    choice = order[0] if order else None
    jev_choice = opt.get("choice")
    needs_effort = bool(choice and supported_efforts(candidates[choice]))
    conf = min(option_conf, effort_conf) if needs_effort and effort_conf is not None else option_conf
    selected, sel_model, sel_effort, sel_tier = None, None, None, None
    if choice:
        o = candidates[choice]
        sel_model, sel_effort, sel_tier = resolve_requirement(o, required["effort"])
        selected = {"option": choice, "tool": o.get("tool"), "model": sel_model,
                    "effort": sel_effort, "resolvedEffort": sel_tier}
    backup = None
    if choice:
        for name in order[1:]:
            if candidates[name].get("tool") != candidates[choice].get("tool"):
                bm, be, bt = resolve_requirement(candidates[name], required["effort"])
                backup = {"option": name, "tool": candidates[name].get("tool"), "model": bm,
                          "effort": be, "resolvedEffort": bt, "probability": probs.get(name)}
                break
    if not choice:
        rec["status"] = "blocked"
        rec["blocked"] = f"no option meets the requirement (effort >= {required['effort'] or '-'})"
        reasons = [f"{n}: {w}" for n, w in inadequate.items()] + [f"{n}: {w}" for n, w in held.items()]
        if reasons:
            rec["blocked"] += "; " + "; ".join(reasons[:6])
    elif conf < LOW:
        rec["status"] = "low-confidence"
    else:
        rec["status"] = "ok"
    if choice == jev_choice:
        reason = "meets the requirement"
    elif jev_choice in inadequate:
        reason = f"{jev_choice} is below the requirement ({inadequate[jev_choice]})"
    elif jev_choice in held:
        reason = f"{jev_choice} is held ({held[jev_choice]}); {choice} is the adequate pick"
    elif jev_choice in candidates:
        reason = f"{jev_choice} is adequate; the policy order prefers {choice}"
    elif jev_choice:
        reason = f"{jev_choice} is not eligible ({excluded.get(jev_choice, 'unconfigured')}); {choice} is the pick"
    else:
        reason = "Jev named no option; the policy order selected"
    rec.update({"floor": _floor_record(cfg), "prefer": cfg.get("prefer") or [],
                "required": required, "inadequate": inadequate, "adequateHeld": held,
                "candidates": order, "jevChoice": jev_choice, "choice": choice,
                "probabilities": probs, "confidence": conf, "band": band(conf),
                "optionConfidence": option_conf, "effortConfidence": effort_conf,
                "jevEffort": effort_answer.get("choice"), "complexity": cx_score,
                "complexityConfidence": cx.get("confidence"), "selectionReason": reason,
                "selected": selected, "tool": (selected or {}).get("tool"), "model": sel_model,
                "effort": sel_effort, "resolvedEffort": sel_tier, "backup": backup,
                "backupChoice": (backup or {}).get("option"), "backupTool": (backup or {}).get("tool"),
                "backupModel": (backup or {}).get("model"), "backupEffort": (backup or {}).get("effort"),
                "backupProbability": (backup or {}).get("probability"),
                "availability": {"at": rec["at"], "source": "cli executables + observed limits (machine registry)"}})
    print(f"{tid}: {choice or '-'} -> Tool: {(selected or {}).get('tool')}"
          + (f", Model: {sel_model}" + (f", effort={sel_effort}" if sel_effort else "") if sel_model else ""))
    effort_text = (f"; effort {effort_answer.get('choice')} -> {sel_tier} (confidence {effort_conf:.2f})"
                   if needs_effort and effort_conf is not None else "")
    print(f"  option confidence {option_conf:.2f}" + (f", top/second {margin:.1f}x" if margin else "")
          + effort_text + f"; overall {conf:.2f} ({band(conf)})"
          + f"; complexity {cx_score or 0:.2f} of 2 (confidence {float(cx.get('confidence', 0)):.2f})"
          + f"; required effort >= {required['effort'] or '-'}")
    for k, v in sorted(probs.items(), key=lambda kv: -kv[1])[:5]:
        print(f"  {v:.2f}  {k}")
    if choice and choice != jev_choice:
        print(f"  {reason}" + (f": escalated to {choice}" if jev_choice in inadequate else ""))
    if backup:
        print(f"  backup {backup['option']} -> Tool: {backup['tool']}"
              + (f", Model: {backup['model']}" if backup["model"] else ""))
    u = meta.get("usage") or {}
    print(f"  TypeSafe {meta.get('model')}: {u.get('input_tokens', '?')} in / {u.get('output_tokens', '?')} out tokens,"
          f" request {meta.get('requestId') or '-'}")
    if rec["status"] == "blocked":
        print(f"  blocked: {rec['blocked']}")
        _log(tid, rec)
        return BLOCKED
    if rec["status"] == "low-confidence":
        print("  low confidence: no decision; decide by tool-routing.md")
        _log(tid, rec)
        return NO_DECISION
    if conf < HIGH:
        print("  medium confidence: the Orchestrator confirms before using it (not applied)")
        _log(tid, rec)
        return MEDIUM
    if apply:
        status = gate.ledger_rows().get(tid, {}).get("Status")
        if status not in (None, "", "ready", "blocked"):
            _log(tid, rec)
            raise NoDecision(f"{tid} is '{status}': --apply changes only a task that has not started")
        set_header(t["file"], selected["tool"], sel_model, sel_effort,
                   (backup["tool"], backup["model"], backup["effort"]) if backup else None)
        if status:
            subprocess.run([sys.executable, str(FLOW_ROOT / "tools" / "ledger.py"), "set", tid,
                            "--tool", selected["tool"]], check=True, capture_output=True)
        rec["applied"] = True
        print(f"  applied to {Path(t['file']).name}")
    _log(tid, rec)
    return OK


# --- persisted records and launch admission ------------------------------------------------------------------------
def _rt_dir(rt_dir=None):
    """The record folder, resolved per call: a patched or relocated FLOW_ROOT must redirect it."""
    return Path(rt_dir) if rt_dir else FLOW_ROOT / "tasks" / ".runtime"


def _log(tid, rec, rt_dir=None):
    rt = _rt_dir(rt_dir)
    rt.mkdir(parents=True, exist_ok=True)
    p = rt / f"{tid}.route.json"
    hist = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    tmp = p.with_suffix(p.suffix + ".tmp")  # temp + replace: never a half-written record (protocol: Runtime state)
    try:
        tmp.write_text(json.dumps(hist + [rec], indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, p)
    finally:
        tmp.unlink(missing_ok=True)


def history(tid, rt_dir=None):
    """The persisted routing history of one task. Malformed content raises ValueError - a record that
    cannot be read admits nothing."""
    p = _rt_dir(rt_dir) / f"{tid}.route.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or any(not isinstance(e, dict) for e in data):
        raise ValueError(f"{p.name}: expected a list of records")
    for e in data:
        if e.get("task") not in (None, tid):
            raise ValueError(f"{p.name}: a record belongs to {e.get('task')}")
    return data


def latest_assessment(tid, rt_dir=None):
    """The newest persisted assessment (schemaVersion 1), or None."""
    for e in reversed(history(tid, rt_dir)):
        if e.get("event") == "assessment" and e.get("schemaVersion") == 1:
            return e
    return None


def env_selected(tool):
    """(model, effort) AGENTFLOW_<TOOL>_ARGS would set when the Task File names none - the same tokens
    run_task.remove_overridden guards, duplicated here because this standalone tool cannot import the
    launcher."""
    args = [a for a in os.environ.get(f"AGENTFLOW_{tool.upper()}_ARGS", "").split() if a]
    model = effort = None
    for i, a in enumerate(args):
        nxt = args[i + 1] if i + 1 < len(args) else ""
        if model is None and a in ("-m", "--model") and nxt:
            model = nxt
        elif model is None and (m := re.match(r"^(?:-m|--model)=(.+)$", a)):
            model = m.group(1)
        elif effort is None and a == "--effort" and nxt:
            effort = nxt
        elif effort is None and a.startswith("--effort="):
            effort = a.split("=", 1)[1]
        elif effort is None and a == "-c" and nxt.startswith("model_reasoning_effort="):
            effort = nxt.split("=", 1)[1]
    return model, effort


def identity_tier(o, model, effort):
    """The effort tier a launch on this option actually reaches. model_by_effort names encode their tier;
    an efforts-style option runs at the effort flag (header line beats machine args); the rest sit at
    their declared 'tier' (or default_effort), else medium."""
    if model:
        for tier, m in (o.get("model_by_effort") or {}).items():
            if m == model:
                return tier
    return effort or o.get("default_effort") or o.get("tier") or "medium"


def identity_problems(required, tool, header_model, header_effort):
    """Why the launch the header+env actually resolve to cannot meet the recorded requirement."""
    required = required or {}
    env_model, env_effort = env_selected(tool)
    model, effort = header_model or env_model, header_effort or env_effort
    name, o = quota_groups.option_for(tool, model)
    if o is None:
        if model:
            return [f"{tool} model '{model}' is not in model-options.json: adequacy cannot be verified"]
        return [f"model-options.json describes no default model for {tool}: name one in the Task File's "
                "Model: line or in the configuration"]
    tier = identity_tier(o, model, effort)
    problems = []
    need = required.get("effort")
    if need and need in EFFORT_ORDER:
        if tier not in EFFORT_ORDER:
            problems.append(f"{tool} would run '{model or 'the default model'}' at an unverifiable effort "
                            f"('{tier}'): the recorded requirement is >= {need}")
        elif EFFORT_ORDER.index(tier) < EFFORT_ORDER.index(need):
            problems.append(f"{tool} would run '{model or 'the default model'}' at effort {tier}: below the "
                            f"recorded requirement >= {need}")
    cap, cx = o.get("max_complexity"), required.get("complexity")
    if cap is not None and cx is not None and float(cx) > float(cap) + 0.5:
        problems.append(f"{name} caps at complexity {cap}; the task was assessed {cx:.2f}")
    return problems


def assessment_problems(t, rt_dir=None):
    """(problems, record): whether the task carries a usable assessment - the record-level gate tick.py
    runs without resolving the launch's env overrides. A `Routing exception:` line admits and is
    reported as a human exception, not as evidence."""
    try:
        text = Path(t["file"]).read_text(encoding="utf-8-sig")
        req_hash = gate.requirements_hash(text)
    except (KeyError, TypeError, OSError) as e:
        return [f"the Task File cannot be read for admission: {e}"], None
    exception = gate.field(gate.header(text), "Routing exception")
    try:
        rec = latest_assessment(t["id"], rt_dir)
    except ValueError as e:
        rec, problems = None, [f"the routing record is unreadable: {e}"]
    else:
        problems = []
        if rec is None:
            problems.append("no recorded routing assessment: run route.py on the task, or write a "
                            "'Routing exception: <reason>' line into its header")
        elif rec.get("requirementsHash") != req_hash:
            problems.append("the recorded assessment is stale: the task contract changed "
                            "(requirementsHash differs); route the task again")
        elif rec.get("status") != "ok":
            detail = rec.get("blocked") or rec.get("error") or ""
            problems.append(f"the recorded assessment is '{rec.get('status')}'"
                            + (f": {detail}" if detail else ""))
    if problems and exception:
        return [], {"source": "human-exception", "reason": exception, "requirementsHash": req_hash,
                    "overrode": problems}
    if problems:
        return problems, None
    return [], {"source": "jev", "requirementsHash": req_hash, "assessedAt": rec.get("at"),
                "jevRequestId": (rec.get("jev") or {}).get("requestId"), "band": rec.get("band"),
                "required": rec.get("required"), "floor": rec.get("floor"), "selected": rec.get("selected")}


def admission(t, tool, rt_dir=None):
    """(problems, evidence): the launch-side gate. assessment_problems plus the resolved-identity check:
    after env/CLI overrides the selected model/effort must still meet the recorded requirement."""
    problems, evidence = assessment_problems(t, rt_dir)
    if problems or not evidence or evidence["source"] != "jev":
        return problems, evidence
    if tool and tool in CLI_TOOLS:
        problems = identity_problems(evidence.get("required"), tool, t.get("model"), t.get("effort"))
        if problems:
            if text_exc := _routing_exception(t):
                return [], {"source": "human-exception", "reason": text_exc,
                            "requirementsHash": evidence["requirementsHash"], "overrode": problems}
            return problems, None
        env_model, env_effort = env_selected(tool)
        model, effort = t.get("model") or env_model, t.get("effort") or env_effort
        _name, o = quota_groups.option_for(tool, model)
        evidence = dict(evidence)
        evidence["admitted"] = {"tool": tool, "model": model, "effort": effort,
                                "tier": identity_tier(o, model, effort),
                                "option": _name}
        sel = evidence.get("selected") or {}
        evidence["deviation"] = bool(sel) and (sel.get("tool"), sel.get("model"), sel.get("effort")) != \
            (tool, model, effort)
    return [], evidence


def _routing_exception(t):
    try:
        return gate.field(gate.header(Path(t["file"]).read_text(encoding="utf-8-sig")), "Routing exception")
    except (KeyError, TypeError, OSError):
        return None


def log_admission(tid, evidence, rt_dir=None):
    """Record one admitted launch: 'admission' for Jev evidence, 'human-exception' when a person
    overrode the gate - the latter is always visible as a human decision, never as Jev evidence."""
    ev = {"event": "admission" if evidence["source"] == "jev" else "human-exception",
          "task": tid, "at": now_iso(), "requirementsHash": evidence.get("requirementsHash"),
          "source": evidence["source"], "admitted": evidence.get("admitted"),
          "deviation": evidence.get("deviation")}
    if evidence["source"] == "human-exception":
        ev["reason"] = evidence.get("reason")
        ev["overrode"] = evidence.get("overrode")
    _log(tid, ev, rt_dir)


def backup_ok(tid, tool, model, effort, rt_dir=None):
    """(ok, reason): may the recorded backup serve this task? Same requirement as the primary - a weaker
    backup is ineligible."""
    try:
        rec = latest_assessment(tid, rt_dir)
    except ValueError as e:
        return False, f"the routing record is unreadable: {e}"
    if rec is None or rec.get("status") != "ok":
        return False, "no ok assessment is recorded for the task"
    problems = identity_problems(rec.get("required"), tool, model, effort)
    return (False, "; ".join(problems)) if problems else (True, "")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("id")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    try:
        sys.exit(route(a.id, a.apply))
    except (NoDecision, gate.TaskError) as e:
        print(f"{a.id}: no recommendation: {e}. Decide by .agentflow/roles/tool-routing.md")
        sys.exit(NO_DECISION)


if __name__ == "__main__":
    main()
