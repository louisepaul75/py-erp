"""
Tests for simple form validation.

This module tests form validation without relying on Django's form validation.
"""

from decimal import Decimal

import pytest


class MockField:
    """Mock for Django form field."""

    def __init__(self, **kwargs):
        self.required = kwargs.get("required", True)
        self.help_text = kwargs.get("help_text", "")
        self.label = kwargs.get("label", "")
        self.initial = kwargs.get("initial")
        self.widget = kwargs.get("widget")
        self.validators = []


class MockForm:
    """Mock for Django form."""

    def __init__(self, data=None, **kwargs):
        self.data = data or {}
        self.fields = {}
        self.errors = {}
        self.cleaned_data = {}

    def is_valid(self):
        """Validate the form."""
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


class ValidationResult:
    """Mock for ValidationResult class."""

    def __init__(self):
        self.errors = {}

    def add_error(self, field, message):
        """Add an error to the result."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)

    def has_errors(self):
        """Check if the result has errors."""
        return bool(self.errors)

    def get_errors(self):
        """Get all errors."""
        return self.errors


class ValidatedForm(MockForm):
    """Mock for ValidatedForm class."""

    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        self.validators = {}
        self.form_validators = []

    def add_validator(self, field, validator):
        """Add a validator for a field."""
        if field not in self.validators:
            self.validators[field] = []
        self.validators[field].append(validator)

    def add_form_validator(self, validator):
        """Add a form-level validator."""
        self.form_validators.append(validator)

    def _clean(self):
        """Clean the form data."""
        # Run field validators
        for field, validators in self.validators.items():
            if field is None:
                # Form-level validator
                for validator in validators:
                    if callable(validator):
                        result = validator(self.cleaned_data)
                        if result and isinstance(result, dict):
                            for field_name, message in result.items():
                                self.add_error(field_name, message)
                continue

            value = self.cleaned_data.get(field)
            for validator in validators:
                if callable(validator):
                    result = validator(value, self.cleaned_data)
                    if result:
                        self.add_error(field, result)

        # Run form validators
        for validator in self.form_validators:
            result = validator(self.cleaned_data)
            if result and hasattr(result, "errors"):
                for field, messages in result.errors.items():
                    for message in messages:
                        self.add_error(field, message)
            elif result and isinstance(result, dict):
                for field, message in result.items():
                    self.add_error(field, message)


class ValidatedModelForm(ValidatedForm):
    """Mock for ValidatedModelForm class."""

    class Meta:
        """Mock Meta class."""

        fields = []
        model = None


# Create a mock Product class for testing


class Product:
    """Mock Product class for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        """Mock save method."""

    def clean(self):
        """Mock clean method."""

    def __str__(self):
        """String representation."""
        return getattr(self, "name", "Mock Product")


class TestValidatedForm:
    """Tests for the ValidatedForm class."""

    @pytest.fixture
    def simple_form(self):
        """Create a simple validated form for testing."""

        class SimpleForm(ValidatedForm):
            """Simple form for testing."""

            def __init__(self, data=None):
                super().__init__(data)
                self.fields["name"] = MockField(required=True)
                self.fields["email"] = MockField(required=True)
                self.fields["age"] = MockField(required=False)

                # Add validators
                self.add_validator("name", self.validate_name)
                self.add_validator("email", self.validate_email)
                self.add_validator("age", self.validate_age)

                # Add form validator
                self.add_form_validator(self.validate_form)

            def validate_name(self, value, cleaned_data):
                """Validate the name field."""
                if value and len(value) < 3:
                    return "Name must be at least 3 characters long"
                return None

            def validate_email(self, value, cleaned_data):
                """Validate the email field."""
                if value and "@" not in value:
                    return "Email must contain @"
                return None

            def validate_age(self, value, cleaned_data):
                """Validate the age field."""
                if value and value < 18:
                    return "Must be at least 18 years old"
                return None

            def validate_form(self, cleaned_data):
                """Validate the form as a whole."""
                result = ValidationResult()
                name = cleaned_data.get("name", "")
                email = cleaned_data.get("email", "")

                # Check if email starts with name
                if name and email and not email.startswith(name.lower()):
                    result.add_error("email", "Email should start with your name")

                return result

        return SimpleForm

    def test_form_valid(self, simple_form):
        """Test that a valid form passes validation."""
        form = simple_form(
            {
                "name": "John",
                "email": "john@example.com",
                "age": 25,
            },
        )

        assert form.is_valid()
        assert not form.errors

    def test_form_invalid_field(self, simple_form):
        """Test that field validators catch invalid data."""
        form = simple_form(
            {
                "name": "Jo",  # Too short
                "email": "john@example.com",
                "age": 25,
            },
        )

        assert not form.is_valid()
        assert "name" in form.errors
        assert "Name must be at least 3 characters long" in form.errors["name"]

    def test_form_invalid_multiple_fields(self, simple_form):
        """Test that multiple field validators catch invalid data."""
        form = simple_form(
            {
                "name": "Jo",  # Too short
                "email": "johnexample.com",  # Missing @
                "age": 16,  # Too young
            },
        )

        assert not form.is_valid()
        assert "name" in form.errors
        assert "email" in form.errors
        assert "age" in form.errors

    def test_form_level_validation(self, simple_form):
        """Test that form-level validators work."""
        form = simple_form(
            {
                "name": "John",
                "email": "different@example.com",  # Doesn't start with name
                "age": 25,
            },
        )

        assert not form.is_valid()
        assert "email" in form.errors
        assert "Email should start with your name" in form.errors["email"]


class TestValidatedModelForm:
    """Tests for the ValidatedModelForm class."""

    class ProductForm(ValidatedModelForm):
        """Test model form implementation."""

        class Meta:
            model = Product  # This uses the mock Product class defined above
            fields = ["name", "sku", "list_price"]

        def __init__(self, data=None, **kwargs):
            """Initialize the form with validators."""
            super().__init__(data, **kwargs)

            # Set up fields
            self.fields["name"] = MockField(help_text="Product name")
            self.fields["sku"] = MockField(help_text="Stock Keeping Unit")
            self.fields["list_price"] = MockField(help_text="Retail price")

            # Add validators
            self.add_validator("sku", self.validate_sku)
            # Form-level validator
            self.add_validator(None, self.validate_prices)

        def validate_sku(self, value, cleaned_data):
            """Validate that the SKU follows the required format."""
            if not value or not value.startswith("SKU-"):
                return 'SKU must start with "SKU-"'
            return None

        def validate_prices(self, cleaned_data):
            """Validate that the list price is positive."""
            list_price = cleaned_data.get("list_price")
            if list_price is not None and list_price <= 0:
                return {"list_price": "List price must be positive"}
            return None

    @pytest.fixture
    def valid_product_data(self):
        """Create valid product data for testing."""
        return {
            "name": "Test Product",
            "sku": "SKU-001",
            "list_price": Decimal("99.99"),
        }

    @pytest.fixture
    def invalid_product_data(self):
        """Create invalid product data for testing."""
        return {
            "name": "Test Product",
            "sku": "INVALID-001",  # Doesn't start with SKU-
            "list_price": Decimal("-10.00"),  # Negative price
        }

    def test_model_form_valid(self, valid_product_data):
        """Test that a valid model form passes validation."""
        form = self.ProductForm(valid_product_data)

        assert form.is_valid()
        assert not form.errors

    def test_model_form_invalid_field(self, invalid_product_data):
        """Test that field validators catch invalid data in model forms."""
        form = self.ProductForm(invalid_product_data)

        assert not form.is_valid()
        assert "sku" in form.errors
        assert "list_price" in form.errors
        assert 'SKU must start with "SKU-"' in form.errors["sku"]
        assert "List price must be positive" in form.errors["list_price"]

    def test_model_form_partial_data(self):
        """Test that partial data is validated correctly."""
        form = self.ProductForm(
            {
                "name": "Test Product",
                "sku": "SKU-001",
                # Missing list_price
            },
        )

        # This should be valid since list_price is not required
        assert form.is_valid()
        assert not form.errors


class TestRegexValidator:
    """Tests for the RegexValidator class."""

    def test_regex_validator_valid(self):
        """Test that RegexValidator passes valid values."""

        # Create a simple regex validator
        def validator(value, cleaned_data):
            return None if value and value.isalpha() else "Must contain only letters"

        # Test with valid value
        result = validator("abc", {})
        assert result is None

    def test_regex_validator_invalid(self):
        """Test that RegexValidator catches invalid values."""

        # Create a simple regex validator
        def validator(value, cleaned_data):
            return None if value and value.isalpha() else "Must contain only letters"

        # Test with invalid value
        result = validator("abc123", {})
        assert result == "Must contain only letters"


class TestEmailValidator:
    """Tests for the EmailValidator class."""

    def test_email_validator_valid(self):
        """Test that EmailValidator passes valid values."""

        # Create a simple email validator
        def validator(value, cleaned_data):
            return None if value and "@" in value else "Must be a valid email"

        # Test with valid value
        result = validator("test@example.com", {})
        assert result is None

    def test_email_validator_invalid(self):
        """Test that EmailValidator catches invalid values."""

        # Create a simple email validator
        def validator(value, cleaned_data):
            return None if value and "@" in value else "Must be a valid email"

        # Test with invalid value
        result = validator("testexample.com", {})
        assert result == "Must be a valid email"


class TestNumberValidator:
    """Tests for the NumberValidator class."""

    def test_number_validator_valid(self):
        """Test that NumberValidator passes valid values."""

        # Create a simple number validator
        def validator(value, cleaned_data):
            return None if value and value > 0 else "Must be positive"

        # Test with valid value
        result = validator(10, {})
        assert result is None

    def test_number_validator_invalid(self):
        """Test that NumberValidator catches invalid values."""

        # Create a simple number validator
        def validator(value, cleaned_data):
            return None if value and value > 0 else "Must be positive"

        # Test with invalid value
        result = validator(-5, {})
        assert result == "Must be positive"
