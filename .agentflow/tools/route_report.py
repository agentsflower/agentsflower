"""Compare Jev recommendations with task outcomes without changing project state."""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT  # noqa: E402
import gate  # noqa: E402
import machine_capacity  # noqa: E402


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default


def complexity_band(value):
    if value is None:
        return "unknown"
    return "small" if value < 0.5 else "moderate" if value < 1.5 else "hard"


def attempt_seconds(attempts):
    total = 0.0
    for attempt in attempts:
        try:
            start = datetime.fromisoformat(attempt["startedAt"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(attempt["finishedAt"].replace("Z", "+00:00"))
            total += max(0, (end - start).total_seconds())
        except (KeyError, TypeError, ValueError, AttributeError):
            return None
    return round(total, 1) if attempts else None


def summarize(tid, row, history, attempts, verdict=None):
    recommendations = [entry for entry in history if isinstance(entry, dict) and entry.get("jevChoice")]
    if not recommendations:
        return None
    selected = next((entry for entry in reversed(recommendations) if entry.get("applied")), recommendations[-1])
    actual_tool = attempts[-1].get("tool") if attempts else None
    primary, backup = selected.get("tool"), selected.get("backupTool")
    if actual_tool == primary:
        actual_source, actual_model = "primary", selected.get("model")
    elif actual_tool == backup:
        actual_source, actual_model = "backup", selected.get("backupModel")
    elif actual_tool:
        actual_source, actual_model = "other", None
    else:
        actual_source, actual_model = "not-started", None
    done = row.get("Status") == "done"
    passed = done and (row.get("Role") != "tester" or verdict == "pass")
    first_pass = passed and len(attempts) == 1 and attempts[0].get("status") == "exited" and (
        attempts[0].get("exitCode") in (0, None))
    return {"task": tid, "role": row.get("Role"), "status": row.get("Status"),
            "complexity": selected.get("complexity"), "complexityBand": complexity_band(selected.get("complexity")),
            "confidence": selected.get("confidence"), "primaryTool": primary, "primaryModel": selected.get("model"),
            "backupTool": backup, "backupModel": selected.get("backupModel"),
            "eligibleOptions": selected.get("eligibleOptions"), "actualTool": actual_tool,
            "actualModel": actual_model, "actualSource": actual_source, "attempts": len(attempts),
            "attemptWallSeconds": attempt_seconds(attempts), "acceptedPass": passed, "firstAttemptPass": first_pass,
            "routeRequestId": selected.get("requestId")}


def aggregate(tasks):
    groups = defaultdict(lambda: {"tasks": 0, "acceptedPass": 0, "firstAttemptPass": 0, "backupUsed": 0})
    for item in tasks:
        key = (item["role"] or "unknown", item["complexityBand"], item["primaryModel"] or "unknown")
        group = groups[key]
        group["tasks"] += 1
        group["acceptedPass"] += int(item["acceptedPass"])
        group["firstAttemptPass"] += int(item["firstAttemptPass"])
        group["backupUsed"] += int(item["actualSource"] == "backup")
    return {"tasks": tasks, "groups": [{"role": role, "complexityBand": band, "primaryModel": model, **counts}
                                      for (role, band, model), counts in sorted(groups.items())],
            "note": "Counts are descriptive; compare similar tasks and review failures before changing routing policy. "
                    "Worker token use and cost are unavailable unless a CLI reports them separately."}


def report(rows=None, runtime=None):
    rows = gate.ledger_rows() if rows is None else rows
    runtime = FLOW_ROOT / "tasks" / ".runtime" if runtime is None else Path(runtime)
    tasks = []
    for tid, row in rows.items():
        history = read_json(runtime / f"{tid}.route.json", [])
        history = history if isinstance(history, list) else []
        record = read_json(runtime / f"{tid}.json", {})
        attempts = record.get("attempts", []) if isinstance(record, dict) else []
        attempts = attempts if isinstance(attempts, list) else []
        try:
            task = gate.parse(tid)
            verdict = gate.result_field(task, "Verdict") if row.get("Role") == "tester" else None
        except (gate.TaskError, OSError, ValueError):
            verdict = None
        if item := summarize(tid, row, history, attempts, verdict):
            tasks.append(item)
    return aggregate(tasks)


def report_all(projects=None, runner=subprocess.run):
    roots = projects if projects is not None else machine_capacity.known_projects()
    tasks, errors = [], {}
    for root in roots:
        project = Path(root).resolve()
        script = project / ".agentflow" / "tools" / "route_report.py"
        if not script.is_file():
            errors[str(project)] = "route_report.py is not installed"
            continue
        try:
            result = runner([sys.executable, str(script), "--json"], cwd=project, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=30)
            if result.returncode:
                errors[str(project)] = f"report exited {result.returncode}"
                continue
            for item in json.loads(result.stdout)["tasks"]:
                tasks.append({**item, "project": str(project)})
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as error:
            errors[str(project)] = type(error).__name__
    return {**aggregate(tasks), "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--all-projects", action="store_true", help="combine installed projects using this report version")
    args = parser.parse_args()
    result = report_all() if args.all_projects else report()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Routed tasks: {len(result['tasks'])}")
        for group in result["groups"]:
            print(f"{group['role']} / {group['complexityBand']} / {group['primaryModel']}: "
                  f"{group['acceptedPass']}/{group['tasks']} accepted pass, "
                  f"{group['firstAttemptPass']} first-attempt pass, {group['backupUsed']} used backup")
        print(result["note"])


if __name__ == "__main__":
    main()
