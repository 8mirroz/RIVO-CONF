---
name: rivo-multi-agent-orchestrator
description: Orchestrate parallel multi-agent delivery for the RIVO configurator with explicit ownership, dependency sequencing, contract-first integration, and conflict prevention. Use when tasks span multiple domains, when creating sprint plans, when coordinating merges, or when cross-domain contracts may change.
---

# RIVO Multi-Agent Orchestrator

Coordinate domain agents, dependencies, and integration windows so implementation stays parallel without schema or merge conflicts.

## Workflow
1. Load the latest constraints from `AGENTS.md` and `governance/multi-agent-plan.md`.
2. Identify impacted domains: product model, constraints, CPQ/API, UI/3D, quality.
3. Split work into domain-local tasks with explicit owner and required input/output artifacts.
4. Sequence tasks by contract dependency: schema first, implementation second, end-to-end integration last.
5. Define merge batches and validation gates for each batch.
6. Publish handoff notes for every downstream domain.

## Conflict Prevention Rules
- Require one owner per artifact type.
- Gate all cross-domain work behind versioned contracts.
- Reject multi-domain implementation in one PR unless it is a hotfix approved by orchestrator.
- Merge contract changes before consumer code changes.

## Required Outputs
- Updated dependency map and milestone plan.
- Domain backlog with owner, scope, and test gate.
- Integration checklist with merge order.
- Risk log with mitigation owner.

## References
- Read `references/orchestration-checklists.md` for templates and gate criteria.
