"""Preview fair worker allocation across installed AgentFlow projects.

This is a shadow scheduler: it reads ready tasks and shared machine leases but
does not grant slots or launch workers. The existing project conductors remain
the only actors until the allocation policy has been verified in real projects.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine_capacity  # noqa: E402


def ready_tasks(project, runner=subprocess.run):
    tick = project / ".agentflow" / "tools" / "tick.py"
    if not tick.is_file():
        return [], "tick.py is missing"
    env = dict(os.environ, AGENTFLOW_SHARED_DISPATCHER="off")
    try:
        result = runner([sys.executable, str(tick), "run", "--dry-run", "--json"], cwd=project,
                        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        if result.returncode:
            return [], f"tick.py exited {result.returncode}: {result.stderr.strip()[-300:]}"
        report = json.loads(result.stdout)
        return [(item["task"], item["detail"]) for item in report.get("would", [])
                if item.get("action") == "launch"], None
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as error:
        return [], f"tick.py snapshot failed: {type(error).__name__}"


def fair_order(tasks, last_served=None):
    """Interleave projects for each tool, rotating the first project if known."""
    groups = defaultdict(lambda: defaultdict(deque))
    for task in tasks:
        groups[task["tool"]][task["project"]].append(task)
    ordered = []
    for tool in sorted(groups):
        by_project = groups[tool]
        projects = sorted(by_project)
        previous = (last_served or {}).get(tool)
        if previous in projects:
            pivot = projects.index(previous) + 1
            projects = projects[pivot:] + projects[:pivot]
        while any(by_project.values()):
            for project in projects:
                if by_project[project]:
                    ordered.append(by_project[project].popleft())
    return ordered


def allocate(tasks, state, capacities, project_caps, last_served=None):
    """Return a simulation respecting active leases and configured tool/project caps."""
    leases = state.get("leases", [])
    occupied = defaultdict(int)
    per_project = defaultdict(int)
    for lease in leases:
        occupied[lease["tool"]] += 1
        per_project[(lease["tool"], lease["project"])] += 1
    active_caps = defaultdict(list)
    for lease in leases:
        if lease.get("cap"):
            active_caps[lease["tool"]].append(lease["cap"])
    selected, waits = [], []
    for task in fair_order(tasks, last_served):
        tool, project = task["tool"], task["project"]
        maximum, local = capacities[tool], project_caps[(tool, project)]
        effective = min([value for value in [maximum, local, *active_caps[tool]] if value], default=0)
        if state.get("limits", {}).get(tool, 0) > time.time():
            waits.append({**task, "reason": "tool temporarily limited"})
        elif effective and occupied[tool] >= effective:
            waits.append({**task, "reason": "machine slots full"})
        else:
            selected.append(task)
            occupied[tool] += 1
            per_project[(tool, project)] += 1
    return selected, waits


def plan(projects=None, snapshot=ready_tasks):
    roots = [Path(p).resolve() for p in (projects if projects is not None else machine_capacity.known_projects())]
    tasks, errors = [], {}
    for project in roots:
        ready, error = snapshot(project)
        if error:
            errors[str(project)] = error
        for tid, tool in ready:
            if tool in machine_capacity.TOOLS:
                tasks.append({"project": str(project), "task": tid, "tool": tool})
    tools = {task["tool"] for task in tasks}
    capacities = {tool: machine_capacity.capacity(tool) for tool in tools}
    local = {(tool, str(project)): machine_capacity.capacity(tool, project)
             for tool in tools for project in roots}
    with machine_capacity._locked() as state:
        machine_capacity._clean(state)
        selected, waits = allocate(tasks, state, capacities, local,
                                   state.get("dispatch", {}).get("last_served"))
    return {"mode": "shadow", "selected": selected, "waits": waits, "errors": errors,
            "ready": len(tasks), "launches": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--project", action="append", help="restrict snapshot to these projects (repeatable)")
    args = parser.parse_args()
    print(json.dumps(plan(args.project), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
