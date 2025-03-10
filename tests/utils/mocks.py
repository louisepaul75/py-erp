"""
Mock classes and utilities for testing.

This module provides mock classes and utilities that can be used across
different test modules to ensure consistent test behavior.
"""

from unittest.mock import MagicMock


class MockProduct:
    """Mock Product class for testing."""

    class DoesNotExist(Exception):
        """Mock exception for when a product doesn't exist."""

    objects = MagicMock()

    def __init__(self):
        """Initialize with default attributes."""
        self.sku = None
        self.name = None
        self.is_parent = False
        self.variant_code = None
        self.list_price = None
        self.cost_price = None
        self.base_sku = None
        self.category = None
        
        # Create a minimal mock for model metadata
        self._meta = MagicMock()
        self._meta.fields = []
        self._meta.db_table = 'products_product'
        
        # Create a minimal mock for model state
        self._state = MagicMock()
        self._state.adding = True
        
        # Create a minimal mock for primary key field
        class BigAutoField:
            def __init__(self):
                self.__module__ = 'django.db.models'
                self.__class__ = type('BigAutoField', (), {})
                self._subclasses = (object,)
                self.__bases__ = (object,)
                self.__mro__ = (object,)
            
            def __subclasscheck__(self, subclass):
                return True

        self._meta.pk = BigAutoField()

    def __class_getitem__(cls, key):
        """Support for generic type hints."""
        return cls

    def clean(self):
        """Mock clean method."""
        pass

    def save(self, *args, **kwargs):
        """Mock save method."""
        pass

    def delete(self, *args, **kwargs):
        """Mock delete method."""
        pass

    def refresh_from_db(self, *args, **kwargs):
        """Mock refresh_from_db method."""
        pass


class MockProductCategory:
    """Mock ProductCategory class for testing."""

    class DoesNotExist(Exception):
        """Mock exception for when a category doesn't exist."""

    objects = MagicMock()

    def __init__(self, code=None, name=None):
        """Initialize with optional code and name."""
        self.code = code
        self.name = name


class MockAPIResponse:
    """Mock API response for testing."""

    def __init__(self, status_code=200, data=None):
        """Initialize with status code and response data."""
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        """Return response data as JSON."""
        return self._data

    @property
    def content(self):
        """Return raw response content."""
        return str(self._data).encode("utf-8")


def reset_all_mocks():
    """Reset all mock objects to their initial state."""
    MockProduct.objects.reset_mock()
    MockProductCategory.objects.reset_mock()
