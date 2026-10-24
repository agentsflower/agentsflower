# T-124: Domain 9 Specialized Skill: geo-seo-audit & AI Citability

Role: developer
Tool: devin
Model: swe-2-high
Stage: 7
Depends on: T-123
Branch: t-124-domain9-geo-seo-audit
Worktree: C:\Users\Win10Pro\.agentsflower\worktrees\code-t-124-domain9-geo-seo-audit
Independent check: tester
Resume: none
Routing exception: human authorized domain 9 specialized skill (2026-10-24)

## Goal

Implement Domain 9 skill `geo-seo-audit`: comprehensive audit and scoring tool (`scripts/geo_audit.py`) assessing semantic HTML, Schema.org JSON-LD, OpenGraph tags, llms.txt drift, and computing a 100-point AI Citability Index.

## Read first

- .agentsflower/skills/INDEX.md

## Allowed files

- `.agentsflower/skills/geo-seo-audit/*`
- `.agentsflower/tests/test_skills.py`

## Do not touch

- All other files.

## Setup

- nothing

## Acceptance criteria

- [ ] C-01: `scripts/geo_audit.py` assesses semantic HTML and microdata.
- [ ] C-02: 100-point AI Citability Index calculation.
- [ ] C-03: `test_skills.py` regression suite passes.

## Checks

- python -m unittest discover -s .agentsflower/tests -p "test_skills.py"

## Result

Outcome: completed
Change: d124001
Criteria:
- C-01: pass - geo_audit.py parses HTML for metadata and microformats.
- C-02: pass - Generates 100-point citability index with markdown reporting.
- C-03: pass - test_skills.py passes cleanly.
