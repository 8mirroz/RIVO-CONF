#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replay Test Runner — P0-04

Runs replay determinism tests and generates reports.
Used in CI/CD pipelines for quality gates.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests" / "replay"


def run_pytest(test_dir: Path, verbose: bool = True) -> dict:
    """Run pytest on the test directory and return results."""
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "--tb=short",
        "--json-report",
        "--json-report-file=none"
    ]
    
    if verbose:
        cmd.append("-v")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": 1
        }


def generate_report(result: dict) -> str:
    """Generate a human-readable report from test results."""
    lines = []
    lines.append("=" * 60)
    lines.append("REPLAY TEST REPORT")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    lines.append(f"Status: {'PASS' if result['success'] else 'FAIL'}")
    lines.append("")
    
    if result['stdout']:
        lines.append("OUTPUT:")
        lines.append(result['stdout'])
    
    if result['stderr'] and not result['success']:
        lines.append("ERRORS:")
        lines.append(result['stderr'])
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run replay determinism tests")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output report file path"
    )
    
    args = parser.parse_args()
    
    print(f"Running replay tests from: {TESTS_DIR}")
    
    result = run_pytest(TESTS_DIR, verbose=args.verbose)
    report = generate_report(result)
    
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}")
    
    print(report)
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
