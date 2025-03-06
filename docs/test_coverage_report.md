# Test Coverage Report

**Date:** February 27, 2024
**Coverage:** 8% overall

## Overview

This report summarizes the current test coverage for the pyERP project. The coverage analysis was performed using pytest-cov and covers all Python modules in the `pyerp` package.

## Coverage Summary

| Module Type                  | Coverage % | Notes                                  |
|------------------------------|------------|----------------------------------------|
| Core modules                 | 8%         | Initial focus on validators            |
| Product modules              | 10%        | Models coverage is good, others limited|
| Legacy sync modules          | 0%         | Not yet covered                        |
| Settings/Config              | minimal    | Configuration files typically excluded |

## Well-Tested Components

The following components have reasonable test coverage:

- `pyerp.products.models` (97%)
- `pyerp.__init__` (100%)
- `pyerp.products.__init__` (100%)
- `pyerp.core.validators` (79%)
- `tests.unit.test_product_validation` (100%)

## Coverage Gaps

Major areas requiring improved test coverage:

1. Form validation classes
2. Views and API endpoints
3. Management commands
4. Signal handlers
5. Legacy sync modules

## Improvement Plan

We've developed a comprehensive test coverage improvement plan to address these gaps:

### Phase 1: Core Framework (Weeks 1-2)

| Task | Target Coverage | Files |
|------|----------------|-------|
| Complete validator tests | 95% | pyerp/core/validators.py |
| Add form validation tests | 80% | pyerp/core/forms.py |
| Add utility function tests | 80% | pyerp/core/utils.py |
| Add view and API tests | 80% | pyerp/core/views.py |

### Phase 2: Business Logic (Weeks 3-4)

| Task | Target Coverage | Files |
|------|----------------|-------|
| Product module tests | 80% | pyerp/products/*.py |
| Inventory logic tests | 70% | pyerp/inventory/*.py |
| Sales logic tests | 70% | pyerp/sales/*.py |

### Phase 3: Integration Points (Weeks 5-6)

| Task | Target Coverage | Files |
|------|----------------|-------|
| Legacy sync module tests | 60% | pyerp/legacy_sync/*.py |
| API endpoint tests | 80% | pyerp/*/api.py |
| Management command tests | 70% | pyerp/management/commands/*.py |

## Tools for Coverage Analysis

We've created several tools to facilitate this improvement initiative:

1. **find_low_coverage.py** - Script to identify modules with low coverage percentages
   ```bash
   python tests/find_low_coverage.py
   ```

2. **find_untested_modules.py** - Script to identify modules with no tests at all
   ```bash
   python tests/find_untested_modules.py
   ```

3. **test_template.py** - Templates and examples for writing different types of tests
   ```bash
   # Reference file at:
   tests/unit/test_template.py
   ```

## Coverage Goals

1. **Short-term Goal** (1 month)
   - Increase overall coverage to 30%
   - Focus on critical business logic

2. **Medium-term Goal** (3 months)
   - Increase overall coverage to 60%
   - Cover all public APIs and business logic

3. **Long-term Goal** (6 months)
   - Maintain coverage above 80%
   - Cover all code paths and edge cases

## Running Tests with Coverage

```bash
# Activate virtual environment
venv\Scripts\activate    # Windows
. venv/Scripts/activate  # Unix/Mac

# Run tests with coverage
python -m pytest tests/unit/test_simple.py tests/unit/test_product_command.py --cov=pyerp --cov-report=html

# Or use the custom test runner
python tests/run_tests.py tests/unit/test_core_views.py

# Open coverage report
# Navigate to htmlcov/index.html in your browser
```

## Recent Progress

| Date | Coverage % | New Test Files | Notes |
|------|------------|----------------|-------|
| 2024-02-27 | 8% | - | Initial measurement |
| 2024-02-27 | 8% | test_core_views.py | Added tests for core views |
| 2024-02-27 | 8% | test_product_validation.py | Added isolated product validation tests with 100% coverage |

## Notes on Test Strategy

1. **Targeted Testing**: Focus on business logic over framework code
2. **Mocking Approach**: Use our custom mock objects to avoid Django dependencies
3. **Test Structure**: Keep tests small, focused, and independent
4. **Documentation**: Document tested behaviors alongside the tests

## Future Improvements

1. Add CI/CD integration for automatic coverage reporting
2. Implement coverage badges in documentation
3. Set up pre-commit hooks to enforce minimum coverage
4. Create more comprehensive end-to-end tests

For complete details, refer to the [Test Coverage Improvement Plan](../docs/test_coverage_improvement_plan.md).
