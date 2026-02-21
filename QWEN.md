# RIVO CONF — Project Context

## Project Overview

**RIVO CONF** is a multi-agent development system for building a product configurator (RIVO Fix) — a modular aluminum profile system for engineering communications structures (false walls, partitions, columns, installation modules).

The project enables parallel agent work across multiple domains without conflicts through:
- **Contract-first development** (OpenAPI, JSON Schema, DSL)
- **Domain ownership rules** with strict file path boundaries
- **Multi-agent orchestration** with task routing by complexity/type
- **Quality gates** (smoke, integration, regression, replay tests)

### Core Domains

| Domain | Responsibility | Key Outputs |
|--------|---------------|-------------|
| **Orchestrator** | Plan, dependencies, merge windows | `AGENTS.md`, `governance/**` |
| **Product Modeling** | Catalog schema, attributes, versioning | `models/catalog/**`, `models/attributes/**` |
| **Constraint Engine** | Rule DSL, validation, explainability | `models/rules/**`, `backend/engine/**` |
| **CPQ/API** | Pricing, BOM, snapshot, REST API | `contracts/openapi/**`, `backend/cpq/**` |
| **UI/3D** | Guided UX, viewer, validated snapshot mapping | `frontend/**`, `viewer/**` |
| **Quality Gates** | Tests, CI/CD, release gates | `tests/**`, `ci/**`, `scripts/**` |

---

## Directory Structure

```
RIVO CONF/
├── AGENTS.md                          # Multi-agent development rules (Russian)
├── package.json                       # Node.js dependencies (ajv, ajv-formats)
├── report.md                          # Research analysis & skills selection
├── configs/
│   ├── skills/
│   │   └── ACTIVE_SKILLS.md           # List of active skills for agents
│   └── tooling/
│       ├── model_routing.json         # Task type/complexity → model tier routing
│       ├── mcp_profiles.json          # MCP server profiles by task type
│       ├── model_providers.json       # Model tiers, budgets, providers
│       └── integration_contracts.json # Integration test contracts
├── contracts/
│   ├── openapi.v1.yaml                # OpenAPI 3.1 spec (validate, CPQ, export)
│   └── schemas/
│       └── rivo-config.schema.json    # Canonical config JSON Schema
├── governance/
│   ├── ownership-map.yaml             # Domain ownership by file paths
│   ├── skills-map.md                  # Skill triggers & handoff protocol
│   └── multi-agent-plan.md            # 12-week development plan
├── scripts/
│   ├── swarmctl.py                    # Multi-agent orchestration CLI
│   ├── active_set_lib.py              # Skills publishing utility
│   ├── publish_active_set.py          # Publish active skills to .agent/skills/
│   ├── run_smoke_checks.sh            # Smoke test runner
│   ├── run_integration_tests.sh       # Integration test runner
│   ├── run_regression_suite.py        # Regression test runner
│   └── export_*.py                    # DXF/IFC/PDF/Mapping export scripts
├── skills/                            # 36 specialized skills for agents
│   ├── rivo-multi-agent-orchestrator/
│   ├── rivo-product-modeling/
│   ├── rivo-constraint-engine/
│   ├── rivo-cpq-and-api/
│   ├── rivo-ui-3d-experience/
│   ├── rivo-quality-gates/
│   └── ... (generic skills: backend-architect, threejs-skills, etc.)
├── research/
│   ├── RIVO_Fix_Configurator_Master_Pack/docs/  # Consolidated docs (00-09)
│   ├── RIVO_Fix_Engineering_Model.md  # Engineering calculations & rules
│   ├── configurator_uiux_research.md  # UX research for configurators
│   └── ... (PDFs, DOCX, bundles)
├── ui/
│   └── index.html                     # UI prototype mock (Phase 4)
└── node_modules/
```

---

## Building and Running

### Prerequisites

- **Node.js** (for AJV validation)
- **Python 3.9+** (for scripts and agent-os)
- **Agent OS v2** dependencies (from `antigravity-core`)

### Setup

```bash
# Install Node dependencies
npm install

# Validate JSON Schema against sample data
node test_ajv.js

# Run swarmctl utilities
python scripts/swarmctl.py doctor
python scripts/swarmctl.py publish-skills
python scripts/swarmctl.py smoke
```

### Key Commands

| Command | Description |
|---------|-------------|
| `node test_ajv.js` | Validate `rivo-config.schema.json` against sample project |
| `python scripts/swarmctl.py doctor` | Validate configs, env, published skills |
| `python scripts/swarmctl.py publish-skills` | Publish ACTIVE_SKILLS.md to `.agent/skills/` |
| `python scripts/swarmctl.py smoke` | Run smoke checks (doctor, route, tool_runner, retriever) |
| `python scripts/swarmctl.py triage "<text>"` | Classify task text → (task_type, complexity, model_tier) |
| `python scripts/swarmctl.py route "<text>"` | Resolve full model route contract |
| `./scripts/run_smoke_checks.sh` | Quick smoke test after merges |
| `./scripts/run_integration_tests.sh` | Full integration test suite |
| `./scripts/run_regression_suite.py` | Regression test with snapshot replay |

---

## Development Conventions

### Contract-First Workflow

1. **Define contracts before implementation:**
   - JSON Schema (`contracts/schemas/`)
   - OpenAPI (`contracts/openapi.v1.yaml`)
   - Rule DSL (`models/rules/`)

2. **Breaking changes require:**
   - Version bump in contract
   - Migration notes in `governance/decisions/`
   - Orchestrator approval for cross-domain changes

### Branch & PR Strategy

- **Branch format:** `agent/<domain>/<ticket-or-scope>`
- **PR requirements:**
  1. Contract compatibility check
  2. Domain tests pass
  3. Snapshot replay test
  4. Lint/type checks
  5. Changelog for domain changes

### Task Routing (Adaptive Swarm)

Tasks are classified by **type** (T1-T7) and **complexity** (C1-C5):

| Complexity | Model Tier | Token Budget | Cost Budget |
|------------|-----------|--------------|-------------|
| C1 (trivial) | light | 10K | $0.15 |
| C2 (simple) | light | 20K | $0.30 |
| C3 (feature) | quality | 40K | $0.80 |
| C4 (arch) | reasoning | 80K | $2.50 |
| C5 (critical) | reasoning | 120K | $4.00 |

**Task Types:**
- T1: Config/dependencies
- T2: Bug fixes
- T3: Feature implementation
- T4: Architecture/refactor
- T5: Research/analysis
- T6: UI/UX
- T7: Telegram/Mini App/Payments

### Definition of Done

A task is complete only when:
- [ ] Validation/price/BOM calculated on server
- [ ] UI prevents invalid selection with explanation
- [ ] 3D receives only validated snapshot
- [ ] Tests and documentation updated
- [ ] Version tags saved (`catalog/rules/pricing/assets`)

---

## Key Artifacts

### Contracts

- **`contracts/openapi.v1.yaml`** — REST API for:
  - `POST /api/v1/solutions/generate` — Generate configuration
  - `POST /api/v1/configurations/validate` — Validate state
  - `POST /api/v1/cpq/calculate` — Calculate price + BOM
  - `POST /api/v1/exports/{pdf|dxf|ifc|rivo}` — Export deliverables

- **`contracts/schemas/rivo-config.schema.json`** — Canonical config schema:
  - `meta` (projectId, units, version)
  - `frame` (dimensions, studStep, origin, constraints)
  - `catalog` (items with article, category, material)
  - `elements` (scene graph with transform, geom, connections)
  - `bom` (lines with article, qty, uom)
  - `views` (front/side CAD/shaded projections)

### Governance

- **`governance/ownership-map.yaml`** — Domain ownership boundaries
- **`governance/skills-map.md`** — Skill triggers and handoff protocol
- **`governance/multi-agent-plan.md`** — 12-week roadmap with phases

### Research Documentation

Located in `research/RIVO_Fix_Configurator_Master_Pack/docs/`:

| Doc | Content |
|-----|---------|
| `00_INDEX.md` | Master pack overview |
| `01_System_Architecture.md` | Target architecture & roadmap |
| `02_Product_Model_Template.md` | Product model schema |
| `03_Constraint_DSL.md` | Rule DSL + explainable validation |
| `04_Solution_Engine.md` | Reverse configuration pipeline |
| `05_CPQ.md` | Pricing + BOM calculation |
| `06_API_Contract.md` | REST API specification |
| `07_UI_UX_Task_for_Agent.md` | UI/UX agent task specification |
| `08_DB_Schema_and_Versioning.md` | Snapshot versioning model |
| `09_Roadmap.md` | Enterprise roadmap |

---

## Anti-Patterns (Forbidden)

- ❌ Pricing logic in frontend
- ❌ Constraint logic inside viewer
- ❌ Disabled options without explanation
- ❌ Contract changes without version bump
- ❌ Multi-domain mega-PRs without orchestrator approval

---

## Skills System

The project uses **36 specialized skills** organized by domain:

### Core RIVO Skills
- `rivo-multi-agent-orchestrator` — Decomposition, dependencies, merge order
- `rivo-product-modeling` — Attributes, catalogs, version tags
- `rivo-constraint-engine` — DSL rules, explainability, auto-correct
- `rivo-cpq-and-api` — API contracts, pricing/BOM, snapshot persistence
- `rivo-ui-3d-experience` — Guided/reverse UX, viewer mapping
- `rivo-quality-gates` — Replay determinism, contract compatibility, E2E

### Supporting Skills
- `backend-architect`, `database-architect` — Server-side architecture
- `threejs-skills`, `3d-web-experience` — 3D viewer integration
- `openapi-spec-generation`, `api-design-principles` — Contract design
- `playwright-skill`, `test-automator` — E2E automation
- `tdd-orchestrator` — Test-driven development
- `context-driven-development`, `dispatching-parallel-agents` — Agent coordination

---

## Integration Cadence

- **Daily:** Integration window (green PRs only)
- **Weekly:** Stabilization window (bugfix/hardening only)
- **Pre-release:** 48-hour freeze (blocker fixes only)

---

## Related Files

- `test_ajv.js` — AJV validation test for JSON Schema
- `update_catalog.py` — Catalog update utility
- `ui/index.html` — Phase 4 UI mock with catalog rendering
- `report.md` — Skills selection analysis from research
