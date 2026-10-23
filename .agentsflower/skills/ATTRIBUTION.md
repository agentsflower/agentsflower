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
