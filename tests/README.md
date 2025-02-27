# pyERP Testing Framework

This directory contains the testing infrastructure for the pyERP project. We use pytest as our primary testing framework, along with several custom tools to facilitate testing in Django's environment.

## Directory Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for multiple components
- `tests/e2e/` - End-to-end tests for entire workflows
- `conftest.py` - Pytest configuration and shared fixtures
- `run_tests.py` - Main test runner script
- `find_low_coverage.py` - Tool to identify modules with low test coverage
- `find_untested_modules.py` - Tool to identify modules with no tests

## Running Tests

Due to Django's app registry constraints, we have a custom test runner script:

```bash
# Run known working tests (default)
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py --verbose

# Run with coverage reporting
python tests/run_tests.py --coverage

# Run a specific test file
python tests/run_tests.py tests/unit/test_simple.py

# Run multiple test files
python tests/run_tests.py tests/unit/test_simple.py tests/unit/test_product_command.py

# Attempt to run all tests (may fail due to Django app registry issues)
python tests/run_tests.py --all
```

Alternatively, you can use pytest directly, but you may encounter app registry issues:

```bash
# Basic test execution
python -m pytest tests/unit/test_simple.py

# With coverage
python -m pytest tests/unit/test_simple.py --cov=pyerp --cov-report=html
```

## Coverage Analysis

We have two tools to help analyze test coverage:

### 1. Find Low Coverage Modules

This script identifies modules with the lowest test coverage:

```bash
python tests/find_low_coverage.py
```

The output includes:
- A list of modules sorted by coverage percentage
- Coverage statistics grouped by directory
- Detailed information about executed statements vs. total statements

### 2. Find Untested Modules

This script identifies modules with no tests at all:

```bash
python tests/find_untested_modules.py
```

The output includes:
- A list of all modules without corresponding test files
- Modules grouped by directory
- Modules categorized by type (views, models, etc.)
- Suggested testing priorities based on business importance

## Test Templates

To help write new tests, we've created a test template with examples for various component types:

```bash
tests/unit/test_template.py
```

This file includes examples for:
- Model tests
- Form validation tests
- View tests
- API tests
- Utility function tests
- Management command tests

## Testing Best Practices

1. **Test Organization**
   - Name test files `test_<module_name>.py`
   - Name test classes `Test<ClassBeingTested>`
   - Name test methods `test_<behavior_being_tested>`

2. **Test Structure**
   - Keep tests small and focused
   - Use descriptive docstrings
   - Group related tests into classes
   - Use pytest fixtures for setup/teardown

3. **Test Isolation**
   - Tests should be independent from each other
   - Use mocks to avoid external dependencies
   - Clean up after your tests

4. **Mocking Strategy**
   - Django ORM is mocked to avoid database dependencies
   - Use MagicMock for external services
   - For views, use APIRequestFactory from rest_framework.test

## Test Coverage Goals

Our test coverage improvement plan includes these targets:

1. **Short-term Goal (1 month)**
   - Increase overall coverage to 30%
   - Focus on core modules and critical business logic

2. **Medium-term Goal (3 months)**
   - Increase overall coverage to 60%
   - Cover all public APIs and business logic

3. **Long-term Goal (6 months)**
   - Maintain coverage above 80%
   - Cover all code paths and edge cases

For full details on our test coverage improvement plan, refer to:
- `docs/test_coverage_improvement_plan.md`
- `.ai/stories/test_coverage_improvement.md` 