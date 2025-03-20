# PyERP Test Migration Plan

## Overview
This document outlines the plan to migrate tests from the centralized `tests/` directory to co-located test directories within each Django app/module, following Django's best practices.

## Benefits
- **Django Best Practice**: Aligns with Django's recommended approach
- **Better Discoverability**: Developers can find tests alongside the code they're working on
- **Easier Maintenance**: When refactoring code, related tests are right there
- **Modularity**: Each business module owns its tests
- **Prevents Namespace Collisions**: Avoids import conflicts

## Migration Steps

### 1. Preparation Phase
- [ ] Create a `tests` directory in each app/module if it doesn't exist
- [ ] Copy `conftest.py` to project root for global fixtures
- [ ] Update `pytest.ini` to recognize new test locations
- [ ] Create app-specific `conftest.py` files for local fixtures

### 2. Migration Phase
- [ ] For each module:
  - [ ] Create matching subdirectories in module's `tests/` dir (if needed)
  - [ ] Move test files to appropriate locations
  - [ ] Update imports in test files
  - [ ] Run tests to verify functionality
  - [ ] Move fixtures to app-level conftest.py

### 3. Configuration Update Phase
- [ ] Update CI/CD pipeline configurations
- [ ] Update test running scripts
- [ ] Update coverage report configuration

### 4. Cleanup Phase
- [ ] Remove central test directory (after ensuring all tests pass)
- [ ] Document the new test structure
- [ ] Update developer documentation

## New Directory Structure

For each app module (e.g., `pyerp/core/`), the structure will be:

```
pyerp/core/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── ...
└── tests/
    ├── __init__.py
    ├── conftest.py           # Module-specific fixtures
    ├── test_models.py
    ├── test_serializers.py
    ├── test_views.py
    └── ...
```

## Migration Script
A migration script (`migrate_tests.py`) will be created to automate the migration process for each module.

## Test Discovery
Test discovery will continue to work with pytest since we'll configure it to look for tests in all directories.

## Implementation Timeline
1. Create the migration script (1 day)
2. Migrate one module as a pilot (1 day)
3. Review and adjust approach based on pilot (1 day)
4. Complete migration for all modules (3-5 days)
5. Update CI/CD and verify all tests pass (1-2 days)
6. Final cleanup and documentation (1 day)

Total estimated time: 7-11 days 