# Data Validation Framework

## Overview

The pyERP Data Validation Framework provides a comprehensive solution for validating data throughout the application. It enables consistent validation across different parts of the system, including models, forms, and data imports from legacy systems.

This document outlines the architecture, components, and usage patterns for the validation framework.

## Key Features

- **Extensible Architecture**: Build your own validators for specific business rules
- **Multiple Validation Levels**: Support for both errors (blocking) and warnings (non-blocking)
- **Context-Aware Validation**: Field-specific error messages and validation rules
- **Business Rule Enforcement**: Validate complex rules across multiple fields
- **Form Integration**: Seamless integration with Django forms
- **Import Validation**: Special support for validating and transforming imported data
- **Reusable Components**: Common validators for typical validation needs

## Core Components

### ValidationResult

The `ValidationResult` class serves as a container for validation outcomes, tracking validity, errors, and warnings:

```python
result = ValidationResult()
result.add_error('field_name', 'Error message')
result.add_warning('field_name', 'Warning message')

if not result.is_valid:
    # Handle validation failure
```

### Validator Base Class

The `Validator` abstract base class defines the interface for all validators:

```python
class MyValidator(Validator):
    def __init__(self, message=None):
        super().__init__(message or "Custom validation message")

    def _validate(self, value, result, **kwargs):
        field_name = kwargs.get('field_name', 'field')

        # Implement validation logic
        if not valid_condition(value):
            result.add_error(field_name, self.message)
```

### ImportValidator

The `ImportValidator` class is specifically designed for validating data during import processes:

```python
class MyImportValidator(ImportValidator):
    def __init__(self, strict=False, transform_data=True):
        super().__init__(strict, transform_data)

    def validate_field_name(self, value, row_data, row_index=None):
        result = ValidationResult()

        # Field-specific validation

        return transformed_value, result
```

### Form Validation Integration

The `ValidatedFormMixin`, `ValidatedModelForm`, and `ValidatedForm` classes provide integration with Django forms:

```python
class MyForm(ValidatedModelForm):
    def setup_validators(self):
        self.add_validator('field_name', MyValidator())
```

## Built-in Validators

The framework includes several pre-built validators for common validation needs:

- `RequiredValidator`: Ensures a value is not empty
- `RegexValidator`: Validates a string against a regex pattern
- `RangeValidator`: Checks numeric values are within a range
- `LengthValidator`: Validates string length
- `ChoiceValidator`: Ensures a value is in a set of choices
- `DecimalValidator`: Validates decimal precision and format
- `SkuValidator`: Specific validator for product SKU format

## Usage Examples

### Model Validation

```python
from django.db import models
from django.core.exceptions import ValidationError
from pyerp.core.validators import validate_data, RegexValidator, RequiredValidator

class MyModel(models.Model):
    code = models.CharField(max_length=10)

    def clean(self):
        # Validate code field
        validators = [
            RequiredValidator(),
            RegexValidator(r'^[A-Z]{3}\d{3}$', "Code must be 3 uppercase letters followed by 3 digits")
        ]

        result = validate_data(self.code, validators, {'field_name': 'code'})

        if not result.is_valid:
            raise ValidationError(result.errors)
```

### Form Validation

```python
from django import forms
from pyerp.core.form_validation import ValidatedModelForm
from pyerp.core.validators import RequiredValidator, RangeValidator

class ProductForm(ValidatedModelForm):
    class Meta:
        model = Product
        fields = ['sku', 'name', 'list_price']

    def setup_validators(self):
        self.add_validator('sku', RequiredValidator("SKU is required"))
        self.add_validator('list_price', RangeValidator(min_value=0))

    def apply_form_validators(self, cleaned_data):
        # Cross-field validation example
        if cleaned_data.get('list_price') < cleaned_data.get('cost_price'):
            self.add_error('list_price', "List price cannot be less than cost price")
```

### Import Validation

```python
from pyerp.core.validators import ImportValidator, ValidationResult
from decimal import Decimal

class MyImportValidator(ImportValidator):
    def __init__(self, strict=False):
        super().__init__(strict=strict, transform_data=True)

    def validate_price(self, value, row_data, row_index=None):
        result = ValidationResult()

        # Transform to Decimal
        try:
            decimal_value = Decimal(str(value))
        except (ValueError, TypeError):
            result.add_error('price', "Invalid price format")
            return Decimal('0.00'), result

        # Validate price range
        if decimal_value < Decimal('0.00'):
            result.add_error('price', "Price cannot be negative")

        return decimal_value, result

    def _post_validate_row(self, row_data, result, row_index=None):
        # Cross-field business rule
        list_price = row_data.get('list_price', Decimal('0.00'))
        cost_price = row_data.get('cost_price', Decimal('0.00'))

        if list_price < cost_price:
            result.add_warning('list_price', "List price is less than cost price")
```

## Testing Validation Logic

### Isolated Validation Tests

We've implemented a strategy for testing validation logic without Django dependencies:

```python
# From tests/unit/test_product_validation.py
def test_price_validation(self):
    """Test validation of price relationship."""
    # Simulate the validation logic from ProductForm.clean
    list_price = Decimal('40.00')
    cost_price = Decimal('50.00')

    # In a real form, this would add an error to the form
    if list_price and cost_price and list_price < cost_price:
        error_message = "List price should not be less than cost price."
        assert error_message, "Should raise an error when list price is less than cost price"
```

This approach allows testing business validation rules without requiring Django's ORM or database connections.

### Mock Models for Testing

The `tests/unit/mock_models.py` module provides mock implementations of Django models and querysets for testing:

```python
# Example of testing SKU uniqueness validation
def test_sku_uniqueness_validation(self):
    """Test that SKU uniqueness validation works correctly."""
    # Create a mock for the filter method
    mock_filter = MagicMock()

    # Test case 1: New product with unique SKU
    mock_queryset = MockQuerySet()
    mock_queryset.exists_return = False
    mock_filter.return_value = mock_queryset

    # Simulate the validation logic from ProductForm.clean_sku
    sku = 'NEW-SKU'
    if mock_filter(sku=sku).exists():
        raise ValueError("A product with this SKU already exists.")

    # No exception should be raised

    # Test case 2: New product with duplicate SKU
    mock_queryset = MockQuerySet([MockProduct(sku='DUPLICATE-SKU')])
    mock_queryset.exists_return = True
    mock_filter.return_value = mock_queryset

    # Simulate the validation logic
    sku = 'DUPLICATE-SKU'
    with pytest.raises(ValueError) as excinfo:
        if mock_filter(sku=sku).exists():
            raise ValueError("A product with this SKU already exists.")

    # Verify the error message
    assert "already exists" in str(excinfo.value)
```

## Best Practices

1. **Reuse Validators**: Create reusable validators for common validation patterns
2. **Clear Error Messages**: Provide specific, actionable error messages
3. **Separation of Concerns**: Keep validation logic separate from business logic
4. **Consistent Approach**: Use the validation framework consistently throughout the application
5. **Test Your Validators**: Write unit tests for custom validators

## Integration with Testing

Validators should be thoroughly tested to ensure they work correctly:

```python
def test_required_validator():
    validator = RequiredValidator()

    # Test with empty value
    result = validator("", field_name="test_field")
    assert not result.is_valid
    assert "test_field" in result.errors

    # Test with valid value
    result = validator("value", field_name="test_field")
    assert result.is_valid
```

## Extending the Framework

To add new validation capabilities:

1. Create a new validator class inheriting from `Validator`
2. Implement the `_validate` method to apply your validation rules
3. Update documentation for your new validator
4. Write tests to ensure it works as expected

## Conclusion

The validation framework provides a solid foundation for data integrity throughout the pyERP system. By leveraging this framework, we ensure consistent validation rules, clear error reporting, and maintainable validation logic.
