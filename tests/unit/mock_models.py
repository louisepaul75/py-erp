"""
Mock models for unit testing.

This module contains mock classes to simulate Django models without requiring
the Django app registry to be set up.
"""
from unittest.mock import MagicMock


class MockQuerySet:
    """Mock implementation of a Django QuerySet."""

    def __init__(self, items=None):
        self.items = items or []
        self.exists_return = bool(self.items)
        self.filter_args = []
        self.order_by_args = []

    def filter(self, *args, **kwargs):
        """Mock filter method."""
        self.filter_args.append((args, kwargs))
        return self

    def order_by(self, *args):
        """Mock order_by method."""
        self.order_by_args.append(args)
        return self

    def exists(self):
        """Mock exists method."""
        return self.exists_return

    def get(self, *args, **kwargs):
        """Mock get method."""
        if not self.items:
            raise DoesNotExist("Requested object does not exist")
        return self.items[0]

    def __iter__(self):
        """Make the query set iterable."""
        return iter(self.items)

    def __getitem__(self, key):
        """Support indexing."""
        return self.items[key]

    def count(self):
        """Return count of items."""
        return len(self.items)


class DoesNotExist(Exception):
    """Mock DoesNotExist exception."""
    pass


class MultipleObjectsReturned(Exception):
    """Mock MultipleObjectsReturned exception."""
    pass


class MockModelBase:
    """Base class for mock model objects."""

    DoesNotExist = DoesNotExist
    MultipleObjectsReturned = MultipleObjectsReturned

    @classmethod
    def setup_objects_manager(cls):
        """Set up the objects manager with all the necessary methods."""
        objects = MagicMock()
        objects.get = MagicMock()
        objects.filter = MagicMock(return_value=MockQuerySet())
        objects.create = MagicMock(return_value=cls())
        objects.all = MagicMock(return_value=MockQuerySet())
        objects.none = MagicMock(return_value=MockQuerySet())
        return objects


class MockProduct(MockModelBase):
    """Mock Product model."""

    objects = MagicMock()

    def __init__(self, **kwargs):
        """Initialize with given attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Default attributes
        if 'sku' not in kwargs:
            self.sku = "MOCK-SKU"
        if 'name' not in kwargs:
            self.name = "Mock Product"
        if 'list_price' not in kwargs:
            self.list_price = 100.0
        if 'is_active' not in kwargs:
            self.is_active = True

    def save(self, *args, **kwargs):
        """Mock save method."""
        pass

    def clean(self):
        """Mock clean method."""
        pass

    def __str__(self):
        """String representation."""
        return self.name


class MockProductCategory(MockModelBase):
    """Mock ProductCategory model."""

    objects = MagicMock()

    def __init__(self, **kwargs):
        """Initialize with given attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Default attributes
        if 'code' not in kwargs:
            self.code = "MOCK-CAT"
        if 'name' not in kwargs:
            self.name = "Mock Category"

    def save(self, *args, **kwargs):
        """Mock save method."""
        pass

    def __str__(self):
        """String representation."""
        return self.name


# Set up the objects managers
MockProduct.objects = MockProduct.setup_objects_manager()
MockProductCategory.objects = MockProductCategory.setup_objects_manager()
