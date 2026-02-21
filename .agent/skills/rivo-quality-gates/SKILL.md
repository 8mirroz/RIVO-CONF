---
name: rivo-quality-gates
description: Enforce test, compatibility, and release gates for the RIVO configurator across domains. Use when validating pull requests, preparing integration batches, running regression checks, or making release decisions.
---

# RIVO Quality Gates

Protect integration quality with deterministic tests, contract checks, and release readiness criteria.

## Workflow
1. Run static checks: lint, types, schema validation.
2. Run domain unit tests: model, rules, CPQ, UI adapters.
3. Run snapshot replay tests for deterministic outputs.
4. Run end-to-end smoke path from requirements to export.
5. Validate performance and error-budget thresholds.
6. Publish gate report with pass/fail and blocking defects.

## Gate Rules
- Block merge on contract incompatibility.
- Block merge on replay non-determinism.
- Block release when critical E2E path fails.
- Require regression evidence for bugfix PRs.

## Required Outputs
- CI quality matrix.
- Replay test artifacts.
- E2E smoke report.
- Release readiness checklist status.

## References
- Read `references/quality-gates.md` before merge or release validation.
