# Skills Attribution & Licensing

The skills within `.agentsflower/skills/` build upon open-source research, industry standards, and community best practices.

## Standards & Specifications

1. **Agent Skill Standard:**
   - Adheres to the declarative `SKILL.md` format recognized by Google Antigravity, Claude Code, and Cursor.
   - Frontmatter specifies metadata (`name`, `description`), execution patterns, and environment constraints.

2. **Generative Engine Optimization (GEO) & llms.txt:**
   - Follows the [llms.txt specification](https://llmstxt.org/) proposed for providing structured, clean markdown for Large Language Models.
   - Leverages Schema.org vocabulary (W3C community) for linked data and search engine rich snippets.
   - Respects Google Search Central, Perplexity AI, and OpenAI Search crawler guidelines.

3. **Graft Codebase Knowledge Graph:**
   - Integrates AST analysis via `@nanonets/graft` (Apache-2.0 / MIT compatible) running in WebAssembly mode with zero binary compilation overhead.

## Distilled Skills

Skills in this registry are authored distillations of upstream work. Format:
`skill | upstream repo | upstream path | license | commit pin` — commits are
pinned so a later upstream license change cannot silently re-license what was
distilled.

| Skill | Upstream repo | Upstream path | License | Commit pin |
|---|---|---|---|---|
| `frontend-art-direction` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `skills/taste-skill` (skill name `design-taste-frontend`) | MIT | `6010f91a9935f1c167dfc500fb1a475681892e6b` (`main`, pinned 2026-10-25) |
| `frontend-art-direction` | [emilkowalski/skills](https://github.com/emilkowalski/skills) | `skills/emil-design-eng` (`metadata.source` id `emilkowalski/design-eng`) | MIT | `2d228630ba1446365f614a108cb8252f1feda202` (`main`, pinned 2026-10-25) |
