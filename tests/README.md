# pyERP Test Suite

This directory contains the test suite for the pyERP system. The tests are organized into logical categories to improve maintainability and clarity.

## Test Structure

```
tests/
├── ui/                 # User Interface Tests
│   ├── test_forms.py   # Form rendering and validation
│   ├── test_templates.py # Template rendering
│   └── test_views.py   # View rendering and interaction
│
├── backend/           # Backend Service Tests
│   ├── test_celery.py    # Async task processing
│   ├── test_middleware.py # Middleware functionality
│   └── test_services.py  # Service layer
│
├── database/         # Database Tests
│   ├── test_migrations.py # Migration testing
│   ├── test_models.py    # Model definitions and methods
│   └── test_queries.py   # Complex query operations
│
├── api/              # API Tests
│   ├── test_direct_api/  # Direct API integration
│   ├── test_rest_api.py  # REST API endpoints
│   └── test_wsgi.py     # WSGI interface
│
└── core/             # Core Business Logic Tests
    ├── business/
    │   ├── test_products.py    # Product management
    │   ├── test_inventory.py   # Inventory control
    │   └── test_production.py  # Production processes
    ├── test_validators.py      # Data validation
    ├── test_utils.py          # Utility functions
    └── test_config.py         # System configuration
```

## Running Tests

### Running All Tests
```bash
python tests/run_tests.py
```

### Running Tests by Category
```bash
# UI Tests
python tests/run_tests.py tests/ui/

# Backend Tests
python tests/run_tests.py tests/backend/

# Database Tests
python tests/run_tests.py tests/database/

# API Tests
python tests/run_tests.py tests/api/

# Core Tests
python tests/run_tests.py tests/core/
```

### Running Specific Test Files
```bash
# Run specific test file
python tests/run_tests.py tests/ui/test_forms.py

# Run with coverage
python tests/run_tests.py --coverage tests/ui/test_forms.py
```

## Test Categories

### UI Tests
- Form rendering and validation
- Template rendering
- View functionality and interaction
- Frontend component integration

### Backend Tests
- Asynchronous task processing
- Middleware functionality
- Service layer operations
- Background job processing

### Database Tests
- Model definitions and relationships
- Migration testing
- Complex query operations
- Data integrity checks

### API Tests
- Direct API integration
- REST API endpoints
- Authentication and authorization
- Rate limiting and throttling
- API versioning

### Core Tests
- Business logic validation
- Product management
- Inventory control
- Production processes
- System configuration
- Utility functions

## Writing Tests

### Test File Naming
- All test files should start with `test_`
- Name should clearly indicate what is being tested
- Use lowercase with underscores

### Test Class Naming
- Test classes should start with `Test`
- Name should match the class/module being tested
- Example: `TestProductForm`, `TestInventoryService`

### Test Method Naming
- Test methods should start with `test_`
- Name should describe the scenario being tested
- Example: `test_valid_form_submission`, `test_invalid_input_handling`

### Documentation
- Each test module should have a docstring explaining its purpose
- Each test class should have a docstring describing what it tests
- Complex test methods should have docstrings explaining the test scenario

## Test Fixtures

Common test fixtures are available in `conftest.py`:

- `client`: Django test client for UI testing
- `api_client`: DRF test client for API testing
- `sample_db`: Database fixture with test data
- `mock_api_response`: Sample API response data
- `sample_product_data`: Sample product test data

## Coverage Reports

To generate test coverage reports:

```bash
# Generate HTML coverage report
python tests/run_tests.py --coverage --html

# Generate XML coverage report
python tests/run_tests.py --coverage --xml

# View coverage report
open htmlcov/index.html
```
