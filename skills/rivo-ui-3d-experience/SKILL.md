---
name: rivo-ui-3d-experience
description: Design and implement RIVO guided/reverse configurator UX and 3D presentation layer with explainable constraints and validated-state rendering. Use when building UI flows, state handling, viewer integration, or UX behavior for unavailable options.
---

# RIVO UI and 3D Experience

Build guided and reverse configuration interfaces that expose engineering logic clearly while keeping the viewer purely presentational.

## Workflow
1. Implement IA for Guided and Reverse modes from research docs.
2. Bind UI state to backend contracts for validity, messages, BOM, and price.
3. Show unavailable options with reason and corrective action.
4. Update summary block on every server recalculation.
5. Render viewer from validated snapshot mapping only.
6. Add responsive behavior for desktop and mobile, including sticky summary.

## UX Rules
- Never allow silent invalid selections.
- Show explicit recalculation feedback.
- Keep selected state visible at all times.
- Keep error text actionable and specific.

## Required Outputs
- Screen flow for reverse + guided modes.
- Component states: default/disabled/error/loading/success.
- Viewer mapping spec from `StructureGraph` to render state.
- UI integration tests for invalid-option and fix scenarios.

## References
- Read `references/ui-3d-guidelines.md` before implementing interaction or viewer logic.
