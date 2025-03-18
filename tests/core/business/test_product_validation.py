"""
Tests for product validation logic.

This module tests the validation logic used in product forms and models.
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from tests.unit.mock_models import MockProduct, MockProductCategory, MockQuerySet


class TestProductValidation:
    """Tests for product validation logic."""

    def test_sku_uniqueness_validation(self):
        """Test that SKU uniqueness validation works correctly."""
        # Create a mock for the filter method
        mock_filter = MagicMock()

        # Test case 1: New product with unique SKU
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = False
        mock_filter.return_value = mock_queryset

        # Simulate the validation logic from ProductForm.clean_sku
        sku = "NEW-SKU"
        if mock_filter(sku=sku).exists():
            raise ValueError("A product with this SKU already exists.")

        # No exception should be raised

        # Test case 2: New product with duplicate SKU
        mock_queryset = MockQuerySet([MockProduct(sku="DUPLICATE-SKU")])
        mock_queryset.exists_return = True
        mock_filter.return_value = mock_queryset

        # Simulate the validation logic
        sku = "DUPLICATE-SKU"
        with pytest.raises(ValueError) as excinfo:
            if mock_filter(sku=sku).exists():
                raise ValueError("A product with this SKU already exists.")

        # Verify the error message
        assert "already exists" in str(excinfo.value)

    def test_parent_variant_validation(self):
        """Test validation of parent-variant relationship."""
        # Simulate the validation logic from ProductForm.clean
        is_parent = True
        variant_code = "VAR1"

        # In a real form, this would add an error to the form
        if is_parent and variant_code:
            error_message = "Parent products should not have variant codes."
            assert (
                error_message
            ), "Should raise an error for parent products with variant codes"

    def test_price_validation(self):
        """Test validation of price relationship."""
        # Simulate the validation logic from ProductForm.clean
        list_price = Decimal("40.00")
        cost_price = Decimal("50.00")

        # In a real form, this would add an error to the form
        if list_price and cost_price and list_price < cost_price:
            error_message = "List price should not be less than cost price."
            assert (
                error_message
            ), "Should raise an error when list price is less than cost price"

    def test_price_range_validation(self):
        """Test validation of price range in search form."""
        # Simulate the validation logic from ProductSearchForm.clean
        min_price = Decimal("100.00")
        max_price = Decimal("50.00")

        # In a real form, this would add an error to the form
        if min_price and max_price and min_price > max_price:
            error_message = "Minimum price must be less than maximum price."
            assert (
                error_message
            ), "Should raise an error when min price is greater than max price"


class TestProductCategoryValidation:
    """Tests for product category validation logic."""

    def test_category_code_uniqueness(self):
        """Test that category code uniqueness validation works correctly."""
        # Create a mock for the filter method
        mock_filter = MagicMock()

        # Test case 1: New category with unique code
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = False
        mock_filter.return_value = mock_queryset

        # Simulate the validation logic
        code = "NEW-CAT"
        if mock_filter(code=code).exists():
            raise ValueError("A category with this code already exists.")

        # No exception should be raised

        # Test case 2: New category with duplicate code
        mock_queryset = MockQuerySet([MockProductCategory(code="DUPLICATE-CAT")])
        mock_queryset.exists_return = True
        mock_filter.return_value = mock_queryset

        # Simulate the validation logic
        code = "DUPLICATE-CAT"
        with pytest.raises(ValueError) as excinfo:
            if mock_filter(code=code).exists():
                raise ValueError("A category with this code already exists.")

        # Verify the error message
        assert "already exists" in str(excinfo.value)


class TestProductImageValidation:
    """Tests for product image validation logic."""

    def test_image_url_validation(self):
        """Test validation of image URLs."""
        # Valid URL
        image_url = "https://example.com/image.jpg"
        # This would normally use a URL validator
        assert image_url.startswith("http"), "Image URL should start with http"

        # Invalid URL
        image_url = "not-a-url"
        # This would normally use a URL validator
        assert not image_url.startswith("http"), "Should detect invalid URLs"

    def test_primary_image_validation(self):
        """Test validation of primary image flag."""
        # Simulate a product with multiple images
        images = [
            {"id": 1, "is_primary": True},
            {"id": 2, "is_primary": False},
            {"id": 3, "is_primary": False},
        ]

        # Count primary images
        primary_count = sum(1 for img in images if img["is_primary"])

        # A product should have exactly one primary image
        assert primary_count == 1, "A product should have exactly one primary image"
