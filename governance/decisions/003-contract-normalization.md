# ADR 003: Contract Normalization (API v1.1.0)

## Status
Accepted (2026-02-21)

## Context
Discrepancies exist between:
- `docs/05_CPQ.md` (BomItem, PriceQuote)
- `docs/08_DB_Schema_and_Versioning.md` (ConfigurationSnapshot)
- `contracts/schemas/*.json` (current implementations)
- `contracts/examples/*.json` (example payloads)

## Decision

### 1. BomItem Canonical Schema
Use hybrid approach preserving backward compatibility:

```typescript
interface BomItem {
  // Canonical (docs/05)
  sku: string;
  name?: string;
  qty: number;
  unit: "pcs" | "m" | "set" | "mm";  // extended with mm
  
  // Legacy aliases (deprecated, for backward compatibility)
  article?: string;  // alias for sku
  uom?: string;      // alias for unit
  
  meta?: Record<string, any>;
}
```

**Migration:**
- `article` → `sku` (server normalizes)
- `uom` → `unit` (server normalizes)

### 2. PriceQuote Canonical Schema
Full implementation per docs/05:

```typescript
interface PriceLine {
  sku: string;
  title: string;
  qty: number;
  unitPrice: number;
  lineTotal: number;
}

interface PriceQuote {
  quoteId?: string;
  currency: "RUB" | "USD" | "EUR";
  subtotal: number;
  discounts: number;
  taxes: number;
  total: number;        // canonical (replaces totalPrice)
  lines: PriceLine[];   // canonical (replaces bom array)
  
  // Legacy
  totalPrice?: number;  // alias for total
  bom?: BomItem[];      // kept for backward compatibility
}
```

### 3. ConfigurationSnapshot Canonical Schema
Full implementation per docs/08:

```typescript
interface ConfigurationSnapshot {
  stateId?: string;
  
  // Canonical (docs/08)
  selectedOptions: Record<string, any>;
  derivedValues?: Record<string, any>;
  calculatedPrice?: PriceQuote;
  bom?: BomItem[];
  validationState?: ValidationResultItem[];
  
  // Versioning
  versionTag: {
    catalogVersion: string;
    rulesVersion: string;
    pricingVersion: string;
    assetsVersion: string;
  };
  
  // Legacy (for backward compatibility)
  dimensions?: { width: number; height: number; depth: number; };
  graph?: StructureGraph;
}
```

### 4. API Endpoint Naming
Already normalized in openapi.v1.yaml v1.1.0:
- Canonical: `/configuration/*`, `/export/*`
- Legacy (deprecated): `/configurations/*`, `/exports/*`

## Consequences

### Positive
- Full compatibility with docs/05, docs/08
- Backward compatibility via aliases
- Clear migration path

### Negative
- Schema complexity with dual naming
- Server-side normalization overhead

## Implementation
1. Update JSON schemas in `contracts/schemas/`
2. Update examples in `contracts/examples/`
3. Server normalizes legacy fields to canonical on input
4. Server can emit both canonical and legacy on output

## References
- docs/05_CPQ.md
- docs/08_DB_Schema_and_Versioning.md
- contracts/openapi.v1.yaml v1.1.0
