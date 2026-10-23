"""agentsflower-sdlc: the AgentsFlower template bundle and unified CLI.

`agentsflower/template/` holds a copy of this repository's `.agentsflower/` template
files, generated at build time from the single source (see setup.py); it is the
same set install.py copies into a project. It carries no state/, no task
contracts and no project rules, so it is never mistaken for an installed project.
"""
from importlib import resources
from pathlib import Path

TEMPLATE = Path(str(resources.files("agentsflower") / "template"))

_version = TEMPLATE / "VERSION"
__version__ = _version.read_text(encoding="utf-8").strip() if _version.is_file() else "0+unknown"
