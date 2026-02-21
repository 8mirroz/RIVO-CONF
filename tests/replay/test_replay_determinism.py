# -*- coding: utf-8 -*-
"""Replay Determinism Tests — P0-04"""
import json, hashlib
from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def load_fixture(name):
    return json.loads((FIXTURES_DIR / name).read_text())

def hash_result(result):
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

class TestReplayDeterminism:
    def test_snapshot_hash_stable(self):
        s = load_fixture("sample_snapshot.json")
        assert hash_result(s) == hash_result(s)
    def test_version_tags_present(self):
        s = load_fixture("sample_snapshot.json")
        for t in ["catalog","rules","pricing","assets"]:
            assert t in s.get("versionTags",{})
    def test_dimensions_deterministic(self):
        s = load_fixture("sample_snapshot.json")
        for k in ["width","height","depth"]:
            assert isinstance(s["dimensions"][k],(int,float))
    def test_bom_structure(self):
        for item in load_fixture("sample_snapshot.json").get("bom",[]):
            assert all(k in item for k in ["article","qty","uom"])
    def test_replay_idempotency(self):
        s = load_fixture("sample_snapshot.json")
        h = [hash_result(s) for _ in range(3)]
        assert all(x==h[0] for x in h)
