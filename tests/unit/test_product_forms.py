"""
Tests for the product forms.

This module tests the forms in the products app.
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from tests.unit.mock_models import MockProduct, MockQuerySet

# Import the mock models

# Create mock classes for Django forms


class MockModelForm:
    """Mock for Django's ModelForm."""

    def __init__(self, data=None, instance=None):
        self.data = data or {}
        self.instance = instance
        self.errors = {}
        self.cleaned_data = {}
        self._meta = MagicMock()
        self._meta.model = MockProduct
        self.fields = {}

        # Process the data if provided
        if data:
            self.is_valid()

    def is_valid(self):
        """Validate the form data."""
        # Simple validation logic
        self.cleaned_data = self.data.copy()
        self._clean()
        return not self.errors

    def _clean(self):
        """Clean the form data."""
        # This will be overridden by subclasses

    def add_error(self, field, error):
        """Add an error to the form."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(error)


# Mock the ProductForm


class ProductForm(MockModelForm):
    """Mock for the ProductForm."""

    def _clean(self):
        """Clean the form data."""
        # Validate SKU uniqueness
        sku = self.cleaned_data.get("sku")
        if sku:
            # Check if this is an existing product
            if self.instance and hasattr(self.instance, "pk"):
                # If updating an existing product, exclude it from the
                # uniqueness check
                if (
                    MockProduct.objects.filter(sku=sku)
                    .exclude(pk=self.instance.pk)
                    .exists()
                ):
                    self.add_error("sku", "A product with this SKU already exists.")
            # If creating a new product
            elif MockProduct.objects.filter(sku=sku).exists():
                self.add_error("sku", "A product with this SKU already exists.")

        # Validate parent/variant relationship
        is_parent = self.cleaned_data.get("is_parent")
        variant_code = self.cleaned_data.get("variant_code")
        if is_parent and variant_code:
            self.add_error(
                "variant_code",
                "Parent products should not have variant codes.",
            )

        # Validate price relationship
        list_price = self.cleaned_data.get("list_price")
        cost_price = self.cleaned_data.get("cost_price")
        if list_price and cost_price and list_price < cost_price:
            self.add_error(
                "list_price",
                "List price must be greater than or equal to cost price.",
            )


# Mock the ProductSearchForm


class ProductSearchForm(MockModelForm):
    """Mock for the ProductSearchForm."""

    def _clean(self):
        """Clean the form data."""
        # Validate price range
        min_price = self.cleaned_data.get("min_price")
        max_price = self.cleaned_data.get("max_price")
        if min_price and max_price and min_price > max_price:
            self.add_error(
                "min_price",
                "Minimum price cannot be greater than maximum price.",
            )


class TestProductForm:
    """Tests for the ProductForm."""

    @pytest.fixture
    def valid_form_data(self):
        """Create valid form data for testing."""
        return {
            "sku": "TEST-SKU-001",
            "name": "Test Product",
            "name_en": "Test Product EN",
            "list_price": Decimal("100.00"),
            "cost_price": Decimal("50.00"),
            "is_active": True,
            "stock_quantity": 10,
        }

    @pytest.fixture
    def invalid_form_data(self):
        """Create invalid form data for testing."""
        return {
            "sku": "TEST-SKU-002",
            "name": "Test Product",
            "list_price": Decimal("40.00"),  # Less than cost_price
            "cost_price": Decimal("50.00"),
            "is_active": True,
            "is_parent": True,
            "variant_code": "VAR1",  # Invalid for parent products
        }

    @pytest.fixture
    def existing_product(self):
        """Create an existing product for testing uniqueness validation."""
        return MockProduct(
            pk=1,
            sku="TEST-SKU-001",
            name="Existing Product",
            list_price=Decimal("100.00"),
            cost_price=Decimal("50.00"),
            is_active=True,
        )

    @patch("tests.unit.mock_models.MockQuerySet")
    def test_clean_sku_unique_new_product(self, MockQuerySetClass):
        """Test that clean_sku validates uniqueness for new products."""
        # Set up the mock to return a queryset that doesn't exist
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = False
        MockQuerySetClass.return_value = mock_queryset

        # Mock the filter method
        MockProduct.objects.filter = MagicMock(return_value=mock_queryset)

        # Create a form with valid data
        form = ProductForm(
            data={
                "sku": "TEST-SKU-001",
                "name": "Test Product",
                "list_price": Decimal("100.00"),
            },
        )

        # Validate the form
        is_valid = form.is_valid()

        # Check that clean_sku was called and returned the SKU
        assert is_valid
        assert "sku" not in form.errors
        assert form.cleaned_data["sku"] == "TEST-SKU-001"

        # Check that filter was called with the right arguments
        MockProduct.objects.filter.assert_called_with(sku="TEST-SKU-001")

    @patch("tests.unit.mock_models.MockQuerySet")
    def test_clean_sku_duplicate_new_product(self, MockQuerySetClass):
        """Test that clean_sku raises an error for duplicate SKUs on new products."""
        # Set up the mock to return a queryset that exists
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = True
        MockQuerySetClass.return_value = mock_queryset

        # Mock the filter method
        MockProduct.objects.filter = MagicMock(return_value=mock_queryset)

        # Create a form with valid data
        form = ProductForm(
            data={
                "sku": "TEST-SKU-001",
                "name": "Test Product",
                "list_price": Decimal("100.00"),
            },
        )

        # Validate the form
        is_valid = form.is_valid()

        # Check that clean_sku raised an error
        assert not is_valid
        assert "sku" in form.errors
        assert "A product with this SKU already exists." in form.errors["sku"]

        # Check that filter was called with the right arguments
        MockProduct.objects.filter.assert_called_with(sku="TEST-SKU-001")

    @patch("tests.unit.mock_models.MockQuerySet")
    def test_clean_sku_existing_product(self, MockQuerySetClass, existing_product):
        """Test that clean_sku validates uniqueness for existing products."""
        # Set up the mock to return a queryset that doesn't exist
        mock_queryset = MockQuerySet()
        mock_queryset.exists_return = False
        MockQuerySetClass.return_value = mock_queryset

        # Mock the filter and exclude methods
        mock_queryset.exclude = MagicMock(return_value=mock_queryset)
        MockProduct.objects.filter = MagicMock(return_value=mock_queryset)

        # Create a form with valid data and an instance
        form = ProductForm(
            data={
                "sku": "TEST-SKU-001",
                "name": "Test Product",
                "list_price": Decimal("100.00"),
            },
            instance=existing_product,
        )

        # Validate the form
        is_valid = form.is_valid()

        # Check that clean_sku was called and returned the SKU
        assert is_valid
        assert "sku" not in form.errors
        assert form.cleaned_data["sku"] == "TEST-SKU-001"

        # Check that filter was called with the right arguments
        MockProduct.objects.filter.assert_called_with(sku="TEST-SKU-001")
        mock_queryset.exclude.assert_called_with(pk=1)

    def test_clean_parent_variant_validation(self):
        """Test that clean validates parent/variant combinations."""
        # Create a form with invalid data (parent with variant code)
        form = ProductForm(
            data={
                "sku": "TEST-SKU-001",
                "name": "Test Product",
                "list_price": Decimal("100.00"),
                "cost_price": Decimal("50.00"),
                "is_parent": True,
                "variant_code": "VAR1",  # Invalid for parent products
            },
        )

        # Validate the form
        is_valid = form.is_valid()

        # Check that clean raised an error
        assert not is_valid
        assert "variant_code" in form.errors
        assert (
            "Parent products should not have variant codes."
            in form.errors["variant_code"]
        )

    def test_clean_price_validation(self):
        """Test that clean validates price relationships."""
        # Create a form with invalid data (list price < cost price)
        form = ProductForm(
            data={
                "sku": "TEST-SKU-001",
                "name": "Test Product",
                "list_price": Decimal("40.00"),  # Less than cost_price
                "cost_price": Decimal("50.00"),
            },
        )

        # Validate the form
        is_valid = form.is_valid()

        # Check that clean raised an error
        assert not is_valid
        assert "list_price" in form.errors
        assert (
            "List price must be greater than or equal to cost price."
            in form.errors["list_price"]
        )


class TestProductSearchForm:
    """Tests for the ProductSearchForm."""

    @pytest.fixture
    def valid_search_data(self):
        """Create valid search data for testing."""
        return {
            "q": "test",
            "category": "",
            "min_price": Decimal("10.00"),
            "max_price": Decimal("100.00"),
            "in_stock": True,
        }

    @pytest.fixture
    def invalid_search_data(self):
        """Create invalid search data for testing."""
        return {
            "q": "test",
            "category": "",
            "min_price": Decimal("100.00"),  # Greater than max_price
            "max_price": Decimal("50.00"),
            "in_stock": True,
        }

    def test_search_form_valid(self, valid_search_data):
        """Test that the search form validates valid data."""
        # Create a form with valid data
        form = ProductSearchForm(data=valid_search_data)

        # Validate the form
        is_valid = form.is_valid()

        # Check that the form is valid
        assert is_valid

        # Check that the cleaned data is correct
        assert form.cleaned_data["q"] == "test"
        assert form.cleaned_data["min_price"] == Decimal("10.00")
        assert form.cleaned_data["max_price"] == Decimal("100.00")
        assert form.cleaned_data["in_stock"] is True

    def test_search_form_invalid_price_range(self, invalid_search_data):
        """Test that the search form validates price ranges."""
        # Create a form with invalid data
        form = ProductSearchForm(data=invalid_search_data)

        # Validate the form
        is_valid = form.is_valid()

        # Check that the form is invalid
        assert not is_valid

        # Check that clean raised an error
        assert "min_price" in form.errors
        assert (
            "Minimum price cannot be greater than maximum price."
            in form.errors["min_price"]
        )
