# Skills Ecosystem Catalog

Research spike for T-113: a curated map of best-in-class open-source agent-skill
repositories (SKILL.md packages, prompt playbooks, evaluation heuristics) across
nine engineering disciplines, for distillation into `.agentflow/skills/`.

Researched 2026-10-23. Licenses and activity verified against repository license
files and the GitHub API on that date; star counts are snapshots, not criteria.

Companion document: [skills-implementation-roadmap.md](skills-implementation-roadmap.md).

## 1. The ecosystem in brief

"Agent Skill" is an open format: a folder with a `SKILL.md` (YAML frontmatter
`name` + `description`, Markdown body) plus optional `scripts/`, `references/`,
`assets/`. Anthropic released it as an open standard (agentskills.io); it is now
loaded by Claude Code, Codex, Cursor, Gemini CLI, Antigravity, Copilot, Windsurf
and ~40 more tools. The defining property is progressive disclosure: an agent
sees ~100 tokens of metadata per skill, loads the body (recommended < 5k tokens)
only when the description matches the task, and pulls referenced files on demand.

Distribution channels: raw git repos, per-tool plugin marketplaces
(`/.claude-plugin`, `/.codex-plugin` manifests), and the `npx skills` CLI
(`vercel-labs/skills`) which resolves `owner/repo` sources and installs into the
detected agent's skills directory; skills.sh and skilltrove.dev are public
registries with usage metrics.

Measured context cost is small: the 15-skill `obra/superpowers` bundle costs
~489 tokens of metadata per session (agentmods.dev measurement).

## 2. Selection criteria

A repository is "primary" (C-xx) when it meets most of:

- Authoritative author: the vendor of the technology, a named domain expert, or
  a team shipping the practice in production — not AI-generated bulk content.
- Clear license: OSI-approved for code, Creative Commons for content; anything
  restrictive or absent goes to the watchlist (section 5).
- Executable structure: SKILL.md frontmatter + progressive references, not a
  wall of one-file prompts.
- Maintained: commits in 2026; issue activity.
- Measurable guidance: rules, thresholds, checklists, scripts a reviewer can
  verify against — the property AgentFlow's Tester role needs (R-04).

## 3. Curated catalog (primary sources)

### Cross-cutting: format, distribution, vetting

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-01 | [agentskills/agentskills](https://github.com/agentskills/agentskills) | Agent Skills org (Anthropic-originated open standard) | Apache-2.0 (code), CC-BY-4.0 (docs) | The format spec, `skills-ref` validator CLI | Normative reference; run `skills-ref validate` on every authored skill |
| C-02 | [anthropics/skills](https://github.com/anthropics/skills) | Anthropic | Apache-2.0 most skills; `docx`/`pdf`/`pptx`/`xlsx` source-available (not OSS) | Reference skills + `skill-creator` (authoring workflow, eval guidance) | Distill authoring patterns; never vendor the document skills |
| C-03 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | Vercel Labs | MIT | `npx skills` CLI: install/find/use across 75+ agents; skills.sh registry | Optional per-tool install path; AgentFlow keeps its own canonical dir instead |
| C-04 | [VoltAgent/awesome-claude-skills](https://github.com/VoltAgent/awesome-claude-skills) | VoltAgent community | MIT | Curated index of 1000+ skills, hand-picked official team skills | Discovery index for future waves; not vendored |
| C-05 | [trailofbits/skills-curated](https://github.com/trailofbits/skills-curated) | Trail of Bits | CC-BY-SA-4.0 | Staff-vetted skill marketplace; `scripts/scan_plugin.py` — deterministic scanner (network calls, unicode tricks, destructive ops) | Adapt the scanner as AgentFlow's skill-adoption gate |

### Domain 1 — Product Discovery & Market Validation

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-06 | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | Pawel Huryn (product management author) | MIT | 68 PM skills / 42 workflows in 9 plugins; `pm-product-discovery`: Opportunity Solution Trees, JTBD interview scripts + synthesis, assumption identification/prioritization, lean pretotype experiments | Distill `product-discovery` skill: OST + JTBD + assumption-matrix rituals |
| C-07 | [github/spec-kit](https://github.com/github/spec-kit) | GitHub | MIT | Spec-Driven Development toolkit: `/speckit.*` flow constitution -> specify -> clarify -> plan -> tasks -> analyze -> implement -> converge; skills mode for Copilot/Codex | Distill `spec-driven-feature` skill; borrow its clarify/checklist quality gates |
| C-08 | [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | BMad Code, LLC | MIT | Agile AI-driven development: analyst/PM/architect/QA personas, sized delivery loop (Clarify/Plan/Build/Learn), durable decision context | Distill persona handoff pattern; mirrors AgentFlow role model closely |

Secondary: `snarktank/ai-dev-tasks` (Apache-2.0, Ryan Carson — minimal
PRD -> task-list -> one-task-at-a-time playbook; a simpler precursor of
spec-kit's flow).

### Domain 2 — UI/UX Design & Micro-motion

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-09 | [emilkowalski/skills](https://github.com/emilkowalski/skills) | Emil Kowalski (ex-Vercel, Linear) | MIT | `emil-design-eng`, `animate`, `review-animations`, `improve-animations`, `animation-vocabulary`, `apple-design`; catalog of concrete agent mistakes (wrong easing direction, opaque borders vs translucent shadows) | Distill `motion-design` + `ui-polish-review` skills almost verbatim-level guidance |
| C-10 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | GreenSock (GSAP vendor) | MIT | Official GSAP skills: core, timeline, ScrollTrigger, React, plugins, performance; "when to recommend GSAP" decision rules | Distill `web-animation-gsap`; vendor-correct API usage |
| C-11 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | Leonxlnx | MIT | `design-taste-frontend`: anti-slop page builder distilled from 247 curated gallery sites; direction-dealing script, real-browser inspector, look-and-fix loop (max 3 rounds) | Distill `frontend-art-direction`; adopt its measure-in-a-real-browser loop as the anti-AI-slop gate |

Secondary: `expo/skills` (MIT — official Expo skills; `expo-animation` was
co-authored with Kowalski: Reanimated worklets, gesture handoff, haptics —
React Native scope), `DonkeyKing01/tasteful-ui-skill` (MIT — taste-first modes
with anti-generic rules), `mager/frontend-design` (no license — reference only).

### Domain 3 — Modern Frontend Engineering

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-12 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Vercel | No repository LICENSE (all rights reserved; treat as reference) | `react-best-practices` (40+ rules / 8 categories ranked by impact: waterfalls, bundle, server-side, data fetching, re-render), `web-design-guidelines` (100+ a11y/perf/UX rules), `vercel-composition-patterns`, `vercel-optimize` | Install at runtime via `npx skills` or consult as reference; do not vendor text |
| C-13 | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills) | Addy Osmani (Google Chrome) | MIT | Measurement-first skills: `web-quality-audit`, `performance`, `core-web-vitals` (LCP/INP/CLS), `accessibility` (WCAG 2.2), `seo`, `best-practices`; Lighthouse + CrUX + Chrome DevTools MCP loops | Distill `frontend-quality-audit`: evidence-before-opinion is the model for every AgentFlow quality skill |
| C-14 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Addy Osmani | MIT | Lifecycle skills + commands: `/spec /plan /build /test /constraints /review /webperf /code-simplify /ship`; debugging-and-error-recovery, code-review five-axis method | Distill `code-review-method` + constraints-once pattern; overlaps AgentFlow gates |

### Domain 4 — Chrome Extension Architecture

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-15 | [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance) | Google Chrome team | Apache-2.0 | `modern-web-guidance` + `chrome-extensions` skills (MV3 mandatory rules, Web Store publishing); ships `.claude-plugin`/`.codex-plugin`/`.cursor-plugin`/`gemini-extension.json` manifests — the multi-tool packaging precedent | Distill `chrome-extension-mv3`; copy its one-source-many-manifests layout for AgentFlow tool bindings |
| C-16 | [samber/cc-skills](https://github.com/samber/cc-skills) | samber | MIT | `chrome-extension` skill: thin SKILL.md router -> `references/` files per topic (manifest-v3, service-worker, content-scripts...), `allowed-tools` scoping | Structural template for AgentFlow skills: router + on-demand references |
| C-17 | [quangpl/browser-extension-skills](https://github.com/quangpl/browser-extension-skills) | quangpl | MIT | Full extension lifecycle: create (WXT/CRXJS), dev, manifest, analyze (security + CWS compliance), test (Puppeteer E2E), assets, payment, backend | Distill `extension-security-audit` checklist into the quality gate |

### Domain 5 — Backend Architecture & Algorithms

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-18 | [peterhdd/agent-skills](https://github.com/peterhdd/agent-skills) | peterhdd | MIT | `engineering-backend-architect`: concrete scaling thresholds (PgBouncer >200 conns, Redis >100 identical q/m, shard >5TB), data-migration rules (expand-migrate-contract, `CREATE INDEX CONCURRENTLY` >10M rows, no in-place rename), self-verification protocol (`EXPLAIN ANALYZE` gate) | Distill `backend-architecture` + `safe-db-migration` skills; the numeric thresholds are the differentiator |
| C-19 | [wshobson/agents](https://github.com/wshobson/agents) | Seth Hobson | MIT | 94 plugins / 202 agents / 185 skills / 105 commands (backend-architect, deployment-engineer, security-auditor...); one Markdown source compiled per harness via `tools/adapters/` | Source for backend/devops sub-skills; its adapter layer is the precedent for generating per-tool bindings |

Secondary: `siviter-xyz/dot-agent` (MIT — backend-engineer skill, OWASP/auth
patterns), `borghei/Claude-Skills` (Commons Clause + MIT — see watchlist;
`migration-architect` covers zero-downtime phased migrations).

### Domain 6 — DevOps & Infrastructure

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-20 | [yonatangross/orchestkit](https://github.com/yonatangross/orchestkit) | OrchestKit | MIT | `devops-deployment` skill: GH Actions/Docker/Helm/Terraform patterns, path-gated loading (`paths:` frontmatter on `Dockerfile*`, `.github/workflows/**`), invocation hooks | Distill `ci-cd-hardening`; borrow path-pattern triggers |
| C-21 | [trailofbits/skills](https://github.com/trailofbits/skills) | Trail of Bits | CC-BY-SA-4.0 | Security skills incl. `agentic-actions-auditor` (AI-agent injection vectors in GH Actions: `pull_request_target`+checkout, env-var intermediaries, wildcard allowlists), `differential-review`, `fp-check`, `insecure-defaults` | Distill the CI audit checklist (share-alike: adapt with attribution, or re-derive from docs) |

Secondary: `dolutech/dolu-agents-skills` (MIT — `deploy-automation` canonical
pipeline map: source -> build -> test -> security -> package -> deploy ->
verify).

### Domain 7 — System Architecture & Decisions

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-22 | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Anthropic | Apache-2.0 | Engineering skills: `architecture` (ADR create/evaluate with options matrix + trade-off analysis), `system-design` (requirements -> scale -> trade-offs) | Distill `adr-authoring` output template |
| C-23 | [vercel/ai](https://github.com/vercel/ai) — `skills/adr-skill` | Vercel | Apache-2.0 | `adr-skill`: ADR as "executable specification for coding agents" — measurable constraints, non-goals, implementation plan + verification; Socratic intake before drafting | Distill the agent-executable ADR format — matches AgentFlow's Task File philosophy |

Secondary: `sbrudz/agent-skills` (MIT — Nygard-template ADR skill with a
"2+ of 4 questions" threshold gate and propose->review two-agent flow).

### Domain 8 — Engineering Management & Quality Assurance

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-24 | [obra/superpowers](https://github.com/obra/superpowers) | Jesse Vincent / Prime Radiant | MIT | ~20 methodology skills: test-driven-development (RED-GREEN-REFACTOR + anti-patterns), systematic-debugging (4-phase root cause), verification-before-completion, writing-plans, requesting/receiving-code-review, using-git-worktrees | Distill `tdd-discipline` + `verify-before-done`; AgentFlow's own lifecycle already rhymes with it |
| C-25 | [pactflow/pactflow-agent-skills](https://github.com/pactflow/pactflow-agent-skills) | SmartBear / PactFlow | MIT | Official contract-testing skills: Pact consumer/provider patterns, can-i-deploy diagnostics, Drift OpenAPI test authoring | Distill `contract-testing` skill + review checklist for API changes |

Secondary: `felixgeelhaar/skills` (MIT — `quality-expert`: Socratic QA strategy,
test-pyramid judgment, mutation/contract/chaos framing),
`Fujigo-Software/f5-framework-claude` (MIT — `testing-advanced`: Stryker
thresholds, Pact examples, flaky-test management).

### Domain 9 — SEO & GEO

| ID | Repository | Author / source | License | What it ships | Integration method |
|----|-----------|-----------------|---------|---------------|--------------------|
| C-26 | [Auriti-Labs/geo-optimizer-skill](https://github.com/Auriti-Labs/geo-optimizer-skill) | Auriti Labs | MIT | GEO/AEO toolkit: 0-100 citability score across ChatGPT/Perplexity/Gemini/AI Overviews/Claude, llms.txt generation + drift check, AI-crawler access audit; CLI, Python lib, MCP server, GH Action, Astro integration | Distill `geo-seo-audit` skill; the scorer itself is a candidate `scripts/` asset |
| C-13 | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills) — `seo` skill | Addy Osmani | MIT | Crawlability, structured data, modern SEO checks inside the measurement-first framework | Shared primary (domain 3); its seo rules feed `geo-seo-audit` |

Secondary: `alirezarezvani/claude-skills` (MIT — ~390 skills incl. AEO/answer-
engine-optimization marketing set, DevOps, compliance, C-level personas; broad
but less curated), `madeburo/GEO-AI` (MIT — TS engine: llms.txt, bot rules,
crawl tracking), `cloudapp-dev/awesome-open-geo` (CC0 — index of OSS GEO
tooling), `continuedev/next-geo` (Apache-2.0, archived — llms.txt + markdown
content negotiation for Next.js), `cortega26/geo-opt` (custom license — local
GEO/JSON-LD/technical-SEO CLI with labeled evidence levels).

## 4. Standards layer (distill from, do not wrap)

Canonical specifications and reference tools that ground the skills above.
These are the sources a skill cites, not skills themselves.

| Domain | Source | License/owner |
|--------|--------|---------------|
| Format | [Agent Skills spec](https://github.com/agentskills/agentskills) + `skills-ref` validator | Apache-2.0 / CC-BY-4.0 |
| Backend | twelve-factor.net; `golang-migrate/migrate` (MIT); `ardalis/CleanArchitecture` (MIT); PostgreSQL docs (expand-contract, `CREATE INDEX CONCURRENTLY`) | as listed |
| DevOps | SLSA framework; sigstore/cosign signing; `GoogleContainerTools/distroless`; OWASP CI/CD cheatsheet; `step-security/harden-runner` | mixed OSS |
| SysArch | `adr/madr` (dual MIT/CC0-1.0); `microsoft/api-guidelines` (CC-BY-4.0); `zalando/restful-api-guidelines` (CC-BY-4.0); `OAI/OpenAPI-Specification` (Apache-2.0); `joelparkerhenderson/architecture-decision-record` (CC BY-NC-SA — reference only) | as listed |
| EM/QA | `stryker-mutator/stryker-js` (Apache-2.0); `mutmut`; `pact-foundation/pact-js` (MIT); Google testing pyramid | as listed |
| SEO/GEO | `AnswerDotAI/llms-txt` spec+tooling (Apache-2.0); schema.org JSON-LD; web.dev Core Web Vitals; GEO research (Aggarwal et al., KDD'24); robots.txt/AI-crawler directives | as listed |

## 5. License watchlist (reference only, never vendor)

- `deanpeters/Product-Manager-Skills` — CC BY-NC-SA 4.0 (non-commercial): 77 PM
  frameworks incl. JTBD. Read for structure, re-derive content.
- `anthropics/skills` `docx`/`pdf`/`pptx`/`xlsx` — source-available, not OSS.
- `trailofbits/skills`, `skills-curated` — CC-BY-SA-4.0: adaptation requires
  attribution + share-alike; safest is pattern-level reuse.
- `joelparkerhenderson/architecture-decision-record` — author's text is
  CC BY-NC-SA; individual templates carry their own terms.
- `vercel-labs/agent-skills` — no repository LICENSE file (GitHub `license:
  null`). Consume at runtime via `npx skills` or as reading; do not copy text.
- `borghei/Claude-Skills` — Commons Clause + MIT: no right to "sell" the
  software; fine for internal reference, avoid vendoring.
- `code-yeongyu/oh-my-openagent` — "Sustainable Use License"
  (source-available). Reference only.
- `mager/frontend-design`, repos with no LICENSE — all rights reserved.
- Extracted-prompt collections (e.g. `x1xhlol/system-prompts-and-models-of-ai-tools`):
  provenance unclear; never vendor, consult only.

AgentFlow policy encoded by this: **distill behavior into authored skills with
an attribution note; vendor nothing verbatim unless the license is permissive
(MIT/Apache-2.0/CC0/CC-BY-4.0) and the `metadata.source` field records origin.**

## 6. Gap analysis — generic LLM defaults vs skill-guided behavior

| Domain | Generic LLM failure modes | What the specialized skills change |
|--------|---------------------------|-------------------------------------|
| 1. Product discovery | Writes feature-list PRDs from a one-line brief; conflates solutions with problems; no assumption inventory; success criteria absent or unmeasurable | Forces what-and-why before how (spec-kit specify->clarify); JTBD interviews mine jobs/pains/gains not feature requests (pm-skills); risky assumptions get an Impact x Risk matrix and pretotype experiments before build; tasks generated only after a checked spec |
| 2. UI/UX & micro-motion | "AI-slop": centered hero + 3 icon cards + soft gradient + mono caption — the category average; `ease-in` on enter animations; opaque borders where translucent shadows belong; hover-only affordances; janky JS-driven motion | taste-skill deals researched directions instead of defaults and fails builds on a real-browser slop check; Kowalski skills enumerate the concrete mistakes (easing direction, shadow vs border, duration); GSAP skills give vendor-correct timeline/ScrollTrigger/performance patterns |
| 3. Frontend engineering | Request waterfalls; server data fetched client-side; unmemoized re-renders; bundle bloat; missing alt/focus-visible/reduced-motion; performance by opinion not measurement | Vercel's ranked 40+ rules fix the highest-impact classes first; web-quality-skills require Lighthouse/CrUX evidence before and after; WCAG 2.2 AA checklist is explicit (focus, keyboard, contrast) |
| 4. Chrome extensions | Emits MV2 idioms: `background.scripts`, `chrome.browserAction`, `tabs.executeScript`, merged host/permissions, inline scripts/handlers violating CSP, content scripts without world isolation | Google's own skill makes MV3 rules mandatory (service_worker, `chrome.action`, `chrome.scripting`, split `host_permissions`, no inline); lifecycle skills add store-compliance and security audits |
| 5. Backend architecture | `ALTER TABLE` on hot tables; in-place column renames; NOT NULL without default; no `EXPLAIN` on new queries; scaling advice without thresholds; leaky abstractions | Numeric scaling triggers (pool >200 conns, shard >5TB); expand-migrate-contract pattern; `CREATE INDEX CONCURRENTLY` >10M rows; self-verification protocol demands `EXPLAIN ANALYZE` evidence |
| 6. DevOps & infra | Pipelines without security stage; secrets in env/logs; `pull_request_target` + checkout of PR head; wildcard permissions; no canary/rollback; fat privileged containers | Stage-gated pipeline map (test->security->package->deploy->verify); ToB's agentic-actions-auditor catches AI-in-CI injection vectors generic review misses; distroless/least-privilege + rollback as named rules |
| 7. System architecture | Decisions live in chat and evaporate; "use a database" vagueness; no alternatives or consequences; scope creep via unstated non-goals | ADR skills add a write-threshold gate, options matrix with trade-off analysis, and the Vercel variant makes ADRs agent-executable: measurable constraints, explicit non-goals, implementation plan + verification steps |
| 8. EM & QA | Coverage-chasing; assertion-free snapshot tests; no mutation score so weak tests pass review; API contracts drift silently; "done" without verification | TDD skill enforces RED-GREEN-REFACTOR + anti-patterns; verification-before-completion demands the check actually run; Pact skills cover consumer/provider + can-i-deploy; quality-expert forces test-pyramid judgment over coverage % |
| 9. SEO & GEO | Classic-SEO-only: keywords + meta; no JSON-LD entities; no `llms.txt`; content behind JS invisible to AI crawlers; prose not chunked for direct-answer extraction; no citability measurement | GEO optimizer scores citability 0-100 across the answer engines and emits fixes (llms.txt, drift check, crawler access map); llms.txt spec gives models a curated index; direct-answer chunking + JSON-LD become checklist items, not afterthoughts |

## 7. Recommended first-distillation shortlist

Ordered by expected leverage for AgentFlow-driven projects:

1. `frontend-art-direction` + `ui-polish-review` — from C-09/C-11/C-12: the
   anti-slop gap is the largest measurable quality jump.
2. `frontend-quality-audit` — C-13: measurement-first gates (Lighthouse, CWV,
   WCAG) translate directly into Tester-verifiable checks.
3. `chrome-extension-mv3` — C-15/C-16/C-17: binary rules, easy to verify.
4. `safe-db-migration` + `backend-architecture` — C-18 + standards layer.
5. `ci-cd-hardening` — C-20/C-21 + SLSA/distroless standards.
6. `adr-authoring` (agent-executable format) — C-22/C-23.
7. `tdd-discipline` + `contract-testing` — C-24/C-25.
8. `geo-seo-audit` — C-26 + llms.txt spec.
9. `product-discovery` (OST/JTBD) + `spec-driven-feature` — C-06/C-07.

Full phasing, binding mechanism and per-domain quality gates:
[skills-implementation-roadmap.md](skills-implementation-roadmap.md).
