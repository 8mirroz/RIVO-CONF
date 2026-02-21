# ADR 004: Contract Normalization for API/Schemas v1.1

Supersedes: ADR 003 (proposed) where conflicts exist.

- Date: 2026-02-21
- Status: Accepted
- Related Issue: #17

## Context
The contract layer had three inconsistencies:
1. Path naming mismatch between docs and OpenAPI (`/configuration/*` vs `/configurations/*`, `/export/*` vs `/exports/*`).
2. BOM/Price field mismatch (`sku/name/unit` vs `article/uom`; `subtotal/total/lines` vs `totalPrice/bom`).
3. Snapshot shape mismatch between docs and schema/examples (`selectedOptions`, `derivedValues`, `calculatedPrice`, `validationState`, `versionTag`).

## Decision
1. Canonical API paths are:
- `POST /solutions/generate`
- `POST /configuration/validate`
- `POST /cpq/calculate`
- `POST /export/pdf`
- `POST /export/dxf`
- `POST /export/ifc`
- `POST /export/rivo`

2. Legacy aliases remain available and are marked deprecated:
- `/configurations/validate`
- `/exports/*`

3. Canonical BOM and pricing fields are adopted:
- `BomItem`: `sku`, `name`, `qty`, `unit`, `meta`
- `PriceQuote`: `currency`, `subtotal`, `discounts`, `taxes`, `total`, `lines[]`

4. Backward compatibility in v1.1 is preserved via schema support for legacy aliases:
- `article/uom/comment` in BOM
- `quoteId/totalPrice/bom` in PriceQuote
- legacy graph fields (`rootNode/edges`) in StructureGraph

5. Snapshot schema now explicitly supports canonical state blocks:
- `selectedOptions`, `derivedValues`, `structureGraph`, `calculatedPrice`, `validationState`, `versionTag`

## Consequences
- API consumers can migrate incrementally without immediate breakage.
- New integrations should use canonical paths and canonical field names.
- Legacy aliases are supported in v1.x and planned for removal in v2.0.

## Migration Notes
1. Prefer `/configuration/validate` over `/configurations/validate`.
2. Prefer `/export/*` over `/exports/*`.
3. For BOM and PriceQuote payloads, emit canonical fields in new clients.
4. Existing clients may continue using legacy fields during v1.x.

## Implementation Status
- OpenAPI v1.1 keeps legacy aliases marked `deprecated: true`.
- JSON Schemas support canonical and legacy payload shapes during v1.x.
- Contract examples are canonical and aligned with v1.1 fields.

## Sunset Policy
- v1.x: dual-format compatibility is maintained.
- v2.0: legacy aliases and legacy fields (`article/uom`, `totalPrice/bom`, `/exports/*`) are removed.
