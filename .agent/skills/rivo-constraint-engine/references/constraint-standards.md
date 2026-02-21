# Constraint Standards

## Rule Types
- `hard`: block invalid states.
- `auto_correct`: modify configuration to nearest valid state.
- `soft`: warning only.
- `optimization`: rank valid candidates.

## Validation Item Minimum
- `ruleId`
- `status`
- `affected`
- `explanation.title`
- `explanation.message`
- `explanation.why[]`
- `suggestedFixes[]` when available

## Determinism Checklist
- Stable sorting by `priority` then `ruleId`
- Explicit tie-break policy
- Snapshot replay test per release
- Same input + versions => same validation output
