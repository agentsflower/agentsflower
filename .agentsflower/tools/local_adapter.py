#!/usr/bin/env python3
"""Local Model Adapter for AgentsFlower.

Enables zero-cost pair programming, task execution, and emergency failover
using locally hosted models (Ollama, LM Studio, LocalAI, vLLM, llama.cpp):
- Auto-probes local ports and endpoints without external Python dependencies
- Discovers coding and reasoning models (DeepSeek-R1, Qwen 2.5 Coder, Llama 3)
- Unified OpenAI / Ollama compatible chat completion interface
"""
import argparse
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
try:
    from paths import FLOW_ROOT, REPO_ROOT
except ImportError:
    FLOW_ROOT = TOOLS_DIR.parent
    REPO_ROOT = FLOW_ROOT.parent

# Default local inference runtime endpoints
DEFAULT_RUNTIMES = [
    {
        "id": "ollama",
        "name": "Ollama Local Runtime",
        "base_url": os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"),
        "probe_path": "/api/tags",
        "chat_path": "/api/chat",
        "type": "ollama",
    },
    {
        "id": "lmstudio",
        "name": "LM Studio (OpenAI-compatible)",
        "base_url": os.environ.get("LMSTUDIO_HOST", "http://127.0.0.1:1234"),
        "probe_path": "/v1/models",
        "chat_path": "/v1/chat/completions",
        "type": "openai",
    },
    {
        "id": "localai",
        "name": "LocalAI / vLLM Server",
        "base_url": os.environ.get("LOCALAI_HOST", "http://127.0.0.1:8000"),
        "probe_path": "/v1/models",
        "chat_path": "/v1/chat/completions",
        "type": "openai",
    },
]

# Preferred coding & reasoning models ranked by autonomous capability
MODEL_PREFERENCES = [
    r"deepseek-r1",
    r"deepseek-coder",
    r"qwen2\.5-coder",
    r"qwen2\.5",
    r"llama-?3\.3",
    r"llama-?3\.2",
    r"llama-?3",
    r"codellama",
    r"starcoder2",
    r"mistral-nemo",
    r"phi-?4",
]


def check_port(host: str, port: int, timeout: float = 0.5) -> bool:
    """Quick socket check before issuing HTTP request."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def _safe_get_json(url: str, timeout: float = 1.0) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgentsFlower/2.17.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    return None


def probe_runtime(runtime_cfg: dict, timeout: float = 1.0) -> dict:
    """Probe a single runtime configuration for reachability and model inventory."""
    base_url = runtime_cfg["base_url"].rstrip("/")
    probe_url = base_url + runtime_cfg["probe_path"]
    r_type = runtime_cfg["type"]

    res = {
        "id": runtime_cfg["id"],
        "name": runtime_cfg["name"],
        "base_url": base_url,
        "type": r_type,
        "online": False,
        "models": [],
        "error": None,
    }

    data = _safe_get_json(probe_url, timeout=timeout)
    if data is None:
        res["error"] = "Connection refused or timed out"
        return res

    res["online"] = True
    models_found = []

    try:
        if r_type == "ollama":
            raw_models = data.get("models", [])
            for m in raw_models:
                m_name = m.get("name", "")
                details = m.get("details", {})
                param_size = details.get("parameter_size", "")
                quant = details.get("quantization_level", "")
                models_found.append({
                    "id": m_name,
                    "name": m_name,
                    "family": details.get("family", ""),
                    "parameter_size": param_size,
                    "quantization": quant,
                    "provider": "ollama",
                })
        elif r_type == "openai":
            raw_data = data.get("data", [])
            for m in raw_data:
                m_id = m.get("id", "")
                models_found.append({
                    "id": m_id,
                    "name": m_id,
                    "provider": runtime_cfg["id"],
                })
    except Exception as e:
        res["error"] = f"Failed to parse model list: {e}"

    res["models"] = models_found
    return res


def probe_all_runtimes(timeout: float = 0.8) -> list[dict]:
    """Probe all configured local runtimes and return their status."""
    results = []
    for cfg in DEFAULT_RUNTIMES:
        results.append(probe_runtime(cfg, timeout=timeout))
    return results


def get_available_models(timeout: float = 0.8) -> list[dict]:
    """Collate all online local models across all reachable runtimes."""
    runtimes = probe_all_runtimes(timeout=timeout)
    all_models = []
    for r in runtimes:
        if r["online"]:
            for m in r["models"]:
                m_copy = dict(m)
                m_copy["runtime_id"] = r["id"]
                m_copy["base_url"] = r["base_url"]
                m_copy["runtime_type"] = r["type"]
                all_models.append(m_copy)
    return all_models


def select_best_coding_model(models: list[dict] = None) -> dict | None:
    """Select the highest-capability local coding model using preference hierarchy."""
    if models is None:
        models = get_available_models()

    if not models:
        return None

    for pattern in MODEL_PREFERENCES:
        regex = re.compile(pattern, re.IGNORECASE)
        for m in models:
            if regex.search(m.get("id", "")):
                return m

    # Fallback to the first available model
    return models[0]


def chat_completion(
    model_info: dict,
    messages: list[dict],
    temperature: float = 0.2,
    timeout: float = 120.0,
) -> dict:
    """Send a chat completion request to the chosen local runtime."""
    r_type = model_info.get("runtime_type", "openai")
    base_url = model_info.get("base_url", "http://127.0.0.1:11434").rstrip("/")
    model_id = model_info.get("id", "")

    if r_type == "ollama":
        url = f"{base_url}/api/chat"
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
    else:
        url = f"{base_url}/v1/chat/completions"
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
        }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "AgentsFlower/2.17.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if r_type == "ollama":
                content = data.get("message", {}).get("content", "")
            else:
                choices = data.get("choices", [])
                content = choices[0].get("message", {}).get("content", "") if choices else ""
            return {"ok": True, "content": content, "raw": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AgentsFlower Local Model Adapter.")
    sub = ap.add_subparsers(dest="command")

    # probe
    p_probe = sub.add_parser("probe", help="Probe local model servers and list available models")
    p_probe.add_argument("--json", action="store_true", help="Output raw JSON")

    # chat
    p_chat = sub.add_parser("chat", help="Send chat prompt to the best available local model")
    p_chat.add_argument("--prompt", required=True, help="Prompt text")
    p_chat.add_argument("--model", help="Explicit model name")

    args = ap.parse_args(argv)

    if args.command == "probe" or not args.command:
        runtimes = probe_all_runtimes()
        best = select_best_coding_model()
        if getattr(args, "json", False):
            print(json.dumps({"runtimes": runtimes, "best_model": best}, indent=2))
            return 0

        print("\n=======================================================")
        print("  [AgentsFlower] Local Model Ecosystem Probe")
        print("=======================================================")
        for r in runtimes:
            status_str = "[ONLINE]" if r["online"] else "[OFFLINE]"
            print(f"  {r['name']} ({r['base_url']}): {status_str}")
            if r["online"]:
                for m in r["models"]:
                    extra = f" ({m.get('parameter_size')})" if m.get("parameter_size") else ""
                    print(f"    - {m['id']}{extra}")
            elif r["error"]:
                print(f"    Notice: {r['error']}")

        print("\n  Recommended Zero-Cost Model:")
        if best:
            print(f"    -> {best['id']} via {best['runtime_id']} ($0 tokens)")
        else:
            print("    -> None detected online (start Ollama or LM Studio to enable)")
        print("=======================================================\n")
        return 0

    if args.command == "chat":
        best = select_best_coding_model()
        if not best and not args.model:
            print("Error: No local model runtime is currently online.")
            return 1
        model_info = {"id": args.model} if args.model else best
        res = chat_completion(model_info, [{"role": "user", "content": args.prompt}])
        if res["ok"]:
            print(res["content"])
            return 0
        else:
            print(f"Error: {res['error']}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
