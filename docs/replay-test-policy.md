# Replay Test Policy

**Version:** 1.0.0

## Principle

`same snapshot + same versions = same result`

## Test Structure

- `tests/replay/test_replay_determinism.py` — Replay tests
- `tests/fixtures/sample_snapshot.json` — Test fixture

## CI Integration

Workflow `replay-gate.yml` runs on every PR.

## Requirements

- All replay tests must pass
- Version tags must be present
- Hash must be deterministic
