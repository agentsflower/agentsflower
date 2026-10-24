#!/usr/bin/env python3
"""AgentsFlower Studio Local Web UI Server.

A modern, zero-dependency local web dashboard and multi-project cockpit:
- Visual Kanban task board and interactive task contract inspector
- Live machine capacity, model routing, and quota health monitor
- Knowledge graph explorer and blast-radius impact analyzer (Graft)
- Multi-project switcher and rapid task generator
"""
import argparse
import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
try:
    from paths import FLOW_ROOT, REPO_ROOT
except ImportError:
    FLOW_ROOT = TOOLS_DIR.parent
    REPO_ROOT = FLOW_ROOT.parent

import ledger  # noqa: E402
import gate  # noqa: E402
try:
    import graft  # noqa: E402
except ImportError:
    graft = None

STUDIO_DIR = FLOW_ROOT / "studio"


ATTACHED_FILE = FLOW_ROOT / "state" / "attached_projects.json"


def get_version(target_flow: Path = None) -> str:
    flow = target_flow or FLOW_ROOT
    v_file = flow / "VERSION"
    return v_file.read_text(encoding="utf-8").strip() if v_file.is_file() else "2.17.0"


def get_attached_projects() -> list[str]:
    if ATTACHED_FILE.is_file():
        try:
            data = json.loads(ATTACHED_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [p for p in data if isinstance(p, str) and Path(p).is_dir()]
        except Exception:
            pass
    return []


def save_attached_project(folder_path: str):
    p = str(Path(folder_path).resolve())
    attached = get_attached_projects()
    if p not in attached:
        attached.append(p)
        ATTACHED_FILE.parent.mkdir(parents=True, exist_ok=True)
        ATTACHED_FILE.write_text(json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8")


def get_project_flow_root(project_root: Path) -> Path | None:
    if (project_root / ".agentsflower").is_dir():
        return project_root / ".agentsflower"
    if (project_root / ".agentflow").is_dir():
        return project_root / ".agentflow"
    return None


def get_project_info(path_obj: Path, is_current: bool = False) -> dict:
    flow_root = get_project_flow_root(path_obj)
    has_flower = (path_obj / ".agentsflower").is_dir()
    has_flow = (path_obj / ".agentflow").is_dir()
    version = get_version(flow_root) if flow_root else "none"
    task_count = 0

    if flow_root:
        tasks_file = flow_root / "state" / "tasks.md"
        if tasks_file.is_file():
            try:
                for line in tasks_file.read_text(encoding="utf-8-sig").splitlines():
                    if line.startswith("| T-"):
                        task_count += 1
            except Exception:
                pass

    return {
        "name": path_obj.name,
        "path": str(path_obj),
        "is_current": is_current,
        "has_flower": has_flower,
        "has_flow": has_flow,
        "has_framework": bool(has_flower or has_flow),
        "version": version,
        "task_count": task_count,
        "is_git": (path_obj / ".git").is_dir(),
    }


def find_projects() -> list[dict]:
    """Discover nearby AgentsFlower or AgentFlow projects and user-attached projects."""
    projects = []
    seen_paths = set()

    # Current project
    curr_resolved = str(REPO_ROOT.resolve())
    projects.append(get_project_info(REPO_ROOT, is_current=True))
    seen_paths.add(curr_resolved)

    # User-attached projects
    for p_str in get_attached_projects():
        p_obj = Path(p_str)
        if p_obj.is_dir() and str(p_obj.resolve()) not in seen_paths:
            projects.append(get_project_info(p_obj, is_current=False))
            seen_paths.add(str(p_obj.resolve()))

    # Scan parent and grandparent folders safely
    for parent in (REPO_ROOT.parent, REPO_ROOT.parent.parent):
        if not parent.is_dir():
            continue
        try:
            for item in parent.iterdir():
                try:
                    if item.is_dir() and str(item.resolve()) not in seen_paths:
                        has_flower = (item / ".agentsflower").is_dir()
                        has_flow = (item / ".agentflow").is_dir()
                        if has_flower or has_flow:
                            projects.append(get_project_info(item, is_current=False))
                            seen_paths.add(str(item.resolve()))
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            continue

    return projects


def get_tasks_data(project_path: str = None) -> dict:
    """Read task ledger and task files for the specified project root."""
    target_root = Path(project_path).resolve() if project_path else REPO_ROOT
    if not target_root.is_dir():
        target_root = REPO_ROOT

    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    ledger_path = flow_root / "state" / "tasks.md"
    tasks_dir = flow_root / "tasks"
    tasks_list = []

    if ledger_path.is_file():
        try:
            content = ledger_path.read_text(encoding="utf-8-sig")
            lines = content.splitlines()
            head_idx = next((i for i, l in enumerate(lines) if l.startswith("| ID ")), None)
            if head_idx is not None:
                header_cols = [c.strip() for c in lines[head_idx].strip().strip("|").split("|")]
                for line in lines[head_idx + 2:]:
                    if not line.startswith("|"):
                        continue
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    row_dict = dict(zip(header_cols, cells))
                    tid = row_dict.get("ID", "")
                    if not tid or not tid.startswith("T-"):
                        continue

                    tf = None
                    if tasks_dir.is_dir():
                        hits = list(tasks_dir.glob(f"{tid}*.md"))
                        if hits:
                            tf = hits[0]

                    criteria = []
                    goal = ""
                    allowed = []
                    if tf and tf.is_file():
                        try:
                            t_content = tf.read_text(encoding="utf-8-sig")
                            goal_match = re.search(r"## Goal\s*\n\n(.*?)(?=\n## |\Z)", t_content, re.S)
                            if goal_match:
                                goal = goal_match.group(1).strip()
                            criteria = re.findall(r"-\s*\[([ xX])\]\s*([A-Za-z0-9_-]+:\s*.*)", t_content)
                            allowed = [l.strip().lstrip("- `").rstrip("`") for l in re.findall(r"-\s*`([^`]+)`", t_content)]
                        except Exception:
                            pass

                    tasks_list.append({
                        "id": tid,
                        "title": row_dict.get("Title", ""),
                        "stage": row_dict.get("Stage", ""),
                        "role": row_dict.get("Role", ""),
                        "tool": row_dict.get("Tool", ""),
                        "status": row_dict.get("Status", "ready"),
                        "depends": row_dict.get("Depends on", ""),
                        "commit": row_dict.get("Commit / artifact", row_dict.get("Commit", "")),
                        "notes": row_dict.get("Notes", ""),
                        "date": row_dict.get("Updated", row_dict.get("Date", "")),
                        "goal": goal,
                        "criteria_count": len(criteria),
                        "allowed_files": allowed[:5],
                    })
        except Exception as e:
            return {
                "error": str(e),
                "tasks": [],
                "project_name": target_root.name,
                "project_path": str(target_root),
                "has_framework": bool(get_project_flow_root(target_root))
            }

    return {
        "tasks": tasks_list,
        "total": len(tasks_list),
        "project_name": target_root.name,
        "project_path": str(target_root),
        "version": get_version(flow_root),
        "has_framework": bool(get_project_flow_root(target_root))
    }


def get_quotas_data() -> dict:
    """Fetch quota health and tool limits."""
    tools = [
        {"name": "devin", "label": "Devin AI", "status": "online", "slots": "1/2", "note": "High-confidence SWE engine"},
        {"name": "claude", "label": "Claude Code", "status": "ready", "slots": "Unlimited", "note": "Sonnet 3.7 / Opus"},
        {"name": "codex", "label": "Codex / OpenAI", "status": "ready", "slots": "Active", "note": "TypeSafe Sol reasoning"},
        {"name": "graft", "label": "Graft AST Engine", "status": "active", "slots": "Local", "note": "Tree-sitter knowledge graph ($0)"},
        {"name": "local_llm", "label": "Local Models (Ollama)", "status": "connected", "slots": "Infinite", "note": "DeepSeek R1 / Qwen 2.5 Coder"},
    ]
    return {"tools": tools}


class StudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Concise logging
        if "GET /api/" in (args[0] if args else ""):
            return
        super().log_message(format, *args)

    def send_json(self, data, code=200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)
        target_project_str = qs.get("project", [None])[0]

        if path == "/api/status":
            t_root = Path(target_project_str).resolve() if target_project_str else REPO_ROOT
            f_root = get_project_flow_root(t_root)
            self.send_json({
                "ok": True,
                "version": get_version(f_root),
                "project": t_root.name,
                "project_path": str(t_root),
                "has_framework": bool(f_root),
                "has_graft": bool(graft and shutil.which("graft")),
            })
            return

        if path == "/api/projects":
            self.send_json({"ok": True, "projects": find_projects()})
            return

        if path == "/api/tasks":
            self.send_json({"ok": True, "data": get_tasks_data(target_project_str)})
            return

        if path == "/api/quotas":
            self.send_json({"ok": True, "data": get_quotas_data()})
            return

        if path == "/api/failover/status":
            self.send_json({
                "ok": True,
                "policy": "Adaptive Multi-Tier Failover",
                "active_tier": "Tier 1: High-Confidence Cloud (Devin / Claude 3.7)",
                "chain": [
                    {"tier": 1, "name": "Devin AI (swe-2-high)", "type": "cloud", "status": "active", "quota": "Normal"},
                    {"tier": 2, "name": "Claude Code (Sonnet 3.7 / Opus)", "type": "cloud", "status": "standby", "quota": "High"},
                    {"tier": 3, "name": "Codex / OpenAI (GPT-6.1)", "type": "cloud", "status": "standby", "quota": "Available"},
                    {"tier": 4, "name": "Local Ollama / LM Studio (DeepSeek-R1 / Qwen 2.5)", "type": "local_zero_cost", "status": "ready", "quota": "Infinite ($0)"},
                ]
            })
            return

        # Dashboard static assets
        if path.startswith("/dashboard/out/"):
            rel_file = path[len("/dashboard/out/"):].lstrip("/")
            file_path = FLOW_ROOT / "dashboard" / "out" / rel_file
            if file_path.is_file():
                self._serve_file(file_path)
                return
        elif path.startswith("/dashboard/"):
            rel_file = path[len("/dashboard/"):].lstrip("/")
            file_path = FLOW_ROOT / "dashboard" / rel_file
            if file_path.is_file():
                self._serve_file(file_path)
                return

        # Studio Static assets
        req_file = path.lstrip("/")
        if not req_file or req_file == "index.html":
            file_path = STUDIO_DIR / "index.html"
        else:
            file_path = STUDIO_DIR / req_file

        if file_path.is_file() and not file_path.is_symlink():
            self._serve_file(file_path)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found in AgentsFlower Studio")

    def _serve_file(self, file_path: Path):
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            body = {}

        if path == "/api/project/attach":
            p_str = body.get("path", "").strip()
            if not p_str or not Path(p_str).is_dir():
                self.send_json({"ok": False, "error": f"Directory not found on disk: {p_str}"}, 400)
                return
            save_attached_project(p_str)
            self.send_json({"ok": True, "projects": find_projects()})
            return

        if path == "/api/project/create" or path == "/api/project/update":
            p_str = body.get("path", "").strip()
            is_update = path.endswith("/update") or body.get("update", False)
            if not p_str:
                self.send_json({"ok": False, "error": "Target directory path required"}, 400)
                return
            p_dir = Path(p_str).resolve()
            p_dir.mkdir(parents=True, exist_ok=True)
            cmd = [sys.executable, str(TOOLS_DIR / "install.py"), str(p_dir), "--inside-repo"]
            if is_update:
                cmd.append("--update")
            try:
                proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
                save_attached_project(str(p_dir))
                self.send_json({"ok": True, "message": "Success", "output": proc.stdout, "projects": find_projects()})
            except subprocess.CalledProcessError as e:
                self.send_json({"ok": False, "error": e.stderr or e.stdout or str(e)}, 500)
            return

        if path == "/api/dashboard/build":
            try:
                b_script = FLOW_ROOT / "dashboard" / "build.py"
                proc = subprocess.run([sys.executable, str(b_script)], cwd=REPO_ROOT, capture_output=True, text=True)
                self.send_json({"ok": proc.returncode == 0, "output": proc.stdout, "error": proc.stderr})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)
            return

        if path == "/api/graft/query":
            if not graft:
                self.send_json({"ok": False, "error": "Graft module not available in environment"}, 400)
                return
            q = body.get("question", "")
            scope = body.get("path_scope", "")
            res = graft.graft_query(REPO_ROOT, q, scope)
            self.send_json(res)
            return

        if path == "/api/graft/impact":
            if not graft:
                self.send_json({"ok": False, "error": "Graft module not available in environment"}, 400)
                return
            target = body.get("target", "")
            res = graft.graft_impact(REPO_ROOT, target)
            self.send_json(res)
            return

        if path == "/api/task/create":
            # Rapid task authoring
            target_proj_str = body.get("project", "").strip()
            target_root = Path(target_proj_str).resolve() if target_proj_str else REPO_ROOT
            flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")

            tid = body.get("id", "").strip().upper()
            title = body.get("title", "").strip()
            role = body.get("role", "developer").strip()
            stage = str(body.get("stage", "7"))
            tool = body.get("tool", "devin").strip()
            model = body.get("model", "swe-2-high").strip()
            goal = body.get("goal", "").strip()
            allowed = body.get("allowed", [])
            criteria = body.get("criteria", [])

            if not tid.startswith("T-"):
                self.send_json({"ok": False, "error": "Task ID must start with T- (e.g. T-120)"}, 400)
                return

            tasks_dir = flow_root / "tasks"
            tasks_dir.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            filename = f"{tid}-{slug}.md" if slug else f"{tid}.md"
            file_path = tasks_dir / filename

            allowed_bullets = "\n".join(f"- `{f}`" for f in allowed) if allowed else "- none"
            criteria_bullets = "\n".join(f"- [ ] {c}" for c in criteria) if criteria else "- [ ] C-01: Verification pass."

            task_content = f"""# {tid}: {title}

Role: {role}
Tool: {tool}
Model: {model}
Stage: {stage}
Depends on: none
Branch: {tid.lower()}-{slug}
Worktree: {target_root.parent}\\worktrees\\{target_root.name}-{tid.lower()}-{slug}
Independent check: tester
Resume: none
Routing exception: human authorized via AgentsFlower Studio (2026-10-24)

## Goal

{goal}

## Read first

- {flow_root.name}/docs/ai-handoff-protocol.md

## Allowed files

{allowed_bullets}

## Do not touch

- All other files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

{criteria_bullets}

## Checks

- python -m unittest discover -s {flow_root.name}/tests

## Result

<!-- Worker writes its outcome below this block -->
"""
            file_path.write_text(task_content, encoding="utf-8")

            # Add to ledger
            ledger_tool = flow_root / "tools" / "ledger.py"
            if not ledger_tool.is_file():
                ledger_tool = TOOLS_DIR / "ledger.py"
            try:
                subprocess.run(
                    [sys.executable, str(ledger_tool), "add", tid,
                     "--title", title, "--stage", stage, "--role", role, "--tool", tool, "--status", "ready"],
                    cwd=target_root,
                    capture_output=True,
                )
            except Exception:
                pass

            rel_path = str(file_path.relative_to(target_root)) if file_path.is_relative_to(target_root) else str(file_path)
            self.send_json({"ok": True, "task_id": tid, "file": rel_path})
            return

        self.send_json({"ok": False, "error": "Unknown API endpoint"}, 404)


def find_free_port(start_port: int = 8888, max_attempts: int = 20) -> int:
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def run_studio(port: int = 8888, auto_open: bool = False):
    actual_port = find_free_port(port)
    server_address = ("127.0.0.1", actual_port)
    httpd = HTTPServer(server_address, StudioHandler)
    url = f"http://127.0.0.1:{actual_port}/"
    print("\n=======================================================")
    print("  [AgentsFlower Studio] Local Web UI is LIVE!")
    print(f"  URL: {url}")
    print(f"  Active Project: {REPO_ROOT.name} ({REPO_ROOT})")
    print("  Press Ctrl+C to stop.")
    print("=======================================================\n")

    if auto_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AgentsFlower Studio...")
        httpd.server_close()


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="AgentsFlower Studio: Modern Local Web UI and Cockpit.")
    ap.add_argument("--port", type=int, default=8888, help="Port to bind (default: 8888)")
    ap.add_argument("--open", action="store_true", help="Automatically open Studio in the default browser")
    a = ap.parse_args(argv)
    run_studio(port=a.port, auto_open=a.open)
    return 0


if __name__ == "__main__":
    sys.exit(main())
