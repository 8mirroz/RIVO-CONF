# CPQ/API Rules

## Core Endpoints
- `POST /api/solutions/generate`
- `POST /api/configuration/validate`
- `POST /api/cpq/calculate`
- `POST /api/export/pdf`
- `POST /api/export/dxf`
- `POST /api/export/ifc`

## Snapshot Integrity Rules
- Store selected options + derived values + version tags.
- Preserve immutable historical versions (append-only).
- Support compare and replay across versions.

## Price/BOM Determinism
- Use canonical rounding policy.
- Use consistent currency conversion source per quote.
- Avoid non-deterministic iteration over unordered maps.
