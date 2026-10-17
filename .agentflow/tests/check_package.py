"""Build integration for the agentflow-sdlc package, run explicitly:

  python .agentflow/tests/check_package.py

Not part of `python -m unittest discover` (name has no test_ prefix): it needs
network access to provision development build tools (the `build` package and
setuptools/wheel) into disposable virtual environments. Runtime stays stdlib-only.

What it proves (task criteria P-02/P-04/P-05):
- sdist and wheel build from the checkout; both carry the generated
  agentflow/template/ resources without the checkout; no second tracked tree.
- a clean venv with the wheel provides the `agentflow` command from any CWD:
  --help/--version work outside the source tree and install/update operate on a
  disposable git project, preserving project-owned files.
- `pip freeze` in that venv shows no core third-party runtime dependencies.
- installing the sdist in another clean venv proves the wheel built from the
  sdist keeps the bundle (provenance: template-source.json points at the
  installed package, not at this checkout).
- a project path containing spaces works.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = (ROOT / ".agentflow" / "VERSION").read_text(encoding="utf-8").strip()
NAME = "agentflow-sdlc"
FAIL = []


def step(msg):
    print(f"== {msg}", flush=True)


def check(cond, what):
    print(f"  {'ok ' if cond else 'FAIL'} {what}", flush=True)
    if not cond:
        FAIL.append(what)


def run(cmd, cwd=None, env=None, ok=True):
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if ok and p.returncode:
        raise RuntimeError(f"{cmd} -> {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


def venv_py(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def venv_exe(venv_dir: Path, name: str) -> Path:
    return venv_dir / ("Scripts" if os.name == "nt" else "bin") / (name + (".exe" if os.name == "nt" else ""))


def make_venv(path: Path) -> Path:
    step(f"venv {path}")
    venv.create(path, with_pip=True)
    return venv_py(path)


def freeze_pkgs(py: Path):
    out = run([py, "-m", "pip", "freeze", "--all"]).stdout.lower()
    return {l.split("==")[0].replace("-", "_") for l in out.splitlines() if "==" in l}


def git(proj: Path, *args):
    run(["git", "-C", proj, *args])


def make_project(tmp: Path) -> Path:
    proj = tmp / "disposable proj"  # a path with a space (P-04)
    proj.mkdir()
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "t@example.invalid")
    git(proj, "config", "user.name", "t")
    (proj / "AGENTS.md").write_text("# Own rules\n\nKeep me.\n", encoding="utf-8")
    git(proj, "add", "-A")
    git(proj, "commit", "-qm", "init")
    return proj


def exercise_cli(af: Path, proj: Path, where: Path):
    """Run the installed CLI from an unrelated CWD against the disposable project."""
    p = run([af, "--version"], cwd=where)
    check(p.returncode == 0 and VERSION in p.stdout, f"agentflow --version prints {VERSION} outside source")
    p = run([af, "--help"], cwd=where)
    check(p.returncode == 0 and "install" in p.stdout and "gate" in p.stdout,
          "agentflow --help lists subcommands")

    p = run([af, "install", str(proj)], cwd=where)
    check(p.returncode == 0, "agentflow install into a fresh git project")
    flow = proj / ".agentflow"
    check((flow / "tools" / "cli.py").is_file() and (flow / "VERSION").is_file(),
          "install wrote template-owned files")
    src = json.loads((flow / "template-source.json").read_text(encoding="utf-8"))
    check("agentflow" in src["template"].replace("\\", "/") and str(ROOT) not in src["template"],
          f"template-source.json records the installed package, not the checkout ({src['template']})")
    check((proj / "AGENTS.md").read_text(encoding="utf-8").startswith("# Own rules"),
          "project-owned AGENTS.md content preserved")
    git(proj, "add", "-A")
    git(proj, "commit", "-qm", "install agentflow")

    p = run([af, "install", str(proj), "--update"], cwd=where)
    check(p.returncode == 0, "agentflow install --update on the same project")
    p = run([af, "install", str(proj), "--update", "--dry-run"], cwd=where)
    check(p.returncode == 0 and "dry run" in p.stdout, "install --update --dry-run prints the plan")
    p = run([af, "--project", str(proj), "ledger", "show"], cwd=where)
    check(p.returncode == 0, "agentflow --project <proj> ledger show on the installed project")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="af pkg check "))  # spaced path on purpose
    dist = tmp / "dist"
    try:
        step(f"build sdist+wheel of {ROOT}")
        bld = make_venv(tmp / "venv build")
        run([bld, "-m", "pip", "install", "-q", "build"])
        run([bld, "-m", "build", "--outdir", dist], cwd=ROOT)
        wheel = next(dist.glob("*.whl"), None)
        sdist = next(dist.glob("*.tar.gz"), None)
        check(wheel is not None, "wheel built")
        check(sdist is not None, "sdist built")
        if not (wheel and sdist):
            return report()

        import zipfile, tarfile
        names = zipfile.ZipFile(wheel).namelist()
        check(any(n == "agentflow/template/tools/install.py" for n in names),
              "wheel carries the generated template bundle")
        check(not any("/state/" in n or n.endswith("/template-source.json") or "/tasks/T-" in n
                      or "project-rules" in n or "project-plan" in n for n in names),
              "wheel bundle has no project memory (state/tasks/rules/plan)")
        check(any(n.startswith("agentflow/template/tests/test_") for n in names)
              and any(n.startswith("agentflow/template/dashboard/") for n in names),
              "wheel carries template tests and dashboard")
        tn = tarfile.open(sdist).getnames()
        check(any(n.endswith("src/agentflow/template/VERSION") for n in tn),
              "sdist embeds the generated template tree")
        check(not any("/.agentflow/state/" in n for n in tn), "sdist carries no checkout state")

        step("wheel: clean venv, CLI outside source, install/update")
        py = make_venv(tmp / "venv wheel")
        run([py, "-m", "pip", "install", "-q", wheel])
        check(freeze_pkgs(py) <= {NAME.replace("-", "_"), "pip", "setuptools", "wheel"},
              f"no core third-party runtime deps ({sorted(freeze_pkgs(py))})")
        proj = make_project(tmp)
        (tmp / "elsewhere").mkdir(exist_ok=True)
        exercise_cli(venv_exe(tmp / "venv wheel", "agentflow"), proj, tmp / "elsewhere")

        step("sdist: clean venv keeps bundled resources (provenance)")
        py2 = make_venv(tmp / "venv sdist")
        run([py2, "-m", "pip", "install", "-q", "setuptools", "wheel"])  # dev tools only
        run([py2, "-m", "pip", "install", "-q", "--no-build-isolation", sdist])
        p = run([venv_exe(tmp / "venv sdist", "agentflow"), "--version"], cwd=tmp)
        check(p.returncode == 0 and VERSION in p.stdout,
              "sdist-installed CLI runs with bundled resources")
    finally:
        if os.environ.get("AGENTFLOW_PKG_KEEP") != "1":
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"kept {tmp}")
    return report()


def report() -> int:
    if FAIL:
        print(f"\nFAILED ({len(FAIL)}):", flush=True)
        for f in FAIL:
            print("  - " + f)
        return 1
    print("\ncheck_package: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
