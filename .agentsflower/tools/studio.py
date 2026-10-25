#!/usr/bin/env python3
"""AgentsFlower Studio Local Web UI Server.

A modern, zero-dependency local web dashboard and multi-project cockpit:
- Visual Kanban task board and interactive task contract inspector
- Live machine capacity, model routing, and quota health monitor
- Knowledge graph explorer and blast-radius impact analyzer (Graft)
- Multi-project switcher and rapid task generator
"""
import argparse
import ast
from datetime import datetime, timezone
import json
import mimetypes
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
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
import machine_capacity  # noqa: E402
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


def _norm(p: Path) -> str:
    return os.path.normcase(str(p.resolve()))


def resolve_known_project(project_str: str | None) -> Path | None:
    """Resolve a `project` query/body param to a directory the Studio may serve.

    An empty param means the current repository. Any other path must resolve to a
    project already known to the cockpit (current, attached, or discovered), so
    file endpoints can never be pointed at arbitrary directories on disk.
    """
    if not project_str or not str(project_str).strip():
        return REPO_ROOT
    try:
        target = Path(project_str).resolve()
    except (OSError, ValueError):
        return None
    if not target.is_dir():
        return None
    t_norm = _norm(target)
    for p in find_projects():
        try:
            if _norm(Path(p["path"])) == t_norm:
                return target
        except (OSError, ValueError, KeyError):
            continue
    return None


def safe_under(root: Path, rel: str) -> Path | None:
    """Join `rel` under `root` and refuse anything that escapes the root.

    Rejects absolute paths, `..` traversal, NUL bytes, and symlinked targets
    outside `root` (resolve() follows links before the boundary check).
    """
    if rel is None or "\x00" in rel:
        return None
    try:
        resolved = (root / rel).resolve()
    except (OSError, ValueError):
        return None
    if resolved != root.resolve() and root.resolve() not in resolved.parents:
        return None
    return resolved


MAX_FILE_READ = 256 * 1024


def get_project_tree(root: Path, rel: str) -> dict:
    """List one directory of a known project for the explorer file tree."""
    target = safe_under(root, rel)
    if target is None or not target.is_dir():
        return {"ok": False, "error": "path outside project or not a directory"}
    entries = []
    truncated = False
    try:
        children = sorted(target.iterdir(), key=lambda c: (not c.is_dir(), c.name.lower()))
    except (PermissionError, OSError) as e:
        return {"ok": False, "error": str(e)}
    for child in children:
        if child.name == ".git":
            continue
        if len(entries) >= 1000:
            truncated = True
            break
        try:
            is_dir = child.is_dir()
            entries.append({
                "name": child.name,
                "path": child.relative_to(root).as_posix(),
                "type": "dir" if is_dir else "file",
                "size": 0 if is_dir else child.stat().st_size,
            })
        except (PermissionError, OSError):
            continue
    return {
        "ok": True,
        "project": str(root),
        "path": rel,
        "entries": entries,
        "truncated": truncated,
    }


def read_project_file(root: Path, rel: str) -> dict:
    """Read a UTF-8 text file inside a known project for the code viewer."""
    if not rel:
        return {"ok": False, "error": "path required"}
    target = safe_under(root, rel)
    if target is None:
        return {"ok": False, "error": "path outside project boundary"}
    if not target.is_file():
        return {"ok": False, "error": "not a file"}
    try:
        size = target.stat().st_size
        with target.open("rb") as fh:
            head = fh.read(min(size, MAX_FILE_READ + 1))
    except (PermissionError, OSError) as e:
        return {"ok": False, "error": str(e)}
    if b"\x00" in head[:4096]:
        return {"ok": False, "error": "binary file not shown"}
    truncated = len(head) > MAX_FILE_READ
    content = head[:MAX_FILE_READ].decode("utf-8", errors="replace")
    return {
        "ok": True,
        "path": rel,
        "size": size,
        "truncated": truncated,
        "content": content,
    }


def _git(root: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=15,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except Exception as e:
        return 1, str(e)


def get_git_summary(root: Path) -> dict:
    """Branch, working-tree change list, and diff stat for the context inspector."""
    code, out = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if code != 0:
        return {"ok": True, "is_git": False}
    branch = out.strip().splitlines()[0] if out.strip() else "HEAD"
    _, status_out = _git(root, "status", "--porcelain")
    changed = [l for l in status_out.splitlines() if l.strip()][:200]
    _, diffstat = _git(root, "diff", "--stat", "HEAD")
    return {
        "ok": True,
        "is_git": True,
        "branch": branch,
        "changed": changed,
        "diffstat": diffstat.strip()[:4000],
    }


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
                    header = {}
                    if tf and tf.is_file():
                        try:
                            t_content = tf.read_text(encoding="utf-8-sig")
                            goal_match = re.search(r"## Goal\s*\n\n(.*?)(?=\n## |\Z)", t_content, re.S)
                            if goal_match:
                                goal = goal_match.group(1).strip()
                            for chk, cid, ctext in re.findall(
                                r"-\s*\[([ xX])\]\s*([A-Za-z0-9_-]+):\s*(.*)", t_content
                            ):
                                criteria.append({
                                    "id": cid,
                                    "text": ctext.strip(),
                                    "done": chk.lower() == "x",
                                })
                            allowed = [l.strip().lstrip("- `").rstrip("`") for l in re.findall(r"-\s*`([^`]+)`", t_content)]
                            for field in ("Branch", "Worktree", "Model"):
                                fm = re.search(rf"^{field}:\s*(.+?)\s*$", t_content, re.M)
                                if fm:
                                    header[field.lower()] = fm.group(1)
                        except Exception:
                            pass

                    tasks_list.append({
                        "id": tid,
                        "title": row_dict.get("Title", ""),
                        "stage": row_dict.get("Stage", ""),
                        "role": row_dict.get("Role", ""),
                        "tool": row_dict.get("Tool", ""),
                        "status": row_dict.get("Status", "ready"),
                        "branch": header.get("branch", ""),
                        "worktree": header.get("worktree", ""),
                        "model": header.get("model", ""),
                        "depends": row_dict.get("Depends on", ""),
                        "commit": row_dict.get("Commit / artifact", row_dict.get("Commit", "")),
                        "notes": row_dict.get("Notes", ""),
                        "date": row_dict.get("Updated", row_dict.get("Date", "")),
                        "goal": goal,
                        "criteria": criteria,
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


def _next_task_number(flow_root: Path) -> int:
    max_num = 0
    ledger_file = flow_root / "state" / "tasks.md"
    if ledger_file.is_file():
        try:
            for m in re.finditer(r"T-([0-9]+)", ledger_file.read_text(encoding="utf-8-sig")):
                max_num = max(max_num, int(m.group(1)))
        except Exception:
            pass
    tasks_dir = flow_root / "tasks"
    if tasks_dir.is_dir():
        try:
            for tf in tasks_dir.glob("T-*.md"):
                m = re.match(r"^T-([0-9]+)", tf.name)
                if m:
                    max_num = max(max_num, int(m.group(1)))
        except Exception:
            pass
    return max_num + 1


def _index_repo_ast_symbols(root: Path) -> tuple[dict[str, str], dict[str, set[str]], dict[str, str]]:
    symbol_to_file: dict[str, str] = {}
    module_importers: dict[str, set[str]] = {}
    basename_to_rel: dict[str, str] = {}

    flow = get_project_flow_root(root) or (root / ".agentsflower")
    scan_dirs = [flow / "tools", flow / "studio", flow / "tests", root / "src"]
    for d in scan_dirs:
        if not d.is_dir():
            continue
        try:
            for fp in d.rglob("*"):
                if not fp.is_file() or "__pycache__" in fp.parts or ".runtime" in fp.parts:
                    continue
                rel = fp.relative_to(root).as_posix()
                basename_to_rel.setdefault(fp.name.lower(), rel)
                if fp.suffix == ".py":
                    try:
                        tree = ast.parse(fp.read_text(encoding="utf-8-sig", errors="replace"))
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                if len(node.name) >= 3 and not node.name.startswith("_"):
                                    symbol_to_file.setdefault(node.name, rel)
                            elif isinstance(node, ast.Import):
                                for alias in node.names:
                                    mod = alias.name.split(".")[-1]
                                    module_importers.setdefault(mod, set()).add(rel)
                            elif isinstance(node, ast.ImportFrom) and node.module:
                                mod = node.module.split(".")[-1]
                                module_importers.setdefault(mod, set()).add(rel)
                    except Exception:
                        continue
        except Exception:
            continue
    return symbol_to_file, module_importers, basename_to_rel


def compute_conversation_blast_radius(root: Path, text: str, invoke_graft: bool = True) -> dict:
    symbol_to_file, module_importers, basename_to_rel = _index_repo_ast_symbols(root)
    affected: list[str] = []
    matched_symbols: list[str] = []
    targets: list[str] = []

    def _add_file(rel_path: str):
        norm = rel_path.replace(chr(92), "/").removeprefix("./").lstrip("/")
        if norm and norm not in affected:
            affected.append(norm)

    for m in re.finditer(r"([A-Za-z0-9_./-]+[.][A-Za-z0-9]+)", text or ""):
        token = m.group(1).strip(".,:;()[]" + chr(96) + chr(34) + chr(39))
        ext = Path(token).suffix.lower()
        if ext not in (".py", ".js", ".css", ".html", ".md", ".json", ".ts", ".tsx"):
            continue
        low = Path(token).name.lower()
        if (root / token).is_file():
            rel = (root / token).resolve().relative_to(root.resolve()).as_posix()
            _add_file(rel)
            targets.append(rel)
        elif low in basename_to_rel:
            _add_file(basename_to_rel[low])
            targets.append(basename_to_rel[low])

    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", text or ""):
        if tok in symbol_to_file:
            if tok not in matched_symbols:
                matched_symbols.append(tok)
            if tok not in targets:
                targets.insert(0, tok)
            def_file = symbol_to_file[tok]
            _add_file(def_file)
            stem = Path(def_file).stem
            for imp_rel in sorted(module_importers.get(stem, ())):
                _add_file(imp_rel)

    if invoke_graft and graft and hasattr(graft, "graft_blast_radius"):
        flow = get_project_flow_root(root) or (root / ".agentsflower")
        graft_rt_root = flow / "tasks" / ".runtime" / "graft"
        had_rt = graft_rt_root.exists()
        probe_targets = targets[:1] if targets else ["studio.py"]
        try:
            g_files = graft.graft_blast_radius(root, probe_targets)
            for gf in g_files or []:
                _add_file(str(gf))
        except Exception:
            pass
        finally:
            if not had_rt and graft_rt_root.is_dir():
                try:
                    shutil.rmtree(graft_rt_root, ignore_errors=True)
                except Exception:
                    pass

    for f in list(affected):
        stem = Path(f).stem
        if f.endswith(".py") and not stem.startswith("test_"):
            test_key = f"test_{stem}.py".lower()
            if test_key in basename_to_rel:
                _add_file(basename_to_rel[test_key])

    if not affected:
        flow_name = (get_project_flow_root(root) or (root / ".agentsflower")).name
        for default_rel in (f"{flow_name}/tools/studio.py", f"{flow_name}/tests/test_studio.py"):
            _add_file(default_rel)

    return {
        "targets": targets[:8],
        "symbols": matched_symbols[:10],
        "affected_files": affected[:12],
        "engine": "graft-ast",
    }


def _assess_task_complexity(item_text: str, allowed_files: list[str]) -> dict:
    low = (item_text or "").lower()
    escalation_kw = (
        "architect", "ast", "blast", "graph", "synthesize", "synthesis",
        "security", "cross-cutting", "concurrency", "protocol", "engine",
        "complex", "multi-file", "migration", "orchestrat", "escalat", "argon", "refactor",
    )
    floor_only_kw = ("minor", "css", "badge", "label", "typo", "unit test", "verify")
    has_esc = any(k in low for k in escalation_kw)
    non_test_files = [f for f in allowed_files if not Path(f).name.startswith("test_")]
    is_simple_floor = any(k in low for k in floor_only_kw) and not any(
        k in low for k in ("architect", "ast", "blast", "graph", "complex", "multi-file", "security", "refactor")
    )
    if (has_esc and not is_simple_floor) or len(non_test_files) >= 3:
        return {
            "complexity": "high",
            "effort": "high",
            "model": "gemini-4-argon-high",
            "tier": "escalation",
        }
    return {
        "complexity": "standard",
        "effort": "medium",
        "model": "swe-2-high",
        "tier": "floor",
    }


def _extract_discussion_items(text: str) -> list[str]:
    inline_parts = [seg.strip() for seg in re.split(r"(?:^|\s+)[0-9]+[.)]\s+", (text or "").strip()) if seg.strip()]
    if len(inline_parts) >= 2:
        return inline_parts[:6]
    raw_lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    numbered = []
    for ln in raw_lines:
        m = re.match(r"^(?:[0-9]+[.)]|[-*]) +(.+)$", ln)
        if m:
            numbered.append(m.group(1).strip())
    if len(numbered) >= 2:
        return numbered[:6]
    if len(raw_lines) >= 2:
        return [re.sub(r"^(?:[0-9]+[.)]|[-*]) +", "", ln).strip() for ln in raw_lines[:6]]
    single = (text or "").strip() or "Implement conversational feature and verification suite"
    clean = re.sub(r"^(?:[0-9]+[.)]|[-*]) +", "", single).strip()
    return [
        clean,
        f"Add unit tests and gate verification for: {clean[:72]}",
    ]


def synthesize_tasks_from_chat(root: Path, body: dict) -> dict:
    flow_root = get_project_flow_root(root) or (root / ".agentsflower")
    stage = str(body.get("stage") or "7")
    thread = str(body.get("thread") or "research")
    nl = chr(10)

    msgs = body.get("messages") or body.get("history") or []
    parts: list[str] = []
    if isinstance(msgs, list):
        for m in msgs:
            if isinstance(m, dict):
                role = str(m.get("role") or "user").lower()
                content = str(m.get("content") or m.get("text") or "").strip()
                if content and role in ("user", "human", ""):
                    parts.append(content)
            elif isinstance(m, str) and m.strip():
                parts.append(m.strip())
    for key in ("discussion", "prompt", "text", "context"):
        val = body.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())

    full_text = nl.join(parts).strip()
    if not full_text:
        full_text = nl.join([
            "1. Architect conversational task synthesis in studio.py with Graft AST blast radius.",
            "2. Verify synthesized task pool in test_studio.py.",
        ])

    blast = compute_conversation_blast_radius(root, full_text, invoke_graft=True)
    items = _extract_discussion_items(full_text)
    next_num = _next_task_number(flow_root)
    tasks: list[dict] = []

    for idx, item in enumerate(items):
        tid = f"T-{next_num + idx:03d}"
        item_blast = compute_conversation_blast_radius(root, item, invoke_graft=False)
        item_files = item_blast["affected_files"] or blast["affected_files"]
        for f in item_files:
            if f not in blast["affected_files"]:
                blast["affected_files"].append(f)

        title = item.rstrip(".").strip()
        if len(title) > 78:
            title = title[:75].rsplit(" ", 1)[0] + "..."

        assess = _assess_task_complexity(item, item_files)
        role = "developer"
        criteria = [
            f"C-01: {title} implemented within allowed files ({', '.join(item_files[:3])}).",
            f"C-02: Verification suite passes cleanly: python -m unittest discover -s {flow_root.name}/tests.",
        ]
        tasks.append({
            "id": tid,
            "title": title,
            "stage": stage,
            "role": role,
            "tool": "devin",
            "effort": assess["effort"],
            "complexity": assess["complexity"],
            "tier": assess["tier"],
            "model": assess["model"],
            "goal": item,
            "allowed": item_files,
            "allowed_files": item_files,
            "blast_radius": item_files,
            "criteria": criteria,
        })

    result = {
        "ok": True,
        "project": str(root),
        "thread": thread,
        "summary": f"Synthesized {len(tasks)} atomic task contracts with AST blast radius ({len(blast['affected_files'])} affected files).",
        "symbols": blast["symbols"],
        "blast_radius": blast,
        "tasks": tasks,
        "pool": tasks,
    }
    if body.get("register") is True or body.get("approve") is True:
        reg = register_task_pool(root, tasks, default_stage=stage)
        result["registered"] = reg.get("registered", [])
        result["files"] = reg.get("files", [])
    return result


def register_task_pool(target_root: Path, tasks_payload: list[dict], default_stage: str = "7") -> dict:
    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    tasks_dir = flow_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = flow_root / "state" / "tasks.md"

    next_num = _next_task_number(flow_root)
    registered_ids: list[str] = []
    created_files: list[str] = []
    normalized_tasks: list[dict] = []

    lines, cols, rows, head, end = ledger.load(ledger_file)
    idx_map = {r[0]: i for i, r in enumerate(rows)}
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    bt = chr(96)
    nl = chr(10)
    bs = chr(92)

    for raw in tasks_payload or []:
        if not isinstance(raw, dict):
            continue
        tid = str(raw.get("id") or "").strip().upper()
        if not re.fullmatch(r"T-[0-9]+", tid):
            tid = f"T-{next_num:03d}"
            next_num += 1
        title = str(raw.get("title") or f"Task {tid}").strip()
        role = str(raw.get("role") or "developer").strip()
        stage = str(raw.get("stage") or default_stage).strip()
        tool = str(raw.get("tool") or "devin").strip()
        model = str(raw.get("model") or "swe-2-high").strip()
        effort = str(raw.get("effort") or "high").strip()
        depends = str(raw.get("depends") or "none").strip()
        goal = str(raw.get("goal") or title).strip()
        allowed = raw.get("allowed_files") or raw.get("allowed") or []
        raw_criteria = raw.get("criteria") or []

        norm_criteria: list[str] = []
        for c_idx, c in enumerate(raw_criteria, 1):
            c_str = str(c.get("text") if isinstance(c, dict) else c).strip()
            if not c_str:
                continue
            if not re.match(r"^[A-Za-z]-[0-9]+:", c_str):
                c_str = f"C-{c_idx:02d}: {c_str}"
            norm_criteria.append(c_str)
        if not norm_criteria:
            norm_criteria = ["C-01: Verification pass."]

        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48].strip("-")
        filename = f"{tid}-{slug}.md" if slug else f"{tid}.md"
        file_path = tasks_dir / filename

        allowed_bullets = nl.join(f"- {bt}{f}{bt}" for f in allowed) if allowed else "- none"
        criteria_bullets = nl.join(f"- [ ] {c}" for c in norm_criteria)
        wt_path = f"{target_root.parent}{bs}worktrees{bs}{target_root.name}-{tid.lower()}-{slug or 'task'}"

        task_lines = [
            f"# {tid}: {title}",
            "",
            f"Role: {role}",
            f"Tool: {tool}",
            f"Model: {model}",
            f"Effort: {effort}",
            f"Stage: {stage}",
            f"Depends on: {depends}",
            f"Branch: {tid.lower()}-{slug or 'task'}",
            f"Worktree: {wt_path}",
            "Independent check: tester",
            "Resume: none",
            "Routing exception: human authorized via AgentsFlower Studio (2026-10-24)",
            "",
            "## Goal",
            "",
            goal,
            "",
            "## Read first",
            "",
            f"- {flow_root.name}/docs/ai-handoff-protocol.md",
            "",
            "## Allowed files",
            "",
            allowed_bullets,
            "",
            "## Do not touch",
            "",
            "- All other files.",
            "",
            "## Setup",
            "",
            "- nothing",
            "",
            "## Port",
            "",
            "- nothing",
            "",
            "## Rebuild together",
            "",
            "- nothing",
            "",
            "## Acceptance criteria",
            "",
            criteria_bullets,
            "",
            "## Checks",
            "",
            f"- python -m unittest discover -s {flow_root.name}/tests",
            "",
            "## Result",
            "",
            "<!-- Worker writes its outcome below this block -->",
            "",
        ]
        file_path.write_text(nl.join(task_lines), encoding="utf-8")

        row = [""] * len(cols)
        row[cols.index("ID")] = tid
        row[cols.index("Title")] = title
        row[cols.index("Stage")] = stage
        row[cols.index("Role")] = role
        row[cols.index("Tool")] = tool
        row[cols.index("Status")] = "ready"
        row[cols.index("Depends on")] = "" if depends == "none" else depends
        row[cols.index("Notes")] = f"model={model}; effort={effort}"
        row[cols.index("Updated")] = now_str
        if tid in idx_map:
            rows[idx_map[tid]] = row
        else:
            idx_map[tid] = len(rows)
            rows.append(row)

        rel_path = file_path.relative_to(target_root).as_posix() if file_path.is_relative_to(target_root) else str(file_path)
        registered_ids.append(tid)
        created_files.append(rel_path)
        normalized_tasks.append({
            "id": tid,
            "title": title,
            "stage": stage,
            "role": role,
            "tool": tool,
            "model": model,
            "effort": effort,
            "file": rel_path,
        })

    if registered_ids:
        ledger.save(ledger_file, lines, head, end, rows)

    return {
        "ok": bool(registered_ids),
        "registered": registered_ids,
        "files": created_files,
        "tasks": normalized_tasks,
        "task_id": registered_ids[0] if registered_ids else "",
        "file": created_files[0] if created_files else "",
    }


def get_task_context(target_root: Path, task_id: str) -> dict:
    tid = (task_id or "").strip().upper()
    tasks_data = get_tasks_data(str(target_root))
    all_tasks = tasks_data.get("tasks", [])
    task_obj = next((t for t in all_tasks if t.get("id", "").upper() == tid), None)
    if not task_obj and all_tasks and not tid:
        task_obj = all_tasks[0]
        tid = task_obj["id"]
    if not task_obj:
        return {"ok": False, "error": f"Task not found: {task_id}"}

    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    tasks_dir = flow_root / "tasks"
    contract_file = ""
    checks: list[str] = []
    effort = "high"
    full_allowed = list(task_obj.get("allowed_files") or [])
    bt = chr(96)
    if tasks_dir.is_dir():
        hits = sorted(tasks_dir.glob(f"{tid}*.md"))
        if hits:
            tf = hits[0]
            contract_file = tf.relative_to(target_root).as_posix() if tf.is_relative_to(target_root) else str(tf)
            try:
                t_text = tf.read_text(encoding="utf-8-sig")
                for line in t_text.splitlines():
                    if line.startswith("Effort:"):
                        effort = line.split(":", 1)[1].strip() or effort
                        break
                sections = re.split(r"^## ", t_text, flags=re.M)
                for sec in sections:
                    if sec.startswith("Allowed files"):
                        parsed_allowed = [
                            ln.strip().lstrip("- ").strip(bt).strip()
                            for ln in sec.splitlines()[1:]
                            if ln.strip().startswith("-")
                        ]
                        if parsed_allowed:
                            full_allowed = [a for a in parsed_allowed if a and a.lower() != "none"]
                    elif sec.startswith("Checks"):
                        checks = [
                            ln.strip().lstrip("- ").strip(bt).strip()
                            for ln in sec.splitlines()[1:]
                            if ln.strip().startswith("-")
                        ]
            except Exception:
                pass

    recent_log: list[str] = []
    rt_file = flow_root / "tasks" / ".runtime" / f"{tid}.json"
    if rt_file.is_file():
        try:
            rt_data = json.loads(rt_file.read_text(encoding="utf-8-sig"))
            for att in (rt_data.get("attempts") or [])[-3:]:
                recent_log.append(
                    f"Attempt #{att.get('n', 1)}: status={att.get('status', 'unknown')} tool={att.get('tool', task_obj.get('tool', 'devin'))}"
                )
        except Exception:
            pass
    code, git_log = _git(target_root, "log", "-n", "3", "--oneline")
    if code == 0 and git_log.strip():
        for ln in git_log.strip().splitlines()[:3]:
            recent_log.append(f"git: {ln.strip()}")
    if not recent_log:
        recent_log.append(f"Task {tid} registered in ledger (status: {task_obj.get('status', 'ready')})")

    enriched = dict(task_obj)
    enriched["allowed_files"] = full_allowed
    enriched["checks"] = checks
    enriched["effort"] = effort
    enriched["contract_file"] = contract_file

    return {
        "ok": True,
        "task": enriched,
        "recent_log": recent_log,
        "git": get_git_summary(target_root),
    }


# --- Live CLI capacity probe (Model Quota Hub) ---
# Bounded subprocess/HTTP scans of the installed agent CLIs; results are cached for a
# short TTL so repeated UI queries stay instantaneous. Probe output is returned to the
# caller of this process only - it is never written to disk.

CAPACITY_PROBE_TTL = 60
CLI_PROBE_TIMEOUT = 20
OLLAMA_URL = "http://127.0.0.1:11434"

_capacity_probe_cache = {"at": 0.0, "data": None}
_platform_probe_cache = {}
_capacity_probe_lock = threading.Lock()

SUGGESTED_LOCAL_MODELS = [
    {"id": "qwen2.5-coder", "note": "Code-focused open-weight model for autonomous local runs",
     "install": "ollama pull qwen2.5-coder"},
    {"id": "deepseek-r1", "note": "Reasoning open-weight model, zero token cost",
     "install": "ollama pull deepseek-r1"},
    {"id": "llama3.3", "note": "General-purpose open-weight model, zero token cost",
     "install": "ollama pull llama3.3"},
]


def _kill_probe_tree(pid: int):
    """Best-effort kill of a timed-out probe and its children."""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        else:
            os.killpg(pid, signal.SIGKILL)
    except (OSError, AttributeError):
        pass


def _probe_run(argv: list, timeout: int = CLI_PROBE_TIMEOUT):
    """One bounded CLI probe: (exit code, combined output); (None, "") on launch failure/timeout."""
    kw = {"stdin": subprocess.DEVNULL, "stdout": subprocess.PIPE, "stderr": subprocess.STDOUT,
          "text": True, "encoding": "utf-8", "errors": "replace"}
    if os.name == "nt":
        kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    try:
        proc = subprocess.Popen(argv, **kw)
    except OSError:
        return None, ""
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_probe_tree(proc.pid)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
        return None, ""
    return proc.returncode, (out or "").strip()


def _probe_version(exe: str) -> str:
    code, out = _probe_run([exe, "--version"], timeout=15)
    line = next((ln.strip() for ln in out.splitlines() if ln.strip()), "")
    return line[:120] if code == 0 and line else ""


_DEVIN_FAMILY = re.compile(r"^([A-Za-z0-9][^\n()]*?)\s*\(([a-z0-9_.-]+)\)\s*$")
_DEVIN_MODEL = re.compile(r"^\s+(\S+)\s{2,}(.*?)(?:\s{2,}\[(.*?)\])?\s*$")


def parse_devin_models(text: str) -> list[dict]:
    """`devin models list` -> [{id,label,context,pricing,family,free}]."""
    models = []
    family = ""
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        if line[:1] in (" ", "\t"):
            if line.strip().startswith("aliases:"):
                continue
            m = _DEVIN_MODEL.match(line)
            if not m:
                continue
            bracket = m.group(3) or ""
            context, pricing = "", ""
            if bracket:
                head, _, rest = bracket.partition(",")
                if "context" in head:
                    context, pricing = head.strip(), rest.strip()
                else:
                    pricing = bracket.strip()
            models.append({"id": m.group(1), "label": m.group(2).strip() or m.group(1),
                           "context": context, "pricing": pricing, "family": family,
                           "free": "free" in bracket.lower()})
            continue
        fam = _DEVIN_FAMILY.match(line.strip())
        if fam:
            family = fam.group(2)
    return models


def parse_agy_models(text: str) -> list[dict]:
    """`agy models` -> [{id,label}]: tab- or column-separated rows."""
    models = []
    for line in (text or "").splitlines():
        line = line.strip()
        m = re.match(r"^(\S+)\t+(.+?)\s*$", line) or re.match(r"^(\S+)\s{2,}(.+?)\s*$", line)
        if m:
            models.append({"id": m.group(1), "label": m.group(2).strip(), "context": "",
                           "pricing": "", "family": "", "free": False})
    return models


_CLI_MODEL_SKIP = re.compile(r"^(model|models|id|name|available|error|failed|usage)\b", re.I)


def parse_cli_models(text: str) -> list[dict]:
    """Generic account model listing -> [{id,label}]: one model id per line; header/error lines skipped."""
    models = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        first = line.split()[0]
        if not re.fullmatch(r"[A-Za-z0-9][\w./:-]*", first) or _CLI_MODEL_SKIP.match(first):
            continue
        models.append({"id": first, "label": line, "context": "", "pricing": "",
                       "family": "", "free": False})
    return models


def _configured_tool_models(flow_root: Path, tool: str) -> list[dict]:
    """Fallback model list for a CLI with no catalog command: the project's docs/model-options.json."""
    try:
        cfg = json.loads((flow_root / "docs" / "model-options.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return []
    ids = []
    for opt in (cfg.get("options") or {}).values():
        if not isinstance(opt, dict) or opt.get("tool") != tool:
            continue
        mbe = opt.get("model_by_effort")
        values = list(mbe.values()) if isinstance(mbe, dict) else [opt.get("model")]
        for v in values:
            if isinstance(v, str) and v.strip() and v.strip() not in ids:
                ids.append(v.strip())
    return [{"id": i, "label": i, "context": "configured catalog", "pricing": "",
             "family": "", "free": False} for i in ids]


def _fetch_ollama_json(path: str, timeout: int = 3):
    try:
        req = urllib.request.Request(OLLAMA_URL + path, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _platform(key: str, label: str, installed: bool, authenticated: bool,
              version: str = "", models: list = None, note: str = "") -> dict:
    if not installed:
        status, status_label = "missing", "Not Installed"
    elif authenticated:
        status, status_label = "active", "Active & Authenticated"
    else:
        status, status_label = "limited", "Limited / Unauthenticated"
    return {"key": key, "label": label, "status": status, "status_label": status_label,
            "version": version, "authenticated": bool(authenticated),
            "models": models or [], "note": note}


def _probe_devin(flow_root: Path = None) -> dict:
    exe = shutil.which("devin")
    if not exe:
        return _platform("devin", "Devin", False, False, note="devin CLI not found on PATH")
    code, auth_out = _probe_run([exe, "auth", "status"])
    authed = code == 0 and "logged in" in auth_out.lower()
    mcode, mout = _probe_run([exe, "models", "list"])
    models = parse_devin_models(mout) if mcode == 0 else []
    note = ""
    if mcode != 0:
        note = "model catalog probe failed"
    elif not models:
        note = "model catalog returned no models"
    return _platform("devin", "Devin", True, authed,
                     version=_probe_version(exe), models=models, note=note)


def _probe_claude(flow_root: Path = None) -> dict:
    exe = shutil.which("claude")
    if not exe:
        return _platform("claude", "Claude Code", False, False, note="claude CLI not found on PATH")
    version = _probe_version(exe)
    code, out = _probe_run([exe, "auth", "status"])
    try:
        logged_in = bool(json.loads(out).get("loggedIn")) if code == 0 else False
    except (ValueError, AttributeError):
        logged_in = False
    # `auth status` reports the stored credential; `claude models` proves it still works.
    mcode, mout = _probe_run([exe, "models"])
    auth_failed = any(marker in mout.lower() for marker in
                      ("failed to authenticate", "not logged in", "unauthorized"))
    authed = logged_in and not auth_failed
    models = parse_cli_models(mout) if mcode == 0 and not auth_failed else []
    if authed and not models:
        models = _configured_tool_models(flow_root or FLOW_ROOT, "claude")
    note = mout.splitlines()[0].strip()[:140] if auth_failed and mout else ""
    return _platform("claude", "Claude Code", True, authed, version=version,
                     models=models, note=note)


def _probe_codex(flow_root: Path = None) -> dict:
    exe = shutil.which("codex")
    if not exe:
        return _platform("codex", "Codex", False, False, note="codex CLI not found on PATH")
    version = _probe_version(exe)
    # `login status` exits nonzero when the CLI holds no usable credential.
    code, out = _probe_run([exe, "login", "status"])
    authed = code == 0 and not any(
        marker in out.lower() for marker in ("not logged in", "logged out", "unauthorized"))
    mcode, mout = _probe_run([exe, "models"])
    models = parse_cli_models(mout) if mcode == 0 else []
    if authed and not models:
        models = _configured_tool_models(flow_root or FLOW_ROOT, "codex")
    note = "" if code == 0 else (out.splitlines()[0].strip()[:140] if out else "login status probe failed")
    return _platform("codex", "Codex", True, authed, version=version, models=models, note=note)


def _probe_agy(flow_root: Path = None) -> dict:
    exe = shutil.which("agy")
    if not exe:
        return _platform("agy", "Antigravity", False, False, note="agy CLI not found on PATH")
    version = _probe_version(exe)
    code, out = _probe_run([exe, "models"])
    models = parse_agy_models(out) if code == 0 else []
    note = "" if code == 0 else "account model probe failed"
    return _platform("agy", "Antigravity", True, code == 0 and bool(models),
                     version=version, models=models, note=note)


def _probe_ollama(flow_root: Path = None) -> dict:
    tags = _fetch_ollama_json("/api/tags")
    if not isinstance(tags, dict):
        return _platform("ollama", "Ollama (Local)", False, False,
                         note="no Ollama server answering on 127.0.0.1:11434")
    version = (_fetch_ollama_json("/api/version") or {}).get("version", "")
    models = []
    for m in tags.get("models") or []:
        models.append({"id": m.get("name", ""), "label": m.get("name", ""),
                       "context": (m.get("details") or {}).get("parameter_size", ""),
                       "pricing": "$0 local", "family": (m.get("details") or {}).get("family", ""),
                       "free": True, "local": True})
    return _platform("ollama", "Ollama (Local)", True, True,
                     version=f"v{version}" if version else "", models=models,
                     note="offline zero-token models")


_PLATFORM_PROBES = {
    "devin": _probe_devin,
    "claude": _probe_claude,
    "codex": _probe_codex,
    "agy": _probe_agy,
    "ollama": _probe_ollama,
}


def _apply_quota_hold(p: dict) -> dict:
    if p["status"] == "active" and p["key"] in machine_capacity.TOOLS:
        try:
            hold = machine_capacity.limit_until(p["key"])
        except Exception:
            hold = None
        if hold:
            p["status"], p["status_label"] = "limited", "Limited / Unauthenticated"
            p["hold_until"] = hold.isoformat()
            p["note"] = (f"{p['note']} " if p["note"] else "") + f"quota hold until {p['hold_until']}"
    return p


def _single_platform_probe(key: str, force: bool, flow_root: Path = None):
    """Probe one platform on demand (?platform=<key>); each key has its own TTL cache entry."""
    now = time.time()
    with _capacity_probe_lock:
        ent = _platform_probe_cache.get(key)
        if not force and ent and now - ent["at"] < CAPACITY_PROBE_TTL:
            return dict(ent["data"]), True
    p = _apply_quota_hold(_PLATFORM_PROBES[key](flow_root))
    with _capacity_probe_lock:
        _platform_probe_cache[key] = {"at": time.time(), "data": p}
    return p, False


def probe_capacity(force: bool = False, platform: str = "", flow_root: Path = None) -> dict:
    """Scan the agent CLIs on this machine; results are cached for CAPACITY_PROBE_TTL seconds.
    `platform` limits the scan to one platform key (/api/capacity/probe?platform=<tool>)."""
    now = time.time()
    if platform:
        p, cached = _single_platform_probe(platform, force, flow_root or FLOW_ROOT)
        return {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ttl": CAPACITY_PROBE_TTL,
            "cached": cached,
            "platform": p,
            "platforms": [p],
        }
    with _capacity_probe_lock:
        cached = _capacity_probe_cache["data"]
        if not force and cached and now - _capacity_probe_cache["at"] < CAPACITY_PROBE_TTL:
            data = dict(cached)
            data["cached"] = True
            return data

    results: dict = {}
    probes = tuple(_PLATFORM_PROBES.items())
    threads = [
        threading.Thread(target=lambda n=n, f=f: results.__setitem__(n, f(flow_root or FLOW_ROOT)), daemon=True)
        for n, f in probes
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=CLI_PROBE_TIMEOUT + 15)

    platforms = []
    for name, _fn in probes:
        p = results.get(name) or _platform(
            name, name, True, False, note="probe timed out or crashed")
        platforms.append(_apply_quota_hold(p))

    ollama = next((p for p in platforms if p["key"] == "ollama"), {})
    data = {
        "ok": True,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ttl": CAPACITY_PROBE_TTL,
        "cached": False,
        "platforms": platforms,
        "local_free": {
            "installed": ollama.get("models", []),
            "suggested": SUGGESTED_LOCAL_MODELS,
        },
    }
    with _capacity_probe_lock:
        _capacity_probe_cache["at"] = time.time()
        _capacity_probe_cache["data"] = data
    return data


def get_default_worker_model(flow_root: Path):
    """The Studio-persisted default worker model from docs/model-options.json, or None."""
    try:
        cfg = json.loads((flow_root / "docs" / "model-options.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None
    entry = cfg.get("default_worker_model")
    return entry if isinstance(entry, dict) and entry.get("model") else None


def set_default_worker_model(flow_root: Path, model: str, tool: str = "") -> dict:
    """Persist the project's default worker model inside docs/model-options.json."""
    docs = flow_root / "docs"
    path = docs / "model-options.json"
    if not docs.is_dir():
        return {"ok": False, "error": "project has no docs/model-options.json location"}
    try:
        cfg = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}
        if not isinstance(cfg, dict):
            cfg = {}
    except ValueError:
        return {"ok": False, "error": "model-options.json is not valid JSON"}
    cfg["default_worker_model"] = {
        "model": model, "tool": tool,
        "set_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "studio",
    }
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"ok": True, "default_model": cfg["default_worker_model"]}


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

        if path == "/api/task/context":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            tid = qs.get("id", qs.get("task_id", [""]))[0]
            res = get_task_context(root, tid)
            self.send_json(res, 200 if res.get("ok") else 404)
            return

        if path == "/api/project/tree":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            rel = qs.get("path", [""])[0]
            self.send_json(get_project_tree(root, rel))
            return

        if path == "/api/file/read":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            rel = qs.get("path", [""])[0]
            res = read_project_file(root, rel)
            code = 200 if res.get("ok") else (403 if "outside" in res.get("error", "") else 404)
            self.send_json(res, code)
            return

        if path == "/api/project/git":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            self.send_json(get_git_summary(root))
            return

        if path == "/api/capacity/probe":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            flow = get_project_flow_root(root)
            platform = qs.get("platform", [""])[0].strip().lower()
            if platform and platform not in _PLATFORM_PROBES:
                self.send_json({"ok": False, "error": f"unknown platform: {platform}"}, 400)
                return
            data = probe_capacity(force=qs.get("refresh", [""])[0] in ("1", "true"),
                                  platform=platform, flow_root=flow)
            data["default_model"] = get_default_worker_model(flow) if flow else None
            self.send_json(data)
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

        # Dashboard static assets (project-scoped via ?project=<known project>)
        if path.startswith("/dashboard/"):
            dash_root = FLOW_ROOT / "dashboard"
            if target_project_str:
                proj = resolve_known_project(target_project_str)
                flow = get_project_flow_root(proj) if proj else None
                dash_root = flow / "dashboard" if flow else None
            if dash_root is not None:
                rel_file = path[len("/dashboard/"):].lstrip("/")
                file_path = safe_under(dash_root, rel_file)
                if file_path and file_path.is_file():
                    self._serve_file(file_path)
                    return
                if target_project_str:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Dashboard file not found for this project")
                    return

        # Studio Static assets
        req_file = path.lstrip("/")
        if not req_file or req_file == "index.html":
            file_path = STUDIO_DIR / "index.html"
        else:
            file_path = safe_under(STUDIO_DIR, req_file)

        if file_path and file_path.is_file() and not file_path.is_symlink():
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
            if body.get("authorized") is not True:
                self.send_json({
                    "ok": False,
                    "error": "Explicit human authorization required before running install.py",
                    "requires_authorization": True,
                }, 403)
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

        if path == "/api/capacity/default-model":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            flow_root = get_project_flow_root(target_root)
            if not flow_root:
                self.send_json({"ok": False, "error": "project has no AgentsFlower install"}, 400)
                return
            model = str(body.get("model") or "").strip()
            tool = str(body.get("tool") or "").strip()
            if not re.fullmatch(r"[A-Za-z0-9][\w./:-]{0,80}", model):
                self.send_json({"ok": False, "error": "invalid model id"}, 400)
                return
            if tool and not re.fullmatch(r"[A-Za-z0-9][\w.-]{0,30}", tool):
                self.send_json({"ok": False, "error": "invalid tool id"}, 400)
                return
            res = set_default_worker_model(flow_root, model, tool)
            self.send_json(res, 200 if res.get("ok") else 400)
            return

        if path == "/api/dashboard/build":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            target_flow = get_project_flow_root(target_root)
            b_script = target_flow / "dashboard" / "build.py" if target_flow else None
            if not b_script or not b_script.is_file():
                self.send_json({"ok": False, "error": "project has no AgentsFlower dashboard to build"}, 400)
                return
            try:
                proc = subprocess.run([sys.executable, str(b_script)], cwd=target_root, capture_output=True, text=True)
                self.send_json({"ok": proc.returncode == 0, "output": proc.stdout, "error": proc.stderr})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)
            return

        if path == "/api/graft/query":
            if not graft:
                self.send_json({"ok": False, "error": "Graft module not available in environment"}, 400)
                return
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            q = body.get("question", "")
            scope = body.get("path_scope", "")
            res = graft.graft_query(target_root, q, scope)
            self.send_json(res)
            return

        if path == "/api/graft/impact":
            if not graft:
                self.send_json({"ok": False, "error": "Graft module not available in environment"}, 400)
                return
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            target = body.get("target", "")
            res = graft.graft_impact(target_root, target)
            self.send_json(res)
            return

        if path == "/api/task/synthesize":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            res = synthesize_tasks_from_chat(target_root, body)
            self.send_json(res, 200 if res.get("ok") else 400)
            return

        if path in ("/api/task/pool/register", "/api/task/register", "/api/task/batch"):
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            pool_items = body.get("tasks") or body.get("pool") or []
            if not isinstance(pool_items, list) or not pool_items:
                self.send_json({"ok": False, "error": "No tasks provided in pool"}, 400)
                return
            res = register_task_pool(target_root, pool_items, default_stage=str(body.get("stage") or "7"))
            self.send_json(res, 200 if res.get("ok") else 400)
            return

        if path == "/api/task/create":
            # Rapid task authoring
            target_root = resolve_known_project(body.get("project", "").strip())
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
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
