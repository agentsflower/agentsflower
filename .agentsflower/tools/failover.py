#!/usr/bin/env python3
"""AgentsFlower Adaptive Model Failover Router.

Provides automated, context-preserving failover when CLI or API models hit
token budgets, rate limits (429), or quota exhaustion:
- Tier 1: High-Confidence Cloud (Devin swe-2-high, Claude 3.7 Sonnet)
- Tier 2: Secondary Cloud (Codex GPT-6.1, Gemini 3.8 Flash, Kimi K3)
- Tier 3: Zero-Cost Local Runtimes (Ollama DeepSeek-R1 / Qwen 2.5 Coder, LM Studio)
"""
import argparse
import json
import os
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
try:
    from paths import FLOW_ROOT, REPO_ROOT
except ImportError:
    FLOW_ROOT = TOOLS_DIR.parent
    REPO_ROOT = FLOW_ROOT.parent

import limit_detection
import local_adapter

FAILOVER_TIERS = [
    {
        "tier": 1,
        "name": "High-Confidence Cloud Tier",
        "primary_tool": "devin",
        "default_model": "swe-2-high",
        "candidates": [
            {"tool": "devin", "model": "swe-2-high", "label": "Devin AI swe-2"},
            {"tool": "claude", "model": "claude-3-7-sonnet", "label": "Claude 3.7 Sonnet"},
        ],
        "type": "cloud",
    },
    {
        "tier": 2,
        "name": "Secondary Cloud Tier",
        "primary_tool": "codex",
        "default_model": "gpt-6.1-sol",
        "candidates": [
            {"tool": "codex", "model": "gpt-6.1-sol", "label": "Codex / GPT-6.1"},
            {"tool": "devin", "model": "gemini-3.8-flash", "label": "Devin Gemini 3.8 Flash"},
            {"tool": "devin", "model": "kimi-k3", "label": "Devin Kimi K3"},
        ],
        "type": "cloud",
    },
    {
        "tier": 3,
        "name": "Zero-Cost Local Runtime Tier",
        "primary_tool": "local",
        "default_model": "auto",
        "candidates": [
            {"tool": "local", "model": "deepseek-r1", "label": "Ollama DeepSeek-R1"},
            {"tool": "local", "model": "qwen2.5-coder", "label": "Ollama Qwen 2.5 Coder"},
            {"tool": "local", "model": "lmstudio", "label": "LM Studio Local Server"},
        ],
        "type": "local_zero_cost",
    },
]


def get_failover_status() -> dict:
    """Return full failover hierarchy, active tier, and live local status."""
    local_probe = local_adapter.probe_all_runtimes(timeout=0.6)
    best_local = local_adapter.select_best_coding_model()
    has_local = bool(best_local is not None)

    tiers = []
    for t in FAILOVER_TIERS:
        t_copy = dict(t)
        if t["type"] == "local_zero_cost":
            t_copy["online"] = has_local
            t_copy["best_model"] = best_local["id"] if best_local else "None online"
        else:
            t_copy["online"] = True
        tiers.append(t_copy)

    return {
        "policy": "Tiered Context-Preserving Autonomous Failover",
        "active_tier": 1,
        "tiers": tiers,
        "local_available": has_local,
        "best_local_model": best_local,
    }


def resolve_failover_candidate(
    failed_tool: str,
    failed_model: str = "",
    failure_reason: str = "token_exhaustion",
) -> dict:
    """Determine the next best fallback tool and model given a failure."""
    # Find which tier the failed tool belongs to
    current_tier_num = 1
    found = False
    for t in FAILOVER_TIERS:
        for c in t["candidates"]:
            if c["tool"] == failed_tool and (not failed_model or c["model"] == failed_model):
                current_tier_num = t["tier"]
                found = True
                break
        if found:
            break

    # Look for candidates in subsequent tiers
    for t in FAILOVER_TIERS:
        if t["tier"] > current_tier_num:
            if t["type"] == "local_zero_cost":
                best_local = local_adapter.select_best_coding_model()
                if best_local:
                    return {
                        "tool": "local",
                        "model": best_local["id"],
                        "tier": t["tier"],
                        "runtime": best_local.get("runtime_id", "ollama"),
                        "type": "local_zero_cost",
                        "reason": f"Failover from {failed_tool} due to {failure_reason}",
                    }
            else:
                c = t["candidates"][0]
                return {
                    "tool": c["tool"],
                    "model": c["model"],
                    "tier": t["tier"],
                    "type": t["type"],
                    "reason": f"Failover from {failed_tool} due to {failure_reason}",
                }

    # If all cloud tiers exhausted, try local regardless of tier
    best_local = local_adapter.select_best_coding_model()
    if best_local:
        return {
            "tool": "local",
            "model": best_local["id"],
            "tier": 3,
            "runtime": best_local.get("runtime_id", "ollama"),
            "type": "local_zero_cost",
            "reason": "Emergency fallback to local zero-cost model",
        }

    return {
        "tool": "wait",
        "model": "none",
        "tier": 0,
        "type": "blocked",
        "reason": "All cloud quotas exhausted and no local model runtime online",
    }


def transfer_session_context(
    messages: list[dict],
    from_tool: str,
    to_candidate: dict,
) -> list[dict]:
    """Inject failover continuity notice into conversation history."""
    notice = (
        f"[AgentsFlower Failover Protocol]: Cloud model '{from_tool}' reached quota or limit. "
        f"Session seamlessly migrated to Tier {to_candidate['tier']} ({to_candidate['tool']}: {to_candidate['model']}). "
        f"Full conversation and task contract preserved."
    )
    migrated = list(messages)
    migrated.append({"role": "system", "content": notice})
    return migrated


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AgentsFlower Failover Router.")
    sub = ap.add_subparsers(dest="command")

    # status
    p_status = sub.add_parser("status", help="Print failover hierarchy and local runtime status")
    p_status.add_argument("--json", action="store_true", help="Output JSON format")

    # resolve
    p_res = sub.add_parser("resolve", help="Resolve fallback target for a limited tool")
    p_res.add_argument("--tool", required=True, help="Failed tool name (devin, claude, codex, etc.)")
    p_res.add_argument("--reason", default="token_limit", help="Reason for failure")

    args = ap.parse_args(argv)

    if args.command == "status" or not args.command:
        status = get_failover_status()
        if getattr(args, "json", False):
            print(json.dumps(status, indent=2))
            return 0

        print("\n=======================================================")
        print("  [AgentsFlower] Adaptive Model Failover Architecture")
        print("=======================================================")
        print(f"  Policy: {status['policy']}")
        print(f"  Local Runtimes Available: {'YES' if status['local_available'] else 'NO'}\n")
        for t in status["tiers"]:
            print(f"  Tier {t['tier']}: {t['name']}")
            print(f"    Type: {t['type']} | Online: {t['online']}")
            for c in t["candidates"]:
                print(f"      - {c['label']} ({c['tool']}:{c['model']})")
        print("=======================================================\n")
        return 0

    if args.command == "resolve":
        target = resolve_failover_candidate(args.tool, failure_reason=args.reason)
        print(json.dumps(target, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
