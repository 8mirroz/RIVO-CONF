---
name: rivo-cpq-and-api
description: Define and implement RIVO server contracts for solution generation, validation, pricing, BOM, and exports. Use when changing OpenAPI contracts, CPQ logic, BOM generation, snapshot APIs, or export endpoints.
---

# RIVO CPQ and API

Keep API contracts explicit and keep all pricing, BOM, and validation-critical logic on the server.

## Workflow
1. Update OpenAPI/schema contracts before implementation.
2. Implement endpoint behavior for generate, validate, calculate, and export flows.
3. Compute pricing and BOM from validated `StructureGraph` only.
4. Persist configuration snapshots with full version tags.
5. Verify idempotency: same snapshot + versions returns same CPQ output.
6. Add compatibility and regression tests for all contract changes.

## Contract Rules
- Do not move business rules into frontend.
- Return machine-readable codes and human-readable messages.
- Version every breaking response/request change.
- Keep export API asynchronous if generation is long-running.

## Required Outputs
- OpenAPI spec and examples.
- CPQ calculation module with deterministic tests.
- BOM generation module with SKU-level coverage.
- Snapshot persistence contract and replay tests.

## References
- Read `references/cpq-api-rules.md` before changing API or CPQ behavior.
