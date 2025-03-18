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
import pytest

# Configure Django settings before any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.test")

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Django
import django

django.setup()

# Now we can safely import Django components
from django.test import Client
from django.conf import settings
from rest_framework.test import APIClient

# Configure URL patterns for tests

# Append our test URLs to the ROOT_URLCONF
settings.ROOT_URLCONF = "tests.test_urls"


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
    return {"status": "success", "data": {"id": 1, "name": "Test Item"}}


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
