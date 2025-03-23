# Sync Tests Migration

## Overview

This document describes the migration of the sync module tests from their original location in `pyerp/sync/tests/` to the standardized location in `tests/backend/sync/`. The migration also includes converting the tests from unittest-style to pytest-style.

## Changes Made

1. **Standardized Test Location**
   - Moved tests from `pyerp/sync/tests/` to `tests/backend/sync/`
   - This aligns with the project's standard of having all tests in the `tests/` directory

2. **Converted to pytest Format**
   - Replaced unittest-based tests with pytest-style tests
   - Converted `TestCase` classes to module-level test functions
   - Replaced `setUp` methods with pytest fixtures
   - Converted assertions to pytest-style assertions

3. **CI/CD Integration**
   - Ensured sync tests are included in the "backend" test group in the CI/CD pipeline
   - Tests now run automatically on pushes to the `prod` and `dev` branches and on pull requests

4. **Added Helper Scripts**
   - Created `scripts/migrate_sync_tests.py` to help migrate the remaining tests
   - Created `scripts/run_sync_tests.sh` to run the sync tests specifically

## Benefits

1. **Consistency**: All tests now follow the same structure and style
2. **Maintainability**: Tests are easier to understand and maintain
3. **Discoverability**: Tests are now in a standard location, making them easier to find
4. **CI/CD Integration**: Tests are automatically run as part of the CI/CD pipeline

## Running Sync Tests

To run the sync tests specifically, use:

```bash
./run_all_tests.sh --type sync
```

This will run only the synchronization-related tests.

## Future Work

1. **Complete Migration**: Use the migration script to convert the remaining sync tests
2. **Update Documentation**: Update any documentation that references the old test location
3. **Remove Old Tests**: Once all tests are migrated and verified, remove the old test files 