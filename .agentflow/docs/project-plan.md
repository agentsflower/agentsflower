# Project Plan

Project: AgentFlow template.

## Goal

A small, tool-agnostic template that lets one Orchestrator and fresh worker sessions run a software project without losing state, with rules enforced by the tools.

Tasks are not listed here: they live in `state/tasks.md` with a `Stage` column. See `docs/ai-handoff-protocol.md`, "Planning levels".

## Roadmap

### Stage 6. Public release and production upgrade (2.12.0)

Status: planned.

Human approved the task sequence on 2026-10-15. Specification:
[agentflow-production-roadmap.txt](agentflow-production-roadmap.txt).
Contract preparation does not authorize worker launch in this session.
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

Status: current.

Exit criteria: `upstream.py` drift reports from every installed project are reviewed periodically;
changes that flow upstream are generalized, released (CHANGELOG, VERSION, decisions.md) and rolled
out with `install.py --update`.

### Stage 5. Reliability and efficient project practices

Status: planned.

Implementation sequence and acceptance criteria: [improvement-plan.md](improvement-plan.md).
The human authorized the bounded launcher/end-check repair on 2026-10-10;
2.11.3 implements that subset. The broader stage remains planned. Cover recovery next,
then artifact-bound completion checks, bounded automation and concise instructions.

Exit criteria: the scenarios in that plan pass, migration preserves open tasks,
and the pilot installation receives the tested release without template drift.
