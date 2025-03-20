# PyERP Test Migration Summary

## Migration Status

The initial test migration has been completed, with tests moved from the central `tests/` directory to co-located test directories within each module. However, several issues were discovered during test execution that need to be addressed.

## Issues Found

### 1. Database Schema Issues

The most critical issue is with the `dimensions` field in product models:

```
django.db.utils.IntegrityError: NOT NULL constraint failed: products_product.dimensions
django.db.utils.IntegrityError: NOT NULL constraint failed: products_parentproduct.dimensions
```

These errors occur because the field was removed from the model but still exists in the database schema with a NOT NULL constraint.

### 2. Import Path Issues

Many import issues were detected due to the change in module structure:

```
AssertionError: <class 'pyerp.sync.tests.test_pipeline_factory.MockExtractor'> != <class 'test_pipeline_factory.MockExtractor'>
```

The migrated tests are still trying to import from the old locations.

### 3. Mock Object Issues

Several mocking-related issues were found:

```
AttributeError: Mock object has no attribute '_state'
TypeError: TestBaseTransformer.test_apply_custom_transformers.<locals>.uppercase_name() missing 1 required positional argument: '_'
```

### 4. Parameter Issues

Several tests have parameter mismatches:

```
TypeError: LoadResult.__init__() got an unexpected keyword argument 'created'
TypeError: TestSyncPipeline.test_run_updates_sync_state_on_failure() missing 1 required positional argument: 'mock_sync_state_class'
```

## Next Steps

### 1. Fix Database Schema Issues

Create a migration to properly handle the dimensions field:

```bash
python manage.py makemigrations products --empty
```

Then edit the generated migration file to:
- Add the dimensions field if it doesn't exist in the model but exists in the database
- Or make the NOT NULL constraint optional
- Or provide a default value

### 2. Fix Import Paths

For each failed test, update imports to use the correct module paths:

- From: `from tests.unit.module import X`
- To: `from pyerp.module.tests import X`

In some cases, you may need to move mock classes and helper functions to appropriate locations.

### 3. Fix Mock Objects

- Update the mock creation to include required attributes like `_state`
- Fix test functions that require additional parameters

### 4. Update Test Parameters

- Check constructor signatures and update parameter names
- Add missing parameters to function calls

### 5. Test Each Module Individually

Run tests for one module at a time to isolate and fix issues:

```bash
python -m pytest pyerp/core/tests/
```

### 6. Complete the Migration

After all tests are passing, you can:

1. Update CI/CD configurations to run tests from the new locations only
2. Remove the old test directory
3. Update documentation

## Temporary Testing Configuration

During the migration period, keep testing both locations to ensure nothing is missed:

```python
# In pytest.ini
testpaths = . pyerp tests
```

## Future Improvements

After migration is complete, consider:

1. Refactoring common test fixtures to reduce duplication
2. Adding more specific markers for easier test filtering
3. Improving test coverage by module
4. Creating a test documentation guide for each module 