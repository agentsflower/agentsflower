#!/usr/bin/env python3
"""Autonomous SEO & Generative Engine Optimization (GEO) auditor for AgentsFlower.
Evaluates semantic structure, metadata, schema.org JSON-LD, llms.txt, and AI citability.
Zero external dependencies (Python standard library only).
"""
import argparse
import html.parser
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


class HTMLAuditParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_script = False
        self.script_type = None
        self.title = ""
        self.meta_tags = []
        self.headings = []  # list of (tag, text)
        self.scripts = []  # list of (type, content)
        self.links = []  # list of (rel, href)
        self.semantic_tags = set()
        self.current_tag = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attr_dict = dict(attrs)
        if tag in ("header", "nav", "main", "article", "section", "footer", "aside"):
            self.semantic_tags.add(tag)

        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "link":
            rel = attr_dict.get("rel", "")
            href = attr_dict.get("href", "")
            self.links.append((rel, href))
        elif tag == "script":
            self.in_script = True
            self.script_type = attr_dict.get("type", "")
            self.current_text = []
        elif re.match(r"^h[1-6]$", tag):
            self.current_text = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_script = False
            content = "".join(self.current_text).strip()
            self.scripts.append((self.script_type, content))
            self.script_type = None
            self.current_text = []
        elif re.match(r"^h[1-6]$", tag):
            text = "".join(self.current_text).strip()
            self.headings.append((tag, text))
            self.current_text = []
        self.current_tag = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_script or (self.current_tag and re.match(r"^h[1-6]$", self.current_tag)):
            self.current_text.append(data)


def audit_html_content(html_text: str, source_name: str, base_dir: Path = None) -> dict:
    parser = HTMLAuditParser()
    try:
        parser.feed(html_text)
    except Exception as e:
        return {"source": source_name, "error": f"Failed to parse HTML: {e}", "score": 0}

    findings = []
    categories = {
        "semantic_structure": {"score": 20, "max": 20, "notes": []},
        "meta_tags": {"score": 20, "max": 20, "notes": []},
        "structured_data": {"score": 25, "max": 25, "notes": []},
        "ai_citability": {"score": 20, "max": 20, "notes": []},
        "llms_txt": {"score": 15, "max": 15, "notes": []},
    }

    # 1. Semantic Structure (20 pts)
    h1s = [h for h in parser.headings if h[0] == "h1"]
    if len(h1s) == 0:
        categories["semantic_structure"]["score"] -= 10
        categories["semantic_structure"]["notes"].append("Missing <h1> tag: page needs exactly one primary title.")
    elif len(h1s) > 1:
        categories["semantic_structure"]["score"] -= 6
        categories["semantic_structure"]["notes"].append(f"Multiple <h1> tags found ({len(h1s)}): prefer exactly one <h1> per document.")
    else:
        categories["semantic_structure"]["notes"].append(f"Single <h1> verified: '{h1s[0][1]}'")

    if "main" not in parser.semantic_tags:
        categories["semantic_structure"]["score"] -= 5
        categories["semantic_structure"]["notes"].append("Missing <main> tag: landmark element aids AI scrapers and accessibility.")
    else:
        categories["semantic_structure"]["notes"].append("Semantic <main> landmark verified.")

    # 2. Meta Tags & Social (20 pts)
    title = parser.title.strip()
    if not title:
        categories["meta_tags"]["score"] -= 10
        categories["meta_tags"]["notes"].append("Missing <title> tag.")
    elif len(title) < 30 or len(title) > 70:
        categories["meta_tags"]["score"] -= 3
        categories["meta_tags"]["notes"].append(f"Suboptimal title length ({len(title)} chars): optimal is 40-60 characters.")
    else:
        categories["meta_tags"]["notes"].append(f"Optimal title length ({len(title)} chars): '{title}'")

    meta_desc = None
    og_title = None
    og_desc = None
    og_image = None
    for m in parser.meta_tags:
        name = m.get("name", "").lower()
        prop = m.get("property", "").lower()
        content = m.get("content", "")
        if name == "description":
            meta_desc = content
        elif prop == "og:title":
            og_title = content
        elif prop == "og:description":
            og_desc = content
        elif prop == "og:image":
            og_image = content

    if not meta_desc:
        categories["meta_tags"]["score"] -= 6
        categories["meta_tags"]["notes"].append("Missing meta description: search engines and AI summaries rely on this.")
    else:
        categories["meta_tags"]["notes"].append(f"Meta description present ({len(meta_desc)} chars).")

    if not og_title or not og_desc:
        categories["meta_tags"]["score"] -= 4
        categories["meta_tags"]["notes"].append("Missing OpenGraph tags (og:title/og:description).")
    else:
        categories["meta_tags"]["notes"].append("OpenGraph social tags present.")

    # 3. Structured Data / Schema.org JSON-LD (25 pts)
    json_ld_blocks = [s[1] for s in parser.scripts if s[0] and "ld+json" in s[0].lower()]
    if not json_ld_blocks:
        categories["structured_data"]["score"] = 0
        categories["structured_data"]["notes"].append("No Schema.org JSON-LD found: search and AI models lack structured entity graph.")
    else:
        valid_schemas = 0
        for block in json_ld_blocks:
            try:
                data = json.loads(block)
                if isinstance(data, dict):
                    t = data.get("@type", "Unknown")
                    categories["structured_data"]["notes"].append(f"Schema.org JSON-LD entity verified: @type='{t}'")
                    valid_schemas += 1
            except Exception as e:
                categories["structured_data"]["notes"].append(f"JSON-LD parse error: {e}")
        if valid_schemas == 0:
            categories["structured_data"]["score"] = 5
        else:
            categories["structured_data"]["score"] = 25

    # 4. AI Citability & Information Density (20 pts)
    headings_count = len(parser.headings)
    if headings_count < 2:
        categories["ai_citability"]["score"] -= 8
        categories["ai_citability"]["notes"].append("Sparse outline: add informative <h2> sections to aid LLM grounding.")
    else:
        categories["ai_citability"]["notes"].append(f"Rich content structure: {headings_count} headings detected.")

    # Check for direct answer definitions
    has_definitions = any(re.search(r"\b(is a|provides|enables|designed for|allows)\b", h[1], re.I) for h in parser.headings)
    if not has_definitions:
        categories["ai_citability"]["score"] -= 4
        categories["ai_citability"]["notes"].append("Tip: Ensure prominent definition and benefit statements exist near the top.")
    else:
        categories["ai_citability"]["notes"].append("Definition grounding keywords detected in content structure.")

    # 5. LLMs.txt & Machine context (15 pts)
    if base_dir and base_dir.is_dir():
        llms_file = base_dir / "llms.txt"
        llms_full = base_dir / "llms-full.txt"
        if llms_file.exists():
            categories["llms_txt"]["notes"].append("llms.txt found at project root.")
        else:
            categories["llms_txt"]["score"] -= 10
            categories["llms_txt"]["notes"].append("llms.txt missing: create /llms.txt to provide AI crawlers with clean markdown index.")

        if llms_full.exists():
            categories["llms_txt"]["notes"].append("llms-full.txt comprehensive context found.")
        else:
            categories["llms_txt"]["score"] -= 5
            categories["llms_txt"]["notes"].append("llms-full.txt missing: consider generating full context file.")
    else:
        # If auditing a single file or URL, check if links reference llms.txt
        has_llms_link = any("llms.txt" in l[1] for l in parser.links)
        if has_llms_link:
            categories["llms_txt"]["notes"].append("Discovered link reference to llms.txt.")
        else:
            categories["llms_txt"]["score"] = 5
            categories["llms_txt"]["notes"].append("No llms.txt link detected in document header.")

    # Clamp scores
    total_score = sum(max(0, c["score"]) for c in categories.values())
    total_score = max(0, min(100, total_score))

    return {
        "source": source_name,
        "score": total_score,
        "verdict": "OPTIMIZED" if total_score >= 85 else ("NEEDS_IMPROVEMENT" if total_score >= 60 else "POOR"),
        "categories": categories,
    }


def audit_target(target: str) -> dict:
    if target.startswith("http://") or target.startswith("https://"):
        req = urllib.request.Request(target, headers={"User-Agent": "AgentsFlower-GEOAudit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            return audit_html_content(content, target)

    p = Path(target).resolve()
    if p.is_file():
        text = p.read_text(encoding="utf-8", errors="replace")
        return audit_html_content(text, str(p), base_dir=p.parent)
    elif p.is_dir():
        # Look for index.html or dist/index.html
        for candidate in [p / "index.html", p / "dist" / "index.html", p / "out" / "index.html"]:
            if candidate.exists():
                text = candidate.read_text(encoding="utf-8", errors="replace")
                return audit_html_content(text, str(candidate), base_dir=p)
        return {"source": str(p), "error": "No index.html found in target folder", "score": 0}
    else:
        return {"source": str(p), "error": f"Target path {p} does not exist", "score": 0}


def main():
    ap = argparse.ArgumentParser(description="AgentsFlower SEO, GEO & AI Citability Auditor")
    ap.add_argument("target", nargs="?", default=".", help="Path to HTML file, folder, or remote URL (default: .)")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    ap.add_argument("--out", type=Path, help="Write JSON report to file")
    args = ap.parse_args()

    report = audit_target(args.target)

    if args.out:
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Audit report saved to {args.out}")

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("=" * 64)
    print(f"AgentsFlower SEO & Generative Engine Optimization (GEO) Audit")
    print(f"Target: {report.get('source')}")
    print(f"Overall Score: {report.get('score')}/100 [{report.get('verdict', 'N/A')}]")
    print("=" * 64)

    if "error" in report:
        print(f"ERROR: {report['error']}")
        return 1

    for cat_name, cat in report.get("categories", {}).items():
        title = cat_name.replace("_", " ").title()
        print(f"\n[{title}] - {cat['score']}/{cat['max']} pts")
        for note in cat.get("notes", []):
            bullet = "+" if "verified" in note.lower() or "optimal" in note.lower() or "found" in note.lower() else "!"
            print(f"  {bullet} {note}")

    print("\n" + "=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
