"""Model quota groups: which observed provider holds block which configured models.

  python .agentflow/tools/quota_groups.py <tool> [model]   # print the model's quota group ('' = tool-wide only)

One tool stays one CLI identity: one machine slot, one executable. Its models can still be billed
independently by the provider (Antigravity: Gemini apart from the shared Claude/GPT pool). An option
in .agentflow/docs/model-options.json marks that with "quota_group"; a hold is then recorded under
"<tool>:<group>" and blocks only options in that group. Holds on the bare "<tool>" key stay tool-wide,
and account/access failures are always recorded there.

The option named exactly after the tool ("agy") defines the group of the CLI's own default model, so
unmodelled launches and background sessions check the group they would actually consume.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import FLOW_ROOT  # noqa: E402

OPTIONS = FLOW_ROOT / "docs" / "model-options.json"


def options(path=None):
    """The configured options dict; {} when the file is missing or unreadable."""
    try:
        return json.loads(Path(path or OPTIONS).read_text(encoding="utf-8-sig")).get("options", {})
    except (OSError, ValueError):
        return {}


def default_group(tool, opts=None):
    """The quota group of the CLI's own default model: the option named after the tool, else None."""
    opts = options() if opts is None else opts
    return (opts.get(tool) or {}).get("quota_group")


def group_for(tool, model=None, opts=None):
    """The quota group a <tool> session on <model> consumes.

    model None -> the tool's default group (the CLI's own model choice). A configured model -> its
    option's group (None when the option is ungrouped). An unknown model -> None: only tool-wide
    holds apply, since its real group cannot be known."""
    opts = options() if opts is None else opts
    if not tool:
        return None
    if model is None:
        return default_group(tool, opts)
    for o in opts.values():
        if o.get("tool") != tool:
            continue
        if model == o.get("model") or model in (o.get("model_by_effort") or {}).values():
            return o.get("quota_group")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("tool")
    ap.add_argument("model", nargs="?", default=None)
    a = ap.parse_args()
    print(group_for(a.tool, a.model) or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
