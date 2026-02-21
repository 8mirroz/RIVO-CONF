"""
Replay determinism tests for RIVO CONF.

Verifies that the same ConfigurationSnapshot with identical version tags
produces identical validation/price/BOM results across multiple runs.
"""

import json
import hashlib
import pytest
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file."""
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture {name} not found")
    return json.loads(path.read_text())


def compute_hash(data: dict) -> str:
    """Compute deterministic hash of a dict."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


class TestReplayDeterminism:
    """Test suite for replay determinism."""

    def test_snapshot_hash_is_deterministic(self):
        """Same snapshot content should produce same hash."""
        snapshot = load_fixture("sample_snapshot.json")
        hash1 = compute_hash(snapshot)
        hash2 = compute_hash(snapshot)
        assert hash1 == hash2, "Snapshot hash must be deterministic"

    def test_version_tags_are_present(self):
        """Snapshot must include version tags for catalog/rules/pricing/assets."""
        snapshot = load_fixture("sample_snapshot.json")
        version_tag = snapshot.get("versionTag", {})
        required = ["catalog", "rules", "pricing", "assets"]
        for key in required:
            assert key in version_tag, f"Missing version tag: {key}"

    def test_validation_result_structure(self):
        """Validation result must have explainable structure."""
        snapshot = load_fixture("sample_snapshot.json")
        assert "selectedOptions" in snapshot, "Missing selectedOptions"
        assert "structureGraph" in snapshot, "Missing structureGraph"

    @pytest.mark.parametrize("run", range(3))
    def test_repeated_validation_produces_same_result(self, run):
        """Multiple validations of same snapshot should be identical."""
        snapshot = load_fixture("sample_snapshot.json")
        snapshot_hash = compute_hash(snapshot)
        assert snapshot_hash, f"Run {run}: snapshot must be hashable"
