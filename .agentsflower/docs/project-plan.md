# Project Plan

Project: AgentFlow template.

## Goal

A small, tool-agnostic template that lets one Orchestrator and fresh worker sessions run a software project without losing state, with rules enforced by the tools.

Tasks are not listed here: they live in `state/tasks.md` with a `Stage` column. See `docs/ai-handoff-protocol.md`, "Planning levels".

## Roadmap

### Stage 7. AgentsFlower Studio, Multi-Project Gateway and Specialized Skills Ecosystem (2.17.0)

Status: closed.

Human approved the transition to Stage 7 and the Specialized Skills Ecosystem on 2026-10-23.
Closed on 2026-10-24: all 16 stage tasks `done`, `gate.py stage 7` PASS; the human declared
closure in commit b3b9bd2 and questions.md (2026-10-24). Next stage is new scope and waits
for human approval.
Focus areas:
- AgentsFlower Studio: modern Local Web UI (`.agentsflower/studio/`) with dark mode, glassmorphism, multi-project switching, Kanban task board, task creation wizard, and AST knowledge graph explorer.
- Graft AST Semantic Knowledge Graph (`@nanonets/graft` via WASM with auto-install and blast radius analysis).
- Specialized Skills Ecosystem: curated library in `.agentsflower/skills/` across 9 core engineering domains, starting with Domain 9 `geo-seo-audit`.
- Multi-project gateway and local model protocol.

Exit criteria: Studio local web server operates with zero pip dependencies; Graft auto-installs via npm --ignore-scripts without node-gyp; specialized skills pass deterministic validation suites; `install.py` deploys studio and skills to target workspaces.

### Stage 6. Public release and production upgrade (2.12.0)

Status: closed.

Human approved the task sequence on 2026-10-15. Specification:
[agentflow-production-roadmap.txt](agentflow-production-roadmap.txt).
Worker execution was subsequently authorized by the human; current readiness
and verification blockers are recorded in the ledger and state/current-step.md.
Stages 4 and 5 remain separate; their unfinished scope is not implicitly adopted.

Exit criteria: Python launcher parity and PowerShell compatibility; packaged
zero-dependency core CLI; optional SDK-based MCP with privileged tools off by
default; measured English dashboard metrics with marked demo data; CI on three
OSes and Python 3.10-3.12; English/Russian guides; accurate README; independent
clean-install and update verification. Conductor/autostart stays Windows-only.
The human performs push and GitHub publication.

### Stage 1. Team layer and launcher

Status: closed.

Exit criteria: roles, Task Files, ledger, launcher with preflight work on a live project (1.2.0).

### Stage 2. 2.0.0: enforcement, states, template vs project

Status: closed.

Exit criteria: P0-P4 of the FPF audit committed; sandbox checks pass; the branch is merged by the human.

### Stage 3. Pilot 2.0.0

Status: closed (Watermark Remover, 2.2.x-2.11.0, 48+ tasks).

Exit criteria: one real project updated with the "Update" procedure and a full task cycle run with the real tools; findings in `state/known-issues.md`.

### Stage 4. Upstream sync

Status: closed (bounded audit cycle, 2026-10-17; external rollout deferred).

The bounded drift audit and transfer of generalized findings into Stage 5
were completed (state/decisions.md, 2026-10-17). The latest repository-only
authorization excludes further external updates. Recurring cross-project
audits and rollout remain deferred rather than claimed complete.

Exit criteria: `upstream.py` drift reports from every installed project are reviewed periodically;
changes that flow upstream are generalized, released (CHANGELOG, VERSION, decisions.md) and rolled
out with `install.py --update`.

### Stage 5. Reliability and efficient project practices

Status: current.

Implementation sequence and acceptance criteria: [improvement-plan.md](improvement-plan.md).
Implementation was authorized on 2026-10-17. Lifecycle, recovery, completion
checks and bounded autonomy have accepted implementations. Routing enforcement,
instruction alignment and final evaluation remain; live task state is in the
ledger. The 2026-10-18 urgent watchdog repair precedes recovery of routing work.

Exit criteria: the scenarios in that plan pass, migration preserves open tasks,
and installer/migration behavior is validated in disposable AgentFlow fixtures.
(2026-10-17 boundary: repository-only scope - no external pilot rollout; that
criterion is deferred, not claimed.)
