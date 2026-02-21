import pytest
from pathlib import Path
import yaml
import json


class TestContractSchemas:
    def test_schemas_are_valid_yaml_or_json(self, schemas_dir):
        if not schemas_dir.exists():
            pytest.skip("Schemas directory not found")

        for schema_file in schemas_dir.glob("*"):
            if schema_file.suffix in [".yaml", ".yml"]:
                content = yaml.safe_load(schema_file.read_text())
                assert isinstance(content, dict), f"Invalid YAML schema: {schema_file}"
            elif schema_file.suffix == ".json":
                content = json.loads(schema_file.read_text())
                assert isinstance(content, dict), f"Invalid JSON schema: {schema_file}"

    def test_openapi_spec_valid(self, contracts_dir):
        openapi_path = contracts_dir / "openapi.v1.yaml"
        if not openapi_path.exists():
            pytest.skip("OpenAPI spec not found")

        content = yaml.safe_load(openapi_path.read_text())
        assert "openapi" in content, "OpenAPI version field missing"
        assert "info" in content, "OpenAPI info field missing"
        assert "paths" in content, "OpenAPI paths field missing"
