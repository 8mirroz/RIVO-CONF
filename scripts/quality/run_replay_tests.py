#!/usr/bin/env python3
"""Replay Test Runner — P0-04"""
import subprocess, sys
from pathlib import Path
TESTS_DIR = Path(__file__).parent.parent.parent / "tests" / "replay"
sys.exit(subprocess.run([sys.executable,"-m","pytest",str(TESTS_DIR),"-v"]).returncode)
