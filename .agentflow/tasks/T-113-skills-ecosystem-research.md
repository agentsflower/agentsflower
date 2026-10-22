# T-113: Research and map best-in-class open-source agent skills ecosystem

Role: developer
Tool: devin
Model: swe-2-max
Stage: 6
Depends on: none
Branch: t-113-skills-ecosystem-research
Worktree: E:\Projects\AgentFlow\worktrees\agentflow-t-113-skills-ecosystem-research
Independent check: none - research spike
Resume: none
Routing exception: human authorized research spike for open-source skills ecosystem mapping (2026-10-23)

## Goal

Conduct a comprehensive research spike across the open-source AI agent ecosystem to identify,
evaluate, and curate authoritative agent skills (SKILL.md specifications, prompt playbooks,
and automated evaluation heuristics) across 9 critical engineering disciplines:
1. Product Discovery & Market Validation (JTBD, lean specs, user pain framing).
2. UI/UX Design & Micro-motion (impeccable, taste-skill, emilkowalski design-eng).
3. Modern Frontend Engineering (Next.js/Vite/Svelte, Web Vitals, accessibility AA).
4. Chrome Extension Architecture (Manifest V3, sandboxed content scripts, secure CSP).
5. Backend Architecture & Algorithms (Clean/Hexagonal Architecture, Twelve-Factor, Safe DB migrations).
6. DevOps & Infrastructure (Hardened CI/CD, least-privilege containers, rollback automation).
7. System Architecture & Decisions (ADR frameworks, API design standards).
8. Engineering Management & Quality Assurance (Mutation testing, contract verification).
9. SEO & GEO (Generative Engine Optimization for AI agent search like Perplexity, ChatGPT Search, Google AI Overviews, and classic Google Search indexing; best practices for modern web/blogs/Astro SSG sites: structured schema.org JSON-LD microdata, llms.txt protocol, dynamic OpenGraph/Twitter cards, automated sitemap.xml, robots.txt crawl directives, canonical URLs, semantic HTML5 heading hierarchy, Core Web Vitals, and direct-answer chunking for AI search extractors).

Deliver a structured implementation plan and curated repository catalog ready for distillation
into AgentFlow's `.agentflow/skills/` directory. Change no product code in this task.

## Read first

- .agentflow/docs/project-rules.md
- .agentflow/docs/ai-handoff-protocol.md
- .agentflow/docs/engineering-rules.md

## Allowed files

- .agentflow/docs/skills-ecosystem-catalog.md
- .agentflow/docs/skills-implementation-roadmap.md

## Do not touch

- Product code, existing tools, ledger, canonical state files (propose updates in Result).
- Existing test suites and configuration files.

## Setup

- nothing

## Port

- nothing

## Rebuild together

- nothing

## Acceptance criteria

- [ ] R-01: Curated catalog of at least 18-25 top-tier open-source skill repositories mapped across the 9 required domains with exact licenses, author sources, and integration methods.
- [ ] R-02: Gap analysis comparing generic LLM defaults against specialized skill-guided behaviors for each domain (identifying specific failure modes like "AI-slop", MV2 legacy bugs, poor crawlability/missing JSON-LD, leaky abstractions).
- [ ] R-03: Architectural specification for embedding these skills into AgentFlow (directory structure `.agentflow/skills/`, automatic binding via `## Read first`, and mapping to `engineering-rules.md`).
- [ ] R-04: Quality gate criteria defined for each domain so independent Tester tasks can objectively verify adherence in code reviews.
- [ ] R-05: Clean artifact committed in the branch with zero product regressions.

## Checks

- `python -c "import pathlib; assert pathlib.Path('.agentflow/docs/skills-ecosystem-catalog.md').exists() and pathlib.Path('.agentflow/docs/skills-implementation-roadmap.md').exists()"`

## Result
Outcome: completed
Change: 025e696fce64ab3eab93730a0eed9c47813c8e79 on t-113-skills-ecosystem-research
Files:
- .agentflow/docs/skills-ecosystem-catalog.md - curated ecosystem map: 25 primary sources across the 9 domains plus cross-cutting infrastructure, secondary sources, standards layer, license watchlist, per-domain gap analysis, first-distillation shortlist
- .agentflow/docs/skills-implementation-roadmap.md - architecture spec for .agentflow/skills/ (spec-conformant SKILL.md, flat naming, INDEX/ATTRIBUTION), binding via ## Read first + engineering-rules.md routing table + optional generated native wrappers, licensing policy, security vetting, per-domain quality gates, 4-phase implementation plan, evaluation plan
Checks:
- `python -c "import pathlib; assert pathlib.Path('.agentflow/docs/skills-ecosystem-catalog.md').exists() and pathlib.Path('.agentflow/docs/skills-implementation-roadmap.md').exists()"` -> pass
Criteria:
- R-01: pass - .agentflow/docs/skills-ecosystem-catalog.md sections 2-4 list 25 primary repositories (C-01..C-26, one ID shared across domains) each with author, exact verified license, and integration method, plus ~15 secondary sources and a standards layer
- R-02: pass - .agentflow/docs/skills-ecosystem-catalog.md section 6 gives a per-domain table of generic LLM failure modes (AI-slop page composition, MV2 idioms, hot-table ALTER, missing JSON-LD/llms.txt, leaky scaling advice) vs the specialized skills' mechanisms
- R-03: pass - .agentflow/docs/skills-implementation-roadmap.md sections 2-3 specify .agentflow/skills/ layout (flat name==dir, spec frontmatter, references/ split), the ## Read first binding plus an engineering-rules.md routing table plus optional generated per-tool wrappers
- R-04: pass - .agentflow/docs/skills-implementation-roadmap.md section 6 defines a Tester-verifiable quality gate per domain (binary manifest checks, EXPLAIN ANALYZE evidence, Lighthouse budgets, ADR completeness, contract/mutation coverage, GEO checklist)
- R-05: pass - single commit 025e696 touching only the two allowed files; the mandatory full suite ran 461 tests with one failure matching the documented transient ledger _write_atomic os.replace WinError 5 flake (isolated rerun of that test module: 7/7 green); zero product-code changes
Found, not fixed:
- The transient ledger _write_atomic os.replace WinError 5 recurred in test_workspace.test_develop_and_accept during the pre-commit suite run - same signature as the known-issues entry dated 2026-10-18; that entry's suggested bounded hardening (replace-retry on ledger writes) remains open.
- The Task File's Read first named .agentflow/docs/engineering-rules.md, which does not exist in this repository; the roadmap proposes creating it as the project-owned routing layer for skills.
- vercel-labs/agent-skills (a primary source for frontend rules) ships no repository LICENSE file - cataloged as reference-only; runtime install via npx skills is the clean consumption path.
Proposed memory updates:
- decisions.md: record the skills architecture decision when the Orchestrator adopts the roadmap (flat spec-conformant .agentflow/skills/, ## Read first binding first, native wrappers optional/later, distill-don't-vendor licensing policy).
- known-issues.md: add a dated note that the ledger _write_atomic os.replace flake reproduced on 2026-10-23 in test_workspace.test_develop_and_accept (another data point for the bounded hardening task).
- project-plan.md / tasks: the roadmap's P1-P4 phase table is ready to become developer+tester Task Files when the human approves skills work.
