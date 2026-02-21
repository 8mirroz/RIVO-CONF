import pytest
from pathlib import Path


class TestProjectStructure:
    def test_contracts_dir_exists(self, contracts_dir):
        assert contracts_dir.exists(), f"Contracts directory not found: {contracts_dir}"
        assert contracts_dir.is_dir(), (
            f"Contracts path is not a directory: {contracts_dir}"
        )

    def test_schemas_dir_exists(self, schemas_dir):
        assert schemas_dir.exists(), f"Schemas directory not found: {schemas_dir}"
        assert schemas_dir.is_dir(), f"Schemas path is not a directory: {schemas_dir}"

    def test_examples_dir_exists(self, examples_dir):
        assert examples_dir.exists(), f"Examples directory not found: {examples_dir}"
        assert examples_dir.is_dir(), (
            f"Examples path is not a directory: {examples_dir}"
        )

    def test_openapi_spec_exists(self, contracts_dir):
        openapi_path = contracts_dir / "openapi.v1.yaml"
        assert openapi_path.exists(), f"OpenAPI spec not found: {openapi_path}"

    def test_ownership_map_exists(self, project_root):
        ownership_map = project_root / "governance" / "ownership-map.yaml"
        assert ownership_map.exists(), f"Ownership map not found: {ownership_map}"
