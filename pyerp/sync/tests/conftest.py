"""
Pytest configuration for sync module tests.
"""

import pytest

# Import test settings to configure Django before tests run
# pylint: disable=unused-wildcard-import,wildcard-import
from pyerp.sync.tests.test_settings import *  # noqa


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Configure Django DB for tests.
    This overrides the pytest-django fixture to use our in-memory DB.
    """
    pass  # Settings are already configured in test_settings.py
