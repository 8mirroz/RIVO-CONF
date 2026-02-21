import pytest
from pathlib import Path

@pytest.fixture
def project_root():
    return Path(__file__).parent.parent

@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"
