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

### Individual Tests

We've created utilities to run specific tests in isolation:

```bash
# Run all simple tests to verify test environment
python run_specific_tests.py
```

This script uses subprocess to run pytest on specific test modules, avoiding collection of problematic tests.

### Test Scripts

- `run_specific_tests.py`: Runs selected test modules individually
- `run_working_tests.py`: Runs confirmed working tests through Django's test runner

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

# View the report
# Open htmlcov/index.html in a browser
```

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