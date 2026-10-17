"""Console entry point: delegates to the bundled .agentflow/tools/cli.py.

One implementation lives in the template (`.agentflow/tools/cli.py`, also used
in-place by source checkouts); this module loads the bundled copy so the
installed `agentflow` command and `python .agentflow/tools/cli.py` behave the
same. The bundled copy sees its own tools/ directory, so `agentflow install`
uses bundled template resources from any working directory.
"""
import importlib.util
import sys

from agentflow import TEMPLATE

_CLI = TEMPLATE / "tools" / "cli.py"


def _load():
    spec = importlib.util.spec_from_file_location("agentflow_bundled_cli", _CLI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    if not _CLI.is_file():
        print(f"agentflow: bundled template is missing {_CLI} "
              "(broken installation; reinstall agentflow-sdlc)", file=sys.stderr)
        return 2
    return _load().main()


if __name__ == "__main__":
    sys.exit(main())
