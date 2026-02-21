# Quality Gates

## Per-PR Mandatory Checks
1. Lint and type checks
2. Schema and contract validation
3. Domain unit tests
4. Snapshot replay test
5. Critical E2E smoke test

## Release Checklist
- Zero open critical defects
- Stable snapshot replay across latest build
- Export pipeline success for PDF and DXF MVP targets
- Observability checks configured for key endpoints
- Rollback procedure documented

## Critical E2E Path
`requirements -> solutions/generate -> configuration/validate -> cpq/calculate -> export`
