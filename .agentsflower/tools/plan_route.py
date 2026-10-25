"""Ask Jev for a planning model without changing the user's current chat or project tasks."""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT  # noqa: E402
import route  # noqa: E402

EFFORT_OUTPUT_TOKENS = {
    "low": 1000,
    "medium": 4000,
    "high": 12000,
    "xhigh": 18000,
    "max": 24000,
    "ultra": 24000,
}

BASE_PROMPT_TOKENS = 500
DEFAULT_FILE_CONTEXT_TOKENS = 1200
MAX_FILE_CONTEXT_TOKENS = 16000

MODEL_PRICING_USD_PER_1M = {
    "swe-2": 0.0,
    "swe-2-low": 0.0,
    "swe-2-medium": 0.0,
    "swe-2-high": 0.0,
    "swe-2-max": 0.0,
    "devin-swe-2": 0.0,
    "adaptive": 0.0,
    "devin-adaptive": 0.0,
    "local-ollama": 0.0,
    "ollama": 0.0,
    "qwen2.5-coder": 0.0,
    "deepseek-r1": 0.0,
    "llama3.3": 0.0,
    "claude-opus-5.5": 15.0,
    "devin-claude-opus-5.5": 15.0,
    "claude-opus-5-5-low": 15.0,
    "claude-opus-5-5-medium": 15.0,
    "claude-opus-5-5-high": 15.0,
    "claude-opus-5-5-xhigh": 15.0,
    "claude-opus-5-5-max": 15.0,
    "claude-opus-4-6-thinking": 15.0,
    "agy-claude-opus-4.6-thinking": 15.0,
    "opus": 15.0,
    "claude-sonnet-5.5": 3.0,
    "devin-claude-sonnet-5.5": 3.0,
    "claude-sonnet-5-5-low": 3.0,
    "claude-sonnet-5-5-medium": 3.0,
    "claude-sonnet-5-5-high": 3.0,
    "claude-sonnet-5-5-xhigh": 3.0,
    "claude-sonnet-5-5-max": 3.0,
    "claude-sonnet-4-6": 3.0,
    "agy-claude-sonnet-4.6": 3.0,
    "sonnet": 3.0,
    "gemini-4-argon-low": 2.5,
    "gemini-4-argon-medium": 2.5,
    "gemini-4-argon-high": 2.5,
    "devin-gemini-4-argon": 2.5,
    "gemini-3.1-pro-low": 1.25,
    "gemini-3.1-pro-high": 1.25,
    "agy-gemini-3.1-pro": 1.25,
    "gemini-3.8-flash-low": 0.35,
    "gemini-3.8-flash-medium": 0.35,
    "gemini-3.8-flash-high": 0.35,
    "gemini-3-8-flash-low": 0.35,
    "gemini-3-8-flash-medium": 0.35,
    "gemini-3-8-flash-high": 0.35,
    "devin-gemini-3.8-flash": 0.35,
    "agy-gemini-3.8-flash": 0.35,
    "agy": 0.35,
    "gpt-6-astra": 10.0,
    "gpt-6-astra-low": 10.0,
    "gpt-6-astra-medium": 10.0,
    "gpt-6-astra-high": 10.0,
    "gpt-6-astra-xhigh": 10.0,
    "gpt-6-astra-max": 10.0,
    "devin-gpt-6-astra": 10.0,
    "codex-gpt-6-astra": 10.0,
    "gpt-6.1-sol": 2.5,
    "gpt-6-1-sol-low": 2.5,
    "gpt-6-1-sol-medium": 2.5,
    "gpt-6-1-sol-high": 2.5,
    "gpt-6-1-sol-xhigh": 2.5,
    "gpt-6-1-sol-max": 2.5,
    "devin-gpt-6.1-sol": 2.5,
    "codex-gpt-6.1-sol": 2.5,
    "gpt-6-sol-low": 2.5,
    "gpt-6-sol-medium": 2.5,
    "gpt-6-sol-high": 2.5,
    "gpt-6-sol-xhigh": 2.5,
    "gpt-6-sol-max": 2.5,
    "devin-gpt-6-sol": 2.5,
    "gpt-5-5-high": 5.0,
    "gpt-5.5": 5.0,
    "gpt-oss-120b-medium": 0.5,
    "agy-gpt-oss-120b": 0.5,
    "deepseek-v4-pro-high": 1.0,
    "deepseek-v4-pro-max": 1.0,
    "devin-deepseek-v4-pro": 1.0,
    "kimi-k3-low": 1.0,
    "kimi-k3-medium": 1.0,
    "kimi-k3-high": 1.0,
    "kimi-k3-max": 1.0,
    "devin-kimi-k3": 1.0,
}


def _parse_pricing_entry(raw_pricing) -> dict | None:
    if isinstance(raw_pricing, (int, float)) and not isinstance(raw_pricing, bool):
        rate = max(0.0, float(raw_pricing))
        return {
            "rate_per_1m": rate,
            "input_per_1m": rate,
            "output_per_1m": rate,
            "free": rate == 0.0,
        }
    if isinstance(raw_pricing, dict):
        if "input_per_1m" in raw_pricing or "output_per_1m" in raw_pricing:
            in_rate = max(0.0, float(raw_pricing.get("input_per_1m", raw_pricing.get("rate_per_1m", 0.0))))
            out_rate = max(0.0, float(raw_pricing.get("output_per_1m", in_rate)))
            rate = max(0.0, float(raw_pricing.get("rate_per_1m", in_rate)))
            return {
                "rate_per_1m": rate,
                "input_per_1m": in_rate,
                "output_per_1m": out_rate,
                "free": in_rate == 0.0 and out_rate == 0.0,
            }
        for k in ("rate_per_1m", "cost_per_1m", "usd_per_1m", "rate"):
            if k in raw_pricing:
                rate = max(0.0, float(raw_pricing[k]))
                return {
                    "rate_per_1m": rate,
                    "input_per_1m": rate,
                    "output_per_1m": rate,
                    "free": rate == 0.0,
                }
    if isinstance(raw_pricing, str) and raw_pricing.strip():
        low = raw_pricing.strip().lower()
        if "free" in low or "$0" in low or "zero-token" in low:
            return {"rate_per_1m": 0.0, "input_per_1m": 0.0, "output_per_1m": 0.0, "free": True}
        m_in = re.search(r"\$([0-9]+(?:\.[0-9]+)?)\s*/\s*1m\s*input", low)
        m_out = re.search(r"\$([0-9]+(?:\.[0-9]+)?)\s*/\s*1m\s*output", low)
        if m_in or m_out:
            in_rate = float(m_in.group(1)) if m_in else float(m_out.group(1))
            out_rate = float(m_out.group(1)) if m_out else in_rate
            return {
                "rate_per_1m": in_rate,
                "input_per_1m": in_rate,
                "output_per_1m": out_rate,
                "free": in_rate == 0.0 and out_rate == 0.0,
            }
        m_flat = re.search(r"\$([0-9]+(?:\.[0-9]+)?)", low)
        if m_flat:
            rate = float(m_flat.group(1))
            return {
                "rate_per_1m": rate,
                "input_per_1m": rate,
                "output_per_1m": rate,
                "free": rate == 0.0,
            }
    return None


def lookup_model_pricing(
    model: str | None,
    tool: str | None = None,
    config: dict | None = None,
    flow_root: Path | None = None,
    catalog_pricing: str = "",
) -> dict:
    """Resolve per-1M token pricing in USD from model-options.json or catalog rates."""
    if catalog_pricing:
        parsed = _parse_pricing_entry(catalog_pricing)
        if parsed is not None:
            return parsed

    cfg = config
    if cfg is None:
        cfg_path = (flow_root or FLOW_ROOT) / "docs" / "model-options.json"
        if cfg_path.is_file():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError):
                cfg = {}

    m_key = (model or "").strip().lower()
    t_key = (tool or "").strip().lower()

    if isinstance(cfg, dict):
        top_pricing = cfg.get("pricing")
        if isinstance(top_pricing, dict):
            for candidate in (m_key, t_key):
                if candidate and candidate in top_pricing:
                    parsed = _parse_pricing_entry(top_pricing[candidate])
                    if parsed is not None:
                        return parsed
        for opt_name, opt in (cfg.get("options") or {}).items():
            if not isinstance(opt, dict):
                continue
            mbe = opt.get("model_by_effort")
            opt_models = [str(v).lower() for v in mbe.values()] if isinstance(mbe, dict) else []
            if opt.get("model"):
                opt_models.append(str(opt["model"]).lower())
            if m_key and (m_key == opt_name.lower() or m_key in opt_models):
                for field in ("pricing", "rate_per_1m", "cost_per_1m"):
                    if field in opt:
                        parsed = _parse_pricing_entry(opt[field])
                        if parsed is not None:
                            return parsed

    if t_key == "ollama" or "ollama" in m_key or "local" in m_key or "free" in m_key:
        return {"rate_per_1m": 0.0, "input_per_1m": 0.0, "output_per_1m": 0.0, "free": True}

    if m_key in MODEL_PRICING_USD_PER_1M:
        rate = MODEL_PRICING_USD_PER_1M[m_key]
        return {"rate_per_1m": rate, "input_per_1m": rate, "output_per_1m": rate, "free": rate == 0.0}

    if "swe-2" in m_key or m_key in ("swe", "adaptive"):
        return {"rate_per_1m": 0.0, "input_per_1m": 0.0, "output_per_1m": 0.0, "free": True}
    if "opus" in m_key:
        return {"rate_per_1m": 15.0, "input_per_1m": 15.0, "output_per_1m": 15.0, "free": False}
    if "sonnet" in m_key:
        return {"rate_per_1m": 3.0, "input_per_1m": 3.0, "output_per_1m": 3.0, "free": False}
    if "argon" in m_key:
        return {"rate_per_1m": 2.5, "input_per_1m": 2.5, "output_per_1m": 2.5, "free": False}
    if "gemini-3.1-pro" in m_key or "gemini-3-1-pro" in m_key:
        return {"rate_per_1m": 1.25, "input_per_1m": 1.25, "output_per_1m": 1.25, "free": False}
    if "flash" in m_key:
        return {"rate_per_1m": 0.35, "input_per_1m": 0.35, "output_per_1m": 0.35, "free": False}
    if "astra" in m_key:
        return {"rate_per_1m": 10.0, "input_per_1m": 10.0, "output_per_1m": 10.0, "free": False}
    if "gpt-5-5" in m_key or "gpt-5.5" in m_key:
        return {"rate_per_1m": 5.0, "input_per_1m": 5.0, "output_per_1m": 5.0, "free": False}
    if "sol" in m_key:
        return {"rate_per_1m": 2.5, "input_per_1m": 2.5, "output_per_1m": 2.5, "free": False}
    if "gpt-oss" in m_key:
        return {"rate_per_1m": 0.5, "input_per_1m": 0.5, "output_per_1m": 0.5, "free": False}
    if "deepseek-v4" in m_key or "kimi-k3" in m_key:
        return {"rate_per_1m": 1.0, "input_per_1m": 1.0, "output_per_1m": 1.0, "free": False}
    if t_key == "devin" and not m_key:
        return {"rate_per_1m": 0.0, "input_per_1m": 0.0, "output_per_1m": 0.0, "free": True}
    return {"rate_per_1m": 2.5, "input_per_1m": 2.5, "output_per_1m": 2.5, "free": False}


def estimate_output_tokens(effort: str | None = None, complexity=None) -> int:
    """Derive planned_output_tokens from Jev complexity / effort rating (low: 1K, medium: 4K, high: 12K, max: 24K)."""
    if isinstance(effort, str) and effort.strip():
        eff = effort.strip().lower()
        if eff in EFFORT_OUTPUT_TOKENS:
            return EFFORT_OUTPUT_TOKENS[eff]
    if isinstance(complexity, (int, float)) and not isinstance(complexity, bool):
        score = float(complexity)
        if score <= 0.4:
            return 1000
        if score <= 1.1:
            return 4000
        if score < 1.8:
            return 12000
        return 24000
    if isinstance(complexity, str) and complexity.strip():
        cx = complexity.strip().lower()
        if cx in ("low", "small", "trivial"):
            return 1000
        if cx in ("medium", "standard", "moderate"):
            return 4000
        if cx in ("high", "hard", "escalation"):
            return 12000
        if cx in ("max", "xhigh", "ultra", "extreme"):
            return 24000
    return 4000


def estimate_input_tokens(
    prompt_text: str = "",
    blast_files: list[str] | None = None,
    root: Path | None = None,
) -> int:
    """Calculate planned_input_tokens from prompt size + estimated context from AST blast radius files."""
    prompt_chars = len(prompt_text or "")
    prompt_tokens = BASE_PROMPT_TOKENS + ((prompt_chars + 3) // 4 if prompt_chars > 0 else 0)

    context_tokens = 0
    seen: set[str] = set()
    base_root = Path(root).resolve() if root is not None else None
    for raw_f in blast_files or ():
        if not raw_f:
            continue
        rel = str(raw_f).replace("\\", "/").removeprefix("./").lstrip("/")
        if not rel or rel in seen:
            continue
        seen.add(rel)
        file_tokens = DEFAULT_FILE_CONTEXT_TOKENS
        if base_root is not None:
            try:
                candidate = (base_root / rel).resolve()
                if (candidate == base_root or base_root in candidate.parents) and candidate.is_file():
                    sz = candidate.stat().st_size
                    file_tokens = min(max(250, (sz + 3) // 4), MAX_FILE_CONTEXT_TOKENS)
            except OSError:
                pass
        context_tokens += file_tokens

    return int(prompt_tokens + context_tokens)


def estimate_task_budget(
    prompt_text: str = "",
    blast_files: list[str] | None = None,
    effort: str | None = None,
    complexity=None,
    model: str | None = None,
    tool: str | None = None,
    config: dict | None = None,
    root: Path | None = None,
    flow_root: Path | None = None,
    catalog_pricing: str = "",
) -> dict:
    """Compute Plan Model token and USD cost estimates for a task."""
    planned_input = estimate_input_tokens(prompt_text=prompt_text, blast_files=blast_files, root=root)
    planned_output = estimate_output_tokens(effort=effort, complexity=complexity)
    planned_total = planned_input + planned_output
    pricing = lookup_model_pricing(
        model=model,
        tool=tool,
        config=config,
        flow_root=flow_root,
        catalog_pricing=catalog_pricing,
    )
    cost_usd = round(
        (planned_input * pricing["input_per_1m"] + planned_output * pricing["output_per_1m"]) / 1_000_000,
        6,
    )
    return {
        "planned_input_tokens": planned_input,
        "planned_output_tokens": planned_output,
        "planned_tokens": planned_total,
        "planned_cost_usd": cost_usd,
        "rate_per_1m": pricing["rate_per_1m"],
        "input_per_1m": pricing["input_per_1m"],
        "output_per_1m": pricing["output_per_1m"],
        "free": pricing["free"],
    }


def recommend(goal, config, current_tool=None, current_model=None, asker=route.ask, key=None,
              kind="plan", blast_files=None, root=None):
    options, _excluded = route.eligibility(config.get("options", {}), "orchestrator", None,
                                           date.today().isoformat())
    if not options:
        raise route.NoDecision("no configured CLI option is currently usable for planning")
    state = {"planning_date": date.today().isoformat(),
             "planning": {"goal": route.clip(goal, 2500), "kind": kind}}
    policy = config.get("policy", "") + " Choose a model capable of planning this goal; the current chat is only the interface."
    qs = route.questions(options, policy, config.get("recommended"))
    if kind != "plan":
        qs["effort"]["instructions"]["note"] += \
            f" This is a {kind} decision: judge the effort the decision itself needs, not the task's."
    answers, meta = asker(state, qs, key or route.api_key(),
                          config.get("jev_model", route.JEV_MODEL))
    option_answer, effort_answer, complexity = (answers["option"], answers.get("effort", {}),
                                                 answers.get("complexity", {}))
    effort = effort_answer.get("choice")
    probabilities = option_answer.get("probabilities", {})
    required = {"effort": effort, "complexity": complexity.get("score")}
    candidates = {n: o for n, o in options.items() if route.adequate_reason(o, required) is None}
    if not candidates:
        raise route.NoDecision("no usable option can meet the assessed planning requirement")
    order = route.admission_order(candidates, config, probabilities, required.get("effort"))
    chosen = order[0]
    model, flag, resolved = route.resolve_requirement(options[chosen], effort)
    backup_name = next((n for n in order[1:] if options[n]["tool"] != options[chosen]["tool"]), None)
    backup = options.get(backup_name) if backup_name else None
    backup_model, backup_flag, _ = (route.resolve_requirement(backup, effort)
                                    if backup else (None, None, None))
    confidence = min(float(option_answer.get("confidence", 0)),
                     float(effort_answer.get("confidence", 0)) if route.supported_efforts(options[chosen]) else 1)
    budget = estimate_task_budget(
        prompt_text=goal,
        blast_files=blast_files,
        effort=resolved or flag or effort,
        complexity=complexity.get("score"),
        model=model or chosen,
        tool=options[chosen]["tool"],
        config=config,
        root=root,
    )
    result = {"at": date.today().isoformat(), "goalHash": hashlib.sha256(goal.encode("utf-8")).hexdigest(),
              "goalLength": len(goal), "kind": kind,
              "jevModel": meta.get("model"), "requestId": meta.get("requestId"),
              "usage": meta.get("usage"), "complexity": complexity.get("score"), "confidence": confidence,
              "band": route.band(confidence), "eligibleOptions": sorted(options), "choice": chosen,
              "tool": options[chosen]["tool"], "model": model, "effort": flag, "resolvedEffort": resolved,
              "planned_input_tokens": budget["planned_input_tokens"],
              "planned_output_tokens": budget["planned_output_tokens"],
              "planned_tokens": budget["planned_tokens"],
              "planned_cost_usd": budget["planned_cost_usd"],
              "backupChoice": backup_name, "backupProbability": probabilities.get(backup_name),
              "backupTool": backup["tool"] if backup else None, "backupModel": backup_model,
              "backupEffort": backup_flag,
              "currentTool": current_tool, "currentModel": current_model,
              "matchesCurrent": current_tool == options[chosen]["tool"] and current_model == model
              if current_tool and current_model else None}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("goal", help="brief description of the planning goal")
    parser.add_argument("--current-tool", choices=("claude", "codex", "devin", "agy"))
    parser.add_argument("--current-model")
    parser.add_argument("--kind", default="plan",
                        help="what kind of decision this recommendation feeds (default: plan)")
    args = parser.parse_args()
    config_path = FLOW_ROOT / "docs" / "model-options.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        result = recommend(args.goal, config, args.current_tool, args.current_model, kind=args.kind)
    except (OSError, ValueError, route.NoDecision) as error:
        print(f"no planning recommendation: {error}")
        return route.NO_DECISION
    runtime = FLOW_ROOT / "tasks" / ".runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    with (runtime / "planning.route.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(f"planning primary: {result['tool']} / {result['model'] or 'default'}"
          + (f", effort={result['effort']}" if result["effort"] else ""))
    if result["backupTool"]:
        print(f"planning backup: {result['backupTool']} / {result['backupModel'] or 'default'}")
    print(f"Jev confidence: {result['confidence']:.2f} ({result['band']}); request {result['requestId'] or '-'}")
    if result["matchesCurrent"] is not None:
        print("current chat model matches" if result["matchesCurrent"] else "current chat model differs; switch manually if appropriate")
    return route.OK if result["band"] == "high" else (route.MEDIUM if result["band"] == "medium" else route.NO_DECISION)


if __name__ == "__main__":
    sys.exit(main())
