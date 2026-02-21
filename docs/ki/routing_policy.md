# Adaptive Swarm Routing Policy (RIVO CONF)

## Architecture Overview
The **RIVO CONF** project employs a **Hybrid Local+Global Routing** model for AI tasks. This ensures maximum consistency for configurator code generation while allowing fallback to the shared runtime.

## Core Mechanisms
1. **Local Configurations** (Single Source of Truth for this Project):
   - `configs/tooling/model_routing.json`: Determines cost/tier based on task structure.
   - `configs/tooling/model_providers.json`: Maps abstract models to physical API keys and token budgets.
   - `configs/tooling/mcp_profiles.json`: Activates required MCP servers (e.g., stitch, github, local tooling) based on complexity.
   - `configs/tooling/integration_contracts.json`: Defines machine-readable interfaces between swarm components.
   - `.agent/config/model_router.yaml`: YAML-based fallback and secondary routing logic.
   - `configs/skills/ACTIVE_SKILLS.md`: Determines the subset of abilities loaded into the project's Swarm memory.

2. **Skill Publication**:
   - Project-specific skills are located in `skills/`.
   - The `.agent/skills/` directory holds the active set, synchronized via `swarmctl.py publish-skills`.

3. **Runtime Alignment**:
   - The primary entrypoint is `./scripts/swarmctl.py`, pinned specifically to resolve paths to the local `RIVO CONF` directory.
   - Core runtime packages (like `agent_os`) are referenced from the central `antigravity-core` workspace for updates to fundamental orchestration, but routing strictly obeys the local `configs/tooling` rules.

## Execution Rules
- `swarmctl triage`: Predicts Task Type (T1-T7) and Complexity (C1-C5).
- `swarmctl route`: Outputs deterministic model and context budgets based on the local rules.
- **Fail-safes**: If local routing constraints mismatch with global logic, the local configurations (`configs/tooling/`) always take precedence.
