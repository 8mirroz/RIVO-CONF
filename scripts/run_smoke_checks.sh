#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT_DIR"

python3 repos/packages/agent-os/scripts/swarmctl.py smoke
python3 repos/packages/agent-os/scripts/swarmctl.py route "fix typo in README" --task-type T2 --complexity C1
python3 repos/packages/agent-os/scripts/swarmctl.py run "verify baseline route and memory"
