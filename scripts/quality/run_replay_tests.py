#!/usr/bin/env python3
"""Replay Test Runner — P0-04"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "replay"

def main() -> int:
    cmd = [sys.executable, "-m", "pytest", str(TESTS_DIR), "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
