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

# Import test settings first to configure Django
from .test_settings import *  # noqa

import pytest
from django.test import Client
from rest_framework.test import APIClient

# Create a simplified approach - mock Django modules for unit tests
# This will prevent the "Apps aren't loaded yet" errors
sys.modules["django.db.models.base"] = MagicMock()
sys.modules["django.db.models"] = MagicMock()
sys.modules["django.core.validators"] = MagicMock()

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
def sample_db(db):
    """Create a sample database for testing."""
    # Add any initial data setup here
    pass

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
