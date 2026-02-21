import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    return Path(__file__).parent.parent


@pytest.fixture
def contracts_dir(project_root):
    return project_root / "contracts"


@pytest.fixture
def schemas_dir(contracts_dir):
    return contracts_dir / "schemas"


@pytest.fixture
def examples_dir(contracts_dir):
    return contracts_dir / "examples"
