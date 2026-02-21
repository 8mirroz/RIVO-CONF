# CI/CD Workflows

Quality gates for RIVO CONF.

## Workflows

- `test.yml` — Unit/integration tests
- `lint.yml` — Code quality checks
- `quality-gate.yml` — Contract + ownership validation
- `replay-gate.yml` — Replay determinism tests

## Running Locally

```bash
pytest tests/ -v
python scripts/quality/run_replay_tests.py
```
