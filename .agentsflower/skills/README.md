# AgentsFlower Specialized Skills Ecosystem

This directory contains the curated library of specialized agent skills for AgentsFlower.
Skills follow the Antigravity / Claude Code skill standard (`SKILL.md` with YAML frontmatter, execution workflows, reference documentation, and deterministic verification scripts).

## Directory Structure

```
.agentsflower/skills/
├── README.md                  # Ecosystem overview & guidelines
├── INDEX.md                   # Taxonomy of all 9 specialized domains
├── ATTRIBUTION.md             # Open-source sources and upstream credits
└── <skill-name>/
    ├── SKILL.md               # Frontmatter, triggers, instructions, guidelines
    ├── scripts/               # Deterministic execution tools & CLI validators
    ├── references/            # Deep technical references & prompt guidelines
    └── examples/              # Verified input/output patterns
```

## How Skills Are Used

1. **Role Execution:** When an AI worker launches with a role (`developer`, `tester`, `deployer`, `orchestrator`), the worker loads relevant skills based on task context and allowed files.
2. **Deterministic Scripts:** Each skill includes lightweight Python scripts (`scripts/`) with zero external dependencies to compute metrics, validate compliance, or generate assets without human intervention.
3. **Template Packaging:** Skills are template-owned (`install.py`), ensuring all child projects receive continuous updates when running `agentsflower install --update`.
