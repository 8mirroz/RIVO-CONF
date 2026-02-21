# 002 - Lock Policy Practical Example

## Scenario

Two agents work in parallel:
- **Agent A**: Updates OpenAPI contract
- **Agent B**: Adds validation script

Without lock policy, they could conflict. With locks, they work safely.

## Agent A: Contract Update

### Issue #101
```yaml
Summary: Add new endpoint /api/v1/products
Task Type: T3
Complexity: C3
Lock Paths: contracts/openapi.v1.yaml,contracts/schemas/
Lock Owner: agent-contract-updater
Lock Type: contract
Lock Expiry: 2026-03-15
Contracts Changed: yes
Risk: medium
```

### Branch
```bash
git checkout -b task/add-products-endpoint
```

### Changes
- Modified: `contracts/openapi.v1.yaml`
- Added: `contracts/schemas/product.schema.json`

### PR
```markdown
## Summary
- Add /api/v1/products endpoint with schema
- Issue: #101

## Lock
- lock_paths: contracts/openapi.v1.yaml,contracts/schemas/
- lock_owner: agent-contract-updater
- lock_type: contract
- lock_expiry: 2026-03-15

## Contracts
- contracts_changed: yes
- breaking_change: no
```

## Agent B: Validation Script

### Issue #102
```yaml
Summary: Add contract validation helper
Task Type: T4
Complexity: C2
Lock Paths: scripts/quality/
Lock Owner: agent-quality-tools
Lock Type: dir
Lock Expiry: 2026-03-15
Contracts Changed: no
Risk: low
```

### Branch
```bash
git checkout -b task/validation-helper
```

### Changes
- Added: `scripts/quality/validate_schemas.js`

### PR
```markdown
## Summary
- Add schema validation utility
- Issue: #102

## Lock
- lock_paths: scripts/quality/
- lock_owner: agent-quality-tools
- lock_type: dir
- lock_expiry: 2026-03-15

## Contracts
- contracts_changed: no
```

## Result

Both agents work simultaneously without conflicts:
- Agent A: `contracts/` (locked)
- Agent B: `scripts/quality/` (locked)
- No overlap → No conflicts
- CI validates each PR independently

## Anti-Pattern: Lock Violation

❌ **Wrong**: Agent B modifies `contracts/openapi.v1.yaml`
- File outside `lock_paths: scripts/quality/`
- CI fails with lock violation
- PR rejected

✅ **Correct**: Agent B stays in `scripts/quality/`
- All changes within lock boundary
- CI passes
- PR approved

## Key Takeaways

1. **Plan locks before starting**: Define scope in Issue
2. **Respect boundaries**: Never touch files outside lock_paths
3. **Reference Issue in PR**: Enables automated validation
4. **Parallel safety**: Multiple agents can work without coordination overhead
