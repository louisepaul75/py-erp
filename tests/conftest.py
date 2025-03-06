"""
Configuration file for pytest tests.

This file sets up Django's environment for running tests.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Create a simplified approach - mock Django modules for unit tests
# This will prevent the "Apps aren't loaded yet" errors
sys.modules["django.db.models.base"] = MagicMock()
sys.modules["django.db.models"] = MagicMock()
sys.modules["django.core.validators"] = MagicMock()

# Set up environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings.testing")
os.environ.setdefault("PYTEST_RUNNING", "1")


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up a test database."""
    # This is a simplified mock fixture for tests that don't need a real DB
