#!/usr/bin/env python3
"""Assembles the self-contained roadmap-view mockup pages.

  python .agentflow/dashboard/mockups/build.py

Reads fixtures.json, the real shared layer (../common.css, ../filterbar.css,
../filterbar.js) and the mockup chrome (chrome.css, chrome.js), substitutes the
markers in src/*.src.html and writes one self-contained roadmap-*.html per
variant. The outputs are committed so the human can open them offline and pick
a layout (UI-RULES A1.2). Product sources are never touched.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DASH = HERE.parent
SRC = HERE / "src"
VARIANTS = {
    "cards.src.html": "roadmap-a-cards.html",
    "journey.src.html": "roadmap-b-journey.html",
    "matrix.src.html": "roadmap-c-matrix.html",
}


def build():
    fixtures = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))
    fixtures["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    css = "".join((DASH / f).read_text(encoding="utf-8") for f in ("common.css", "filterbar.css")) \
        + (HERE / "chrome.css").read_text(encoding="utf-8")
    js = (DASH / "filterbar.js").read_text(encoding="utf-8") \
        + (HERE / "chrome.js").read_text(encoding="utf-8")
    data = json.dumps(fixtures, ensure_ascii=False).replace("</", "<\\/")
    for src_name, out_name in VARIANTS.items():
        page = (SRC / src_name).read_text(encoding="utf-8")
        page = (page.replace("/*MOCKUP_CSS*/", css).replace("/*MOCKUP_JS*/", js)
                    .replace("__DATA__", data).replace("__PROJECT__", fixtures["project"]))
        (HERE / out_name).write_text(page, encoding="utf-8")
        print("built", out_name)


if __name__ == "__main__":
    sys.exit(build())
