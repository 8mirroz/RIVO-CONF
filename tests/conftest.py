# -*- coding: utf-8 -*-
"""
Pytest configuration for RIVO CONF tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def contracts_dir(project_root):
    """Return the contracts directory."""
    return project_root / "contracts"


@pytest.fixture
def schemas_dir(contracts_dir):
    """Return the schemas directory."""
    return contracts_dir / "schemas"


@pytest.fixture
def examples_dir(contracts_dir):
    """Return the examples directory."""
    return contracts_dir / "examples"


@pytest.fixture
def fixtures_dir(project_root):
    """Return the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def replay_dir(project_root):
    """Return the replay tests directory."""
    return Path(__file__).parent / "replay"
