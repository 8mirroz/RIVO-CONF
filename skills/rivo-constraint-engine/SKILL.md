---
name: rivo-constraint-engine
description: Implement and maintain RIVO configuration rules, explainable validation, auto-correction, and candidate filtering logic. Use when authoring DSL rules, building validation pipelines, tuning solver behavior, or debugging invalid configuration paths.
---

# RIVO Constraint Engine

Implement deterministic rule evaluation and explainable outcomes for guided and reverse configuration flows.

## Workflow
1. Classify each rule as `hard`, `auto_correct`, `soft`, or `optimization`.
2. Encode predicates and actions in DSL with stable rule IDs.
3. Execute pipeline in fixed order: HARD -> AUTO_CORRECT -> REVALIDATE -> SOFT.
4. Return explainability payload with reason, affected entities, and suggested fixes.
5. Reject candidate solutions that remain invalid after auto-correction.
6. Add regression tests for known edge cases and rule priority ordering.

## Engine Rules
- Never hide failed validation reasons.
- Preserve deterministic rule priority.
- Keep solver objective separate from hard safety constraints.
- Log rule ID and status for every decision.

## Required Outputs
- Rule pack with IDs and priorities.
- Validation response schema examples.
- Candidate filtering logic with tests.
- Explainability examples for UI copy.

## References
- Read `references/constraint-standards.md` before modifying DSL or evaluation flow.
