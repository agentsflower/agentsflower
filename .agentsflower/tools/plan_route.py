"""Ask Jev for a planning model without changing the user's current chat or project tasks."""
import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT  # noqa: E402
import route  # noqa: E402


def recommend(goal, config, current_tool=None, current_model=None, asker=route.ask, key=None,
              kind="plan"):
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
    result = {"at": date.today().isoformat(), "goalHash": hashlib.sha256(goal.encode("utf-8")).hexdigest(),
              "goalLength": len(goal), "kind": kind,
              "jevModel": meta.get("model"), "requestId": meta.get("requestId"),
              "usage": meta.get("usage"), "complexity": complexity.get("score"), "confidence": confidence,
              "band": route.band(confidence), "eligibleOptions": sorted(options), "choice": chosen,
              "tool": options[chosen]["tool"], "model": model, "effort": flag, "resolvedEffort": resolved,
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
