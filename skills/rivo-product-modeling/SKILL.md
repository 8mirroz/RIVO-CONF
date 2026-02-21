---
name: rivo-product-modeling
description: Build and evolve the RIVO product definition layer, including attributes, component catalogs, and semantic versions for catalog/rules/pricing/assets. Use when creating or updating product schemas, engineering parameters, compatibility dictionaries, and versioned model data.
---

# RIVO Product Modeling

Translate engineering and configurator research into normalized, versioned product data that downstream engines can consume safely.

## Workflow
1. Extract parameter definitions from engineering docs and source inputs.
2. Normalize attributes: key, type, unit, min/max/step, enum domains, defaults.
3. Build component dictionaries for profiles, nodes, fasteners, and modules.
4. Define derived values that are computed server-side only.
5. Apply semantic versions to catalog/rules/pricing/assets and snapshot tags.
6. Publish schema examples for CPQ, solver, and UI consumers.

## Modeling Rules
- Keep IDs stable and machine-readable.
- Preserve unit consistency across all numeric attributes.
- Separate user selections from derived values.
- Store compatibility in data/rules, not in UI code.

## Required Outputs
- Product schema document or JSON schema.
- Seed catalog dataset.
- Version policy notes and migration notes when breaking.
- Compatibility matrix for critical modules.

## References
- Read `references/product-model-spec.md` before editing product model artifacts.
