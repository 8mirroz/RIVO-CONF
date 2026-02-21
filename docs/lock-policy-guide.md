# Lock Policy Guide

## Overview

The Lock Policy ensures safe parallel execution of multi-agent tasks by restricting each agent to specific files or directories. This prevents conflicts and maintains code stability.

## Core Concepts

### Lock Fields

Every Agent Work Item must specify:

- **lock_paths**: Comma-separated list of allowed files/directories
- **lock_owner**: GitHub login of the responsible agent/operator
- **lock_type**: Scope of lock (`file`, `dir`, or `contract`)
- **lock_expiry**: ISO-8601 date when lock expires (YYYY-MM-DD)

### Rules

1. **Strict Boundaries**: Agents must only modify files within their `lock_paths`
2. **No Overlap**: Multiple agents should not lock the same paths simultaneously
3. **Expiry**: Locks expire automatically; extend if needed
4. **CI Enforcement**: Lock violations fail CI checks

## Creating an Agent Work Item

1. Go to Issues → New Issue
2. Select "Agent Work Item" template
3. Fill all required fields:
   - Summary: Brief task description
   - Task Type: T1-T7 (routing class)
   - Complexity: C1-C5
   - Lock Paths: `contracts/,scripts/validate.py`
   - Lock Owner: `your-github-login`
   - Lock Type: `dir` or `file`
   - Lock Expiry: `2026-12-31`
   - Contracts Changed: `yes` or `no`
   - Risk: `low`, `medium`, or `high`

## PR Requirements

Every PR must reference its Issue and include lock metadata:

```markdown
## Summary
- Implement feature X
- Issue: #123

## Lock
- lock_paths: contracts/,scripts/
- lock_owner: agent-name
- lock_type: dir
- lock_expiry: 2026-12-31
```

## Validation

The `lock-check.yml` workflow validates:
- All changed files are within declared `lock_paths`
- Lock has not expired
- Issue reference is present

## Best Practices

- **Minimal Scope**: Lock only what you need
- **Clear Ownership**: Use descriptive owner names
- **Reasonable Expiry**: Set realistic deadlines
- **Update Issues**: If scope changes, update the Issue first
