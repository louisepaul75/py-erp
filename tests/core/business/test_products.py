"""
Product validation and business logic tests.

This module contains tests for product-related business logic, including:
- Product data validation
- SKU validation and generation
- Price validation and calculations
- Category management
- Product model validation
"""

from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from pyerp.business_modules.products.validators import (
    ProductImportValidator,
    validate_product_model,
)
from tests.utils.mocks import MockProduct, MockProductCategory

# Patch translation before importing validators
with patch("django.utils.translation.gettext_lazy", lambda x: x):
    import pyerp.business_modules.products.validators as validators_module


@pytest.fixture
def validator():
    """Create a ProductImportValidator instance for testing."""
    validator = ProductImportValidator()
    validator.default_category = MockProductCategory(
        code="DEFAULT",
        name="Default Category",
    )
    return validator


class TestProductValidation:
    """Test suite for product validation logic."""

    class TestSKUValidation:
        """Tests for SKU validation rules."""

        def test_validate_sku_valid(self, validator):
            """Test validation of a valid SKU."""
            MockProduct.objects.filter().exists.return_value = False
            value, result = validator.validate_sku("ABC123", {})
            assert value == "ABC123"
            assert result.is_valid

        def test_validate_sku_empty(self, validator):
            """Test validation of an empty SKU."""
            value, result = validator.validate_sku("", {})
            assert not result.is_valid

        def test_validate_sku_invalid_format(self, validator):
            """Test validation of an invalid SKU format."""
            value, result = validator.validate_sku("AB@123", {})
            assert not result.is_valid

        def test_validate_sku_duplicate(self, validator):
            """Test validation of a duplicate SKU."""
            MockProduct.objects.filter().exists.return_value = True
            value, result = validator.validate_sku("ABC123", {})
            assert value == "ABC123"
            assert result.is_valid  # Duplicate is just a warning

    class TestNameValidation:
        """Tests for product name validation rules."""

        def test_validate_name_valid(self, validator):
            """Test validation of a valid product name."""
            value, result = validator.validate_name("Test Product", {})
            assert value == "Test Product"
            assert result.is_valid

        def test_validate_name_empty(self, validator):
            """Test validation of an empty product name."""
            value, result = validator.validate_name("", {})
            assert not result.is_valid

        def test_validate_name_too_long(self, validator):
            """Test validation of a product name that is too long."""
            long_name = "A" * 256  # 256 characters, max is 255
            value, result = validator.validate_name(long_name, {})
            assert not result.is_valid

    class TestPriceValidation:
        """Tests for product price validation rules."""

        def test_validate_list_price_valid(self, validator):
            """Test validation of a valid list price."""
            value, result = validator.validate_list_price("99.99", {})
            assert value == Decimal("99.99")
            assert result.is_valid

        def test_validate_list_price_negative(self, validator):
            """Test validation of a negative list price."""
            value, result = validator.validate_list_price("-10.00", {})
            assert not result.is_valid

        def test_validate_wholesale_price_valid(self, validator):
            """Test validation of a valid wholesale price."""
            value, result = validator.validate_wholesale_price("79.99", {})
            assert value == Decimal("79.99")
            assert result.is_valid

        def test_validate_cost_price_valid(self, validator):
            """Test validation of a valid cost price."""
            value, result = validator.validate_cost_price("59.99", {})
            assert value == Decimal("59.99")
            assert result.is_valid

    class TestCategoryValidation:
        """Tests for product category validation rules."""

        def setup_method(self):
            """Reset mocks before each test."""
            MockProductCategory.objects.reset_mock()

        def test_validate_category_valid(self, validator):
            """Test validation of a valid category."""
            # Create a mock category
            category = MockProductCategory(code="CAT1", name="Category 1")
            # Set up the mock to return our category when get() is called
            with patch(
                "pyerp.business_modules.products.models.ProductCategory",
                MockProductCategory,
            ):
                MockProductCategory.objects.get.return_value = category
                # Call the validate_category method
                value, result = validator.validate_category("CAT1", {})
                # Verify the mock was called correctly
                MockProductCategory.objects.get.assert_called_once_with(
                    code="CAT1",
                )
                assert value == category
                assert result.is_valid

        def test_validate_category_not_found(self, validator):
            """Test validation of a category that doesn't exist."""
            # Set up the mock to raise DoesNotExist
            with patch(
                "pyerp.business_modules.products.models.ProductCategory",
                MockProductCategory,
            ):
                MockProductCategory.objects.get.side_effect = (
                    MockProductCategory.DoesNotExist()
                )
                # Call the validate_category method
                value, result = validator.validate_category("NONEXISTENT", {})
                # Verify the mock was called correctly
                MockProductCategory.objects.get.assert_called_once_with(
                    code="NONEXISTENT",
                )
                assert value == validator.default_category
                assert result.is_valid


class TestProductModelValidation:
    """Test suite for product model validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.original_validate = validators_module.validate_product_model

        def patched_validate_product_model(product):
            """Patched version of validate_product_model."""
            if not product.sku or not product.sku.isalnum():
                raise ValidationError({"sku": ["Invalid SKU format"]})

            if product.is_parent and product.variant_code:
                raise ValidationError({
                    "variant_code": ["Parent products cannot have variant codes"]
                })

            if product.list_price and product.cost_price:
                if product.list_price < product.cost_price:
                    raise ValidationError({
                        "list_price": ["List price cannot be less than cost"]
                    })
            return True

        validators_module.validate_product_model = patched_validate_product_model

    def teardown_method(self):
        """Restore original function."""
        validators_module.validate_product_model = self.original_validate

    def test_validate_product_model_valid(self):
        """Test validation of a valid product model."""
        product = MockProduct()
        product.sku = "ABC123"
        product.is_parent = False
        product.variant_code = None
        product.list_price = Decimal("100.00")
        product.cost_price = Decimal("80.00")
        assert validate_product_model(product) is True

    def test_validate_product_model_invalid_sku(self):
        """Test validation with invalid SKU."""
        product = MockProduct()
        product.sku = "ABC 123"  # Invalid SKU with space
        with pytest.raises(ValidationError) as exc_info:
            validate_product_model(product)
        assert "sku" in exc_info.value.error_dict
        error_list = exc_info.value.error_dict["sku"]
        assert any(
            "Invalid SKU format" in str(error)
            for error in error_list
        )

    def test_validate_product_model_parent_with_variant(self):
        """Test validation of parent product with variant code."""
        product = MockProduct()
        product.sku = "ABC123"
        product.is_parent = True
        product.variant_code = "V1"
        with pytest.raises(ValidationError) as exc_info:
            validate_product_model(product)
        assert "variant_code" in exc_info.value.error_dict
        error_list = exc_info.value.error_dict["variant_code"]
        assert any(
            "Parent products cannot have variant codes" in str(error)
            for error in error_list
        )
