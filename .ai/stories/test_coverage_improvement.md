# Test Coverage Improvement Initiative

## Context & Background

As part of our commitment to code quality and stability, we're implementing a structured test coverage improvement initiative for the pyERP project. Currently, the overall test coverage stands at 8%, with only the core validators module having reasonable coverage (approximately 79%). This low coverage increases the risk of bugs, regression issues, and makes future development more challenging.

## Objectives

1. **Short-term Goal (1 month)**: Increase overall coverage to 30%, focusing on core modules
2. **Medium-term Goal (3 months)**: Increase overall coverage to 60%, covering all public APIs
3. **Long-term Goal (6 months)**: Maintain coverage above 80% across all modules

## Implementation Strategy

We've designed a phased approach to systematically improve test coverage:

### Phase 1: Core Framework (Weeks 1-2)

- **Focus Areas**:
  - Core validators
  - Form validation
  - Core utilities
  - Views and API endpoints

- **Target Components**:
  - `pyerp/core/validators.py` (target: 95% coverage)
  - `pyerp/core/views.py` (target: 80% coverage)
  - `pyerp/core/form_validation.py` (target: 80% coverage)

- **Implementation Approach**:
  - Complete tests for validator classes
  - Test edge cases and validation logic
  - Implement view tests with mock requests
  - Test form validation with valid/invalid data scenarios

### Phase 2: Business Logic (Weeks 3-4)

- **Focus Areas**:
  - Product module business logic
  - Inventory logic
  - Sales logic

- **Target Components**:
  - `pyerp/products/*.py` (target: 80% coverage)
  - `pyerp/inventory/*.py` (target: 70% coverage)
  - `pyerp/sales/*.py` (target: 70% coverage)

- **Implementation Approach**:
  - Test model methods and business rules
  - Test product workflows (creation, updates)
  - Test pricing and availability logic
  - Test inventory operations and stock management

### Phase 3: Integration Points (Weeks 5-6)

- **Focus Areas**:
  - Legacy sync modules
  - API endpoints
  - Management commands

- **Target Components**:
  - `pyerp/legacy_sync/*.py` (target: 60% coverage)
  - `pyerp/*/api.py` (target: 80% coverage)
  - `pyerp/management/commands/*.py` (target: 70% coverage)

- **Implementation Approach**:
  - Test data import/export functionality
  - Test API authentication and responses
  - Test command execution and parameter handling
  - Implement integration tests for key workflows

## Tools & Resources

We've developed several tools to support this initiative:

1. **find_low_coverage.py**: Analyzes coverage data to identify modules with low coverage
   - Sorts modules by coverage percentage
   - Groups results by directory for targeted improvements
   - Reports detailed coverage statistics for planning

2. **find_untested_modules.py**: Identifies modules with no tests at all
   - Categorizes untested modules by type
   - Prioritizes modules based on business importance
   - Provides a clear starting point for test creation

3. **test_template.py**: Example test implementations for different component types
   - Model test examples
   - Form validation test examples
   - View test examples
   - API test examples
   - Management command test examples

4. **run_specific_tests.py**: Custom testing script to avoid Django app registry issues
   - Sets Django environment
   - Allows running specific test modules
   - Tracks test results and generates coverage reports

## Best Practices

Throughout this initiative, we'll follow these testing best practices:

1. **Mocking Strategy**:
   - Mock database access for unit tests
   - Create consistent fixtures for test data
   - Mock external API services

2. **Test Organization**:
   - Place unit tests in `tests/unit/`
   - Place integration tests in `tests/integration/`
   - Name test files `test_<module_name>.py`
   - Name test methods `test_<behavior_being_tested>`

3. **Test Structure**:
   - Focus on small, specific test cases
   - Use descriptive docstrings
   - Group related tests into classes
   - Use pytest fixtures for setup/teardown

## Progress Tracking

We'll track progress using the following methods:

1. **Weekly Coverage Reports**:
   - Generate weekly coverage reports
   - Compare against targets
   - Identify gaps and adjust priorities

2. **Visual Dashboard**:
   - Create visual representation of coverage progress
   - Track coverage by module/component
   - Show trend over time

3. **Code Review Integration**:
   - Include coverage metrics in code reviews
   - Require tests for new features
   - Prevent coverage decreases

## Current Status

- Created test coverage improvement plan document
- Developed coverage analysis tools
- Created test template examples
- Implemented initial tests for core views
- ✅ **Completed tests for DirectAPIClient**: Fixed and improved test cases for the DirectAPIClient class with 19 passing tests
- **Next Steps**: Implement Phase 1 testing for core validators and forms

## Implementation Example: Direct API Client

We've successfully implemented comprehensive tests for `pyerp/direct_api/client.py`. These tests demonstrate:

1. Testing of client initialization with different parameters
2. Validation of URL building methods
3. Mocking of session management and requests
4. Testing of request handling including authentication, errors, and retries
5. Testing of data processing with pagination and error handling
6. Coverage of all key methods in the DirectAPIClient class

Key achievements:
- 19 passing test methods covering various aspects of the DirectAPIClient
- Fixed issues with tests reflecting the actual behavior of the implementation
- Proper mocking of external dependencies for reliable unit testing
- Test cases for both success and error scenarios ensuring robustness

This implementation serves as a model for testing other client classes and API integrations throughout the codebase.

## Progress Updates

### March 2024 Update: Product Validators Testing Improvements

#### Achievements

We have successfully improved test coverage for the `products/validators.py` module:

- **Coverage Increase**: Increased test coverage of `pyerp/products/validators.py` from 9% to 59%
- **New Test Cases**: Added comprehensive test cases for the `validate_product_model` function, covering:
  - Validation of valid product models
  - Detection of invalid SKUs
  - Validation of parent-variant relationships
  - Validation of price relationships (list price vs cost price)
  - Setting base_sku from variant SKUs

#### Technical Challenges Overcome

We encountered and solved several challenging testing issues:

1. **Circular Import Challenges**: The Product class was imported under `TYPE_CHECKING`, making standard mocking approaches ineffective
2. **Gettext Patching Issues**: We had to develop a specialized approach for patching Django's translation functions
3. **Validator Function Patching**: Created a robust approach to replace the validator function during tests while preserving its original behavior

#### Implementation Approach

The solution involved:

1. Creating a custom `setup_method` and `teardown_method` in the test class
2. Storing and later restoring the original function
3. Explicitly importing required dependencies in the patched function
4. Creating comprehensive test cases for all code paths

#### Next Steps

- Apply similar techniques to increase coverage of other validator functions
- Address remaining uncovered code in the products module
- Document the approach for other team members to use in similar testing scenarios

## Conclusion

By following this structured approach to test coverage improvement, we'll systematically reduce risk, improve code quality, and build a more maintainable codebase. The phased implementation ensures we prioritize the most critical components first while making steady progress toward our overall coverage goals.
