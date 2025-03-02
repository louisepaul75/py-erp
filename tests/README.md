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

## Advanced Testing Techniques

### Testing Components with Circular Imports

When testing modules that use TYPE_CHECKING imports or have circular dependencies, standard mocking approaches may not work. Here's a pattern that has proven effective:

```python
class TestCircularImportComponent:
    def setup_method(self):
        """Set up before each test."""
        # Import the component to test
        from myapp.module import target_function
        
        # Store the original function for restoration
        self.original_function = target_function
        
        # Define a patched version that avoids circular imports
        def patched_function(arg1, arg2):
            # Re-import any needed dependencies
            from myapp.other_module import Helper
            
            # Implement the same logic, but in a way that's testable
            # ...
            return result
                
        # Replace the function with our patched version
        import myapp.module
        myapp.module.target_function = patched_function
    
    def teardown_method(self):
        """Clean up after each test."""
        # Restore the original function
        import myapp.module
        myapp.module.target_function = self.original_function
        
    def test_function(self):
        """Test the function."""
        from myapp.module import target_function
        result = target_function(arg1, arg2)
        assert result == expected_result
```

See the `tests/unit/test_product_validators_extended.py` file for a real-world example of this technique applied to testing the `validate_product_model` function.

### Testing Django Translation-Enabled Code

Testing code that uses Django's translation functions (gettext, gettext_lazy) can be challenging. Two effective approaches are:

1. **Direct Function Patching** (preferred):
```python
def setup_method(self):
    # Define a mock implementation
    def mock_gettext(text):
        return text
        
    # Patch at the module level
    import myapp.module
    self.original_gettext = myapp.module._  # Store original
    myapp.module._ = mock_gettext  # Replace
    
def teardown_method(self):
    # Restore original
    import myapp.module
    myapp.module._ = self.original_gettext
```

2. **Using unittest.mock.patch**:
```python
@patch('django.utils.translation.gettext_lazy', lambda x: x)
def test_translated_message(self):
    # Test code that uses gettext_lazy
    pass
```

Both techniques are demonstrated in the validator tests in the pyERP codebase. 