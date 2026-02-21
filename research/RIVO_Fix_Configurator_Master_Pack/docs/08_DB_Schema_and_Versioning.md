# 8. База данных (PostgreSQL) + Versioning

## Таблицы (минимум)
- catalog_profiles
- catalog_nodes
- catalog_fasteners
- catalog_products
- rulesets
- pricing_rules
- configurations
- configuration_versions
- structure_graphs
- boms
- orders

## Snapshot Model
Configuration хранится как snapshot:

```ts
interface ConfigurationSnapshot {
  selectedOptions: Record<string, any>;
  derivedValues: Record<string, any>;
  calculatedPrice: PriceQuote;
  bom: BomItem[];
  validationState: any;
  versionTag: {
    catalogVersion: string;
    rulesVersion: string;
    pricingVersion: string;
    assetsVersion: string;
  };
}
```

## Versioning
- каждая правка создаёт новую версию (append-only)
- хранить diff (опционально) + полный snapshot
- поддержка compare, undo/redo, shareable URL

