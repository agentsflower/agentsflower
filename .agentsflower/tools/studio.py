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
import copy
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
import local_adapter  # noqa: E402
import plan_route  # noqa: E402
from plan_route import (  # noqa: E402
    EFFORT_OUTPUT_TOKENS,
    MODEL_PRICING_USD_PER_1M,
    estimate_input_tokens,
    estimate_output_tokens,
    estimate_task_budget,
    lookup_model_pricing,
)
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
                            for field in ("Branch", "Worktree", "Model", "Skills", "Planned tokens", "Planned cost USD"):
                                fm = re.search(rf"^{field}:\s*(.+?)\s*$", t_content, re.M)
                                if fm:
                                    header[field.lower()] = fm.group(1)
                        except Exception:
                            pass

                    raw_sk = header.get("skills", "")
                    task_skills = [
                        s.strip() for s in raw_sk.split(",")
                        if s.strip() and s.strip().lower() != "none"
                    ] if raw_sk else []

                    plan_meta: dict = {}
                    plan_json_path = tasks_dir / f"{tid}.plan.json" if tasks_dir.is_dir() else None
                    if plan_json_path and plan_json_path.is_file():
                        try:
                            loaded_plan = json.loads(plan_json_path.read_text(encoding="utf-8-sig"))
                            if isinstance(loaded_plan, dict):
                                plan_meta = loaded_plan
                        except Exception:
                            pass

                    planned_tokens = plan_meta.get("planned_tokens")
                    if planned_tokens is None and header.get("planned tokens"):
                        m_tok = re.search(r"\d+", header["planned tokens"])
                        if m_tok:
                            planned_tokens = int(m_tok.group(0))

                    planned_cost_usd = plan_meta.get("planned_cost_usd")
                    if planned_cost_usd is None and header.get("planned cost usd"):
                        m_cost = re.search(r"[0-9]+(?:\.[0-9]+)?", header["planned cost usd"])
                        if m_cost:
                            planned_cost_usd = float(m_cost.group(0))

                    task_entry = {
                        "id": tid,
                        "title": row_dict.get("Title", ""),
                        "stage": row_dict.get("Stage", ""),
                        "role": row_dict.get("Role", ""),
                        "tool": row_dict.get("Tool", ""),
                        "status": row_dict.get("Status", "ready"),
                        "branch": header.get("branch", ""),
                        "worktree": header.get("worktree", ""),
                        "model": header.get("model", ""),
                        "skills": task_skills,
                        "depends": row_dict.get("Depends on", ""),
                        "commit": row_dict.get("Commit / artifact", row_dict.get("Commit", "")),
                        "notes": row_dict.get("Notes", ""),
                        "date": row_dict.get("Updated", row_dict.get("Date", "")),
                        "goal": goal,
                        "criteria": criteria,
                        "criteria_count": len(criteria),
                        "allowed_files": allowed[:5],
                    }
                    if planned_tokens is not None:
                        task_entry["planned_tokens"] = int(planned_tokens)
                    if "planned_input_tokens" in plan_meta:
                        task_entry["planned_input_tokens"] = int(plan_meta["planned_input_tokens"])
                    if "planned_output_tokens" in plan_meta:
                        task_entry["planned_output_tokens"] = int(plan_meta["planned_output_tokens"])
                    if planned_cost_usd is not None:
                        task_entry["planned_cost_usd"] = float(planned_cost_usd)
                    tasks_list.append(task_entry)
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


def compute_conversation_blast_radius(
    root: Path, text: str, invoke_graft: bool = True, fallback_defaults: bool = True
) -> dict:
    symbol_to_file, module_importers, basename_to_rel = _index_repo_ast_symbols(root)
    affected: list[str] = []
    matched_symbols: list[str] = []
    targets: list[str] = []

    def _add_file(rel_path: str):
        norm = rel_path.replace(chr(92), "/").removeprefix("./").lstrip("/")
        if norm and norm not in affected:
            affected.append(norm)

    allowed_exts = (
        ".py", ".js", ".css", ".html", ".md", ".json",
        ".ts", ".tsx", ".txt", ".xml", ".scss", ".less", ".vue", ".svelte",
    )
    known_artifacts = {
        "manifest.json", "llms.txt", "llms-full.txt", "robots.txt", "sitemap.xml",
        "service-worker.js", "service_worker.js", "background.js",
        "content-script.js", "content_script.js", "offscreen.html", "offscreen.js",
        "popup.html", "popup.js", "mv3_lint.py",
    }

    for m in re.finditer(r"([A-Za-z0-9_./-]+[.][A-Za-z0-9]+)", text or ""):
        token = m.group(1).strip(".,:;()[]" + chr(96) + chr(34) + chr(39))
        ext = Path(token).suffix.lower()
        if ext not in allowed_exts:
            continue
        low = Path(token).name.lower()
        if (root / token).is_file():
            rel = (root / token).resolve().relative_to(root.resolve()).as_posix()
            _add_file(rel)
            targets.append(rel)
        elif low in basename_to_rel:
            _add_file(basename_to_rel[low])
            targets.append(basename_to_rel[low])
        elif low in known_artifacts or ext in (".css", ".html", ".txt", ".xml", ".scss", ".less", ".vue", ".svelte"):
            _add_file(token)
            targets.append(token)

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

    if not affected and fallback_defaults:
        flow_name = (get_project_flow_root(root) or (root / ".agentsflower")).name
        for default_rel in (f"{flow_name}/tools/studio.py", f"{flow_name}/tests/test_studio.py"):
            _add_file(default_rel)

    return {
        "targets": targets[:8],
        "symbols": matched_symbols[:10],
        "affected_files": affected[:12],
        "engine": "graft-ast",
    }


def _load_skills_catalog(root: Path) -> set[str]:
    catalog = {
        "frontend-art-direction",
        "chrome-extension-mv3",
        "geo-seo-audit",
        "perf-benchmark",
    }
    flow = get_project_flow_root(root) or (root / ".agentsflower")
    for candidate in (flow / "skills" / "INDEX.md", FLOW_ROOT / "skills" / "INDEX.md"):
        if candidate.is_file():
            try:
                text = candidate.read_text(encoding="utf-8", errors="replace")
                for slug in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", text):
                    catalog.add(slug)
                break
            except Exception:
                continue
    return catalog


def map_task_skills(root: Path, item_text: str, allowed_files: list[str] | None = None) -> list[str]:
    """Match AST blast radius files and task keywords against skills/INDEX.md."""
    catalog = _load_skills_catalog(root)
    low = (item_text or "").lower()
    files = [str(f).replace(chr(92), "/").lower() for f in (allowed_files or []) if f]
    basenames = [Path(f).name.lower() for f in files]
    suffixes = {Path(f).suffix.lower() for f in files}
    matched: list[str] = []

    def _add_skill(slug: str):
        if slug in catalog and slug not in matched:
            matched.append(slug)

    mv3_files = {
        "manifest.json", "service-worker.js", "service_worker.js", "background.js",
        "content-script.js", "content_script.js", "offscreen.html", "offscreen.js",
        "popup.html", "popup.js", "mv3_lint.py",
    }
    has_mv3_file = any(b in mv3_files for b in basenames) or any(
        "chrome-extension" in f or "/mv3" in f or "mv3_" in f for f in files
    )
    has_mv3_kw = bool(re.search(
        r"\b(chrome\s+extension|chrome-extension|browser\s+extension|manifest\s*v3|manifest\.json|"
        r"mv3|declarativenetrequest|service\s+worker|service-worker|offscreen\s+document|"
        r"content\s+script|webextension|chrome\.runtime|chrome\.tabs|chrome\.storage)\b",
        low,
    ))
    if has_mv3_file or has_mv3_kw:
        _add_skill("chrome-extension-mv3")

    ui_exts = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
    non_mv3_ui_files = [
        f for f in files
        if Path(f).suffix.lower() in ui_exts and Path(f).name.lower() not in ("popup.html", "offscreen.html")
    ]
    has_ui_file = bool(non_mv3_ui_files)
    has_ui_kw = bool(re.search(
        r"\b(css|html|ui|ux|frontend|front-end|aesthetics?|typography|glassmorphism|"
        r"dark\s+mode|light\s+mode|contrast|wcag|micro-animations?|animations?|"
        r"design\s+tokens?|design\s+system|styles?|styling|theme|layout|cards?|badges?|"
        r"pills?|modals?|drawers?|dropdowns?|sidebars?|buttons?|icons?|responsive)\b",
        low,
    ))
    if has_ui_file or has_ui_kw:
        _add_skill("frontend-art-direction")

    seo_files = {"llms.txt", "llms-full.txt", "robots.txt", "sitemap.xml"}
    has_seo_file = any(b in seo_files for b in basenames) or any(
        "geo-seo" in f or "llms.txt" in f or "llms-full.txt" in f for f in files
    )
    has_seo_kw = bool(re.search(
        r"\b(seo|geo|aio|llms\.txt|llms-full\.txt|citability|metadata|meta\s+tags?|"
        r"opengraph|open\s+graph|json-ld|schema\.org|structured\s+data|microdata|"
        r"robots\.txt|sitemap|canonical|search\s+engine|ai\s+search|ai\s+visibility|e-e-a-t)\b",
        low,
    ))
    if has_seo_file or has_seo_kw:
        _add_skill("geo-seo-audit")

    has_perf_file = any(
        "benchmark" in f or "bench_" in f or "_bench." in f or "perf_" in f or "profiler" in f
        for f in files
    )
    has_perf_kw = bool(re.search(
        r"\b(perf|performance|benchmarks?|benchmarking|latency|throughput|"
        r"memory\s+leak|profiling|profiler|flamegraph|time\s+complexity|bottleneck|"
        r"load\s+test|speedup)\b",
        low,
    ))
    if has_perf_file or has_perf_kw:
        _add_skill("perf-benchmark")

    for slug in sorted(catalog):
        if slug in low and slug not in matched:
            matched.append(slug)

    return matched


def _infer_item_phase(item_text: str, allowed_files: list[str], skills: list[str]) -> int:
    low = (item_text or "").lower()
    files = [str(f).replace(chr(92), "/") for f in (allowed_files or []) if f]
    is_test_only_files = bool(files) and all(Path(f).name.startswith("test_") for f in files)
    is_test_intent = bool(re.search(
        r"\b(unit\s+tests?|unittest|test\s+suite|write\s+tests?|add\s+tests?|"
        r"regression\s+tests?|gate\s+verification)\b",
        low,
    )) or bool(re.match(r"^\s*(test|verify|validate|check)\b", low))
    if is_test_only_files or is_test_intent:
        return 5
    if "perf-benchmark" in skills or re.search(r"\b(benchmarks?|benchmarking|profiling|profiler|latency|load\s+test)\b", low):
        return 4
    if "geo-seo-audit" in skills or re.search(r"\b(seo|llms\.txt|json-ld|schema\.org|opengraph|citability|integrate|wire\s+up)\b", low):
        return 3
    if "frontend-art-direction" in skills or any(
        Path(f).suffix.lower() in (".css", ".html", ".js") and "service" not in f.lower()
        for f in files if not f.endswith(".py")
    ):
        return 2
    if "chrome-extension-mv3" in skills:
        return 1
    if re.search(r"\b(architect|schema|database|migration|ast|blast|graph|core|parser|engine|protocol|model)\b", low):
        return 0
    return 1


def _assign_stage_topology(
    draft_tasks: list[dict], next_num: int, base_stage: int = 1
) -> tuple[list[dict], list[dict]]:
    n = len(draft_tasks)
    if n == 0:
        return [], []

    phases = [
        _infer_item_phase(t["goal"], t.get("allowed_files") or [], t.get("skills") or [])
        for t in draft_tasks
    ]
    explicit_deps: list[set[int]] = [set() for _ in range(n)]

    for i, t in enumerate(draft_tasks):
        low_i = (t["goal"] or "").lower()
        for m in re.finditer(
            r"\b(?:after|once|following|depends\s+on|depending\s+on|requires|based\s+on|from)\s+"
            r"(?:step|task|item|stage|#)?\s*([1-9][0-9]*)\b",
            low_i,
        ):
            ref_idx = int(m.group(1)) - 1
            if 0 <= ref_idx < n and ref_idx != i:
                explicit_deps[i].add(ref_idx)

        for m in re.finditer(
            r"\b(?:after|once|following|depends\s+on|depending\s+on|requires)\s+([a-z0-9_./ -]{3,40})",
            low_i,
        ):
            phrase = m.group(1)
            tokens = [
                tok for tok in re.findall(r"[a-z0-9_./-]{4,}", phrase)
                if tok not in ("step", "task", "item", "stage", "that", "this", "with", "from", "into")
            ]
            for j, other in enumerate(draft_tasks):
                if j == i or i in explicit_deps[j]:
                    continue
                other_low = (other["goal"] or "").lower()
                if any(tok in other_low for tok in tokens) and phases[j] <= phases[i]:
                    explicit_deps[i].add(j)

    deps: list[set[int]] = [set(s) for s in explicit_deps]

    for i in range(n):
        earlier_phases = [
            phases[j] for j in range(n)
            if j != i and phases[j] < phases[i] and i not in deps[j]
        ]
        if earlier_phases:
            target_phase = max(earlier_phases)
            for j in range(n):
                if j != i and phases[j] == target_phase and i not in deps[j]:
                    deps[i].add(j)

    same_phase_all = len(set(phases)) == 1
    for i in range(n):
        low_i = (draft_tasks[i]["goal"] or "").lower()
        if re.search(r"\b(in\s+parallel|independently|concurrently)\b", low_i):
            continue
        same_prev = [
            j for j in range(i)
            if phases[j] == phases[i] and i not in deps[j]
        ]
        if not same_prev:
            continue
        prev_j = same_prev[-1]
        files_i = set(draft_tasks[i].get("allowed_files") or [])
        files_j = set(draft_tasks[prev_j].get("allowed_files") or [])
        has_seq_word = bool(re.search(r"\b(then|next|after|subsequently|finally|also|second|third)\b", low_i))
        if same_phase_all or has_seq_word or bool(files_i & files_j):
            deps[i].add(prev_j)

    depths = [0] * n
    for _ in range(n + 1):
        changed = False
        for i in range(n):
            for d in list(deps[i]):
                if i in deps[d]:
                    if (phases[d], d) <= (phases[i], i):
                        deps[d].discard(i)
                    else:
                        deps[i].discard(d)
                        continue
                if depths[d] + 1 > depths[i]:
                    depths[i] = depths[d] + 1
                    changed = True
        if not changed:
            break

    unique_depths = sorted(set(depths))
    depth_to_offset = {d: idx for idx, d in enumerate(unique_depths)}
    order = sorted(range(n), key=lambda i: (depth_to_offset[depths[i]], phases[i], i))

    orig_to_tid: dict[int, str] = {}
    for new_pos, orig_idx in enumerate(order):
        orig_to_tid[orig_idx] = f"T-{next_num + new_pos:03d}"

    ordered_tasks: list[dict] = []
    stage_buckets: dict[int, list[str]] = {}
    for orig_idx in order:
        t = dict(draft_tasks[orig_idx])
        tid = orig_to_tid[orig_idx]
        stg_num = base_stage + depth_to_offset[depths[orig_idx]]
        stg_label = f"Stage {stg_num:02d}"
        dep_ids = sorted(
            (orig_to_tid[d] for d in deps[orig_idx] if depth_to_offset[depths[d]] < depth_to_offset[depths[orig_idx]]),
            key=lambda x: int(x.split("-")[1]),
        )
        t["id"] = tid
        t["stage"] = stg_num
        t["stage_label"] = stg_label
        t["depends"] = ", ".join(dep_ids) if dep_ids else "none"
        t["depends_on"] = dep_ids
        ordered_tasks.append(t)
        stage_buckets.setdefault(stg_num, []).append(tid)

    stages_summary = [
        {"stage": s_num, "label": f"Stage {s_num:02d}", "tasks": t_ids}
        for s_num, t_ids in sorted(stage_buckets.items())
    ]
    return ordered_tasks, stages_summary


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
    raw_base_stage = body.get("stage")
    try:
        base_stage = max(1, int(str(raw_base_stage).strip())) if raw_base_stage is not None else 1
    except (ValueError, TypeError):
        base_stage = 1
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

    blast = compute_conversation_blast_radius(root, full_text, invoke_graft=True, fallback_defaults=True)
    items = _extract_discussion_items(full_text)
    next_num = _next_task_number(flow_root)
    draft_tasks: list[dict] = []

    for idx, item in enumerate(items):
        item_blast = compute_conversation_blast_radius(root, item, invoke_graft=False, fallback_defaults=False)
        item_files = list(item_blast["affected_files"] or blast["affected_files"])
        for f in item_files:
            if f not in blast["affected_files"]:
                blast["affected_files"].append(f)

        title = item.rstrip(".").strip()
        if len(title) > 78:
            title = title[:75].rsplit(" ", 1)[0] + "..."

        assess = _assess_task_complexity(item, item_files)
        req_model = str(body.get("model") or "").strip()
        req_tool = str(body.get("tool") or "").strip()
        task_model = (
            req_model
            if req_model and req_model not in ("swe-2-high", "gemini-4-argon-high")
            else assess["model"]
        )
        task_tool = req_tool or ("ollama" if "ollama" in task_model.lower() or "local" in task_model.lower() else "devin")
        task_effort = str(body.get("effort") or assess["effort"]).strip()
        skills = map_task_skills(root, item, item_files)
        role = "developer"
        criteria = [
            f"C-01: {title} implemented within allowed files ({', '.join(item_files[:3])}).",
            f"C-02: Verification suite passes cleanly: python -m unittest discover -s {flow_root.name}/tests.",
        ]
        budget = estimate_task_budget(
            prompt_text=item,
            blast_files=item_files,
            effort=task_effort,
            complexity=assess["complexity"],
            model=task_model,
            tool=task_tool,
            root=root,
            flow_root=flow_root,
        )
        draft_tasks.append({
            "title": title,
            "role": role,
            "tool": task_tool,
            "effort": task_effort,
            "complexity": assess["complexity"],
            "tier": assess["tier"],
            "model": task_model,
            "skills": skills,
            "goal": item,
            "allowed": item_files,
            "allowed_files": item_files,
            "blast_radius": item_files,
            "criteria": criteria,
            "planned_input_tokens": budget["planned_input_tokens"],
            "planned_output_tokens": budget["planned_output_tokens"],
            "planned_tokens": budget["planned_tokens"],
            "planned_cost_usd": budget["planned_cost_usd"],
            "rate_per_1m": budget["rate_per_1m"],
            "free": budget["free"],
        })

    tasks, stages_summary = _assign_stage_topology(draft_tasks, next_num=next_num, base_stage=base_stage)
    total_input_tokens = sum(int(t.get("planned_input_tokens", 0)) for t in tasks)
    total_output_tokens = sum(int(t.get("planned_output_tokens", 0)) for t in tasks)
    total_planned_tokens = sum(int(t.get("planned_tokens", 0)) for t in tasks)
    total_planned_cost = round(sum(float(t.get("planned_cost_usd", 0.0)) for t in tasks), 6)

    result = {
        "ok": True,
        "project": str(root),
        "thread": thread,
        "summary": f"Synthesized {len(tasks)} atomic task contracts across {len(stages_summary)} stages with AST blast radius ({len(blast['affected_files'])} affected files).",
        "symbols": blast["symbols"],
        "blast_radius": blast,
        "stages": stages_summary,
        "planned_input_tokens": total_input_tokens,
        "planned_output_tokens": total_output_tokens,
        "planned_tokens": total_planned_tokens,
        "planned_cost_usd": total_planned_cost,
        "tasks": tasks,
        "pool": tasks,
    }
    if body.get("register") is True or body.get("approve") is True:
        reg = register_task_pool(root, tasks, default_stage=str(base_stage))
        result["registered"] = reg.get("registered", [])
        result["files"] = reg.get("files", [])
        result["plan_files"] = reg.get("plan_files", [])
    return result


def register_task_pool(target_root: Path, tasks_payload: list[dict], default_stage: str = "7") -> dict:
    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    tasks_dir = flow_root / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = flow_root / "state" / "tasks.md"

    next_num = _next_task_number(flow_root)
    registered_ids: list[str] = []
    created_files: list[str] = []
    created_plan_files: list[str] = []
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
        raw_stage = str(raw.get("stage") or default_stage).strip()
        m_stg = re.search(r"\d+", raw_stage)
        stage = str(int(m_stg.group(0))) if m_stg else (raw_stage or str(default_stage))
        tool = str(raw.get("tool") or "devin").strip()
        model = str(raw.get("model") or "swe-2-high").strip()
        effort = str(raw.get("effort") or "high").strip()
        complexity_val = raw.get("complexity") or ("high" if effort in ("high", "xhigh", "max", "ultra") else "standard")
        raw_dep = raw.get("depends") or raw.get("depends_on") or "none"
        if isinstance(raw_dep, list):
            depends = ", ".join(str(d).strip() for d in raw_dep if str(d).strip()) or "none"
        else:
            depends = str(raw_dep).strip() or "none"
        goal = str(raw.get("goal") or title).strip()
        allowed = raw.get("allowed_files") or raw.get("allowed") or []
        raw_skills = raw.get("skills")
        if isinstance(raw_skills, list):
            skills_list = [str(s).strip() for s in raw_skills if str(s).strip() and str(s).strip().lower() != "none"]
        elif isinstance(raw_skills, str) and raw_skills.strip():
            skills_list = [
                s.strip() for s in raw_skills.split(",")
                if s.strip() and s.strip().lower() != "none"
            ]
        else:
            skills_list = map_task_skills(target_root, f"{title}\n{goal}", allowed)
        skills_str = ", ".join(skills_list) if skills_list else "none"
        raw_criteria = raw.get("criteria") or []

        budget = estimate_task_budget(
            prompt_text=goal,
            blast_files=allowed,
            effort=effort,
            complexity=complexity_val,
            model=model,
            tool=tool,
            root=target_root,
            flow_root=flow_root,
        )
        planned_input_tokens = int(raw["planned_input_tokens"]) if raw.get("planned_input_tokens") is not None else budget["planned_input_tokens"]
        planned_output_tokens = int(raw["planned_output_tokens"]) if raw.get("planned_output_tokens") is not None else budget["planned_output_tokens"]
        if raw.get("planned_tokens") is not None:
            planned_tokens = int(raw["planned_tokens"])
            if raw.get("planned_input_tokens") is None:
                planned_input_tokens = max(0, planned_tokens - planned_output_tokens)
        else:
            planned_tokens = planned_input_tokens + planned_output_tokens

        pricing_info = lookup_model_pricing(model=model, tool=tool, flow_root=flow_root)
        if raw.get("planned_cost_usd") is not None:
            planned_cost_usd = round(float(raw["planned_cost_usd"]), 6)
        else:
            planned_cost_usd = round(
                (planned_input_tokens * pricing_info["input_per_1m"] + planned_output_tokens * pricing_info["output_per_1m"]) / 1_000_000,
                6,
            )

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
        plan_path = tasks_dir / f"{tid}.plan.json"

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
            f"Skills: {skills_str}",
            f"Planned tokens: {planned_tokens} (in: {planned_input_tokens}, out: {planned_output_tokens})",
            f"Planned cost USD: ${planned_cost_usd:.4f}",
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

        plan_record = {
            "task_id": tid,
            "id": tid,
            "title": title,
            "stage": int(stage) if str(stage).isdigit() else stage,
            "role": role,
            "tool": tool,
            "model": model,
            "effort": effort,
            "complexity": complexity_val,
            "planned_input_tokens": planned_input_tokens,
            "planned_output_tokens": planned_output_tokens,
            "planned_tokens": planned_tokens,
            "planned_cost_usd": planned_cost_usd,
            "rate_per_1m": pricing_info["rate_per_1m"],
            "input_per_1m": pricing_info["input_per_1m"],
            "output_per_1m": pricing_info["output_per_1m"],
            "free": pricing_info["free"],
            "blast_radius": list(allowed),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        plan_path.write_text(json.dumps(plan_record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        row = [""] * len(cols)
        row[cols.index("ID")] = tid
        row[cols.index("Title")] = title
        row[cols.index("Stage")] = stage
        row[cols.index("Role")] = role
        row[cols.index("Tool")] = tool
        row[cols.index("Status")] = "ready"
        row[cols.index("Depends on")] = "" if depends == "none" else depends
        notes_str = f"model={model}; effort={effort}"
        if skills_list:
            notes_str += f"; skills={','.join(skills_list)}"
        row[cols.index("Notes")] = notes_str
        row[cols.index("Updated")] = now_str
        if tid in idx_map:
            rows[idx_map[tid]] = row
        else:
            idx_map[tid] = len(rows)
            rows.append(row)

        rel_path = file_path.relative_to(target_root).as_posix() if file_path.is_relative_to(target_root) else str(file_path)
        rel_plan_path = plan_path.relative_to(target_root).as_posix() if plan_path.is_relative_to(target_root) else str(plan_path)
        registered_ids.append(tid)
        created_files.append(rel_path)
        created_plan_files.append(rel_plan_path)
        normalized_tasks.append({
            "id": tid,
            "title": title,
            "stage": stage,
            "role": role,
            "tool": tool,
            "model": model,
            "effort": effort,
            "skills": skills_list,
            "planned_input_tokens": planned_input_tokens,
            "planned_output_tokens": planned_output_tokens,
            "planned_tokens": planned_tokens,
            "planned_cost_usd": planned_cost_usd,
            "file": rel_path,
            "plan_file": rel_plan_path,
        })

    if registered_ids:
        ledger.save(ledger_file, lines, head, end, rows)

    return {
        "ok": bool(registered_ids),
        "registered": registered_ids,
        "files": created_files,
        "plan_files": created_plan_files,
        "tasks": normalized_tasks,
        "task_id": registered_ids[0] if registered_ids else "",
        "file": created_files[0] if created_files else "",
    }


def parse_depends_on(raw) -> list[str]:
    """Extract normalized T-NNN task IDs from a `Depends on` value (list or string)."""
    if not raw:
        return []
    if isinstance(raw, list):
        text = " ".join(str(x) for x in raw)
    else:
        text = str(raw)
    if text.strip().lower() in ("none", "-", "n/a"):
        return []
    seen: list[str] = []
    for m in re.finditer(r"(?i)\b(T-\d+)\b", text):
        tid = m.group(1).upper()
        if tid not in seen:
            seen.append(tid)
    return seen


def _parse_stage_number(raw) -> int | None:
    """Parse stage values like `1`, `'02'`, `'Stage 03'` into a positive integer."""
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw if raw >= 1 else None
    s = str(raw).strip()
    if not s:
        return None
    m = re.search(r"\d+", s)
    if not m:
        return None
    val = int(m.group(0))
    return val if val >= 1 else None


def inspect_worktree_status(target_root: Path, worktree_str: str, branch_str: str = "") -> dict:
    """Inspect whether a task's declared worktree exists on disk and its git working-tree state."""
    wt_raw = (worktree_str or "").strip()
    br_raw = (branch_str or "").strip()
    if not wt_raw or wt_raw.lower() == "none":
        return {
            "path": "",
            "branch": br_raw if br_raw.lower() != "none" else "",
            "exists": False,
            "status": "none",
            "clean": True,
            "changed_count": 0,
        }
    try:
        wt_path = Path(wt_raw)
        exists = wt_path.is_dir()
    except OSError:
        exists = False
        wt_path = None

    if not exists or wt_path is None:
        return {
            "path": wt_raw,
            "branch": br_raw,
            "exists": False,
            "status": "not created",
            "clean": True,
            "changed_count": 0,
        }

    code, br_out = _git(wt_path, "rev-parse", "--abbrev-ref", "HEAD")
    active_branch = br_out.strip().splitlines()[0] if (code == 0 and br_out.strip()) else br_raw
    _, st_out = _git(wt_path, "status", "--porcelain")
    changed = [ln for ln in (st_out or "").splitlines() if ln.strip()]
    clean = len(changed) == 0
    return {
        "path": wt_raw,
        "branch": active_branch,
        "exists": True,
        "status": "active (clean)" if clean else f"active ({len(changed)} modified)",
        "clean": clean,
        "changed_count": len(changed),
    }


def detect_dag_cycles(deps_map: dict[str, list[str]], start_tid: str = "") -> list[str]:
    """Detect a directed cycle in `deps_map` (task -> list of prerequisite tasks).

    Returns the cycle path `[T-A, T-B, ..., T-A]` if a cycle exists, or `[]` if acyclic.
    """
    state: dict[str, int] = {}
    stack: list[str] = []

    nodes = list(deps_map.keys())
    if start_tid and start_tid in deps_map:
        nodes = [start_tid] + [n for n in sorted(nodes) if n != start_tid]
    else:
        nodes = sorted(nodes)

    def dfs(u: str) -> list[str]:
        state[u] = 1
        stack.append(u)
        for v in deps_map.get(u, []):
            st = state.get(v, 0)
            if st == 1:
                idx = stack.index(v)
                return stack[idx:] + [v]
            if st == 0 and v in deps_map:
                cyc = dfs(v)
                if cyc:
                    return cyc
        stack.pop()
        state[u] = 2
        return []

    for node in nodes:
        if state.get(node, 0) == 0:
            found = dfs(node)
            if found:
                return found
    return []


def move_task_stage(target_root: Path, body: dict) -> tuple[int, dict]:
    """Validate a stage move request against the task DAG and atomically update ledger + Task File."""
    tid = str(body.get("id") or body.get("task_id") or body.get("task") or "").strip().upper()
    if not re.fullmatch(r"T-\d+", tid):
        return 400, {"ok": False, "error": f"Valid task ID (T-NNN) required, got: {tid or 'empty'}"}

    raw_stage = (
        body.get("stage")
        if "stage" in body
        else (body.get("target_stage") if "target_stage" in body else body.get("to_stage"))
    )
    target_stage = _parse_stage_number(raw_stage)
    if target_stage is None:
        return 400, {"ok": False, "error": f"Invalid target stage: {raw_stage}"}

    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    ledger_file = flow_root / "state" / "tasks.md"
    tasks_dir = flow_root / "tasks"
    if not ledger_file.is_file():
        return 404, {"ok": False, "error": f"Task ledger not found for project: {target_root.name}"}

    lines, cols, rows, head, end = ledger.load(ledger_file)
    idx_map = {r[0].strip().upper(): i for i, r in enumerate(rows) if r and r[0].strip()}
    if tid not in idx_map:
        return 404, {"ok": False, "error": f"Task not found in ledger: {tid}"}

    stage_col = cols.index("Stage")
    dep_col = cols.index("Depends on")
    upd_col = cols.index("Updated")

    stage_map: dict[str, int] = {}
    deps_map: dict[str, list[str]] = {}
    task_files_map: dict[str, Path] = {}

    for r in rows:
        r_tid = r[0].strip().upper()
        if not r_tid.startswith("T-"):
            continue
        r_stage = _parse_stage_number(r[stage_col]) or 1
        r_deps = parse_depends_on(r[dep_col])
        if tasks_dir.is_dir():
            hits = sorted(tasks_dir.glob(f"{r_tid}*.md"))
            if hits:
                task_files_map[r_tid] = hits[0]
                if not r_deps:
                    try:
                        tf_text = hits[0].read_text(encoding="utf-8-sig")
                        m_dep = re.search(r"^Depends on:\s*(.+?)\s*$", tf_text, re.M)
                        if m_dep:
                            r_deps = parse_depends_on(m_dep.group(1))
                    except Exception:
                        pass
        stage_map[r_tid] = r_stage
        deps_map[r_tid] = r_deps

    has_dep_override = "depends" in body or "depends_on" in body
    if has_dep_override:
        deps_map[tid] = parse_depends_on(
            body.get("depends") if "depends" in body else body.get("depends_on")
        )

    from_stage = stage_map.get(tid, 1)

    # 1. Check DAG for cyclic dependencies before any mutation
    cycle = detect_dag_cycles(deps_map, start_tid=tid)
    if cycle:
        cycle_str = " -> ".join(cycle)
        msg = f"Cannot move {tid} to Stage {target_stage:02d}: cyclic dependency detected in DAG ({cycle_str})"
        return 400, {
            "ok": False,
            "collision": True,
            "collision_type": "cycle",
            "task_id": tid,
            "from_stage": from_stage,
            "target_stage": target_stage,
            "cycle": cycle,
            "diagnostic": msg,
            "error": msg,
        }

    # 2. Check upstream prerequisites (direct and transitive) for stage collision / inversion
    visited_up: set[str] = set()
    queue_up = list(deps_map.get(tid, []))
    while queue_up:
        dep_id = queue_up.pop(0)
        if dep_id in visited_up:
            continue
        visited_up.add(dep_id)
        dep_stage = stage_map.get(dep_id)
        if dep_stage is not None and target_stage <= dep_stage:
            msg = (
                f"Cannot move {tid} to Stage {target_stage:02d}: "
                f"depends on {dep_id} in Stage {dep_stage:02d} (dependency inversion)"
            )
            return 400, {
                "ok": False,
                "collision": True,
                "collision_type": "dependency_inversion",
                "task_id": tid,
                "conflicting_task": dep_id,
                "conflicting_stage": dep_stage,
                "from_stage": from_stage,
                "target_stage": target_stage,
                "diagnostic": msg,
                "error": msg,
            }
        for parent_dep in deps_map.get(dep_id, []):
            if parent_dep not in visited_up:
                queue_up.append(parent_dep)

    # 3. Check downstream dependents (direct and transitive) for stage collision / inversion
    reverse_deps: dict[str, list[str]] = {}
    for other_tid, other_deps in deps_map.items():
        for d in other_deps:
            reverse_deps.setdefault(d, []).append(other_tid)

    visited_down: set[str] = set()
    queue_down = list(reverse_deps.get(tid, []))
    while queue_down:
        child_id = queue_down.pop(0)
        if child_id in visited_down:
            continue
        visited_down.add(child_id)
        child_stage = stage_map.get(child_id)
        if child_stage is not None and target_stage >= child_stage:
            msg = (
                f"Cannot move {tid} to Stage {target_stage:02d}: "
                f"dependent {child_id} in Stage {child_stage:02d} depends on {tid} (dependency inversion)"
            )
            return 400, {
                "ok": False,
                "collision": True,
                "collision_type": "dependency_inversion",
                "task_id": tid,
                "conflicting_task": child_id,
                "conflicting_stage": child_stage,
                "from_stage": from_stage,
                "target_stage": target_stage,
                "diagnostic": msg,
                "error": msg,
            }
        for grand_child in reverse_deps.get(child_id, []):
            if grand_child not in visited_down:
                queue_down.append(grand_child)

    # 4. Safe move: atomically update Task File and tasks.md ledger, then re-link stage ordering
    rel_contract_file = ""
    tf = task_files_map.get(tid)
    if tf and tf.is_file():
        rel_contract_file = tf.relative_to(target_root).as_posix() if tf.is_relative_to(target_root) else str(tf)
        try:
            raw_tf = tf.read_text(encoding="utf-8-sig")
            parts = re.split(r"(^## Result[ \t]*$)", raw_tf, maxsplit=1, flags=re.M)
            head_part = parts[0]
            rest_part = "".join(parts[1:])
            if re.search(r"^Stage:\s*.*$", head_part, flags=re.M):
                head_part = re.sub(r"^Stage:\s*.*$", f"Stage: {target_stage}", head_part, count=1, flags=re.M)
            if has_dep_override and re.search(r"^Depends on:\s*.*$", head_part, flags=re.M):
                dep_val = ", ".join(deps_map[tid]) if deps_map[tid] else "none"
                head_part = re.sub(r"^Depends on:\s*.*$", f"Depends on: {dep_val}", head_part, count=1, flags=re.M)
            ledger._write_atomic(tf, head_part + rest_part)
        except Exception as e:
            return 500, {"ok": False, "error": f"Failed to update Task File for {tid}: {e}"}

    row_i = idx_map[tid]
    rows[row_i][stage_col] = str(target_stage)
    if has_dep_override:
        rows[row_i][dep_col] = ", ".join(deps_map[tid])
    rows[row_i][upd_col] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    stage_map[tid] = target_stage

    indexed_rows = list(enumerate(rows))
    indexed_rows.sort(
        key=lambda pair: (
            stage_map.get(pair[1][0].strip().upper(), 999),
            pair[0],
        )
    )
    reordered_rows = [r for _, r in indexed_rows]
    ledger.save(ledger_file, lines, head, end, reordered_rows)

    stage_buckets: dict[int, list[str]] = {}
    for r in reordered_rows:
        r_tid = r[0].strip().upper()
        if r_tid.startswith("T-"):
            s_num = stage_map.get(r_tid, 1)
            stage_buckets.setdefault(s_num, []).append(r_tid)

    stages_summary = [
        {"stage": s_num, "label": f"Stage {s_num:02d}", "tasks": t_ids}
        for s_num, t_ids in sorted(stage_buckets.items())
    ]

    return 200, {
        "ok": True,
        "collision": False,
        "task_id": tid,
        "from_stage": from_stage,
        "to_stage": target_stage,
        "stage": str(target_stage),
        "stage_label": f"Stage {target_stage:02d}",
        "depends_on": deps_map.get(tid, []),
        "dependents": sorted(reverse_deps.get(tid, [])),
        "file": rel_contract_file,
        "stages": stages_summary,
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
    depends_str = str(task_obj.get("depends") or "").strip()
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
                    elif line.startswith("Depends on:") and not depends_str:
                        depends_str = line.split(":", 1)[1].strip()
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

    depends_on = parse_depends_on(depends_str)
    wt_status = inspect_worktree_status(
        target_root,
        str(task_obj.get("worktree") or ""),
        str(task_obj.get("branch") or ""),
    )

    enriched = dict(task_obj)
    enriched["allowed_files"] = full_allowed
    enriched["checks"] = checks
    enriched["effort"] = effort
    enriched["contract_file"] = contract_file
    enriched["depends"] = ", ".join(depends_on) if depends_on else (depends_str or "none")
    enriched["depends_on"] = depends_on
    enriched["worktree_status"] = wt_status

    return {
        "ok": True,
        "task": enriched,
        "contract": {
            "file": contract_file,
            "goal": enriched.get("goal", ""),
            "allowed_files": full_allowed,
            "criteria": enriched.get("criteria", []),
            "checks": checks,
            "stage": enriched.get("stage", ""),
            "depends_on": depends_on,
        },
        "worktree_status": wt_status,
        "recent_log": recent_log,
        "git": get_git_summary(target_root),
    }


def _parse_iso_seconds(start_val, end_val) -> float | None:
    if not start_val or not end_val:
        return None
    try:
        s_dt = datetime.fromisoformat(str(start_val).replace("Z", "+00:00"))
        e_dt = datetime.fromisoformat(str(end_val).replace("Z", "+00:00"))
        return max(0.0, (e_dt - s_dt).total_seconds())
    except (TypeError, ValueError, AttributeError):
        return None


def _num_field(obj: dict, keys: tuple[str, ...]) -> float | None:
    if not isinstance(obj, dict):
        return None
    for k in keys:
        val = obj.get(k)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val)
        if isinstance(val, str) and val.strip():
            try:
                return float(val.strip().lstrip("$"))
            except ValueError:
                continue
    for sub_key in ("usage", "telemetry", "metrics"):
        sub = obj.get(sub_key)
        if isinstance(sub, dict):
            for k in keys:
                val = sub.get(k)
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    return float(val)
                if isinstance(val, str) and val.strip():
                    try:
                        return float(val.strip().lstrip("$"))
                    except ValueError:
                        continue
    return None


def _str_field(obj: dict, keys: tuple[str, ...]) -> str:
    if not isinstance(obj, dict):
        return ""
    for k in keys:
        val = obj.get(k)
        if isinstance(val, str) and val.strip() and val.strip().lower() != "unknown":
            return val.strip()
    return ""


def _extract_task_runtime_telemetry(runtime_dir: Path, tid: str) -> dict:
    """Ingest actual token usage, execution time, and model calls for `tid` from `.runtime/`."""
    has_telemetry = False
    in_tokens = 0
    out_tokens = 0
    total_tokens = 0
    explicit_tokens = False
    explicit_cost_usd: float | None = None
    exec_seconds = 0.0
    model_calls = 0
    attempts_count = 0
    actual_model = ""
    actual_tool = ""

    if not runtime_dir.is_dir():
        return {
            "has_telemetry": False,
            "actual_input_tokens": 0,
            "actual_output_tokens": 0,
            "actual_tokens": 0,
            "explicit_cost_usd": None,
            "execution_time_seconds": 0.0,
            "model_calls": 0,
            "attempts": 0,
            "actual_model": "",
            "actual_tool": "",
        }

    for candidate in (runtime_dir / f"{tid}.json", runtime_dir / f"{tid}.telemetry.json"):
        if not candidate.is_file():
            continue
        try:
            raw_data = json.loads(candidate.read_text(encoding="utf-8-sig"))
        except Exception:
            continue

        attempts_list: list[dict] = []
        top_obj: dict = {}
        if isinstance(raw_data, list):
            attempts_list = [a for a in raw_data if isinstance(a, dict)]
        elif isinstance(raw_data, dict):
            top_obj = raw_data
            if isinstance(raw_data.get("attempts"), list):
                attempts_list = [a for a in raw_data["attempts"] if isinstance(a, dict)]

        if attempts_list:
            has_telemetry = True
            attempts_count += len(attempts_list)
            for att in attempts_list:
                a_in = _num_field(att, ("actual_input_tokens", "input_tokens", "prompt_tokens", "prompt_eval_count"))
                a_out = _num_field(att, ("actual_output_tokens", "output_tokens", "completion_tokens", "eval_count"))
                a_tot = _num_field(att, ("actual_tokens", "total_tokens", "tokens"))
                if a_in is not None or a_out is not None or a_tot is not None:
                    explicit_tokens = True
                    i_val = int(max(0.0, a_in or 0.0))
                    o_val = int(max(0.0, a_out or 0.0))
                    t_val = int(max(0.0, a_tot if a_tot is not None else (i_val + o_val)))
                    if a_in is None and a_out is None and t_val > 0:
                        total_tokens += t_val
                    else:
                        in_tokens += i_val
                        out_tokens += o_val
                        total_tokens += max(t_val, i_val + o_val)

                a_cost = _num_field(att, ("actual_cost_usd", "cost_usd", "total_cost_usd", "cost"))
                if a_cost is not None:
                    explicit_cost_usd = (explicit_cost_usd or 0.0) + max(0.0, a_cost)

                a_dur = _num_field(
                    att,
                    ("execution_time_seconds", "duration_seconds", "execution_time", "elapsed_seconds", "wall_seconds"),
                )
                if a_dur is None:
                    a_ms = _num_field(att, ("duration_ms", "elapsed_ms"))
                    if a_ms is not None:
                        a_dur = a_ms / 1000.0
                if a_dur is None:
                    a_dur = _parse_iso_seconds(att.get("startedAt"), att.get("finishedAt"))
                if a_dur is not None:
                    exec_seconds += max(0.0, a_dur)

                a_calls = _num_field(att, ("model_calls", "calls", "api_calls", "llm_calls", "turns", "requests"))
                model_calls += int(max(1.0, a_calls)) if a_calls is not None else 1

                m_str = _str_field(att, ("effectiveModel", "actual_model", "requestedModel", "model"))
                if m_str:
                    actual_model = m_str
                t_str = _str_field(att, ("actual_tool", "tool"))
                if t_str:
                    actual_tool = t_str

        if top_obj:
            t_in = _num_field(top_obj, ("actual_input_tokens", "input_tokens", "prompt_tokens", "prompt_eval_count"))
            t_out = _num_field(top_obj, ("actual_output_tokens", "output_tokens", "completion_tokens", "eval_count"))
            t_tot = _num_field(top_obj, ("actual_tokens", "total_tokens", "tokens"))
            t_cost = _num_field(top_obj, ("actual_cost_usd", "cost_usd", "total_cost_usd", "cost"))
            t_dur = _num_field(
                top_obj,
                ("execution_time_seconds", "duration_seconds", "execution_time", "elapsed_seconds", "attemptWallSeconds"),
            )
            t_calls = _num_field(top_obj, ("model_calls", "calls", "api_calls", "llm_calls", "turns", "requests"))
            if any(x is not None for x in (t_in, t_out, t_tot, t_cost, t_dur, t_calls)):
                has_telemetry = True
            if not explicit_tokens and (t_in is not None or t_out is not None or t_tot is not None):
                explicit_tokens = True
                in_tokens = int(max(0.0, t_in or 0.0))
                out_tokens = int(max(0.0, t_out or 0.0))
                total_tokens = int(max(float(in_tokens + out_tokens), t_tot or 0.0))
            if explicit_cost_usd is None and t_cost is not None:
                explicit_cost_usd = max(0.0, t_cost)
            if exec_seconds == 0.0 and t_dur is not None:
                exec_seconds = max(0.0, t_dur)
            if model_calls == 0 and t_calls is not None:
                model_calls = int(max(0.0, t_calls))
            if not actual_model:
                actual_model = _str_field(top_obj, ("effectiveModel", "actual_model", "requestedModel", "model"))
            if not actual_tool:
                actual_tool = _str_field(top_obj, ("actual_tool", "tool"))

    # Fallback for completed CLI attempts without inline token fields in T-NNN.json:
    # check JSON usage events in attempt logs or Jev route telemetry when attempts exist.
    if has_telemetry and not explicit_tokens and attempts_count > 0:
        for log_file in sorted(runtime_dir.glob(f"{tid}.*.log")):
            if log_file.name.endswith((".accept.log", ".test_route.log")) or ".verify." in log_file.name:
                continue
            try:
                log_text = log_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for ln in log_text.splitlines():
                s = ln.strip()
                if not (s.startswith("{") and s.endswith("}")):
                    continue
                try:
                    ev = json.loads(s)
                except Exception:
                    continue
                if not isinstance(ev, dict):
                    continue
                l_in = _num_field(ev, ("input_tokens", "prompt_tokens", "prompt_eval_count"))
                l_out = _num_field(ev, ("output_tokens", "completion_tokens", "eval_count"))
                l_tot = _num_field(ev, ("total_tokens", "actual_tokens"))
                if l_in is not None or l_out is not None or l_tot is not None:
                    explicit_tokens = True
                    in_tokens += int(max(0.0, l_in or 0.0))
                    out_tokens += int(max(0.0, l_out or 0.0))
                    total_tokens += int(max(float((l_in or 0.0) + (l_out or 0.0)), l_tot or 0.0))

        if not explicit_tokens:
            route_file = runtime_dir / f"{tid}.route.json"
            if route_file.is_file():
                try:
                    r_entries = json.loads(route_file.read_text(encoding="utf-8-sig"))
                    if isinstance(r_entries, list):
                        for entry in r_entries:
                            if not isinstance(entry, dict):
                                continue
                            jev_u = (entry.get("jev") or {}).get("usage") if isinstance(entry.get("jev"), dict) else None
                            if isinstance(jev_u, dict):
                                in_tokens += int(max(0, jev_u.get("input_tokens") or 0))
                                out_tokens += int(max(0, jev_u.get("output_tokens") or 0))
                except Exception:
                    pass
            for log_file in sorted(runtime_dir.glob(f"{tid}.*.log")):
                if log_file.name.endswith((".accept.log", ".test_route.log")) or ".verify." in log_file.name:
                    continue
                try:
                    sz = log_file.stat().st_size
                    if sz > 0:
                        out_tokens += max(1, sz // 4)
                except Exception:
                    pass
            total_tokens = in_tokens + out_tokens

    if total_tokens == 0 and (in_tokens > 0 or out_tokens > 0):
        total_tokens = in_tokens + out_tokens

    return {
        "has_telemetry": has_telemetry,
        "actual_input_tokens": in_tokens,
        "actual_output_tokens": out_tokens,
        "actual_tokens": total_tokens,
        "explicit_cost_usd": round(explicit_cost_usd, 6) if explicit_cost_usd is not None else None,
        "execution_time_seconds": round(exec_seconds, 2),
        "model_calls": model_calls,
        "attempts": attempts_count,
        "actual_model": actual_model,
        "actual_tool": actual_tool,
    }


def get_analytics_costs(project_root: Path | str | None = None) -> dict:
    """Aggregate Plan (.plan.json) vs Fact (.runtime/) token and USD cost telemetry across project tasks."""
    target_root = Path(project_root).resolve() if project_root else REPO_ROOT
    if not target_root.is_dir():
        target_root = REPO_ROOT

    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    tasks_dir = flow_root / "tasks"
    runtime_dir = tasks_dir / ".runtime"

    tasks_data = get_tasks_data(str(target_root))
    ledger_tasks = tasks_data.get("tasks", [])
    tasks_by_id: dict[str, dict] = {t["id"].upper(): dict(t) for t in ledger_tasks if t.get("id")}
    ordered_ids: list[str] = [t["id"].upper() for t in ledger_tasks if t.get("id")]

    if tasks_dir.is_dir():
        for pf in sorted(tasks_dir.glob("T-*.plan.json")):
            tid = pf.name[: -len(".plan.json")].upper()
            if re.fullmatch(r"T-\d+", tid) and tid not in tasks_by_id:
                tasks_by_id[tid] = {"id": tid, "status": "ready"}
                ordered_ids.append(tid)

    tasks_out: list[dict] = []
    stage_buckets: dict[int, dict] = {}

    total_planned_in = 0
    total_planned_out = 0
    total_planned_tokens = 0
    total_planned_usd = 0.0

    total_actual_in = 0
    total_actual_out = 0
    total_actual_tokens = 0
    total_actual_usd = 0.0

    total_exec_seconds = 0.0
    total_model_calls = 0
    count_with_plan = 0
    count_with_telemetry = 0

    actual_free_tokens = 0
    planned_free_tokens = 0

    for tid in ordered_ids:
        base = tasks_by_id[tid]
        plan_meta: dict = {}
        for plan_candidate in (
            tasks_dir / f"{tid}.plan.json" if tasks_dir.is_dir() else None,
            runtime_dir / f"{tid}.plan.json" if runtime_dir.is_dir() else None,
        ):
            if plan_candidate and plan_candidate.is_file():
                try:
                    loaded = json.loads(plan_candidate.read_text(encoding="utf-8-sig"))
                    if isinstance(loaded, dict):
                        plan_meta = loaded
                        break
                except Exception:
                    pass

        title = str(base.get("title") or plan_meta.get("title") or tid).strip()
        raw_stage = str(base.get("stage") or plan_meta.get("stage") or "1").strip()
        m_stg = re.search(r"\d+", raw_stage)
        stage_num = int(m_stg.group(0)) if m_stg else 1
        stage_str = str(stage_num)
        stage_label = f"Stage {stage_num:02d}"

        role = str(base.get("role") or plan_meta.get("role") or "developer").strip()
        planned_tool = str(plan_meta.get("tool") or base.get("tool") or "devin").strip()
        planned_model = str(plan_meta.get("model") or base.get("model") or "swe-2-high").strip()
        effort = str(plan_meta.get("effort") or base.get("effort") or "high").strip()
        status = str(base.get("status") or "ready").strip()

        has_plan = bool(plan_meta) or ("planned_tokens" in base) or ("planned_cost_usd" in base)
        if plan_meta:
            p_in = int(plan_meta.get("planned_input_tokens") or 0)
            p_out = int(plan_meta.get("planned_output_tokens") or 0)
            p_tok = (
                int(plan_meta["planned_tokens"])
                if plan_meta.get("planned_tokens") is not None
                else (p_in + p_out)
            )
            if p_in == 0 and p_out == 0 and p_tok > 0:
                p_out = min(p_tok, estimate_output_tokens(effort))
                p_in = max(0, p_tok - p_out)
            if plan_meta.get("planned_cost_usd") is not None:
                p_cost = round(float(plan_meta["planned_cost_usd"]), 6)
            else:
                p_pricing = lookup_model_pricing(model=planned_model, tool=planned_tool, flow_root=flow_root)
                p_cost = round(
                    (p_in * p_pricing["input_per_1m"] + p_out * p_pricing["output_per_1m"]) / 1_000_000,
                    6,
                )
        elif "planned_tokens" in base or "planned_cost_usd" in base:
            p_in = int(base.get("planned_input_tokens") or 0)
            p_out = int(base.get("planned_output_tokens") or 0)
            p_tok = int(base.get("planned_tokens") or (p_in + p_out))
            p_cost = round(float(base.get("planned_cost_usd") or 0.0), 6)
        elif tasks_dir.is_dir() and any(tasks_dir.glob(f"{tid}*.md")):
            est = estimate_task_budget(
                prompt_text=str(base.get("goal") or title),
                blast_files=base.get("allowed_files") or [],
                effort=effort,
                model=planned_model,
                tool=planned_tool,
                root=target_root,
                flow_root=flow_root,
            )
            p_in = est["planned_input_tokens"]
            p_out = est["planned_output_tokens"]
            p_tok = est["planned_tokens"]
            p_cost = est["planned_cost_usd"]
            has_plan = True
        else:
            p_in = 0
            p_out = 0
            p_tok = 0
            p_cost = 0.0

        if has_plan:
            count_with_plan += 1

        rt = _extract_task_runtime_telemetry(runtime_dir, tid)
        has_telemetry = rt["has_telemetry"]
        if has_telemetry:
            count_with_telemetry += 1

        actual_model = rt["actual_model"] or planned_model
        actual_tool = rt["actual_tool"] or planned_tool
        pricing = lookup_model_pricing(model=actual_model, tool=actual_tool, flow_root=flow_root)
        is_free = bool(
            pricing.get("free")
            or actual_tool.lower() == "ollama"
            or "ollama" in actual_model.lower()
            or "local" in actual_model.lower()
        )

        a_in = rt["actual_input_tokens"]
        a_out = rt["actual_output_tokens"]
        a_tok = rt["actual_tokens"]

        if rt["explicit_cost_usd"] is not None:
            a_cost = rt["explicit_cost_usd"]
        elif a_tok > 0:
            if a_in > 0 or a_out > 0:
                a_cost = round(
                    (a_in * pricing["input_per_1m"] + a_out * pricing["output_per_1m"]) / 1_000_000,
                    6,
                )
            else:
                a_cost = round((a_tok * pricing["rate_per_1m"]) / 1_000_000, 6)
        else:
            a_cost = 0.0

        delta_tokens = a_tok - p_tok
        delta_usd = round(a_cost - p_cost, 6)
        savings_usd = round(p_cost - a_cost, 6)
        if p_cost > 0:
            delta_pct = round(((a_cost - p_cost) / p_cost) * 100.0, 2)
        elif a_cost == 0.0:
            delta_pct = 0.0
        else:
            delta_pct = 100.0

        task_row = {
            "id": tid,
            "task_id": tid,
            "title": title,
            "stage": stage_str,
            "stage_num": stage_num,
            "stage_label": stage_label,
            "role": role,
            "tool": actual_tool,
            "model": actual_model,
            "planned_model": planned_model,
            "actual_model": actual_model,
            "effort": effort,
            "status": status,
            "has_plan": has_plan,
            "has_telemetry": has_telemetry,
            "planned_input_tokens": p_in,
            "planned_output_tokens": p_out,
            "planned_tokens": p_tok,
            "planned_cost_usd": p_cost,
            "plan_usd": p_cost,
            "actual_input_tokens": a_in,
            "actual_output_tokens": a_out,
            "actual_tokens": a_tok,
            "actual_cost_usd": a_cost,
            "fact_usd": a_cost,
            "delta_tokens": delta_tokens,
            "delta_usd": delta_usd,
            "delta_pct": delta_pct,
            "savings_usd": savings_usd,
            "execution_time_seconds": rt["execution_time_seconds"],
            "duration_seconds": rt["execution_time_seconds"],
            "model_calls": rt["model_calls"],
            "attempts": rt["attempts"],
            "rate_per_1m": pricing["rate_per_1m"],
            "free": is_free,
        }
        tasks_out.append(task_row)

        total_planned_in += p_in
        total_planned_out += p_out
        total_planned_tokens += p_tok
        total_planned_usd = round(total_planned_usd + p_cost, 6)

        total_actual_in += a_in
        total_actual_out += a_out
        total_actual_tokens += a_tok
        total_actual_usd = round(total_actual_usd + a_cost, 6)

        total_exec_seconds = round(total_exec_seconds + rt["execution_time_seconds"], 2)
        total_model_calls += rt["model_calls"]

        if is_free:
            actual_free_tokens += a_tok
            planned_free_tokens += p_tok

        sb = stage_buckets.setdefault(
            stage_num,
            {
                "stage": stage_str,
                "stage_num": stage_num,
                "label": stage_label,
                "task_count": 0,
                "task_ids": [],
                "planned_tokens": 0,
                "actual_tokens": 0,
                "planned_cost_usd": 0.0,
                "actual_cost_usd": 0.0,
                "execution_time_seconds": 0.0,
                "model_calls": 0,
            },
        )
        sb["task_count"] += 1
        sb["task_ids"].append(tid)
        sb["planned_tokens"] += p_tok
        sb["actual_tokens"] += a_tok
        sb["planned_cost_usd"] = round(sb["planned_cost_usd"] + p_cost, 6)
        sb["actual_cost_usd"] = round(sb["actual_cost_usd"] + a_cost, 6)
        sb["execution_time_seconds"] = round(sb["execution_time_seconds"] + rt["execution_time_seconds"], 2)
        sb["model_calls"] += rt["model_calls"]

    total_delta_usd = round(total_actual_usd - total_planned_usd, 6)
    net_savings_usd = round(total_planned_usd - total_actual_usd, 6)
    if total_planned_usd > 0:
        total_delta_pct = round(((total_actual_usd - total_planned_usd) / total_planned_usd) * 100.0, 2)
        savings_pct = round((net_savings_usd / total_planned_usd) * 100.0, 2)
    elif total_actual_usd == 0.0:
        total_delta_pct = 0.0
        savings_pct = 0.0
    else:
        total_delta_pct = 100.0
        savings_pct = -100.0

    if total_actual_tokens > 0:
        local_free_tokens = actual_free_tokens
        local_free_tokens_pct = round((actual_free_tokens / total_actual_tokens) * 100.0, 1)
    elif total_planned_tokens > 0:
        local_free_tokens = planned_free_tokens
        local_free_tokens_pct = round((planned_free_tokens / total_planned_tokens) * 100.0, 1)
    else:
        local_free_tokens = 0
        local_free_tokens_pct = 0.0

    stages_out: list[dict] = []
    for s_num in sorted(stage_buckets.keys()):
        sb = stage_buckets[s_num]
        s_plan = sb["planned_cost_usd"]
        s_act = sb["actual_cost_usd"]
        s_delta = round(s_act - s_plan, 6)
        s_delta_pct = (
            round(((s_act - s_plan) / s_plan) * 100.0, 2)
            if s_plan > 0
            else (0.0 if s_act == 0.0 else 100.0)
        )
        if total_planned_usd > 0:
            share_planned = round((s_plan / total_planned_usd) * 100.0, 1)
        elif total_planned_tokens > 0:
            share_planned = round((sb["planned_tokens"] / total_planned_tokens) * 100.0, 1)
        else:
            share_planned = 0.0

        if total_actual_usd > 0:
            share_actual = round((s_act / total_actual_usd) * 100.0, 1)
        elif total_actual_tokens > 0:
            share_actual = round((sb["actual_tokens"] / total_actual_tokens) * 100.0, 1)
        else:
            share_actual = 0.0

        stages_out.append({
            **sb,
            "plan_usd": s_plan,
            "fact_usd": s_act,
            "delta_usd": s_delta,
            "delta_pct": s_delta_pct,
            "savings_usd": round(s_plan - s_act, 6),
            "share_planned_pct": share_planned,
            "share_actual_pct": share_actual,
        })

    summary = {
        "task_count": len(tasks_out),
        "tasks_with_plan": count_with_plan,
        "tasks_with_telemetry": count_with_telemetry,
        "planned_input_tokens": total_planned_in,
        "planned_output_tokens": total_planned_out,
        "planned_tokens": total_planned_tokens,
        "total_planned_tokens": total_planned_tokens,
        "actual_input_tokens": total_actual_in,
        "actual_output_tokens": total_actual_out,
        "actual_tokens": total_actual_tokens,
        "total_actual_tokens": total_actual_tokens,
        "planned_cost_usd": total_planned_usd,
        "total_planned_usd": total_planned_usd,
        "actual_cost_usd": total_actual_usd,
        "total_actual_usd": total_actual_usd,
        "delta_tokens": total_actual_tokens - total_planned_tokens,
        "delta_usd": total_delta_usd,
        "delta_pct": total_delta_pct,
        "net_savings_usd": net_savings_usd,
        "savings_pct": savings_pct,
        "local_free_tokens": local_free_tokens,
        "local_free_tokens_pct": local_free_tokens_pct,
        "execution_time_seconds": total_exec_seconds,
        "model_calls": total_model_calls,
    }

    return {
        "ok": True,
        "project": str(target_root),
        "project_name": target_root.name,
        **summary,
        "summary": summary,
        "stages": stages_out,
        "tasks": tasks_out,
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


def _single_platform_probe(key: str, force: bool, flow_root: Path = None, scope: str = ""):
    """Probe one platform on demand (?platform=<key>); each key has its own TTL cache entry."""
    cache_key = f"{scope}|{key}" if scope else key
    now = time.time()
    with _capacity_probe_lock:
        ent = _platform_probe_cache.get(cache_key)
        if not force and ent and now - ent["at"] < CAPACITY_PROBE_TTL:
            return copy.deepcopy(ent["data"]), True
    p = _apply_quota_hold(_PLATFORM_PROBES[key](flow_root))
    with _capacity_probe_lock:
        _platform_probe_cache[cache_key] = {"at": time.time(), "data": copy.deepcopy(p)}
    return p, False


def _provider_probe(pid: str, force: bool, project_root: Path, scope: str = ""):
    """Probe one configured third-party provider (?platform=<provider id>); own TTL cache entry."""
    cache_key = f"{scope}|provider:{pid}"
    now = time.time()
    with _capacity_probe_lock:
        ent = _platform_probe_cache.get(cache_key)
        if not force and ent and now - ent["at"] < CAPACITY_PROBE_TTL:
            return copy.deepcopy(ent["data"]), True
    state = load_project_state(project_root) if project_root else {"providers": {}}
    conf = (state.get("providers") or {}).get(pid)
    if not conf:
        return _platform(pid, pid, False, False, note="provider not configured"), False
    secrets = load_project_secrets(project_root)
    api_key = (secrets.get("providers") or {}).get(pid, {}).get("api_key", "")
    p, live = _probe_provider(pid, dict(conf), api_key)
    if live is not None and live != conf.get("models"):
        state["providers"][pid]["models"] = live
        save_project_state(project_root, state)
    with _capacity_probe_lock:
        _platform_probe_cache[cache_key] = {"at": time.time(), "data": copy.deepcopy(p)}
    return p, False


def probe_capacity(force: bool = False, platform: str = "", flow_root: Path = None,
                   project_root: Path = None) -> dict:
    """Scan the agent CLIs on this machine; results are cached for CAPACITY_PROBE_TTL seconds.
    `platform` limits the scan to one platform key (/api/capacity/probe?platform=<tool>) or
    to one configured provider id. `project_root` overlays that project's enabled flags on
    platforms/models and appends its configured third-party providers."""
    now = time.time()
    scope = _norm(Path(project_root)) if project_root else ""
    if platform:
        state = (load_project_state(project_root) if project_root
                 else {"platforms": {}, "models": {}, "providers": {}})
        if platform in _PLATFORM_PROBES:
            p, cached = _single_platform_probe(platform, force, flow_root or FLOW_ROOT, scope)
        else:
            p, cached = _provider_probe(platform, force, project_root, scope)
        _apply_project_state([p], state)
        data = {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ttl": CAPACITY_PROBE_TTL,
            "cached": cached,
            "platform": p,
            "platforms": [p],
        }
        if project_root:
            data["project_state"] = project_state_view(project_root)
        return data
    state = (load_project_state(project_root) if project_root
             else {"platforms": {}, "models": {}, "providers": {}})
    with _capacity_probe_lock:
        cached = _capacity_probe_cache["data"]
        if (not force and cached and now - _capacity_probe_cache["at"] < CAPACITY_PROBE_TTL
                and _capacity_probe_cache.get("scope") == scope):
            data = copy.deepcopy(cached)
            data["cached"] = True
            _apply_project_state(data.get("platforms") or [], state)
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

    if project_root:
        secrets = load_project_secrets(project_root)
        dirty = False
        for pid, conf in list(state.get("providers", {}).items()):
            api_key = (secrets.get("providers") or {}).get(pid, {}).get("api_key", "")
            p, live = _probe_provider(pid, dict(conf), api_key)
            if live is not None and live != conf.get("models"):
                state["providers"][pid]["models"] = live
                dirty = True
            platforms.append(p)
        if dirty:
            save_project_state(project_root, state)

    _apply_project_state(platforms, state)

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
    if project_root:
        data["project_state"] = project_state_view(project_root)
    with _capacity_probe_lock:
        _capacity_probe_cache["at"] = time.time()
        _capacity_probe_cache["data"] = data
        _capacity_probe_cache["scope"] = scope
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


# --- Per-project model state & third-party provider engine (Model Quota Hub) ---
# Enabled flags and provider configs persist under <project>/<flow>/state/
# (project-models.json); API keys live only in .secrets.json - kept git-ignored in
# the target project and never returned, raw or unmasked, by any API response.

PROJECT_MODELS_FILE = "project-models.json"
PROVIDER_SECRETS_FILE = ".secrets.json"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
PROVIDER_TIMEOUT = 15
_PROVIDER_KINDS = ("openrouter", "openai-compatible")
_SECRETS_GITIGNORE = (".agentsflower/state/.secrets.json", ".agentflow/state/.secrets.json")


def _project_state_dir(project_root: Path) -> Path:
    flow = get_project_flow_root(Path(project_root)) or (Path(project_root) / ".agentsflower")
    return flow / "state"


def _read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.parent / f"{path.name}.{os.getpid()}.tmp"
    try:
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def load_project_state(project_root: Path) -> dict:
    """<project>/<flow>/state/project-models.json -> normalized per-project state."""
    raw = _read_json(_project_state_dir(project_root) / PROJECT_MODELS_FILE)
    state = {"version": 1, "platforms": {}, "models": {}, "providers": {}}
    for section in ("platforms", "models", "providers"):
        if isinstance(raw.get(section), dict):
            state[section] = raw[section]
    return state


def save_project_state(project_root: Path, state: dict):
    state = dict(state)
    state["version"] = 1
    _write_json(_project_state_dir(project_root) / PROJECT_MODELS_FILE, state)


def load_project_secrets(project_root: Path) -> dict:
    raw = _read_json(_project_state_dir(project_root) / PROVIDER_SECRETS_FILE)
    providers = raw.get("providers")
    return {"version": 1, "providers": providers if isinstance(providers, dict) else {}}


def save_project_secrets(project_root: Path, secrets: dict):
    _ensure_secrets_ignored(Path(project_root))
    _write_json(_project_state_dir(project_root) / PROVIDER_SECRETS_FILE, secrets)


def _ensure_secrets_ignored(project_root: Path):
    """Guarantee the provider secrets file stays git-ignored in the target project."""
    gitignore = Path(project_root) / ".gitignore"
    try:
        lines = gitignore.read_text(encoding="utf-8-sig").splitlines() if gitignore.is_file() else []
        existing = {ln.strip() for ln in lines}
        missing = [p for p in _SECRETS_GITIGNORE if p not in existing]
        if missing:
            block = ["", "# AgentsFlower provider secrets (never committed)"] + missing
            with gitignore.open("a", encoding="utf-8") as fh:
                fh.write("\n".join(block) + "\n")
    except OSError:
        pass


def mask_api_key(key: str) -> str:
    """'sk-or-v1-abc...' -> 'sk-or-••••••••'; the raw key never crosses an API boundary."""
    key = str(key or "").strip()
    if not key:
        return ""
    return (key[:6] if len(key) > 6 else "") + "••••••••"


def project_state_view(project_root: Path) -> dict:
    """The persisted per-project state as served to clients (credentials never included)."""
    return load_project_state(project_root)


def _apply_project_state(platforms: list, state: dict):
    """Overlay per-project enabled flags on probed platforms and their models."""
    plat_flags = (state or {}).get("platforms") or {}
    model_flags = (state or {}).get("models") or {}
    for p in platforms:
        enabled = bool((plat_flags.get(p.get("key")) or {}).get("enabled", True))
        p["enabled"] = enabled
        overrides = model_flags.get(p.get("key")) or {}
        for m in p.get("models") or []:
            m["enabled"] = bool((overrides.get(m.get("id")) or {}).get("enabled", enabled))


def _provider_request(url: str, api_key: str, timeout: int = PROVIDER_TIMEOUT) -> dict:
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload if isinstance(payload, dict) else {}


def fetch_provider_models(base_url: str, api_key: str, timeout: int = PROVIDER_TIMEOUT):
    """GET <base_url>/models (OpenRouter / OpenAI-compatible) -> (models, error)."""
    url = base_url.rstrip("/") + "/models"
    try:
        payload = _provider_request(url, api_key, timeout)
    except urllib.error.HTTPError as e:
        return None, f"provider returned HTTP {e.code}"
    except Exception as e:
        return None, f"provider connection failed: {e}"
    items = payload.get("data")
    if not isinstance(items, list):
        return None, "provider response carries no model list"
    models = []
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        pricing = item.get("pricing") or {}
        price = ""
        if isinstance(pricing, dict) and pricing.get("prompt"):
            try:
                price = f"${float(pricing['prompt']) * 1_000_000:.2f} / 1M prompt"
            except (TypeError, ValueError):
                price = str(pricing["prompt"])
        ctx = item.get("context_length") or (item.get("top_provider") or {}).get("context_length")
        models.append({
            "id": item["id"],
            "label": item.get("name") or item["id"],
            "context": f"{int(ctx):,} context" if ctx else "",
            "pricing": price,
            "family": str(item["id"]).split("/")[0] if "/" in str(item["id"]) else "",
            "free": False,
            "provider": True,
        })
    return models, ""


def _provider_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")
    return slug or "provider"


def _probe_provider(pid: str, conf: dict, api_key: str) -> tuple[dict, list | None]:
    """Build the platform entry for a configured provider; returns (entry, live models|None)."""
    live, err = ([], "no stored credential") if not api_key else fetch_provider_models(
        conf.get("base_url") or OPENROUTER_BASE_URL, api_key)
    if live is None:
        models = conf.get("models") or []
        note = f"live model refresh failed ({err})" if api_key else "no stored credential"
    else:
        models = live
        note = ""
    p = _platform(pid, conf.get("name") or pid, True, bool(api_key),
                  models=models, note=note or conf.get("base_url", ""))
    p["provider"] = True
    p["kind"] = conf.get("kind") or "openai-compatible"
    p["base_url"] = conf.get("base_url") or ""
    p["api_key_masked"] = conf.get("api_key_masked") or mask_api_key(api_key)
    return p, live


def add_provider(project_root: Path, body: dict) -> tuple[int, dict]:
    """Verify a provider against its live /models API, then persist config + credential."""
    name = str(body.get("name") or body.get("id") or "").strip()
    if not name:
        return 400, {"ok": False, "error": "provider name required"}
    kind = str(body.get("kind") or "openrouter").strip().lower()
    if kind not in _PROVIDER_KINDS:
        return 400, {"ok": False, "error": f"unsupported provider kind: {kind}"}
    base_url = str(body.get("base_url") or "").strip() or (
        OPENROUTER_BASE_URL if kind == "openrouter" else "")
    if not base_url or not re.fullmatch(r"https?://[^\s\"']+", base_url):
        return 400, {"ok": False, "error": "valid provider base_url required"}
    api_key = str(body.get("api_key") or body.get("key") or "").strip()
    if not api_key or len(api_key) < 8:
        return 400, {"ok": False, "error": "provider api_key required"}
    pid = _provider_id(name)
    if pid in _PLATFORM_PROBES:
        return 400, {"ok": False, "error": f"provider id collides with CLI platform: {pid}"}
    models, err = fetch_provider_models(base_url, api_key)
    if models is None:
        return 502, {"ok": False, "error": f"provider verification failed: {err}"}
    state = load_project_state(project_root)
    state["providers"][pid] = {
        "id": pid, "name": name, "kind": kind, "base_url": base_url,
        "api_key_masked": mask_api_key(api_key),
        "models": models,
        "added_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_project_state(project_root, state)
    secrets = load_project_secrets(project_root)
    secrets["providers"][pid] = {"api_key": api_key}
    save_project_secrets(project_root, secrets)
    return 200, {"ok": True, "provider": state["providers"][pid]}


def remove_provider(project_root: Path, body: dict) -> tuple[int, dict]:
    """Drop a provider's config and purge its stored credential."""
    pid = _provider_id(body.get("id") or body.get("name") or "")
    state = load_project_state(project_root)
    if pid not in state["providers"]:
        return 404, {"ok": False, "error": f"unknown provider: {pid}"}
    state["providers"].pop(pid)
    state["platforms"].pop(pid, None)
    state["models"].pop(pid, None)
    save_project_state(project_root, state)
    secrets = load_project_secrets(project_root)
    secrets["providers"].pop(pid, None)
    save_project_secrets(project_root, secrets)
    return 200, {"ok": True, "removed": pid}


def toggle_project_model(project_root: Path, body: dict) -> tuple[int, dict]:
    """Enable/disable a platform or one of its models for this project only."""
    platform = str(body.get("platform") or "").strip()
    model = str(body.get("model") or "").strip()
    if not platform or not re.fullmatch(r"[A-Za-z0-9][\w.@:-]{0,60}", platform):
        return 400, {"ok": False, "error": "valid platform key required"}
    if model and not re.fullmatch(r"[A-Za-z0-9][\w./:@-]{0,160}", model):
        return 400, {"ok": False, "error": "invalid model id"}
    state = load_project_state(project_root)
    target = (state["models"].setdefault(platform, {}).setdefault(model, {"enabled": True})
              if model else state["platforms"].setdefault(platform, {"enabled": True}))
    target["enabled"] = (not target.get("enabled", True)) if "enabled" not in body else bool(body["enabled"])
    save_project_state(project_root, state)
    return 200, {"ok": True, "state": project_state_view(project_root)}


# --- Live CLI Chat Execution Engine (/api/chat) ---

CHAT_EXEC_TIMEOUT = 30
CHAT_TOOLS = ("devin", "claude", "codex", "agy", "ollama")


def _chat_run(argv: list, cwd: Path = None, timeout: int = CHAT_EXEC_TIMEOUT) -> tuple[int | None, str, bool]:
    """Execute one bounded CLI chat command; returns (returncode, stdout_text, timed_out)."""
    kw = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }
    if cwd is not None and Path(cwd).is_dir():
        kw["cwd"] = str(cwd)
    if os.name == "nt":
        kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    try:
        proc = subprocess.Popen(argv, **kw)
    except OSError as e:
        return None, str(e), False
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_probe_tree(proc.pid)
        try:
            proc.kill()
        except OSError:
            pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
        return None, f"CLI execution timed out after {timeout}s", True
    return proc.returncode, (out or "").strip(), False


# --- Persistent multi-research threads (.agentsflower/state/research/<id>.json) ---
# Research threads are named "Task Research - NNN" (id `research-NNN`), can carry a
# folder/category and refs to other research threads or tasks (T-NNN). Ref summaries
# are injected into the chat prompt; turns persist to disk per thread.

_RESEARCH_NUM_RE = re.compile(r"^research-(\d{1,4})$")
_REF_RES_RE = re.compile(
    r"(?i)\bref\s*:\s*(t-\d+|research\s*-?\s*\d+|task\s+research\s*-?\s*\d*)"
)
_FORK_RES_RE = re.compile(
    r"(?i)\bfork\s+from\s+(research\s*-?\s*\d+|task\s+research\s*-?\s*\d*)"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_research_id(raw) -> str:
    """Normalize `research`, `Research-1`, `Task Research - 002` to `research` / `research-NNN`."""
    s = re.sub(r"[^a-z0-9]+", "", str(raw or "").lower())
    if s in ("research", "taskresearch"):
        return "research"
    m = re.fullmatch(r"(?:taskresearch|research)(\d{1,4})", s)
    return f"research-{int(m.group(1)):03d}" if m else ""


def normalize_ref(raw) -> str:
    """Normalize a context reference: `T-NNN` task id or a research thread id."""
    s = str(raw or "").strip()
    if re.fullmatch(r"(?i)t-\d{1,4}", s):
        return s.upper()
    return normalize_research_id(s)


def extract_context_refs(messages) -> list[str]:
    """Pull `Ref: T-013` / `Ref: research-002` / `Fork from Research-001` tokens from chat text."""
    refs: list[str] = []
    for m in messages or []:
        content = str(m.get("content") or "") if isinstance(m, dict) else str(m)
        for tok in list(_REF_RES_RE.findall(content)) + list(_FORK_RES_RE.findall(content)):
            n = normalize_ref(tok)
            if n and n not in refs:
                refs.append(n)
    return refs


def research_store_dir(target_root: Path) -> Path:
    flow_root = get_project_flow_root(target_root) or (target_root / ".agentsflower")
    return flow_root / "state" / "research"


def _research_file(target_root: Path, thread_id) -> Path | None:
    rid = normalize_research_id(thread_id)
    if not rid:
        return None
    return safe_under(research_store_dir(target_root), f"{rid}.json")


def _new_research_record(rid: str) -> dict:
    if rid == "research":
        name = "Research & Inception"
    else:
        name = f"Task Research - {rid.rsplit('-', 1)[1]}"
    now = _now_iso()
    return {
        "id": rid, "name": name, "folder": "", "refs": [], "parent": "",
        "created": now, "updated": now, "messages": [],
    }


def load_research_thread(target_root: Path, thread_id) -> dict | None:
    rf = _research_file(target_root, thread_id)
    if rf is None or not rf.is_file():
        return None
    try:
        rec = json.loads(rf.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    if not isinstance(rec, dict) or not rec.get("id"):
        return None
    rec.setdefault("name", rec["id"])
    rec.setdefault("folder", "")
    rec.setdefault("refs", [])
    rec.setdefault("parent", "")
    rec.setdefault("messages", [])
    return rec


def save_research_thread(target_root: Path, rec: dict) -> bool:
    rf = _research_file(target_root, rec.get("id"))
    if rf is None:
        return False
    try:
        rf.parent.mkdir(parents=True, exist_ok=True)
        rf.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False


def list_research_threads(target_root: Path) -> list[dict]:
    store = research_store_dir(target_root)
    out: list[dict] = []
    if store.is_dir():
        for f in sorted(store.glob("research*.json")):
            rec = load_research_thread(target_root, f.stem)
            if rec:
                out.append(rec)
    out.sort(key=lambda r: (r["id"] != "research", r["id"]))
    return out


def _clean_folder(raw) -> str:
    s = re.sub(r"[\\/]+", " ", str(raw or "")).strip()
    return s[:60]


def _merge_refs(rec: dict, refs, drop_self: bool = True) -> list[str]:
    merged = [r for r in (rec.get("refs") or []) if isinstance(r, str)]
    for raw in refs or []:
        n = normalize_ref(raw)
        if n and (not drop_self or n != rec.get("id")) and n not in merged:
            merged.append(n)
    return merged[:20]


def create_research_thread(target_root: Path, name="", folder="", fork_from="") -> dict:
    store = research_store_dir(target_root)
    nums = []
    if store.is_dir():
        for f in store.glob("research-*.json"):
            m = _RESEARCH_NUM_RE.fullmatch(f.stem)
            if m:
                nums.append(int(m.group(1)))
    rec = _new_research_record(f"research-{max(nums, default=0) + 1:03d}")
    if str(name or "").strip():
        rec["name"] = str(name).strip()[:80]
    rec["folder"] = _clean_folder(folder)
    parent = normalize_research_id(fork_from)
    if parent and parent != rec["id"]:
        rec["parent"] = parent
        rec["refs"] = [parent]
    save_research_thread(target_root, rec)
    return rec


def update_research_thread(target_root: Path, thread_id, fields: dict) -> tuple[dict | None, str]:
    rid = normalize_research_id(thread_id)
    if not rid:
        return None, "invalid research thread id"
    rec = load_research_thread(target_root, rid) or _new_research_record(rid)
    if "name" in fields:
        v = str(fields.get("name") or "").strip()[:80]
        if not v:
            return None, "name must not be empty"
        rec["name"] = v
    if "folder" in fields:
        rec["folder"] = _clean_folder(fields.get("folder"))
    if "refs" in fields:
        if not isinstance(fields.get("refs"), list):
            return None, "refs must be a list"
        rec["refs"] = []
        rec["refs"] = _merge_refs(rec, fields["refs"])
    parent = normalize_research_id(fields.get("fork_from"))
    if parent and parent != rid:
        rec["parent"] = parent
        rec["refs"] = _merge_refs(rec, [parent])
    rec["updated"] = _now_iso()
    save_research_thread(target_root, rec)
    return rec, ""


def maybe_persist_research_turn(target_root: Path, thread, messages: list[dict],
                                reply: str, refs=None, force: bool = False):
    """Persist a completed chat turn for a research thread.

    Writes when the thread record already exists or `persist: true` was sent, so
    bare chat calls against an unpersisted thread stay side-effect free.
    """
    rid = normalize_research_id(thread)
    if not rid:
        return
    rf = _research_file(target_root, rid)
    if rf is None or (not force and not rf.is_file()):
        return
    try:
        rec = load_research_thread(target_root, rid) or _new_research_record(rid)
        rec["messages"] = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ] + [{"role": "assistant", "content": reply}]
        rec["refs"] = _merge_refs(rec, refs)
        rec["updated"] = _now_iso()
        save_research_thread(target_root, rec)
    except Exception:
        pass


def reference_summary(target_root: Path, ref) -> str:
    """One-line context summary for a linked task (T-NNN) or research thread."""
    s = str(ref or "").strip()
    if re.fullmatch(r"(?i)t-\d{1,4}", s):
        ctx = get_task_context(target_root, s.upper())
        if ctx.get("ok") and isinstance(ctx.get("task"), dict):
            t = ctx["task"]
            goal = str(t.get("goal") or "").replace("\n", " ").strip()[:160]
            return f"{t.get('id', s.upper())} {t.get('title', '')} (status: {t.get('status', 'ready')}): {goal}".strip()
        return f"{s.upper()}: referenced task not found"
    rid = normalize_research_id(s)
    if rid:
        rec = load_research_thread(target_root, rid)
        if rec is None:
            return f"{rid}: referenced research thread not found"
        msgs = rec.get("messages") or []
        folder = f" [folder: {rec['folder']}]" if rec.get("folder") else ""
        head = f"{rec.get('name') or rid} ({rid}){folder}: {len(msgs)} messages"
        tail = "; ".join(
            f"{m.get('role', 'user')}: {str(m.get('content', ''))[:80]}"
            for m in msgs[-3:] if isinstance(m, dict)
        )
        return head + (f" - last: {tail}" if tail else "")
    return f"{s}: unrecognized reference"


def _normalize_chat_messages(raw_messages, fallback_prompt: str = "") -> list[dict]:
    normalized: list[dict] = []
    if isinstance(raw_messages, list):
        for m in raw_messages:
            if isinstance(m, dict):
                role = str(m.get("role") or "user").strip().lower()
                if role not in ("user", "assistant", "system"):
                    role = "user"
                content = str(m.get("content") or m.get("text") or "").strip()
                if content:
                    normalized.append({"role": role, "content": content})
            elif isinstance(m, str) and m.strip():
                normalized.append({"role": "user", "content": m.strip()})
    if not normalized and fallback_prompt and str(fallback_prompt).strip():
        normalized.append({"role": "user", "content": str(fallback_prompt).strip()})
    return normalized


def format_chat_prompt(target_root: Path, thread: str, messages: list[dict], refs=None) -> str:
    """Package active thread metadata and prior conversation history into a single prompt."""
    thread_id = (thread or "research").strip()
    lines = [
        f"Workspace: {target_root.name} ({target_root})",
        f"Active Thread: {thread_id}",
        "Mode: Read-only Studio conversational assistant (do not modify files).",
    ]
    if thread_id.upper().startswith("T-"):
        ctx = get_task_context(target_root, thread_id)
        if ctx.get("ok") and isinstance(ctx.get("task"), dict):
            t = ctx["task"]
            wt = ctx.get("worktree_status") or {}
            lines.append(
                f"Task Context: {t.get('id')} - {t.get('title', '')} "
                f"(stage: {t.get('stage', '')}, status: {t.get('status', 'ready')})"
            )
            if t.get("contract_file"):
                lines.append(f"Contract File: {t['contract_file']}")
            lines.append(
                f"Worktree: {t.get('worktree') or 'none'} "
                f"(branch: {wt.get('branch') or t.get('branch') or 'none'}, "
                f"worktree_status: {wt.get('status', 'none')})"
            )
            if t.get("depends"):
                lines.append(f"Depends on: {t['depends']}")
            if t.get("goal"):
                lines.append(f"Task Goal: {t['goal'][:400]}")
            if t.get("allowed_files"):
                lines.append("Allowed Files: " + ", ".join(t["allowed_files"][:8]))
            if t.get("criteria"):
                crit_items = [
                    f"{c.get('id', '')}: {c.get('text', '')}" if isinstance(c, dict) else str(c)
                    for c in t["criteria"][:10]
                ]
                lines.append("Acceptance Criteria: " + " | ".join(crit_items))

    if refs:
        lines.append("")
        lines.append("Referenced context (linked research / tasks):")
        for r in refs:
            lines.append(f"- {reference_summary(target_root, r)}")

    if len(messages) > 1:
        lines.append("")
        lines.append("Conversation history:")
        for msg in messages[:-1]:
            speaker = "Assistant" if msg["role"] == "assistant" else "User"
            lines.append(f"{speaker}: {msg['content']}")

    latest = messages[-1]["content"] if messages else ""
    lines.append("")
    lines.append(f"User: {latest}")
    return "\n".join(lines)


def _build_chat_argv(tool: str, exe: str, prompt: str, model: str = "") -> list[str]:
    """Build bounded read-only CLI invocation for the selected platform."""
    if tool == "devin":
        argv = [exe, "-p", prompt, "--respect-workspace-trust", "false", "--permission-mode", "auto"]
        if model:
            argv += ["--model", model]
        return argv
    if tool == "claude":
        argv = [exe, "-p", prompt, "--allowedTools", ""]
        if model:
            argv += ["--model", model]
        return argv
    if tool == "codex":
        argv = [exe, "exec", prompt, "--sandbox", "read-only", "--skip-git-repo-check"]
        if model:
            argv += ["-m", model]
        return argv
    if tool == "agy":
        argv = [exe, "-p", prompt, "--output-format", "stream-json"]
        if model:
            argv += ["--model", model]
        return argv
    raise ValueError(f"Unsupported CLI tool: {tool}")


def _parse_chat_output(tool: str, raw_out: str, prompt: str = "") -> tuple[str, dict]:
    """Extract assistant reply text and token usage metadata from CLI stdout."""
    text = (raw_out or "").strip()
    usage: dict = {}
    chunks: list[str] = []

    if tool == "agy" or (text.startswith("{") and "\n" in text):
        for ln in text.splitlines():
            s = ln.strip()
            if not (s.startswith("{") and s.endswith("}")):
                continue
            try:
                ev = json.loads(s)
            except ValueError:
                continue
            if not isinstance(ev, dict):
                continue
            if isinstance(ev.get("usage"), dict):
                usage.update(ev["usage"])
            ev_type = str(ev.get("type") or "").lower()
            if ev_type in ("init", "session", "config", "system"):
                continue
            msg = ev.get("message")
            if isinstance(msg, dict):
                if isinstance(msg.get("usage"), dict):
                    usage.update(msg["usage"])
                mc = msg.get("content")
                if isinstance(mc, str) and mc.strip():
                    chunks.append(mc.strip())
                elif isinstance(mc, list):
                    for part in mc:
                        if isinstance(part, dict) and isinstance(part.get("text"), str) and part["text"].strip():
                            chunks.append(part["text"].strip())
                continue
            for key in ("reply", "result", "content", "text", "delta"):
                val = ev.get(key)
                if isinstance(val, str) and val.strip():
                    chunks.append(val.strip())
                    break

    reply = "\n".join(chunks).strip() if chunks else text
    if not usage:
        usage = {
            "prompt_chars": len(prompt or ""),
            "reply_chars": len(reply),
        }
    return reply, usage


def execute_chat_query(target_root: Path, body: dict) -> tuple[int, dict]:
    """Validate and execute a live chat query against the requested CLI or local runtime."""
    raw_tool = str(body.get("tool") or body.get("platform") or "").strip().lower()
    raw_model = str(body.get("model") or "").strip()
    thread = str(body.get("thread") or "research").strip()

    tool = raw_tool or ("ollama" if raw_model == "local-ollama" else "devin")
    if tool not in CHAT_TOOLS:
        return 400, {"ok": False, "error": f"Unsupported chat tool: {tool}"}

    if raw_model and not re.fullmatch(r"[A-Za-z0-9][\w./:-]{0,80}", raw_model):
        return 400, {"ok": False, "error": "invalid model id"}

    messages = _normalize_chat_messages(body.get("messages"), body.get("prompt") or body.get("message") or "")
    if not any(m["role"] == "user" and m["content"] for m in messages):
        return 400, {"ok": False, "error": "No user chat messages provided"}

    refs: list[str] = []
    for raw in body.get("refs") or []:
        n = normalize_ref(raw)
        if n and n not in refs:
            refs.append(n)
    for n in extract_context_refs(messages):
        if n not in refs:
            refs.append(n)
    refs = [r for r in refs if r != normalize_research_id(thread)][:16]

    prompt = format_chat_prompt(target_root, thread, messages, refs=refs)
    persist_turn = bool(body.get("persist"))

    if tool == "ollama":
        if not local_adapter:
            return 500, {"ok": False, "error": "local_adapter module unavailable"}
        model_id = raw_model if (raw_model and raw_model != "local-ollama") else ""
        model_info = None
        if not model_id:
            model_info = local_adapter.select_best_coding_model()
            if model_info:
                model_id = model_info.get("id", "")
        if not model_info:
            model_info = {
                "id": model_id or "qwen2.5-coder:7b",
                "runtime_type": "ollama",
                "base_url": OLLAMA_URL,
            }
            model_id = model_info["id"]
        ollama_msgs = [
            {
                "role": "system",
                "content": f"Workspace: {target_root.name} ({target_root}) | Thread: {thread}",
            },
            *messages,
        ]
        res = local_adapter.chat_completion(model_info, ollama_msgs, temperature=0.2, timeout=CHAT_EXEC_TIMEOUT)
        if not res.get("ok"):
            err = str(res.get("error") or "Local Ollama runtime failed")
            is_timeout = "timed out" in err.lower() or "timeout" in err.lower()
            return (504 if is_timeout else 502), {
                "ok": False,
                "error": err,
                "tool": "ollama",
                "model": model_id,
                "timed_out": is_timeout,
            }
        raw_data = res.get("raw") if isinstance(res.get("raw"), dict) else {}
        reply = str(res.get("content") or "").strip()
        usage = {
            "prompt_tokens": raw_data.get("prompt_eval_count", 0),
            "completion_tokens": raw_data.get("eval_count", 0),
            "prompt_chars": len(prompt),
            "reply_chars": len(reply),
        }
        maybe_persist_research_turn(target_root, thread, messages, reply, refs, force=persist_turn)
        return 200, {
            "ok": True,
            "reply": reply,
            "tool": "ollama",
            "model": model_id,
            "thread": thread,
            "usage": usage,
        }

    exe = shutil.which(tool)
    if not exe:
        return 400, {
            "ok": False,
            "error": f"{tool} CLI not found on PATH",
            "tool": tool,
            "model": raw_model,
        }

    model_for_cli = "" if raw_model in ("local-ollama",) else raw_model
    argv = _build_chat_argv(tool, exe, prompt, model_for_cli)
    rc, out, timed_out = _chat_run(argv, cwd=target_root, timeout=CHAT_EXEC_TIMEOUT)
    if timed_out:
        return 504, {
            "ok": False,
            "error": out or f"CLI execution timed out after {CHAT_EXEC_TIMEOUT}s",
            "tool": tool,
            "model": raw_model or tool,
            "timed_out": True,
        }
    if rc != 0:
        err_msg = (out or f"{tool} exited with code {rc}").splitlines()[0][:240]
        return 502, {
            "ok": False,
            "error": err_msg,
            "tool": tool,
            "model": raw_model or tool,
        }

    reply, usage = _parse_chat_output(tool, out, prompt=prompt)
    maybe_persist_research_turn(target_root, thread, messages, reply, refs, force=persist_turn)
    return 200, {
        "ok": True,
        "reply": reply,
        "tool": tool,
        "model": raw_model or tool,
        "thread": thread,
        "usage": usage,
    }


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

        if path == "/api/analytics/costs":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            self.send_json(get_analytics_costs(root))
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

        if path == "/api/research/list":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            self.send_json({"ok": True, "threads": list_research_threads(root)})
            return

        if path == "/api/research/thread":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            rid = qs.get("id", [""])[0]
            rec = load_research_thread(root, rid)
            if rec is None:
                self.send_json({"ok": False, "error": f"research thread not found: {rid}"}, 404)
                return
            self.send_json({"ok": True, "thread": rec})
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
            if platform and platform not in _PLATFORM_PROBES and \
                    platform not in (load_project_state(root).get("providers") or {}):
                self.send_json({"ok": False, "error": f"unknown platform: {platform}"}, 400)
                return
            data = probe_capacity(force=qs.get("refresh", [""])[0] in ("1", "true"),
                                  platform=platform, flow_root=flow, project_root=root)
            data["default_model"] = get_default_worker_model(flow) if flow else None
            self.send_json(data)
            return

        if path == "/api/capacity/project-state":
            root = resolve_known_project(target_project_str)
            if root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            self.send_json({"ok": True, "project": str(root),
                            "state": project_state_view(root)})
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

        if path == "/api/capacity/project-toggle":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            status_code, res = toggle_project_model(target_root, body)
            self.send_json(res, status_code)
            return

        if path == "/api/capacity/provider/add":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            status_code, res = add_provider(target_root, body)
            self.send_json(res, status_code)
            return

        if path == "/api/capacity/provider/remove":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            status_code, res = remove_provider(target_root, body)
            self.send_json(res, status_code)
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

        if path == "/api/analytics/costs":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            self.send_json(get_analytics_costs(target_root))
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

        if path == "/api/chat":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            status_code, res = execute_chat_query(target_root, body)
            self.send_json(res, status_code)
            return

        if path == "/api/research/create":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            rec = create_research_thread(
                target_root,
                name=body.get("name"),
                folder=body.get("folder"),
                fork_from=body.get("fork_from"),
            )
            self.send_json({"ok": True, "thread": rec})
            return

        if path == "/api/research/update":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            rid = str(body.get("id") or "").strip()
            if not rid:
                self.send_json({"ok": False, "error": "research thread id required"}, 400)
                return
            fields = {
                k: body.get(k) for k in ("name", "folder", "refs", "fork_from") if k in body
            }
            rec, err = update_research_thread(target_root, rid, fields)
            if rec is None:
                self.send_json({"ok": False, "error": err}, 404 if "not found" in err else 400)
                return
            self.send_json({"ok": True, "thread": rec})
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

        if path == "/api/task/move-stage":
            target_root = resolve_known_project(body.get("project"))
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            status_code, res = move_task_stage(target_root, body)
            self.send_json(res, status_code)
            return

        if path == "/api/task/create":
            target_root = resolve_known_project(body.get("project", "").strip())
            if target_root is None:
                self.send_json({"ok": False, "error": "unknown or unregistered project"}, 403)
                return
            if body.get("synthesis_approved") is not True:
                self.send_json(
                    {
                        "ok": False,
                        "error": (
                            "Manual task creation inside Implementations is disabled; "
                            "tasks enter exclusively via approved synthesis pool (/api/task/pool/register)."
                        ),
                        "guard": "implementations_synthesis_only",
                    },
                    403,
                )
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
