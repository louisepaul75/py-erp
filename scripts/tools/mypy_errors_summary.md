# Mypy Errors Summary and Fix Plan

## Progress Made

We've successfully addressed the initial import-related errors by:

1. Installing type stubs for third-party libraries:
   - types-polib
   - pandas-stubs
   - types-stdlib-list
   - types-redis
   - types-requests
   - types-PyYAML
   - types-python-dateutil
   - types-pytz
   - django-stubs
   - djangorestframework-stubs
   - celery-types
   - types-boto3

2. Configuring mypy to ignore missing imports for specific modules in `mypy.ini`

3. Adding proper package structure to the tests directory to fix the duplicate module issue

## Remaining Errors

The remaining errors fall into these categories:

### 1. Missing Type Annotations (most common)

Many model fields are missing type annotations. For example:
```python
# Current code
name = models.CharField(max_length=255)

# Should be
name: models.CharField = models.CharField(max_length=255)
```

### 2. Module Attribute Errors

Several files reference `Product` from `pyerp.products.models`, but this attribute doesn't exist. It might have been renamed to `BaseProduct`.

### 3. Type Incompatibilities

There are various type incompatibility issues, such as:
- Assigning strings to integer fields
- Incompatible default values for function arguments
- Incompatible return types

### 4. Missing wsz_api Module

The `wsz_api` module is referenced but not found. This appears to be a custom module used for integration with a legacy system.

## Fix Plan

### Short-term Fixes

1. **Create a stub package for wsz_api**:
   - Create a minimal package with the required modules and type hints

2. **Fix the most critical type errors**:
   - Focus on the core modules first
   - Address incompatible types in assignments and function returns

### Medium-term Fixes

1. **Add type annotations to model fields**:
   - Start with the most frequently used models
   - Use a consistent approach across all models

2. **Fix module attribute errors**:
   - Update references to `Product` to use the correct class name

### Long-term Improvements

1. **Comprehensive type annotations**:
   - Add proper type annotations to all functions and methods
   - Use generic types where appropriate

2. **Stricter mypy configuration**:
   - Gradually increase the strictness of mypy checks
   - Aim for full type coverage

## Next Steps

1. Create a stub package for wsz_api
2. Fix the Product/BaseProduct references
3. Add type annotations to the most critical models
4. Address the type incompatibility issues in the direct_api module
