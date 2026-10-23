"""Build script for the agentsflower-sdlc distribution.

The single source of the template is this repository's `.agentsflower/`; nothing is
tracked twice. At build time the installer-owned files (the same set
`.agentsflower/tools/install.py` copies into a project) are generated into
`agentsflower/template/` inside the wheel, and into `src/agentsflower/template/`
inside the sdist. A wheel built from the sdist reuses that generated tree, so
neither artifact needs the checkout.

Excluded from the bundle: project-owned memory (state/, task contracts,
project rules/plan, template-source.json), runtime files, dashboard output and
versions, caches, and this repository's maintainer-only root instructions.
"""
import importlib.util
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

ROOT = Path(__file__).resolve().parent
TEMPLATE_DEST = Path("src") / "agentsflower" / "template"  # inside the sdist tree


def load_install():
    spec = importlib.util.spec_from_file_location(
        "agentsflower_install", ROOT / ".agentsflower" / "tools" / "install.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_bundle(dest: Path):
    """Copy every installer-owned file below dest (the template's .agentsflower)."""
    for rel, src in load_install().owned_files():
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)


def bundle_tree(build_dir: Path):
    """Materialize agentsflower/template/ under build_dir (build_lib or sdist root)."""
    dest = build_dir / "agentsflower" / "template"
    src_tree = ROOT / TEMPLATE_DEST  # pre-generated inside an sdist
    if src_tree.is_dir():
        shutil.copytree(src_tree, dest, dirs_exist_ok=True)
    elif (ROOT / ".agentsflower").is_dir():
        write_bundle(dest)
    else:
        raise RuntimeError("no template source: neither .agentsflower/ nor a bundled "
                           f"{TEMPLATE_DEST.as_posix()} exists; build from the checkout or the sdist")


class build_py(_build_py):
    def run(self):
        super().run()
        bundle_tree(Path(self.build_lib))


class sdist(_sdist):
    def make_release_tree(self, base_dir, files):
        super().make_release_tree(base_dir, files)
        base = Path(base_dir)
        write_bundle(base / TEMPLATE_DEST)
        files.extend(str(f.relative_to(base)) for f in sorted((base / TEMPLATE_DEST).rglob("*"))
                     if f.is_file())


def version():
    # .agentsflower/VERSION is the single source; in an sdist it lives in the generated bundle
    for v in (ROOT / ".agentsflower" / "VERSION", ROOT / TEMPLATE_DEST / "VERSION"):
        if v.is_file():
            return v.read_text(encoding="utf-8").strip()
    raise RuntimeError("no VERSION: neither .agentsflower/ nor a bundled template exists")


def main():
    try:
        setup(version=version(), cmdclass={"build_py": build_py, "sdist": sdist})
    finally:
        shutil.rmtree(ROOT / "src" / "agentsflower_sdlc.egg-info", ignore_errors=True)  # build residue


if __name__ == "__main__":
    main()
