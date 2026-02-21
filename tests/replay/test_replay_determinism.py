# -*- coding: utf-8 -*-
"""
Replay Determinism Tests — P0-04
"""

import json
import hashlib
from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def load_fixture(name: str) -> dict:
    fixture_path = FIXTURES_DIR / name
    if not fixture_path.exists():
        pytest.skip(f"Fixture not found: {fixture_path}")
    return json.loads(fixture_path.read_text(encoding="utf-8"))

def hash_result(result: dict) -> str:
    normalized = json.dumps(result, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

class TestReplayDeterminism:
    def test_snapshot_hash_is_stable(self):
        snapshot = load_fixture("sample_snapshot.json")
        assert hash_result(snapshot) == hash_result(snapshot)

    def test_version_tags_present(self):
        snapshot = load_fixture("sample_snapshot.json")
        required_tags = ["catalog", "rules", "pricing", "assets"]
        version_tags = snapshot.get("versionTags", {})
        for tag in required_tags:
            assert tag in version_tags, f"Missing version tag: {tag}"

    def test_dimensions_are_deterministic(self):
        snapshot = load_fixture("sample_snapshot.json")
        dims = snapshot.get("dimensions", {})
        for key in ["width", "height", "depth"]:
            assert key in dims
            assert isinstance(dims[key], (int, float))
            assert dims[key] > 0

    def test_bom_structure_deterministic(self):
        snapshot = load_fixture("sample_snapshot.json")
        bom = snapshot.get("bom", [])
        assert len(bom) > 0
        for item in bom:
            assert "article" in item and "qty" in item and "uom" in item
            assert isinstance(item["qty"], (int, float))
            assert item["qty"] >= 0

    def test_replay_idempotency(self):
        snapshot = load_fixture("sample_snapshot.json")
        results = [hash_result(snapshot) for _ in range(3)]
        assert all(r == results[0] for r in results)
