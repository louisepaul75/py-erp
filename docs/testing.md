# Testing Strategy

This document outlines the testing strategy for pyERP, including test types, mocking approaches, and instructions for running tests.

## Overview

The pyERP testing strategy emphasizes robust unit testing with proper isolation from Django's app registry, which can cause issues in larger Django projects. We use a combination of:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing component interactions
3. **Django-specific Tests**: Using Django's test client for views and middleware
4. **Property-based Tests**: Using Hypothesis to generate test cases
5. **Fuzzing Tests**: Testing with randomly generated inputs to find edge cases
6. **Mutation Tests**: Modifying code to verify test suite effectiveness

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

To run tests, use the main test runner script:

```bash
./run_all_tests.sh
```

You can specify which tests to run:

```bash
./run_all_tests.sh --type unit
./run_all_tests.sh --type backend
./run_all_tests.sh --type ui
```

### Usage

```bash
./run_all_tests.sh [options]
```

Options:
- `-t, --type TYPE` - Type of tests to run (all, unit, backend, ui, etc.)
- `-c, --coverage` - Generate coverage report (default)
- `-n, --no-coverage` - Disable coverage reporting
- `-m, --mutation` - Run mutation tests
- `-f, --fuzz` - Run fuzz tests
- `-v, --verbose` - Verbose output
- `-q, --quiet` - Quiet output

### Examples

Run unit tests with mutation testing:
```bash
./run_all_tests.sh --type unit --mutation
```

Run all tests with fuzzing and no coverage:
```bash
./run_all_tests.sh --type all --fuzz --no-coverage
```

Run backend tests with high verbosity:
```bash
./run_all_tests.sh --type backend --verbose
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

## Property-Based Testing with Hypothesis

Property-based testing allows for more thorough testing by generating many test cases. We use Hypothesis for Python property-based testing:

```python
# Example of a property-based test
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a

@given(st.decimals(min_value=0, max_value=1000))
def test_product_price_formatting(price):
    formatted = format_price(price)
    assert "$" in formatted
    assert isinstance(formatted, str)
```

To run property-based tests:
```bash
./scripts/run_tests.sh --fuzz
```

## Fuzz Testing

Fuzz testing helps discover edge cases and vulnerabilities by testing with random inputs. We use:

- **Hypothesis** for Python fuzz testing
- **Jest-Fuzz** for JavaScript/TypeScript fuzz testing

### JavaScript Fuzz Testing Example

```javascript
// Example of a Jest-Fuzz test
import { fuzz } from 'jest-fuzz';
import { formatCurrency } from '../../utils/formatters';

describe('Currency Formatter Fuzzing', () => {
  fuzz('Should handle any valid number', () => {
    fuzz.number({min: -10000, max: 10000}).forEach(value => {
      const result = formatCurrency(value);
      expect(typeof result).toBe('string');
      expect(result).toMatch(/^\$?-?[\d,]+(\.\d{2})?$/);
    });
  });
});
```

To run fuzz tests:
```bash
./scripts/run_tests.sh --fuzz
```

## Mutation Testing

Mutation testing evaluates the quality of your test suite by making small changes to your code (mutations) and checking if your tests catch these changes.

We use **mutmut** for mutation testing in Python code. Mutation testing helps identify:
- Areas of code not adequately covered by tests
- Tests that don't properly assert behavior
- Dead code that could be removed

To run mutation tests:
```bash
./scripts/run_tests.sh --mutation
```

For more details on mutation testing, see [mutation_testing.md](mutation_testing.md).

## Continuous Integration

For CI/CD, we recommend:

1. Running the basic test suite to verify environment setup
2. Running specific tests relevant to modified code
3. Generating coverage reports to track testing completeness
4. Running mutation tests periodically to evaluate test quality
5. Including fuzz testing to catch edge cases before they reach production

## Current Testing Status

As of the latest assessment (March 2023), our test suite has the following characteristics:

### Test Coverage

- **Overall Coverage**: 44.17% (lines)
- **Frontend Coverage Highlights**:
  - Core auth components: ~100% coverage
  - UI utility components: 75-100% coverage
  - Business logic components (e.g., dashboard.tsx): < 5% coverage
- **Backend Coverage Highlights**:
  - Core business modules: 80-90% coverage
  - API endpoint tests: ~70% coverage 
  - Utilities and helpers: 75-95% coverage

### Current Issues

1. **React Component Testing**:
   - Multiple React components have state updates not wrapped in `act()` causing warnings
   - Footer component and auth hooks particularly affected by async state update warnings
   - Network requests in component tests aren't properly mocked

2. **Database Configuration**:
   - Tests attempt to connect to PostgreSQL at 192.168.73.65 but fall back to SQLite
   - Inconsistent database behavior between development and CI environments
   - Missing database password in environment variables

3. **Fuzz/Property Testing**:
   - Limited application to utility functions
   - Not yet integrated with core business logic
   - Missing strategies for complex business entities

4. **Mutation Testing**:
   - Configuration issues when connecting to database
   - Slow execution on large components
   - Not yet integrated into CI pipeline

## Roadmap for Testing Improvements

### Short-term Improvements (Next 1-2 Months)

1. **Fix React Testing Issues**
   - [ ] Implement proper React Testing Library patterns with `waitFor` and `act()`
   - [ ] Create testing utilities for mocking API calls consistently
   - [ ] Example pattern for Footer component:
     ```tsx
     test('Footer renders correctly', async () => {
       // Mock fetch before rendering
       jest.spyOn(global, 'fetch').mockImplementation(() => 
         Promise.resolve({
           ok: true,
           json: () => Promise.resolve({ status: 'healthy' })
         })
       );
       
       await act(async () => {
         render(<Footer />);
       });
       
       await waitFor(() => {
         expect(screen.getByText('Status: healthy')).toBeInTheDocument();
       });
     });
     ```

2. **Improve Database Testing Configuration**
   - [ ] Create dedicated SQLite test database configuration
   - [ ] Add database fixtures for common test scenarios
   - [ ] Document database setup requirements in README.md
   - [ ] Fix environment variable handling for test databases

3. **Extend Coverage for Critical Components**
   - [ ] Identify and prioritize top 5 business-critical components with low coverage
   - [ ] Create tests for dashboard.tsx components (currently at 2.64%)
   - [ ] Add tests for article-page.tsx and other key UI pages

### Medium-term Improvements (3-6 Months)

1. **Expand Property-based and Fuzz Testing**
   - [ ] Apply property testing to all numeric calculations
   - [ ] Create Hypothesis strategies for business entities (Products, Orders, etc.)
   - [ ] Add fuzz testing for all data processing and formatting functions
   - [ ] Document patterns for effective property-based test design

2. **Improve Mutation Testing Setup**
   - [ ] Configure mutation testing to use SQLite for reliability
   - [ ] Create focused mutation test targets for critical modules
   - [ ] Automate mutation testing in weekly CI builds
   - [ ] Establish minimum mutation score threshold for key modules

3. **Testing Documentation and Training**
   - [ ] Create testing cheat sheets for common patterns
   - [ ] Hold workshop on effective test design
   - [ ] Establish code review criteria for test quality
   - [ ] Create testing patterns library for team reference

### Long-term Goals (6+ Months)

1. **Comprehensive Test Coverage**
   - [ ] Achieve 80%+ coverage for all business-critical components
   - [ ] Implement end-to-end testing with Playwright or Cypress
   - [ ] Automate visual regression testing
   - [ ] Implement accessibility testing

2. **Advanced Testing Techniques**
   - [ ] Explore chaos testing for infrastructure resilience
   - [ ] Implement contract testing between services
   - [ ] Explore AI-assisted test generation
   - [ ] Performance testing benchmarks for critical operations

3. **Testing Culture**
   - [ ] Move toward test-driven development (TDD) for new features
   - [ ] Implement testing champions program
   - [ ] Regular testing metrics in team reviews
   - [ ] Recognition for high-quality test contributions

## Best Practices for Effective Tests

1. **Isolation**: Keep tests isolated, avoid unnecessary database access
2. **Use Mock Objects**: Prefer mock objects over real Django models
3. **Small, Focused Tests**: Write small, targeted tests that verify specific behavior
4. **Test Real Business Logic**: Focus on testing actual business logic, not framework features
5. **Consistent Naming**: Follow the pattern `test_<what_being_tested>_<expected_behavior>`
6. **Setup Fixtures**: Use pytest fixtures to set up test dependencies
7. **React Component Testing**:
   - Wrap async operations in `act()`
   - Use `waitFor` for UI changes
   - Mock API calls consistently
   - Test user interactions, not implementation details
8. **React Hook Testing**:
   - Use `renderHook` from @testing-library/react-hooks
   - Mock external dependencies
   - Test all state transitions

## Automated Testing in CI/CD

Our CI/CD pipeline includes the following testing steps:

1. **Pull Request Checks**:
   - Linting and type checking
   - Unit tests for affected modules
   - Coverage threshold check

2. **Merge to Development Branch**:
   - Full test suite run
   - Integration tests
   - Performance regression tests

3. **Weekly Testing**:
   - Mutation testing
   - Full fuzz testing suite
   - Dependency vulnerability scanning

4. **Production Deployment**:
   - End-to-end smoke tests
   - Canary testing with real traffic
   - Performance benchmarking

By consistently implementing these improvements, we aim to increase the robustness and reliability of the pyERP system while making it easier for developers to write and maintain effective tests.
