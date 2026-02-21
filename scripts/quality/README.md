# Quality Scripts

This directory contains validation and quality gate scripts for the RIVO CONF project.

## Scripts

### validate_contracts.js
Validates contract schemas and OpenAPI specifications.

### check_ownership.py
Validates that all changed files have a defined owner in `governance/ownership-map.yaml`.

**Usage:**
```bash
python scripts/quality/check_ownership.py
```

**Exit Codes:**
- 0: All files have valid ownership
- 1: Ownership violations detected

### check_lock_paths.py
Validates that changes are within the allowed lock_paths from the Issue.

**Usage:**
```bash
python scripts/quality/check_lock_paths.py "<issue_body>"
```

**Exit Codes:**
- 0: All changes within lock_paths
- 1: Lock path violations detected

## Integration

These scripts are used in CI/CD pipelines:
- `check_ownership.py` is called in the quality-gate workflow
- `check_lock_paths.py` should be called in PR validation

## Adding New Scripts

When adding new quality validation scripts:
1. Place them in this directory
2. Make executable: `chmod +x scripts/quality/<script>.py`
3. Add to appropriate workflow in `ci/workflows/`
4. Update this README
