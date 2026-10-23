#!/usr/bin/env python3
"""AgentsFlower Graft codebase knowledge graph integration.

Provides deterministic AST parsing, symbol indexing, dependency call-graph traversal,
and blast-radius impact analysis via @nanonets/graft (tree-sitter AST).

Key design principles:
1. Optional external sidecar: zero third-party Python runtime dependencies in core.
2. Auto-installer: installs @nanonets/graft with --ignore-scripts on first use if npm is present.
3. Clean worktrees: stores graph caches in .agentsflower/tasks/.runtime/graft/<repo-hash>
   with --no-gitignore --no-ignore so worktrees stay git-porcelain clean.
4. Privacy: disables telemetry by default (graft telemetry disable).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
try:
    from paths import FLOW_ROOT, REPO_ROOT
except ImportError:
    FLOW_ROOT = TOOLS_DIR.parent
    REPO_ROOT = FLOW_ROOT.parent

GRAFT_PACKAGE = "@nanonets/graft"


def resolve_graft(auto_install: bool = True, log_fn=None) -> tuple[str | None, str | None]:
    """Locate the graft executable or auto-install it via npm with --ignore-scripts.

    Returns (executable_path, error_message).
    """
    log = log_fn or (lambda msg: None)

    # 1. Check in PATH
    for name in ("graft", "trail"):
        exe = shutil.which(name)
        if exe:
            return exe, None

    # 2. Check standard Windows npm global bin path
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        for candidate in ("graft.cmd", "graft.ps1", "graft"):
            p = Path(appdata) / "npm" / candidate
            if p.is_file():
                return str(p), None

    if not auto_install:
        return None, "graft executable not found (auto-install disabled)"

    # 3. Check if npm is available for auto-installation
    npm_exe = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm_exe:
        return (
            None,
            "graft is not installed and npm is not found in PATH. "
            "Please install Node.js (>=20) and run 'npm i -g @nanonets/graft --ignore-scripts'.",
        )

    log(f"Graft is missing. Auto-installing {GRAFT_PACKAGE} via npm (--ignore-scripts)...")
    try:
        proc = subprocess.run(
            [npm_exe, "i", "-g", GRAFT_PACKAGE, "--ignore-scripts"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if proc.returncode != 0:
            return (
                None,
                f"Failed to auto-install {GRAFT_PACKAGE}: exit {proc.returncode}\n"
                f"{proc.stderr.strip() or proc.stdout.strip()}",
            )
    except Exception as e:
        return None, f"Error during graft auto-installation: {e}"

    # 4. Re-check after install
    for name in ("graft", "trail"):
        exe = shutil.which(name)
        if exe:
            _disable_telemetry(exe)
            return exe, None

    if appdata:
        for candidate in ("graft.cmd", "graft.ps1", "graft"):
            p = Path(appdata) / "npm" / candidate
            if p.is_file():
                _disable_telemetry(str(p))
                return str(p), None

    return None, "npm install succeeded but graft binary could not be located in PATH or npm prefix."


def _disable_telemetry(graft_exe: str) -> None:
    """Ensure telemetry is disabled per security guidelines."""
    try:
        subprocess.run(
            [graft_exe, "telemetry", "disable"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass


def runtime_graph_dir(repo_path: Path, flow_root: Path | None = None) -> Path:
    """Compute an isolated cache directory for the graph outside the git working tree."""
    flow = flow_root or FLOW_ROOT
    repo_resolved = repo_path.resolve()
    h = hashlib.sha256(str(repo_resolved).encode("utf-8")).hexdigest()[:12]
    out = flow / "tasks" / ".runtime" / "graft" / h
    out.mkdir(parents=True, exist_ok=True)
    return out


def run_graft_cmd(
    repo_path: Path,
    args: list[str],
    runtime_dir: Path | None = None,
    timeout: int = 120,
    auto_install: bool = True,
) -> tuple[int, str]:
    """Run graft with --dir pointing to isolated runtime directory."""
    exe, err = resolve_graft(auto_install=auto_install)
    if not exe:
        return 1, f"[graft error] {err}"

    rdir = runtime_dir or runtime_graph_dir(repo_path)
    cmd = [exe, "--dir", str(rdir), *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        output = (proc.stdout + "\n" + proc.stderr).strip()
        return proc.returncode, output
    except Exception as e:
        return 1, f"[graft execution error] {e}"


def graft_build(repo_path: Path, runtime_dir: Path | None = None) -> dict:
    """Build the AST wiring graph cleanly in runtime directory."""
    code, out = run_graft_cmd(
        repo_path,
        ["build", "--no-gitignore", "--no-ignore"],
        runtime_dir=runtime_dir,
    )
    return {"ok": code == 0, "exit_code": code, "output": out}


def graft_query(
    repo_path: Path,
    question: str,
    path_scope: str = "",
    runtime_dir: Path | None = None,
) -> dict:
    """Ask a question or locate code in the codebase knowledge graph."""
    args = ["ask", question, "--source"]
    if path_scope:
        args.extend(["--in", path_scope])
    code, out = run_graft_cmd(repo_path, args, runtime_dir=runtime_dir)
    return {"ok": code == 0, "exit_code": code, "question": question, "output": out}


def graft_impact(
    repo_path: Path,
    target: str,
    runtime_dir: Path | None = None,
) -> dict:
    """Calculate blast radius: callers closure for symbols, or blast for files/diffs."""
    is_path = "/" in target or "\\" in target or (repo_path / target).exists() or target.endswith(
        (".py", ".ts", ".js", ".go", ".rs", ".md")
    )
    if is_path:
        args = ["blast", "--format", "json"]
    else:
        args = ["callers", target, "--depth", "all", "--json"]

    code, out = run_graft_cmd(repo_path, args, runtime_dir=runtime_dir)
    parsed = None
    if code == 0:
        try:
            parsed = json.loads(out)
        except json.JSONDecodeError:
            pass
    return {"ok": code == 0, "exit_code": code, "target": target, "data": parsed, "raw": out}


def graft_symbols(
    repo_path: Path,
    file_path: str,
    runtime_dir: Path | None = None,
) -> dict:
    """Get API skeleton (signatures and spans) for a given file."""
    args = ["skeleton", file_path]
    code, out = run_graft_cmd(repo_path, args, runtime_dir=runtime_dir)
    return {"ok": code == 0, "exit_code": code, "file": file_path, "output": out}


def graft_blast_radius(
    repo_path: Path,
    targets: list[str],
    runtime_dir: Path | None = None,
) -> list[str]:
    """Helper for gate.py: extract affected file list for a set of changed symbols or files."""
    files = set()
    for t in targets:
        res = graft_impact(repo_path, t, runtime_dir=runtime_dir)
        data = res.get("data")
        if isinstance(data, dict):
            # parse matches from callers
            matches = data.get("matches", [])
            for m in matches:
                sym = m.get("symbol", {})
                if sym.get("path"):
                    files.add(sym["path"])
                for hit in m.get("hits", []):
                    if hit.get("path"):
                        files.add(hit["path"])
            # parse blast data
            affected = data.get("affected_files", []) or data.get("files", [])
            for f in affected:
                if isinstance(f, str):
                    files.add(f)
                elif isinstance(f, dict) and f.get("path"):
                    files.add(f["path"])
    return sorted(files)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="agentsflower graft",
        description="Codebase knowledge graph and symbol impact analysis via Graft.",
    )
    sub = ap.add_subparsers(dest="subcmd", required=True)

    # build
    p_build = sub.add_parser("build", help="Build or refresh the AST wiring graph")
    p_build.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository directory")

    # query
    p_query = sub.add_parser("query", help="Query the knowledge graph (graft ask)")
    p_query.add_argument("question", help="Question or query string")
    p_query.add_argument("--in", dest="path_scope", default="", help="Scope query to a subpath")
    p_query.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository directory")

    # impact
    p_impact = sub.add_parser("impact", help="Blast-radius analysis for symbol or file")
    p_impact.add_argument("target", help="Symbol name or file path")
    p_impact.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository directory")

    # symbols
    p_sym = sub.add_parser("symbols", help="Get API signature skeleton of a file")
    p_sym.add_argument("file", help="File path")
    p_sym.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository directory")

    # raw passthrough
    p_raw = sub.add_parser("raw", help="Pass raw arguments to graft CLI")
    p_raw.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for graft")
    p_raw.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository directory")

    a = ap.parse_args(argv)
    repo = a.repo.resolve()

    if a.subcmd == "build":
        res = graft_build(repo)
        print(res["output"])
        return res["exit_code"]

    if a.subcmd == "query":
        res = graft_query(repo, a.question, a.path_scope)
        print(res["output"])
        return res["exit_code"]

    if a.subcmd == "impact":
        res = graft_impact(repo, a.target)
        if res.get("data"):
            print(json.dumps(res["data"], indent=2))
        else:
            print(res["raw"])
        return res["exit_code"]

    if a.subcmd == "symbols":
        res = graft_symbols(repo, a.file)
        print(res["output"])
        return res["exit_code"]

    if a.subcmd == "raw":
        code, out = run_graft_cmd(repo, a.args)
        print(out)
        return code

    return 0


if __name__ == "__main__":
    sys.exit(main())
