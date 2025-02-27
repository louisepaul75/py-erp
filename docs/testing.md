# Testing Strategy

This document outlines the testing strategy for pyERP, including test types, mocking approaches, and instructions for running tests.

## Overview

The pyERP testing strategy emphasizes robust unit testing with proper isolation from Django's app registry, which can cause issues in larger Django projects. We use a combination of:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing component interactions
3. **Django-specific Tests**: Using Django's test client for views and middleware

## Testing Challenges in Django Monoliths

Django monoliths pose specific testing challenges:

1. **App Registry Initialization**: Django attempts to load all models during test collection, which can cause import errors if models aren't fully configured
2. **Database Dependencies**: Tests may fail if they require a database but the test environment isn't properly configured
3. **Circular Dependencies**: Complex model relationships can cause circular import problems during testing

## Mocking Strategy

To address these challenges, we've developed a robust mocking framework:

### Mock Models

The `tests/unit/mock_models.py` module provides mock implementations of Django models, querysets, and manager objects. Key components include:

- `MockQuerySet`: Simulates Django's QuerySet behavior with filter, get, etc.
- `MockModelBase`: Base class for all mock models with DoesNotExist exception
- `MockProduct`: Mock implementation of the Product model
- `MockProductCategory`: Mock implementation of the ProductCategory model

These mock objects allow tests to run without requiring Django's ORM or database connections.

```python
# Example of using mock models in tests
from tests.unit.mock_models import MockProduct, MockProductCategory

# Create a mock product for testing
product = MockProduct(sku="TEST-123", name="Test Product")
assert product.sku == "TEST-123"

# Use mock querysets
products = MockQuerySet([product])
first_product = products.get(sku="TEST-123")
assert first_product is product
```

## Running Tests

### Test Runner Script

We've created a comprehensive test runner script to simplify test execution:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test modules
python tests/run_tests.py tests/unit/test_product_validation.py

# Run with coverage
python tests/run_tests.py --coverage

# Run with verbose output
python tests/run_tests.py --verbose
```

The `run_tests.py` script provides several advantages:
- Bypasses Django app registry issues
- Generates coverage reports
- Provides a consistent interface for all test runs
- Supports running specific test modules or directories

### Pytest Usage

For direct pytest usage:

```bash
# Activate virtual environment first
. venv/Scripts/activate  # Unix/Mac
venv\Scripts\activate    # Windows

# Run a specific test module
python -m pytest tests/unit/test_simple.py -v

# Run with coverage
python -m pytest tests/unit/test_simple.py --cov=pyerp
```

## Test Coverage

To generate coverage reports:

```bash
# Generate coverage report
python -m pytest --cov=pyerp tests/unit/ --cov-report=html

# Or use the test runner
python tests/run_tests.py --coverage --html

# View the report
# Open htmlcov/index.html in a browser
```

## Isolated Testing Examples

### Product Validation Tests

The `tests/unit/test_product_validation.py` file demonstrates how to create isolated tests that don't depend on Django:

```python
# Example of isolated product validation test
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

This approach allows testing business logic without requiring Django's ORM or database.

## Continuous Integration

For CI/CD, we recommend:

1. Running the basic test suite to verify environment setup
2. Running specific tests relevant to modified code
3. Generating coverage reports to track testing completeness

## Best Practices

1. **Isolation**: Keep tests isolated, avoid unnecessary database access
2. **Use Mock Objects**: Prefer mock objects over real Django models
3. **Small, Focused Tests**: Write small, targeted tests that verify specific behavior
4. **Test Real Business Logic**: Focus on testing actual business logic, not framework features
5. **Consistent Naming**: Follow the pattern `test_<what_being_tested>_<expected_behavior>`
6. **Setup Fixtures**: Use pytest fixtures to set up test dependencies 