# CI/CD Workflows

This directory contains GitHub Actions workflow definitions for quality gates.

## Workflows

### test.yml
Runs unit and integration tests on every push and PR.

### lint.yml
Runs code quality checks (Black, Ruff, MyPy).

### quality-gate.yml
Comprehensive quality gate that validates contracts, ownership compliance, and runs smoke tests.

## Usage

These workflows are reference implementations. Copy them to `.github/workflows/` to activate.

## Integration with Lock Policy

The quality-gate workflow enforces the lock policy defined in `governance/ownership-map.yaml`:
- Validates that changes are within lock_paths
- Checks ownership compliance
- Ensures contract compatibility
