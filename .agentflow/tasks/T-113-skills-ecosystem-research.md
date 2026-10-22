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
and automated evaluation heuristics) across 8 critical engineering disciplines:
1. Product Discovery & Market Validation (JTBD, lean specs, user pain framing).
2. UI/UX Design & Micro-motion (impeccable, taste-skill, emilkowalski design-eng).
3. Modern Frontend Engineering (Next.js/Vite/Svelte, Web Vitals, accessibility AA).
4. Chrome Extension Architecture (Manifest V3, sandboxed content scripts, secure CSP).
5. Backend Architecture & Algorithms (Clean/Hexagonal Architecture, Twelve-Factor, Safe DB migrations).
6. DevOps & Infrastructure (Hardened CI/CD, least-privilege containers, rollback automation).
7. System Architecture & Decisions (ADR frameworks, API design standards).
8. Engineering Management & Quality Assurance (Mutation testing, contract verification).

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

- [ ] R-01: Curated catalog of at least 15-20 top-tier open-source skill repositories mapped across the 8 required domains with exact licenses, author sources, and integration methods.
- [ ] R-02: Gap analysis comparing generic LLM defaults against specialized skill-guided behaviors for each domain (identifying specific failure modes like "AI-slop", MV2 legacy bugs, leaky abstractions).
- [ ] R-03: Architectural specification for embedding these skills into AgentFlow (directory structure `.agentflow/skills/`, automatic binding via `## Read first`, and mapping to `engineering-rules.md`).
- [ ] R-04: Quality gate criteria defined for each domain so independent Tester tasks can objectively verify adherence in code reviews.
- [ ] R-05: Clean artifact committed in the branch with zero product regressions.

## Checks

- `python -c "import pathlib; assert pathlib.Path('.agentflow/docs/skills-ecosystem-catalog.md').exists() and pathlib.Path('.agentflow/docs/skills-implementation-roadmap.md').exists()"`

## Result
Outcome: not-started
Checks:
Criteria:
- R-01: unverified - pending
- R-02: unverified - pending
- R-03: unverified - pending
- R-04: unverified - pending
- R-05: unverified - pending
