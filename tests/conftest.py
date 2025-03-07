"""
Global pytest configuration and fixtures.

This module contains test configuration and fixtures that can be used across
all test categories:
- UI
- Backend
- Database
- API
- Core (business logic)
"""

import os
import sys
from unittest.mock import MagicMock

import django
import pytest
from django.conf import settings
from django.test import Client
from rest_framework.test import APIClient

# Set up environment variables
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "pyerp.config.settings.test"
)

# Configure Django settings
django.setup()

# Create a simplified approach - mock Django modules for unit tests
# This will prevent the "Apps aren't loaded yet" errors
sys.modules["django.db.models.base"] = MagicMock()
sys.modules["django.db.models"] = MagicMock()
sys.modules["django.core.validators"] = MagicMock()


# Test database configuration
@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


# UI Testing Fixtures
@pytest.fixture
def client():
    """A Django test client instance."""
    return Client()


@pytest.fixture
def api_client():
    """A Django REST framework API test client instance."""
    return APIClient()


# Database Fixtures
@pytest.fixture
def sample_db(django_db_setup, django_db_blocker):
    """Create a sample database for testing."""
    with django_db_blocker.unblock():
        # Add any initial data setup here
        yield


# API Testing Fixtures
@pytest.fixture
def mock_api_response():
    """Sample API response data for testing."""
    return {
        "status": "success",
        "data": {
            "id": 1,
            "name": "Test Item"
        }
    }


# Business Logic Fixtures
@pytest.fixture
def sample_product_data():
    """Sample product data for testing business logic."""
    return {
        "sku": "TEST001",
        "name": "Test Product",
        "price": "99.99",
        "category": "Test Category",
    }


# Test Environment Setup
def pytest_configure(config):
    """Configure test environment."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "pyerp.config.settings.test"
    settings.DEBUG = False
