"""
Tests for form validation.

This module tests the form validation functionality.
"""

from django.core.exceptions import ValidationError

from pyerp.core.form_validation import ValidatedForm, ValidationResult


class MockField:
    """Mock for Django form field."""

    def __init__(self, **kwargs):
        self.required = kwargs.get("required", True)
        self.help_text = kwargs.get("help_text", "")
        self.label = kwargs.get("label", "")
        self.initial = kwargs.get("initial")
        self.widget = kwargs.get("widget")
        self.validators = []
        self.error_messages = kwargs.get("error_messages", {})
        self.disabled = kwargs.get("disabled", False)

    def get_bound_field(self, form, field_name):
        """Mock implementation of get_bound_field."""
        return MockBoundField(form, self, field_name)

    def clean(self, value):
        """Mock implementation of clean."""
        if self.required and not value:
            raise ValidationError("This field is required.")
        return value

    def _clean_bound_field(self, bound_field):
        """Mock implementation of _clean_bound_field."""
        value = bound_field.form.data.get(bound_field.name)
        return self.clean(value)


class MockBoundField:
    """Mock for Django BoundField."""

    def __init__(self, form, field, name):
        self.form = form
        self.field = field
        self.name = name
        self.html_name = name
        self.html_initial_name = f"initial-{name}"
        self.html_initial_id = f"initial_id_{name}"
        self.label = field.label or name.title()
        self.help_text = field.help_text or ""
        self.data = form.data.get(name) if form.data else None
        self.initial = field.initial


class MockModelForm(ValidatedForm):
    """Mock for Django ModelForm."""

    class Meta:
        """Meta class for the form."""

        model = None
        fields = []

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        self.instance = kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)


# Create a mock Product class for testing


class Product:
    """Mock Product class for testing."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = kwargs.get("id")

    def save(self):
        """Mock save method."""
        if not self.id:
            self.id = 1  # Simulate saving to database
        return self

    def clean(self):
        """Mock clean method."""

    def __str__(self):
        """String representation."""
        return getattr(self, "name", "Mock Product")


class TestValidatedForm:
    """Tests for the ValidatedForm class."""

    def setup_method(self):
        """Set up test cases."""

        class TestForm(ValidatedForm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields = {"field": MockField()}

        self.form_class = TestForm

    def test_add_validator(self):
        """Test adding a validator to a form."""
        form = self.form_class()

        def validator(x, field_name=None):
            return None

        form.add_validator("field", validator)

        assert "field" in form.validators
        assert validator in form.validators["field"]

    def test_add_form_validator(self):
        """Test adding a form-level validator."""
        form = self.form_class()

        def validator(x):
            return None

        form.add_form_validator(validator)

        assert validator in form.form_validators

    def test_is_valid_no_validators(self):
        """Test is_valid with no validators."""
        form = self.form_class({"field": "value"})
        assert form.is_valid()
        assert form.cleaned_data == {"field": "value"}

    def test_is_valid_with_field_validator_passing(self):
        """Test is_valid with a passing field validator."""
        form = self.form_class({"field": "value"})
        form.add_validator("field", lambda x, field_name=None: None)

        assert form.is_valid()
        assert not form.errors

    def test_is_valid_with_field_validator_failing(self):
        """Test is_valid with a failing field validator."""
        form = self.form_class({"field": "value"})

        def failing_validator(value, field_name=None):
            result = ValidationResult()
            result.add_error(field_name or "field", "Error message")
            return result

        form.add_validator("field", failing_validator)

        assert not form.is_valid()
        assert "field" in form.errors
        assert "Error message" in form.errors["field"]

    def test_is_valid_with_form_validator_passing(self):
        """Test is_valid with a passing form validator."""
        form = self.form_class({"field": "value"})
        form.add_form_validator(lambda x: None)

        assert form.is_valid()
        assert not form.errors

    def test_is_valid_with_form_validator_failing_dict(self):
        """Test is_valid with a failing form validator returning a dict."""
        form = self.form_class({"field": "value"})
        form.add_form_validator(lambda x: {"field": ["Error message"]})

        assert not form.is_valid()
        assert "field" in form.errors
        assert "Error message" in form.errors["field"]

    def test_is_valid_with_form_validator_failing_validation_result(self):
        """Test is_valid with failing form validator returning ValidationResult."""
        form = self.form_class({"field": "value"})

        def validator(cleaned_data):
            result = ValidationResult()
            result.add_error("field", "Error message")
            return result

        form.add_form_validator(validator)

        assert not form.is_valid()
        assert "field" in form.errors
        assert "Error message" in form.errors["field"]


class TestValidatedModelForm:
    """Tests for the ValidatedModelForm class."""

    class ProductForm(ValidatedForm):
        """Test model form implementation."""

        def __init__(self, data=None, instance=None, **kwargs):
            """Initialize the form with validators."""
            self.instance = instance
            super().__init__(data, **kwargs)

            # Set up fields
            self.fields = {
                "name": MockField(help_text="Product name"),
                "sku": MockField(help_text="Stock Keeping Unit"),
                "list_price": MockField(help_text="Retail price", required=False),
            }

            # Add validators
            self.add_validator("sku", self.validate_sku)
            self.add_validator("list_price", self.validate_list_price)

        def validate_sku(self, value, field_name=None):
            """Validate that the SKU follows the required format."""
            result = ValidationResult()
            if not value or not value.startswith("SKU-"):
                result.add_error(
                    field_name or "sku",
                    'SKU must start with "SKU-"',
                )
            return result

        def validate_list_price(self, value, field_name=None):
            """Validate that the list price is positive."""
            result = ValidationResult()
            if value is not None:
                try:
                    price = float(value)
                    if price <= 0:
                        result.add_error(
                            field_name or "list_price",
                            "List price must be positive",
                        )
                except (TypeError, ValueError):
                    result.add_error(
                        field_name or "list_price",
                        "Invalid price format",
                    )
            return result

    def test_model_form_init_with_instance(self):
        """Test initializing a model form with an instance."""
        instance = {
            "name": "Test Product",
            "sku": "SKU-001",
            "list_price": "99.99",
        }
        form = self.ProductForm(instance=instance)
        assert form.instance == instance

    def test_model_form_valid(self):
        """Test that a valid model form passes validation."""
        form = self.ProductForm(
            {
                "name": "Test Product",
                "sku": "SKU-001",
                "list_price": "99.99",
            },
        )

        assert form.is_valid()
        assert not form.errors

    def test_model_form_invalid_field(self):
        """Test that field validators catch invalid data in model forms."""
        form = self.ProductForm(
            {
                "name": "Test Product",
                "sku": "INVALID-001",  # Doesn't start with SKU-
                "list_price": "-10.00",  # Negative price
            },
        )

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
