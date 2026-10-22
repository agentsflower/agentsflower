# Skills Implementation Roadmap

How AgentFlow embeds distilled agent skills: directory architecture, binding
mechanism, licensing policy, security vetting, per-domain quality gates, and a
phased implementation plan.

Companion document: [skills-ecosystem-catalog.md](skills-ecosystem-catalog.md)
(source selection, licenses, gap analysis). Both are T-113 research artifacts;
this file specifies, nothing here is implemented yet.

## 1. Design principles

1. **Canonical skills live in `.agentflow/skills/`**, tool-neutral, conforming
   to the Agent Skills spec (agentskills.io): `SKILL.md` + optional
   `scripts/`, `references/`, `assets/`. Tool-native copies are generated, never
   authored.
2. **Authored, not vendored.** Skills are distilled from the catalog's sources
   and rewritten for AgentFlow's worker roles; `metadata.source` records the
   upstream repo. Exception: byte-identical vendoring only under permissive
   licenses (MIT/Apache-2.0/CC0/CC-BY-4.0) with attribution.
3. **Progressive disclosure maps to `## Read first`.** AgentFlow has no
   ~100-token metadata scan; its binding mechanism is the Task File. The
   Orchestrator names skill paths in `## Read first` (or a new `## Skills`
   field — decision below); the worker reads the SKILL.md, then its
   `references/` on demand. Same loading order as the spec: metadata ->
   instructions -> resources.
4. **Rules point at skills; skills never point at rules.**
   `docs/engineering-rules.md` (project-owned, to be created) states
   repo-local commands and constraints; skills are portable how-to. A rule may
   require a skill ("frontend tasks read `frontend-quality-audit`"); a skill
   must stay usable without AgentFlow.
5. **Every skill carries a verifiable gate.** A skill that cannot be checked by
   a Tester is documentation, not a skill. R-04 below defines the bar per
   domain.

## 2. Directory layout

```text
.agentflow/skills/
  INDEX.md                           # one row per skill: name, domain, trigger, status
  ATTRIBUTION.md                     # upstream source -> license -> distilled skill
  frontend-art-direction/SKILL.md    # flat: name == directory name (spec rule)
  frontend-quality-audit/SKILL.md
    references/wcag22.md
    references/core-web-vitals.md
    scripts/lighthouse-audit.mjs     # optional, only if a gate needs a script
  chrome-extension-mv3/SKILL.md
    references/manifest-v3.md
    references/service-worker.md
  ...
```

Decisions for the Orchestrator (recommendations):

- **Flat with domain prefix** (`skills/frontend-quality-audit/`) over nested
  domains (`skills/frontend/quality-audit/`): the spec requires `name` to equal
  the directory's last component, native agents discover flat layouts, and
  domain membership can live in `metadata.domain`. Recommended.
- **SKILL.md frontmatter**: `name`, `description` (what + when-to-use +
  trigger keywords, per spec), `license`, `metadata.author`, `metadata.source`
  (upstream `repo@path`), `metadata.domain`, `metadata.version`. Omit
  `allowed-tools` unless a tool binding needs it.
- **Body <= 500 lines, <= ~5k tokens**; route to `references/` per the spec's
  progressive-disclosure rule. Router-style SKILL.md (list references, say when
  each loads) is the proven shape (samber/cc-skills, Leonxlnx/taste-skill).
- **Validation**: `skills-ref validate <dir>` on every authored skill; add to
  the repo's check list once skills exist.

## 3. Binding: how a worker gets the skill

Three channels, in priority order:

1. **Task File `## Read first`** (exists today, zero code): the Orchestrator
   lists `.agentflow/skills/<name>/SKILL.md` lines in the task. Binding is
   explicit, reviewable, and logged in the ledger. This is the mechanism the
   task mandates; no protocol change needed.
2. **`engineering-rules.md` routing table** (new project-owned file): a short
   "when the task touches X, also read skill Y" table the Orchestrator consults
   when authoring Task Files — the static routing layer, so binding doesn't
   depend on Orchestrator memory.
3. **Native tool wrappers** (optional, later): `install.py` generates thin
   per-tool entries — like the existing `.claude/commands/` pointer pattern —
   into each tool's skills dir (`.claude/skills/`, `.codex/skills/`,
   `.devin/skills/`, `.agents/skills/`), each pointing back to the canonical
   `.agentflow/skills/` folder. Follows the improvement-plan rule: "keep
   canonical procedures platform-neutral and generate or reference native
   command/skill wrappers." Per-tool paths must be verified per tool version
   before generation.

Deliberately rejected: auto-activation by description matching (AgentFlow has
no runtime hook for it and the Task File binding is already deterministic);
vendored third-party skills installed via `npx skills add` into the template
(supply-chain exposure; skills are instructions — an adversarial SKILL.md is a
prompt injection shipped in the repo).

## 4. Licensing & attribution policy

| Upstream license | Policy |
|------------------|--------|
| MIT, Apache-2.0, CC0, CC-BY-4.0 | Adapt freely; `metadata.source` + `ATTRIBUTION.md` row required |
| CC-BY-SA-4.0 (Trail of Bits) | Pattern-level reuse preferred; verbatim adaptation obliges share-alike + attribution — avoid |
| CC BY-NC-SA (deanpeters, joelparkerhenderson text) | Read for structure only; re-derive content |
| Commons Clause + MIT (borghei), Sustainable Use (oh-my-openagent) | Reference only |
| No LICENSE (vercel-labs/agent-skills, mager/frontend-design) | Reference only; recommend runtime install via `npx skills` for users who want the original |
| Source-available (anthropics docx/pdf/pptx/xlsx) | Never vendor |

`ATTRIBUTION.md` row format: `skill | upstream repo | upstream path | license |
commit pin`. Pin upstream commits so a later license change cannot silently
re-license what we distilled.

## 5. Security vetting (adoption gate for any imported material)

Adapted from `trailofbits/skills-curated`'s `scan_plugin.py`: before any
distilled or vendored skill lands, scan for (a) network egress — URLs, curl,
requests/urllib in scripts; (b) unicode tricks — bidi overrides, zero-width
chars, homoglyphs, punycode; (c) destructive ops — `rm -rf`, force-push,
`chmod 777`. BLOCK findings reject the import; WARN needs human review. Skills
must never embed credentials, external fetch-and-execute steps, or hidden
`allowed-tools` escalation. A skill that instructs "download and run X" is a
defect.

## 6. Quality gates per domain (R-04)

Objective checks a Tester task can run in code review. Each becomes a `## Checks`
or criterion line in downstream task files; none require model judgment alone.

| Domain | Quality gate (Tester-verifiable) |
|--------|----------------------------------|
| 1. Product discovery | Artifact exists before build tasks: spec or OST with explicit problem statement, named JTBD pains/gains, assumption list with Impact x Risk rating, measurable success criteria. Reject feature-list PRDs without a problem section |
| 2. UI/UX & micro-motion | Enter animations use ease-out/decelerating curves; no ease-in on enter; motion respects `prefers-reduced-motion`; no hover-only affordances; page passes a real-browser screenshot check at 3 widths with zero items from the anti-slop list (centered hero + icon-card row + soft gradient as the whole design) |
| 3. Frontend | Lighthouse (or equivalent) scores captured before/after; LCP/INP/CLS within budget or documented; no new client-side fetch of server-available data; images have dimensions + lazy loading; `aria-label`/keyboard path on interactive elements; WCAG 2.2 AA checklist items pass |
| 4. Chrome extensions | `manifest_version: 3`; `background.service_worker` not `background.scripts`; `chrome.action`/`chrome.scripting` not `browserAction`/`tabs.executeScript`; `host_permissions` separate from `permissions`; zero inline scripts/handlers in HTML; CSP key present; no `eval`/`unsafe-eval`; permissions list is minimal and each is justified |
| 5. Backend | Migrations use expand-migrate-contract on live tables; no in-place rename/drop on tables >1M rows; indexes via `CONCURRENTLY`; new/changed queries have `EXPLAIN ANALYZE` evidence; config via env not code defaults (twelve-factor); no sequential scan accepted on >10k-row tables |
| 6. DevOps | Pipeline has security stage (SAST/SCA/secrets) before deploy; no `pull_request_target` + PR-head checkout; permissions per-job least-privilege (no `*` allowlists, no `write-all`); secrets never in env logs; deploy strategy names rollback (canary/blue-green) and smoke-verify step exists; containers run non-root from minimal base |
| 7. System architecture | ADR exists for each multi-component/hard-to-reverse decision: Status, Context, options matrix (>=2 real alternatives), Decision, Consequences, explicit non-goals, measurable constraints, verification step. Reject decisions recorded only in chat/commit messages |
| 8. EM & QA | New behavior lands RED-GREEN-REFACTOR (failing test first); no assertion-free tests; contract changes carry consumer/provider contract tests (Pact or equivalent); mutation score above agreed threshold on touched modules (e.g. Stryker >= 60 or documented exception); "done" requires the check command actually run, output captured |
| 9. SEO & GEO | Valid JSON-LD (schema.org) on indexable pages; `/llms.txt` present and drift-checked; robots.txt AI-crawler policy explicit (allow or documented deny); sitemap.xml current; canonical URLs; single-H1 semantic heading hierarchy; OpenGraph/Twitter cards; key pages contain direct-answer blocks (self-contained quotable 40-80 word answers near top); citability score recorded before/after |

## 7. Distillation pipeline

Per shortlisted skill (order in catalog section 7):

1. Author `.agentflow/skills/<name>/` — spec-conformant SKILL.md routing to
   `references/`; encode the domain's R-04 gate inside the skill as
   "Definition of done" so workers self-check.
2. `ATTRIBUTION.md` + `INDEX.md` rows; run `skills-ref validate`.
3. Add the routing line to `engineering-rules.md` (new file, project-owned).
4. Orchestrator names the skill in relevant Task Files' `## Read first`.
5. Evaluate on the seeded scenario for that domain (section 8), then iterate.

## 8. Evaluation plan

Before/after measurement per improvement-plan section 6 (identical criteria,
recorded tool/model): run seeded tasks without vs with the skill bound —
a landing page (anti-slop), an MV2-laden extension request, a destructive
migration request, an API contract change, a page missing JSON-LD/llms.txt.
Compare against the R-04 gates. Skills that don't move the measured outcome get
rewritten or dropped; no skill ships on faith.

## 9. Proposed task sequence (Orchestrator's call, not committed work)

| Phase | Content | New Task Files suggested |
|-------|---------|--------------------------|
| P1 | Skeleton: `skills/INDEX.md`, `ATTRIBUTION.md`, `engineering-rules.md` routing table; pilots `frontend-art-direction` + `chrome-extension-mv3` (clearest binary gates) | 1-2 developer tasks + tester per pilot |
| P2 | Backend/DevOps/SysArch: `safe-db-migration`, `backend-architecture`, `ci-cd-hardening`, `adr-authoring` | per-skill developer tasks, tester on gates |
| P3 | QA + GEO + Product: `tdd-discipline`, `contract-testing`, `geo-seo-audit`, `product-discovery`, `spec-driven-feature` | same |
| P4 | `skills-ref` in repo checks; optional native-wrapper generation in `install.py`; scanner (sec. 5) as `tools/skill_vet.py` | 1 developer task + tester |

Each phase obeys existing protocol: Task File with Allowed files =
`.agentflow/skills/**` (+ `docs/engineering-rules.md`), Checks =
`skills-ref validate` + the domain gate on a fixture.

## 10. Risks and open questions

- **Spec drift**: the format is young (open standard since 2025-12); pin
  `skills-ref` version, re-validate on AgentFlow updates.
- **Skill rot**: upstream best practices move (e.g. Next.js version-matched
  guidance). `metadata.source` pins make refresh audits possible; INDEX.md
  gains a `reviewed` date.
- **Context cost**: binding via `## Read first` loads the full body — keep
  SKILL.md bodies small; split to `references/` aggressively.
- **Prompt-injection via skills**: a distilled skill is instructions in-repo;
  section 5's scan + code review of every skill PR is the mitigation.
- **Open question for the Orchestrator**: add an explicit `## Skills:` Task
  File field (better telemetry in `gate.py`) or keep binding inside
  `## Read first` (zero schema change)? Recommendation: `## Read first` now,
  dedicated field only if gate needs to distinguish skills from context files.
