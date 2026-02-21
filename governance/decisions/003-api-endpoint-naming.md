# ADR 003: API Endpoint Naming Canonicalization

**Date:** 2026-02-21  
**Status:** Proposed  
**Author:** 8mirroz  
**Related Issue:** #19

---

## Context

The RIVO Configurator API has inconsistent endpoint naming between documentation (`docs/06_API_Contract.md`) and the OpenAPI specification (`contracts/openapi.v1.yaml`):

| docs/06 | openapi.v1.yaml |
|---------|-----------------|
| `/api/configuration/validate` | `/configurations/validate` |
| `/api/export/pdf` | `/exports/pdf` |
| `/api/export/dxf` | `/exports/dxf` |
| `/api/export/ifc` | `/exports/ifc` |

This inconsistency creates confusion for API consumers and implementers.

---

## Decision

### Canonical Naming Rules

1. **Use plural nouns for resource collections** (REST best practice)
   - ✅ `/configurations` - collection of configuration snapshots
   - ✅ `/exports` - collection of export jobs/results

2. **Base path separation**
   - Server base path: `/api/v1`
   - Resource paths are relative to base path
   - Full URL: `https://api.rivo.example/api/v1/configurations/validate`

3. **Endpoint canonical forms**

| Endpoint | Canonical Path | Method | Description |
|----------|---------------|--------|-------------|
| Generate Solution | `/solutions/generate` | POST | Generate configuration from requirements |
| Validate Configuration | `/configurations/validate` | POST | Validate configuration snapshot |
| Calculate CPQ | `/cpq/calculate` | POST | Calculate price and BOM |
| Export PDF | `/exports/pdf` | POST | Generate PDF export |
| Export DXF | `/exports/dxf` | POST | Generate DXF export |
| Export IFC | `/exports/ifc` | POST | Generate IFC export |
| Export RIVO | `/exports/rivo` | POST | Generate canonical .rivo.json |

---

## Consequences

### Positive
- Consistent REST conventions (plural resources)
- Clear separation between base path and resource paths
- Aligns with OpenAPI best practices

### Negative
- Documentation (`docs/06`) requires update
- Existing references need migration

### Migration
- Update `docs/06_API_Contract.md` to reflect canonical paths
- Update any client code referencing old paths
- Add deprecation notices if old paths were exposed

---

## Compliance

All future API changes must:
1. Use plural nouns for resource collections
2. Reference base path `/api/v1` in server configuration
3. Document endpoint changes in changelog with version bump

---

## References

- REST API best practices: https://restfulapi.net/resource-naming/
- OpenAPI Specification: https://swagger.io/specification/
- Related: `contracts/openapi.v1.yaml`
