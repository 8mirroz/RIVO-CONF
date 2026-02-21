#!/usr/bin/env python3
"""Check ownership compliance against governance/ownership-map.yaml."""

import sys
from pathlib import Path
import yaml


def load_ownership_map():
    ownership_path = (
        Path(__file__).parent.parent.parent / "governance" / "ownership-map.yaml"
    )

    if not ownership_path.exists():
        print(f"ERROR: Ownership map not found: {ownership_path}")
        sys.exit(1)

    with open(ownership_path) as f:
        return yaml.safe_load(f)


def get_changed_files():
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [Path(f) for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        print("WARNING: Could not get changed files, checking all files")
        return []


def check_file_ownership(file_path, ownership_map):
    file_str = str(file_path)

    for owner_name, owner_config in ownership_map.get("owners", {}).items():
        for pattern in owner_config.get("paths", []):
            if pattern.endswith("/**"):
                dir_pattern = pattern[:-3]
                if file_str.startswith(dir_pattern):
                    return owner_name
            elif file_str == pattern:
                return owner_name

    return None


def main():
    ownership_map = load_ownership_map()
    changed_files = get_changed_files()

    if not changed_files:
        print("No changed files to check")
        return

    violations = []

    for file_path in changed_files:
        owner = check_file_ownership(file_path, ownership_map)
        if owner is None:
            violations.append(file_path)

    if violations:
        print("\nOwnership violations detected:")
        for v in violations:
            print(f"  - {v} has no owner in ownership-map.yaml")
        sys.exit(1)

    print("All files have valid ownership")


if __name__ == "__main__":
    main()
