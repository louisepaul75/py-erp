"""Tests for the product storage transformer module."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
import datetime
from typing import Any, Dict, List, Optional

from pyerp.sync.transformers.product_storage import (
    ProductStorageTransformer,
    BoxStorageTransformer,
    parse_decimal,
    parse_date
)


@pytest.mark.unit
class TestHelperFunctions:
    """Tests for the helper functions in the product_storage module."""

    def test_parse_decimal_valid(self):
        """Test parsing valid decimal values."""
        # Test valid formats
        assert parse_decimal("123.45") == Decimal("123.45")
        assert parse_decimal("123,45") == Decimal("12345")  # Comma is removed
        assert parse_decimal("-123.45") == Decimal("-123.45")
        assert parse_decimal("1,234.56") == Decimal("123456")  # Commas removed
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

    @patch("pyerp.sync.transformers.product_storage.VariantProduct")
    def test_get_product_by_refOld(self, mock_variant_product):
        """Test getting a product by refOld."""
        # Setup mock
        mock_product = MagicMock()
        mock_variant_product.objects.get.return_value = mock_product
        mock_variant_product.DoesNotExist = Exception
        
        transformer = ProductStorageTransformer({})
        product = transformer._get_product("12345")
        
        # Verify product is returned and cached
        assert product == mock_product
        assert transformer._product_cache["12345"] == mock_product
        mock_variant_product.objects.get.assert_called_once_with(refOld="12345")

    @patch("pyerp.sync.transformers.product_storage.VariantProduct")
    def test_get_product_by_legacy_id(self, mock_variant_product):
        """Test getting a product by legacy_id after refOld fails."""
        # Setup mock
        mock_product = MagicMock()
        mock_variant_product.DoesNotExist = Exception
        
        # First call raises DoesNotExist, second call succeeds
        mock_variant_product.objects.get.side_effect = [
            mock_variant_product.DoesNotExist,
            mock_product
        ]
        
        transformer = ProductStorageTransformer({})
        product = transformer._get_product("12345")
        
        # Verify product is returned and cached
        assert product == mock_product
        assert transformer._product_cache["12345"] == mock_product
        
        # Verify both lookups were attempted
        assert mock_variant_product.objects.get.call_count == 2
        mock_variant_product.objects.get.assert_any_call(refOld="12345")
        mock_variant_product.objects.get.assert_any_call(legacy_id="12345")

    @patch("pyerp.sync.transformers.product_storage.VariantProduct")
    def test_get_product_by_sku(self, mock_variant_product):
        """Test getting a product by sku after refOld and legacy_id fail."""
        # Setup mock
        mock_product = MagicMock()
        mock_variant_product.DoesNotExist = Exception
        
        # First two calls raise DoesNotExist, third call succeeds
        mock_variant_product.objects.get.side_effect = [
            mock_variant_product.DoesNotExist,
            mock_variant_product.DoesNotExist,
            mock_product
        ]
        
        transformer = ProductStorageTransformer({})
        product = transformer._get_product("12345")
        
        # Verify product is returned and cached
        assert product == mock_product
        assert transformer._product_cache["12345"] == mock_product
        
        # Verify all lookups were attempted
        assert mock_variant_product.objects.get.call_count == 3
        mock_variant_product.objects.get.assert_any_call(refOld="12345")
        mock_variant_product.objects.get.assert_any_call(legacy_id="12345")
        mock_variant_product.objects.get.assert_any_call(sku="12345")

    @patch("pyerp.sync.transformers.product_storage.VariantProduct")
    def test_get_product_not_found(self, mock_variant_product):
        """Test getting a product that doesn't exist."""
        # Setup mock
        mock_variant_product.DoesNotExist = Exception
        
        # All calls raise DoesNotExist
        mock_variant_product.objects.get.side_effect = mock_variant_product.DoesNotExist
        
        transformer = ProductStorageTransformer({})
        product = transformer._get_product("12345")
        
        # Verify None is returned and nothing is cached
        assert product is None
        assert "12345" not in transformer._product_cache
        
        # Verify all 4 lookups were attempted
        assert mock_variant_product.objects.get.call_count == 4

    @patch("pyerp.sync.transformers.product_storage.StorageLocation")
    def test_get_storage_location(self, mock_storage_location):
        """Test getting a storage location."""
        # Setup mock
        mock_location = MagicMock()
        mock_storage_location.objects.get.return_value = mock_location
        mock_storage_location.DoesNotExist = Exception
        
        transformer = ProductStorageTransformer({})
        location = transformer._get_storage_location("location-123")
        
        # Verify location is returned and cached
        assert location == mock_location
        assert transformer._storage_location_cache["location-123"] == mock_location
        mock_storage_location.objects.get.assert_called_once_with(uuid="location-123")

    @patch("pyerp.sync.transformers.product_storage.StorageLocation")
    def test_get_storage_location_not_found(self, mock_storage_location):
        """Test getting a storage location that doesn't exist."""
        # Setup mock
        mock_storage_location.DoesNotExist = Exception
        mock_storage_location.objects.get.side_effect = mock_storage_location.DoesNotExist
        
        transformer = ProductStorageTransformer({})
        location = transformer._get_storage_location("location-123")
        
        # Verify None is returned and nothing is cached
        assert location is None
        assert "location-123" not in transformer._storage_location_cache
        mock_storage_location.objects.get.assert_called_once_with(uuid="location-123")
      
    @patch("pyerp.sync.transformers.product_storage.BoxSlot")
    def test_get_box_slot_with_box_id_only(self, mock_box_slot):
        """Test getting a box slot with box_id only."""
        # Setup mock
        mock_slot = MagicMock()
        mock_box_slot.objects.get.return_value = mock_slot
        mock_box_slot.DoesNotExist = Exception
        
        transformer = ProductStorageTransformer({})
        slot = transformer._get_box_slot("box-123")
        
        # Verify slot is returned and cached
        assert slot == mock_slot
        assert transformer._box_slot_cache["box-123__None"] == mock_slot
        mock_box_slot.objects.get.assert_called_once_with(box__uuid="box-123", legacy_slot_id=None)

    def test_parse_quantity_valid(self):
        """Test parsing valid quantity values."""
        transformer = ProductStorageTransformer({})
        
        # Test valid formats
        assert transformer._parse_quantity("10") == 10
        assert transformer._parse_quantity("10.5") == 11  # Rounds up
        assert transformer._parse_quantity("-5") == 0  # Negative becomes 0
        assert transformer._parse_quantity(15) == 15  # Integer already
        assert transformer._parse_quantity(15.7) == 16  # Float rounds up
        
    def test_parse_quantity_invalid(self):
        """Test parsing invalid quantity values."""
        transformer = ProductStorageTransformer({})
        
        # Test invalid formats
        assert transformer._parse_quantity("") == 0
        assert transformer._parse_quantity(None) == 0
        assert transformer._parse_quantity("abc") == 0
        assert transformer._parse_quantity("10abc") == 0


@pytest.mark.unit
class TestBoxStorageTransformer:
    """Tests for the BoxStorageTransformer class."""

    def test_init(self):
        """Test initialization of BoxStorageTransformer."""
        transformer = BoxStorageTransformer({})
        
        # Verify product storage cache is initialized
        assert transformer._product_storage_cache == {}
        assert transformer._box_slot_cache == {}

    @patch("pyerp.sync.transformers.product_storage.ProductStorage")
    def test_get_product_storage(self, mock_product_storage):
        """Test getting a product storage."""
        # Setup mock
        mock_storage = MagicMock()
        mock_product_storage.objects.get.return_value = mock_storage
        mock_product_storage.DoesNotExist = Exception
        
        transformer = BoxStorageTransformer({})
        storage = transformer._get_product_storage("storage-123")
        
        # Verify storage is returned and cached
        assert storage == mock_storage
        assert transformer._product_storage_cache["storage-123"] == mock_storage
        mock_product_storage.objects.get.assert_called_once_with(uuid="storage-123")

    def test_extract_box_data(self):
        """Test extracting box data from input data."""
        transformer = BoxStorageTransformer({})
        
        input_data = {
            "Lagerort": "Warehouse A",
            "Artikel": "12345",
            "Bestand": "10",
            "LagerortId": "location-123",
            "SchuettenId": "box-123",
            "Fach": "slot-5",
            "MaxBestand": "15",
            "MinBestand": "5",
            "ArtikelId": "product-123",
        }
        
        result = transformer._extract_box_data(input_data)
        
        # Verify extracted data
        assert result["box_id"] == "box-123"
        assert result["slot_id"] == "slot-5"
        assert result["location_name"] == "Warehouse A"
        assert result["location_id"] == "location-123"
        assert result["product_id"] == "product-123"
        assert result["product_sku"] == "12345"
        assert result["quantity"] == "10"
        assert result["max_quantity"] == "15"
        assert result["min_quantity"] == "5"

    def test_parse_quantity(self):
        """Test parsing quantity values."""
        transformer = BoxStorageTransformer({})
        
        # Test various formats
        assert transformer._parse_quantity("10") == 10
        assert transformer._parse_quantity("10.5") == 11  # Rounds up
        assert transformer._parse_quantity("-5") == 0  # Negative becomes 0
        assert transformer._parse_quantity(15) == 15  # Integer already
        assert transformer._parse_quantity(15.7) == 16  # Float rounds up
        assert transformer._parse_quantity("") == 0
        assert transformer._parse_quantity(None) == 0
        assert transformer._parse_quantity("abc") == 0 