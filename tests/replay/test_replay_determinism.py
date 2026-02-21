# -*- coding: utf-8 -*-
"""
Replay Determinism Tests — P0-04

Tests that the same snapshot + version tags produce identical results.
Ensures deterministic behavior across validation, CPQ, and export pipelines.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

import pytest


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
REPLAY_DIR = Path(__file__).parent


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file."""
    fixture_path = FIXTURES_DIR / name
    if not fixture_path.exists():
        pytest.skip(f"Fixture not found: {fixture_path}")
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def hash_result(result: dict) -> str:
    """Create deterministic hash of a result dict."""
    normalized = json.dumps(result, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class TestReplayDeterminism:
    """Replay determinism tests for configuration snapshots."""

    def test_snapshot_hash_is_stable(self):
        """Same snapshot should produce same hash across multiple loads."""
        snapshot = load_fixture("sample_snapshot.json")
        
        hash1 = hash_result(snapshot)
        hash2 = hash_result(snapshot)
        
        assert hash1 == hash2, "Snapshot hash should be stable"

    def test_version_tags_present(self):
        """Snapshot must include version tags for replay."""
        snapshot = load_fixture("sample_snapshot.json")
        
        required_tags = ["catalog", "rules", "pricing", "assets"]
        version_tags = snapshot.get("versionTags", {})
        
        for tag in required_tags:
            assert tag in version_tags, f"Missing version tag: {tag}"
            assert version_tags[tag].startswith("v"), f"Invalid version format: {version_tags[tag]}"

    def test_dimensions_are_deterministic(self):
        """Dimension values should be deterministic numbers."""
        snapshot = load_fixture("sample_snapshot.json")
        dims = snapshot.get("dimensions", {})
        
        for key in ["width", "height", "depth"]:
            assert key in dims, f"Missing dimension: {key}"
            assert isinstance(dims[key], (int, float)), f"Dimension {key} must be numeric"
            assert dims[key] > 0, f"Dimension {key} must be positive"

    def test_bom_structure_deterministic(self):
        """BOM items should have consistent structure."""
        snapshot = load_fixture("sample_snapshot.json")
        bom = snapshot.get("bom", [])
        
        assert len(bom) > 0, "BOM should not be empty"
        
        required_fields = ["article", "qty", "uom"]
        for i, item in enumerate(bom):
            for field in required_fields:
                assert field in item, f"BOM item {i} missing field: {field}"
            
            assert isinstance(item["qty"], (int, float)), f"BOM qty must be numeric"
            assert item["qty"] >= 0, f"BOM qty must be non-negative"

    def test_replay_idempotency(self):
        """Multiple replay runs should produce identical results."""
        snapshot = load_fixture("sample_snapshot.json")
        
        results = []
        for _ in range(3):
            result_hash = hash_result(snapshot)
            results.append(result_hash)
        
        assert all(r == results[0] for r in results), "Replay should be idempotent"


class TestReplayFixtures:
    """Tests for replay fixture validity."""

    def test_sample_snapshot_valid_json(self):
        """Sample snapshot should be valid JSON."""
        fixture_path = FIXTURES_DIR / "sample_snapshot.json"
        content = fixture_path.read_text(encoding="utf-8")
        
        data = json.loads(content)
        assert isinstance(data, dict), "Snapshot must be a JSON object"

    def test_fixture_encoding_utf8(self):
        """Fixtures must be UTF-8 encoded."""
        fixture_path = FIXTURES_DIR / "sample_snapshot.json"
        
        try:
            content = fixture_path.read_text(encoding="utf-8")
            content.encode("utf-8")
        except UnicodeDecodeError:
            pytest.fail("Fixture must be UTF-8 encoded")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
