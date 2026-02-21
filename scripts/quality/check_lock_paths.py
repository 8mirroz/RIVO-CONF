#!/usr/bin/env python3
"""Validate that changes are within allowed lock_paths from Issue."""

import sys
import re
from pathlib import Path


def extract_lock_paths_from_issue(issue_body):
    lock_paths_match = re.search(r"## Lock Paths\s*\n([^\n]+)", issue_body)

    if not lock_paths_match:
        print("ERROR: Could not find Lock Paths in issue body")
        sys.exit(1)

    lock_paths_str = lock_paths_match.group(1).strip()
    lock_paths = [p.strip() for p in lock_paths_str.split(",")]

    return lock_paths


def get_changed_files():
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [Path(f) for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def is_path_allowed(file_path, lock_paths):
    file_str = str(file_path)

    for lock_path in lock_paths:
        if lock_path.endswith("/"):
            if file_str.startswith(lock_path) or file_str + "/" == lock_path:
                return True
        else:
            if file_str == lock_path or file_str.startswith(lock_path + "/"):
                return True

    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: check_lock_paths.py <issue_body>")
        sys.exit(1)

    issue_body = sys.argv[1]
    lock_paths = extract_lock_paths_from_issue(issue_body)

    print(f"Allowed lock paths: {lock_paths}")

    changed_files = get_changed_files()

    if not changed_files:
        print("No changed files to check")
        return

    violations = []

    for file_path in changed_files:
        if not is_path_allowed(file_path, lock_paths):
            violations.append(file_path)

    if violations:
        print("\nLock path violations detected:")
        for v in violations:
            print(f"  - {v} is outside allowed lock_paths")
        sys.exit(1)

    print("All changes are within allowed lock_paths")


if __name__ == "__main__":
    main()
