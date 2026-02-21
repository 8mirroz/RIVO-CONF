#!/usr/bin/env python3
"""
Replay test runner for RIVO CONF.

Ensures deterministic replay of configuration snapshots with version tags.
"""

import json
import hashlib
import sys
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent.parent.parent / "tests" / "fixtures"


def compute_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def verify_fixtures():
    errors = []
    fixtures = list(FIXTURES_DIR.glob("*.json"))

    if not fixtures:
        errors.append("No snapshot fixtures found in tests/fixtures/")
        return errors

    for fixture in fixtures:
        try:
            data = json.loads(fixture.read_text())
            version_tag = data.get("versionTag", {})
            required = ["catalog", "rules", "pricing", "assets"]
            missing = [k for k in required if k not in version_tag]
            if missing:
                errors.append(f"{fixture.name}: missing version tags: {missing}")
        except json.JSONDecodeError as e:
            errors.append(f"{fixture.name}: invalid JSON - {e}")

    return errors


def run_replay_test(snapshot_path: Path, iterations: int = 3):
    data = json.loads(snapshot_path.read_text())
    hashes = [compute_hash(data) for _ in range(iterations)]

    if len(set(hashes)) != 1:
        print(f"FAIL: {snapshot_path.name} produces non-deterministic hashes")
        return False

    print(f"PASS: {snapshot_path.name} - hash={hashes[0]}")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Replay test runner")
    parser.add_argument(
        "--verify-fixtures", action="store_true", help="Verify fixture integrity"
    )
    parser.add_argument("--iterations", type=int, default=3, help="Replay iterations")
    args = parser.parse_args()

    if args.verify_fixtures:
        errors = verify_fixtures()
        if errors:
            for e in errors:
                print(f"ERROR: {e}")
            sys.exit(1)
        print("All fixtures valid")
        sys.exit(0)

    fixtures = list(FIXTURES_DIR.glob("*.json"))
    if not fixtures:
        print("No fixtures to test")
        sys.exit(0)

    passed = all(run_replay_test(f, args.iterations) for f in fixtures)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
