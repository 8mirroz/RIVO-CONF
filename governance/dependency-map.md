# Phase 0 → Phase 1 Dependency Map and Merge Order

## Version: 1.0.0
## Date: 2026-02-21

## Batch A: Foundation (Pending Approvals)
| Order | PR | Domain | Description | Status |
|-------|-----|--------|-------------|--------|
| 1 | #6 | Orchestrator | ADR 001 lock policy | GREEN, needs approval |
| 2 | #9 | CPQ/API | Monorepo scaffold | GREEN, needs approval |
| 3 | #15 | Quality | Quality gates infrastructure | GREEN, needs approval |
| 4 | #13 | Product | v1 product model | GREEN, needs approval |
| 5 | #11 | CPQ/API | Export scripts | GREEN, needs approval |

## Batch B: Contracts (Merged)
| Order | PR | Domain | Description | Status |
|-------|-----|--------|-------------|--------|
| 1 | #17 | CPQ/API | Contract normalization (ADR 003) | MERGED ✅ |

## Batch C: Quality (In Progress)
| Order | PR | Domain | Description | Status |
|-------|-----|--------|-------------|--------|
| 1 | #31 | Quality | P0-04 replay/smoke CI | OPEN |

## Phase 1 Dependencies

### P1-01: Product Model Finalization
**Depends on:** PR #9 (monorepo scaffold), PR #13 (v1 model)
**Lock paths:** `models/catalog/`, `models/attributes/`, `models/rules/`, `models/versioning/`
**Blockers:** None after Batch A merge

### P1-02: Constraint Engine Pipeline
**Depends on:** P1-01 (catalog/rules), PR #17 (contract schemas)
**Lock paths:** `backend/engine/`, `backend/validation/`, `models/rules/`
**Blockers:** None after P1-01 complete

### P1-03: Explainable Payload
**Depends on:** P1-02 (validation engine)
**Lock paths:** `backend/validation/`, `contracts/schemas/`, `contracts/examples/`
**Blockers:** None after P1-02 complete

### P1-04: Reverse Solver
**Depends on:** P1-02 (validation engine)
**Lock paths:** `backend/solver/`, `backend/validation/`
**Blockers:** None after P1-02 complete

### P1-05: Regression Suite
**Depends on:** P1-02, P1-04
**Lock paths:** `tests/`, `scripts/quality/`
**Blockers:** None after P1-04 complete

## Merge Windows

### Daily Integration (14:00-15:00 MSK)
- Only fully green PRs
- Single-domain changes preferred
- Contract PRs merged first

### Weekly Stabilization (Friday)
- Bugfix/hardening only
- No new features
- Regression suite must pass

### Release Freeze (48h before release)
- Blocker fixes only
- No contract changes
- Full E2E suite required

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Batch A approval delay | Medium | High | Parallel work on P1 tasks |
| Contract rework | Low | High | ADR 003 already merged |
| Test flakiness | Medium | Medium | Dedicated test stabilization |
| Cross-domain conflicts | Low | High | Strict lock_path enforcement |

## Handoff Notes

### To Product Modeling Team
- Catalog schema finalized in PR #17
- Version tags required on all snapshots
- Use canonical field names (sku, unit) not legacy (article, uom)

### To Constraint Engine Team
- ValidationResultItem schema in `contracts/schemas/validation-result-item.schema.json`
- Status values: pass, warning, error, auto_corrected
- Explainability fields: explanation, suggestedFixes

### To CPQ/API Team
- OpenAPI v1.1.0 normalized
- Canonical paths: /configuration/*, /export/*
- Legacy paths deprecated but functional

### To Quality Team
- Replay tests in tests/replay/
- Policy in docs/replay-test-policy.md
- Gate: same snapshot + same versions = same result
