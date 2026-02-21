# Replay Test Policy

## Purpose

Replay tests ensure that the RIVO Configurator produces deterministic, reproducible results when processing the same configuration snapshot with identical version tags.

## Core Principle

> Same `ConfigurationSnapshot` + same `versionTag` = identical validation/price/BOM result

## Required Test Coverage

### 1. Snapshot Hash Determinism
- Multiple hash computations on the same snapshot must produce identical hashes
- Hash function: SHA256 (truncated to 16 chars for readability)

### 2. Version Tag Integrity
Every snapshot must include:
```json
{
  "versionTag": {
    "catalog": "v1.0.0",
    "rules": "v1.0.0",
    "pricing": "v1.0.0",
    "assets": "v1.0.0"
  }
}
```

### 3. Result Reproducibility
- Validation results must be identical across runs
- CPQ calculations must be identical (no floating-point drift)
- BOM generation must produce identical line items

## CI Integration

Replay tests run on every PR via `ci/workflows/replay-gate.yml`:

```yaml
- name: Run replay determinism tests
  run: python -m pytest tests/replay/ -v
```

## Regression Policy

Any bug fix that affects validation/pricing/BOM must:
1. Include a reproducing test case
2. Verify replay determinism is preserved
3. Update fixtures if schema changes

## Test Commands

```bash
# Run all replay tests
pytest tests/replay/ -v

# Verify fixture integrity
python scripts/quality/run_replay_tests.py --verify-fixtures

# Run with custom iterations
python scripts/quality/run_replay_tests.py --iterations 5
```
