# Replay Test Policy

**Version:** 1.0.0  
**Date:** 2026-02-21  
**Status:** Active

---

## Overview

Replay tests ensure deterministic behavior across the RIVO Configurator pipeline. The same input snapshot with identical version tags must produce identical results.

---

## Principles

### 1. Determinism Guarantee

**Rule:** `same snapshot + same versions = same result`

Every configuration snapshot includes version tags:
```json
{
  "versionTags": {
    "catalog": "v1.0.0",
    "rules": "v1.0.0",
    "pricing": "v1.0.0",
    "assets": "v1.0.0"
  }
}
```

### 2. Idempotency

**Rule:** Multiple executions produce identical results.

Replay tests run the same snapshot 3+ times and verify hash consistency.

### 3. Fixture Isolation

**Rule:** Test fixtures are immutable and versioned.

Fixtures in `tests/fixtures/` must not change without explicit version bump.

---

## Test Structure

### Replay Tests Location

```
tests/
├── replay/
│   └── test_replay_determinism.py
└── fixtures/
    └── sample_snapshot.json
```

### Test Categories

| Category | Purpose | Frequency |
|----------|---------|-----------|
| Snapshot hash stability | Verify consistent hashing | Every run |
| Version tags presence | Ensure version metadata | Every run |
| Dimensions determinism | Validate numeric consistency | Every run |
| BOM structure | Verify BOM item format | Every run |
| Replay idempotency | Multi-run consistency | Every run |

---

## CI Integration

### Workflow: replay-gate.yml

Runs on:
- Every pull request
- Every push to `main`

**Stages:**
1. Setup Python 3.11
2. Install pytest + plugins
3. Run replay tests
4. Upload artifacts

**Gate Condition:** All tests must pass for merge.

---

## Running Locally

### Full Test Suite

```bash
python scripts/quality/run_replay_tests.py --verbose
```

### With Report Output

```bash
python scripts/quality/run_replay_tests.py --verbose --output replay-report.md
```

### Direct Pytest

```bash
pytest tests/replay/ -v
```

---

## Fixture Management

### Adding New Fixtures

1. Create JSON file in `tests/fixtures/`
2. Include all required fields:
   - `stateId` (unique identifier)
   - `dimensions` (width, height, depth)
   - `versionTags` (catalog, rules, pricing, assets)
   - `bom` (at least one item)

3. Update test coverage if new fields added

### Fixture Versioning

When fixture structure changes:
1. Increment fixture version in filename (e.g., `sample_snapshot_v2.json`)
2. Update tests to cover both versions if backward compatibility needed
3. Document change in changelog

---

## Failure Handling

### Common Failures

| Error | Cause | Resolution |
|-------|-------|------------|
| Hash mismatch | Non-deterministic data | Check timestamps, UUIDs, random values |
| Missing version tag | Incomplete snapshot | Add all required version tags |
| BOM structure error | Invalid BOM format | Ensure article/qty/uom fields |

### Debugging Steps

1. Run with `--verbose` flag
2. Check fixture JSON validity
3. Verify version tag format
4. Inspect hash computation

---

## Compliance

### Required for Merge

- [ ] All replay tests pass
- [ ] No hash mismatches
- [ ] Version tags present and valid
- [ ] BOM structure consistent

### Release Requirements

- [ ] Replay suite passes on release candidate
- [ ] Fixture coverage documented
- [ ] Performance within budget (<5s for full suite)

---

## Related Documents

- `docs/quality-gates.md` — Quality gates overview
- `governance/decisions/004-contract-normalization-v1.1.md` — Contract standards
- `contracts/schemas/configuration-snapshot.schema.json` — Snapshot schema

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-21 | Initial policy |
