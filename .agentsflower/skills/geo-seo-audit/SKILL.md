---
name: geo-seo-audit
description: Comprehensive SEO, Generative Engine Optimization (GEO), and AI citability auditing tool. Analyzes websites and local directories for search engine visibility, AI search ingestion (Perplexity, ChatGPT, Gemini, Copilot), schema.org JSON-LD microdata, llms.txt drift, and heading hierarchy.
---

# Generative Engine & SEO Audit (`geo-seo-audit`)

This skill provides deterministic auditing and actionable recommendations for:
1. **Traditional SEO:** Semantic HTML hierarchy (`h1..h6`), meta titles, meta descriptions, canonical URLs, viewport settings.
2. **Generative Engine Optimization (GEO / AIO):** Citability quotient, direct-answer definitions, high-density factual statements, entity grounding.
3. **Structured Data:** Schema.org JSON-LD blocks (`SoftwareApplication`, `WebSite`, `Organization`, `FAQPage`, `Article`).
4. **Machine-Readable AI Context:** `llms.txt` and `llms-full.txt` verification, link accuracy, and drift detection.
5. **Social & Sharing Hygiene:** OpenGraph tags (`og:title`, `og:description`, `og:image`, `og:url`), Twitter cards.

## Quick CLI Execution

To run an autonomous audit against any local HTML directory or file:

```bash
python .agentsflower/skills/geo-seo-audit/scripts/geo_audit.py <path-to-html-or-dist> [--json]
```

Or audit a remote live URL:

```bash
python .agentsflower/skills/geo-seo-audit/scripts/geo_audit.py https://example.com [--out report.json]
```

## Audit Scoring Criteria (0 - 100)

| Category | Weight | Evaluated Factors |
|---|:---:|---|
| **Semantic Structure** | 20% | Single `<h1>`, logical heading order (`h1 -> h2 -> h3`), semantic tags (`main`, `nav`, `header`, `footer`, `article`). |
| **Meta & Social Tags** | 20% | Title length (40-65 chars), Meta Description (120-160 chars), Canonical URL, `og:title`, `og:description`, `og:image`. |
| **Structured Data** | 25% | Valid JSON-LD `<script type="application/ld+json">`, valid `@context`, proper `@type`, non-empty required properties. |
| **AI Citability & GEO** | 20% | Information density, presence of concise definitions, bulleted summaries, absence of ungrounded marketing fluff. |
| **LLMs.txt Hygiene** | 15% | Presence of `llms.txt`, presence of `llms-full.txt`, validity of referenced documentation links. |

## Remediation Workflow for Agents

When this skill identifies audit issues:
1. **Missing or Broken JSON-LD:** Generate a complete Schema.org `SoftwareApplication` or `WebSite` JSON-LD block and place inside `<head>`.
2. **Missing `llms.txt`:** Generate an `llms.txt` following the specification with title, description, and key documentation sections.
3. **Heading Hierarchy Flaws:** Fix duplicate `<h1>` tags and ensure sub-sections properly use `<h2>` and `<h3>`.
4. **Citability Improvement:** Add a concise 2-3 sentence definition paragraph near the top of the page under the main heading.
