# Current Step

2026-10-24 (Stage 7 live, AgentsFlower 2.17.0 on main@ac6710a):

## 1. Project Milestone & Version
- **Current Version:** `AgentsFlower 2.17.0` (remote authority `origin`: `https://github.com/agentsflower/agentsflower`).
- **Active Stage:** `Stage 7. AgentsFlower Studio, Multi-Project Gateway and Specialized Skills Ecosystem`.
- **Closed Stages:** Stages 1, 2, 3, 4, 5, and 6 are closed.

## 2. Completed Stage 7 Tasks
- **T-116 / T-117 / T-118 (Graft Integration):** AST knowledge graph with on-demand auto-install (`npm i -g @nanonets/graft --ignore-scripts`), CLI tooling (`agentsflower graft`), MCP tools (`graft_query`, `graft_impact`, `graft_symbols`), and Blast Radius preflight integration.
- **T-121 (AgentsFlower Studio Local Web UI):** Zero-pip-dependency Python `http.server` backend (`studio.py`) + modern dark glassmorphism web cockpit (`studio/`) running on `http://127.0.0.1:8888/` with multi-project switching (`machine_capacity.py`).
- **T-123 (Skills Ecosystem Taxonomy):** 9-domain registry (`.agentsflower/skills/INDEX.md`) packaged as template-owned files via `install.py`.
- **T-124 (Domain 9 Skill - geo-seo-audit):** Autonomous SEO/GEO auditor (`scripts/geo_audit.py`) with 100-pt AI Citability Index, Schema.org JSON-LD validator, and llms.txt drift detector.
- **T-125 (Studio Kanban Card Shrink Fix):** Fixed flexbox card squashing (`flex-shrink: 0; min-height: fit-content;`), verified in browser with full multi-line title and footer visibility.
- **T-126 (Studio Navigation & Breadcrumb Links):** Clickable breadcrumbs (`Studio / Task Board`), brand home navigation, and cancel button in Task Creator.
- **T-127 (Task Contract Creator Interactive Lists):** Dynamic file tag inputs, interactive criteria builder (`C-01:`, `C-02:`), and preset chips replacing malformed raw textareas.
- **T-128 (Multi-Project Gateway):** Dynamic project switcher with `?project=` task loading, external folder attachment modal, and uninitialized workspace banner with auto-installer.
- **T-129 (Classic Dashboard & Analytics):** Embedded Tasks Overview, Gantt & Timeline, and Roadmap tabs with live on-demand rebuild action.
- **T-120 (Local Model Protocol & Failover Architecture):** Probes local inference servers (Ollama, LM Studio) and provides tiered failover protocol preserving context when cloud limits are reached.
- **T-122 (Project Scaffolding CLI):** Workspace management commands (`agentsflower project list|attach|new|update`).

## 3. Ready in the Queue
- **T-130:** AgentsFlower Studio: Multi-Project Explorer, Global Context Sync, and Explicit Authorization Gate (Assigned to Devin swe-2-max).
- **Stage 8:** Advanced Domain Skills (Chrome Extensions, Backend Architecture, Algorithms, DevOps).
