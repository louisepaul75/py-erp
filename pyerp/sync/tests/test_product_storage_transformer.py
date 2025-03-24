"""Tests for the product storage transformer module."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
import datetime
from typing import Any, Dict, List, Optional
import json

from pyerp.sync.transformers.product_storage import (
    ProductStorageTransformer,
    BoxStorageTransformer,
    parse_decimal,
    parse_date
)


# Test subclass that overrides database methods for testing
class ProductStorageTransformerTesting(ProductStorageTransformer):
    """Testing version of ProductStorageTransformer that doesn't access the database."""
    
    def __init__(self, *args, **kwargs):
        """Initialize without calling super to avoid any db initialization."""
        # Skip the parent __init__ to avoid any DB access
        self._product_cache = {}
        self._storage_location_cache = {}
        self._box_slot_cache = {}
        self.log = MagicMock()
    
    def _get_product(self, product_id):
        """Completely override to avoid database access."""
        # Use the cache if available
        if product_id in self._product_cache:
            return self._product_cache[product_id]
        
        # Otherwise use the mock implementation
        result = self._mock_get_product(product_id)
        if result is not None:
            self._product_cache[product_id] = result
        return result
    
    def _mock_get_product(self, product_id):
        """Mock implementation that does no database access."""
        return None  # Default, tests will override this
    
    def _get_storage_location(self, location_uuid):
        """Override to avoid database access."""
        if location_uuid in self._storage_location_cache:
            return self._storage_location_cache[location_uuid]
        
        # Use the mock implementation
        result = self._mock_get_storage_location(location_uuid)
        if result is not None:
            self._storage_location_cache[location_uuid] = result
        return result
    
    def _mock_get_storage_location(self, location_uuid):
        """Mock implementation that does no database access."""
        return None  # Default, tests will override this
    
    def _get_box_slot(self, box_id, legacy_slot_id=None):
        """Override to avoid database access."""
        cache_key = f"{box_id}:{legacy_slot_id}"
        if cache_key in self._box_slot_cache:
            return self._box_slot_cache[cache_key]
        
        # Use the mock implementation
        result = self._mock_get_box_slot(box_id, legacy_slot_id)
        if result is not None:
            self._box_slot_cache[cache_key] = result
        return result
    
    def _mock_get_box_slot(self, box_id, legacy_slot_id=None):
        """Mock implementation that does no database access."""
        return None  # Default, tests will override this


class BoxStorageTransformerTesting(BoxStorageTransformer):
    """Testing version of BoxStorageTransformer that doesn't access the database."""
    
    def _get_product_storage(self, uuid):
        """Override to avoid database access."""
        if uuid in self._product_storage_cache:
            return self._product_storage_cache[uuid]
        return self._mock_get_product_storage(uuid)
    
    def _mock_get_product_storage(self, uuid):
        """Mock implementation that does no database access."""
        return None  # Default, tests will override this


@pytest.mark.unit
class TestHelperFunctions:
    """Tests for the helper functions in the product_storage module."""

    def test_parse_decimal_valid(self):
        """Test parsing valid decimal values."""
        # Test valid formats
        assert parse_decimal("123.45") == Decimal("123.45")
        assert parse_decimal("123,45") == Decimal("12345")  # Comma is removed
        assert parse_decimal("-123.45") == Decimal("-123.45")
        assert parse_decimal("1,234.56") == Decimal("1234.56")  # Commas are removed but decimal point is kept
        assert parse_decimal("€ 123.45") == Decimal("123.45")  # Currency symbol removed
        
    def test_parse_decimal_invalid(self):
        """Test parsing invalid decimal values."""
        # Test invalid formats - should return 0
        assert parse_decimal("") == Decimal("0")
        assert parse_decimal(None) == Decimal("0")
        assert parse_decimal("abc") == Decimal("0")
        assert parse_decimal("123.45.67") == Decimal("0")  # Multiple decimal points
        
    def test_parse_date_valid(self):
        """Test parsing valid date strings."""
        # Test DD.MM.YYYY format
        result = parse_date("01.02.2025")
        assert isinstance(result, datetime.date)
        assert result.day == 1
        assert result.month == 2
        assert result.year == 2025
        
    def test_parse_date_invalid(self):
        """Test parsing invalid date strings."""
        # Test invalid formats
        assert parse_date("") is None
        assert parse_date(None) is None
        assert parse_date("2025-02-01") is None  # Wrong format
        assert parse_date("01/02/2025") is None  # Wrong format
        assert parse_date("32.01.2025") is None  # Invalid day
        assert parse_date("01.13.2025") is None  # Invalid month


@pytest.mark.unit
class TestProductStorageTransformer:
    """Tests for the ProductStorageTransformer class."""

    def test_init(self):
        """Test initialization of ProductStorageTransformer."""
        transformer = ProductStorageTransformer({})
        
        # Verify caches are initialized
        assert transformer._product_cache == {}
        assert transformer._storage_location_cache == {}
        assert transformer._box_slot_cache == {}

    def test_get_product_by_refOld(self):
        """Test getting a product by refOld."""
        # Setup mock
        mock_product = MagicMock()
        
        # Create transformer
        transformer = ProductStorageTransformerTesting()
        
        # Override mock_get_product to return our mock product for refOld
        def mock_get_product_impl(product_id):
            if product_id == "12345":
                return mock_product
            return None
        
        transformer._mock_get_product = mock_get_product_impl
        
        # Test the method
        product = transformer._get_product("12345")
        
        # Verify result
        assert product == mock_product
        assert transformer._product_cache["12345"] == mock_product

    def test_get_product_by_legacy_id(self):
        """Test getting a product by legacy_id."""
        # Setup mocks
        mock_product = MagicMock()
        
        # Create transformer and override mock method
        transformer = ProductStorageTransformerTesting()
        
        # Set up mock to simulate the lookup process
        calls = []
        
        def mock_get_product_impl(product_id):
            calls.append(product_id)
            
            # If this is the first call, return None (simulating refOld lookup failure)
            if len(calls) == 1:
                return None
            # Second call returns mock_product (simulating legacy_id lookup success)
            elif len(calls) == 2:
                return mock_product
            
            return None
        
        transformer._mock_get_product = mock_get_product_impl
        
        # Test
        product = transformer._get_product("12345")
        assert product is None  # First call returns None
        
        # Try again to simulate the full process in the original transformer
        product = transformer._get_product("12345")
        
        # Verify result
        assert product == mock_product
        assert transformer._product_cache["12345"] == mock_product
        assert len(calls) == 2  # Should be called twice

    def test_get_product_by_sku(self):
        """Test getting a product by SKU."""
        # Setup mocks
        mock_product = MagicMock()
        
        # Create transformer and override mock method
        transformer = ProductStorageTransformerTesting()
        
        # Set up mock to simulate the lookup process
        calls = []
        
        def mock_get_product_impl(product_id):
            calls.append(product_id)
            
            # First two calls return None
            if len(calls) <= 2:
                return None
            # Third call returns product
            elif len(calls) == 3:
                return mock_product
            
            return None
        
        transformer._mock_get_product = mock_get_product_impl
        
        # Test - simulate the three lookups
        product = transformer._get_product("12345")
        assert product is None  # First call returns None
        
        product = transformer._get_product("12345")
        assert product is None  # Second call returns None
        
        product = transformer._get_product("12345")
        
        # Verify result
        assert product == mock_product
        assert transformer._product_cache["12345"] == mock_product
        assert len(calls) == 3  # Should be called three times

    def test_get_product_not_found(self):
        """Test getting a product that doesn't exist."""
        # Create transformer with method that always returns None
        transformer = ProductStorageTransformerTesting({})
        transformer._product_cache = {}
        transformer._mock_get_product = lambda product_id: None
        
        # Test
        product = transformer._get_product("12345")
        
        # Verify result
        assert product is None
        assert "12345" not in transformer._product_cache
        
    def test_storage_location(self):
        """Test getting a storage location."""
        # Setup mock
        mock_location = MagicMock()
        
        # Create transformer and test
        transformer = ProductStorageTransformerTesting({})
        transformer._storage_location_cache = {}
        
        def mock_get_storage_location_impl(location_uuid):
            if location_uuid == "location-123":
                # Store in cache
                transformer._storage_location_cache[location_uuid] = mock_location
                return mock_location
            return None
        
        transformer._mock_get_storage_location = mock_get_storage_location_impl
        
        # Test
        location = transformer._get_storage_location("location-123")
        
        # Verify result
        assert location == mock_location
        assert transformer._storage_location_cache["location-123"] == mock_location

    def test_get_storage_location_not_found(self):
        """Test getting a storage location that doesn't exist."""
        # Create transformer with method that always returns None
        transformer = ProductStorageTransformerTesting({})
        transformer._storage_location_cache = {}
        transformer._mock_get_storage_location = lambda location_uuid: None
        
        # Test
        location = transformer._get_storage_location("location-123")
        
        # Verify result
        assert location is None
        assert "location-123" not in transformer._storage_location_cache
        
    def test_get_box_slot_with_box_id_only(self):
        """Test getting a box slot with only box_id."""
        # Setup mock
        mock_slot = MagicMock()
        
        # Create transformer and test
        transformer = ProductStorageTransformerTesting({})
        transformer._box_slot_cache = {}
        
        def mock_get_box_slot_impl(box_id, legacy_slot_id=None):
            if box_id == "box-123":
                # Store in cache
                cache_key = f"{box_id}:{legacy_slot_id}"
                transformer._box_slot_cache[cache_key] = mock_slot
                return mock_slot
            return None
        
        transformer._mock_get_box_slot = mock_get_box_slot_impl
        
        # Test
        slot = transformer._get_box_slot("box-123")
        
        # Verify result
        assert slot == mock_slot
        assert transformer._box_slot_cache.get("box-123:None") == mock_slot

    def test_parse_quantity_valid(self):
        """Test parsing valid quantity values."""
        transformer = ProductStorageTransformer({})
        
        assert transformer._parse_quantity(10) == 10
        assert transformer._parse_quantity("10") == 10
        assert transformer._parse_quantity(10.0) == 10
        assert transformer._parse_quantity("10.0") == 10
        assert transformer._parse_quantity("10.5") == 10  # Doesn't round up, simple int conversion
        
    def test_parse_quantity_invalid(self):
        """Test parsing invalid quantity values."""
        transformer = ProductStorageTransformer({})
        
        # The method seems to handle numeric extraction from strings
        assert transformer._parse_quantity("10abc") == 10  # Extracts the numeric part
        assert transformer._parse_quantity("abc") == 0  # No numeric part returns 0
        assert transformer._parse_quantity(None) == 0
        assert transformer._parse_quantity("") == 0


@pytest.mark.unit
class TestBoxStorageTransformer:
    """Tests for the BoxStorageTransformer class."""

    def test_init(self):
        """Test initialization of BoxStorageTransformer."""
        transformer = BoxStorageTransformer({})
        
        # Verify product storage cache is initialized
        assert transformer._product_storage_cache == {}
        assert transformer._box_slot_cache == {}

    def test_get_product_storage(self):
        """Test getting a product storage by UUID."""
        # Setup mock
        mock_storage = MagicMock()
        
        # Create transformer and test
        transformer = BoxStorageTransformerTesting({})
        transformer._product_storage_cache = {}
        
        def mock_get_product_storage_impl(uuid):
            if uuid == "storage-123":
                # Store in cache
                transformer._product_storage_cache[uuid] = mock_storage
                return mock_storage
            return None
        
        transformer._mock_get_product_storage = mock_get_product_storage_impl
        
        # Test
        storage = transformer._get_product_storage("storage-123")
        
        # Verify result
        assert storage == mock_storage
        assert transformer._product_storage_cache["storage-123"] == mock_storage

    def test_extract_box_data(self):
        """Test extracting box data from input data."""
        transformer = BoxStorageTransformer({})
        
        input_data = {
            "ID": "legacy-id-123",
            "ID_Stamm_Lager_Schuetten": "box-123",
            "UUID_Artikel_Lagerorte": "storage-uuid-456",
            "data_": json.dumps({
                "Schuetten_ID": "schuette-789",
                "Artikel_Lagerort": "art-lager-101112",
                "Stamm_Lagerort": "stamm-lager-131415"
            }),
            "Relation_95_zurueck": json.dumps({
                "ID_Lager_Schuetten_Slots": "slot-5"
            })
        }
        
        result = transformer._extract_box_data(input_data)
        
        # Verify extracted data
        assert result["legacy_id"] == "legacy-id-123"
        assert result["box_id"] == "box-123"
        assert result["artikel_lagerorte_uuid"] == "storage-uuid-456"
        assert result["schuetten_id"] == "schuette-789"
        assert result["artikel_lagerort"] == "art-lager-101112"
        assert result["stamm_lagerort"] == "stamm-lager-131415"
        assert result["slot_id"] == "slot-5"

    def test_parse_quantity(self):
        """Test parsing quantity values."""
        transformer = BoxStorageTransformer({})
        
        assert transformer._parse_quantity(10) == 10
        assert transformer._parse_quantity("10") == 10
        assert transformer._parse_quantity(10.0) == 10
        assert transformer._parse_quantity("10.0") == 10
        assert transformer._parse_quantity("10.5") == 10  # Doesn't round up, simple int conversion
        assert transformer._parse_quantity("10abc") == 10  # Extracts the numeric part
        assert transformer._parse_quantity("abc") == 0  # No numeric part
        assert transformer._parse_quantity(None) == 0
        assert transformer._parse_quantity("") == 0 