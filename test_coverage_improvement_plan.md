# Test Coverage Improvement Plan

**Current Coverage:** 50% overall (as of March 2025)

## 1. Priority Areas

Based on the current coverage report, the following areas need immediate attention:

1. **Business Module Services** (19%)
   - `pyerp/business_modules/inventory/services.py` (19%)
   - Core business logic implementation

2. **Sync Transformers** (extremely low coverage)
   - `transformers/inventory.py` (7%)
   - `transformers/product.py` (11%)
   - `transformers/sales_record.py` (8%)
   - `transformers/product_storage.py` (0%)
   - `transformers/address.py` (0%)
   - `transformers/customer.py` (0%)

3. **External API Modules**
   - `images_cms/client.py` (25%)
   - `connection_manager.py` (29%)
   - `legacy_erp/auth.py` (41%)
   - `legacy_erp/client.py` (42%)

4. **Core Validators** (31%)
   - Critical validation logic with only 31% coverage

5. **Celery Tasks** (35%)
   - Async task handling with 35% coverage

6. **Monitoring Services** (11%)
   - System monitoring implementation

7. **Django View Modules**
   - Many view modules (`views.py`) have 0% coverage
   - API endpoints and API URLs

## 2. Test Implementation Strategy

### Phase 1: Critical Business Logic (2 weeks)

1. **Business Module Services**
   - Add tests for inventory services focusing on core operations
   - Test all public methods in the service classes
   - Cover error handling and edge cases

2. **Core Validators**
   - Complete validator test coverage
   - Test validation rules and error conditions
   - Focus on complex validation logic

3. **Sync Transformers**
   - Create tests for the transformer base classes
   - Add tests for data transformation logic
   - Cover ETL validation and error handling

### Phase 2: Integration Points (2 weeks)

1. **External API Modules**
   - Test API client implementations
   - Mock external service responses
   - Test authentication and error handling
   - Test retry and fallback logic

2. **Celery Tasks**
   - Test task execution and scheduling
   - Test error handling and retry logic
   - Test task chaining and dependencies

3. **Monitoring Services**
   - Test health check implementations
   - Test alert logic and conditions
   - Test error recovery mechanisms

### Phase 3: User Interface (2 weeks)

1. **Django Views**
   - Test all view functions/classes
   - Cover authentication and authorization
   - Test form handling and validation
   - Test API responses and error handling

2. **API Endpoints**
   - Test request validation
   - Test serialization/deserialization
   - Test pagination and filtering
   - Test error responses

## 3. Implementation Plan

### Week 1-2: Critical Business Logic

| Module | Current Coverage | Target | Files | Focus Areas |
|--------|------------------|--------|-------|-------------|
| Business Services | 19% | 70% | `inventory/services.py` | Core inventory operations, validation |
| Core Validators | 31% | 80% | `core/validators.py` | Field validation, business rules |
| Sync Transformers | 7-11% | 60% | `sync/transformers/*.py` | Data transformation, validation |

#### Tasks:

1. **Inventory Services**
   - Write tests for inventory manipulation methods
   - Test validation error handling
   - Test business rule enforcement

2. **Core Validators**
   - Test each validator class
   - Test validation rule combinations
   - Test error messages and contexts

3. **Sync Transformers**
   - Test base transformer methods
   - Test field mappings and transformations
   - Test data filtering and validation

### Week 3-4: Integration Points

| Module | Current Coverage | Target | Files | Focus Areas |
|--------|------------------|--------|-------|-------------|
| External API | 25-42% | 70% | `external_api/*.py` | API clients, authentication |
| Celery Tasks | 35% | 75% | `celery.py`, `sync/tasks.py` | Async tasks, error handling |
| Monitoring | 11% | 60% | `monitoring/services.py` | System monitoring, alerting |

#### Tasks:

1. **External API Modules**
   - Test API client initialization and configuration
   - Test request/response handling
   - Test authentication and session management
   - Test error handling and retries

2. **Celery Tasks**
   - Test task registration and scheduling
   - Test task execution and result handling
   - Test error handling and retry logic
   - Test task dependencies and chaining

3. **Monitoring Services**
   - Test health check implementations
   - Test alert conditions and triggers
   - Test notification mechanisms
   - Test error recovery and logging

### Week 5-6: User Interface

| Module | Current Coverage | Target | Files | Focus Areas |
|--------|------------------|--------|-------|-------------|
| Django Views | 0-67% | 75% | `*/views.py` | View logic, forms, responses |
| API Endpoints | 0-50% | 75% | `*/api.py` | Request handling, serialization |
| URL Configurations | 0% | 60% | `*/urls.py` | URL routing, permissions |

#### Tasks:

1. **Django Views**
   - Test view rendering and context data
   - Test form validation and submission
   - Test authentication and authorization
   - Test redirects and error handling

2. **API Endpoints**
   - Test request validation and parsing
   - Test response formatting and serialization
   - Test authentication and permissions
   - Test pagination, filtering, and sorting

## 4. Test Implementation Best Practices

### Mocking Strategy

1. **External Services**
   - Use `unittest.mock` to mock external API calls
   - Create detailed mock responses for different scenarios
   - Test with both success and error responses

2. **Database Access**
   - Use Django's `TestCase` for database tests
   - Create fixtures for common test data
   - Use factories for complex object creation

3. **Authentication**
   - Mock user authentication for view tests
   - Test with different permission levels
   - Test unauthorized access scenarios

### Test Organization

1. **Test Location**
   - Place tests in a `tests` directory within each module
   - Organize tests to match the structure of the module being tested
   - Group related tests in test classes

2. **Naming Convention**
   - Name test files `test_<module_name>.py`
   - Name test classes `Test<ClassBeingTested>`
   - Name test methods `test_<behavior_being_tested>`

3. **Test Isolation**
   - Each test should be independent
   - Avoid dependencies between tests
   - Use setUp and tearDown methods for test setup/cleanup

## 5. Tools and Resources

1. **Coverage Tools**
   - Run `python -m pytest --cov=pyerp --cov-report=html` for detailed reports
   - Review `htmlcov/index.html` for coverage details

2. **Test Templates**
   - Refer to existing tests in the codebase for patterns
   - Use the unit-testing document for guidance on test structure

3. **Continuous Integration**
   - Configure CI to run tests and report coverage
   - Set up coverage thresholds to prevent decreases

## 6. Success Criteria

1. **Short-term Goal** (2 weeks)
   - Increase overall coverage to 60%
   - Focus on critical business logic modules

2. **Medium-term Goal** (6 weeks)
   - Increase overall coverage to 70% 
   - Cover all public APIs and key business logic

3. **Long-term Goal** (3 months)
   - Maintain coverage above 80%
   - Implement test-driven development for new features 

## 7. Mutation Testing with Stryker

To ensure the effectiveness of our test suite beyond traditional code coverage metrics, we will implement mutation testing using Stryker in the frontend React application:

### Phase 1: Initial Setup (1 week)

1. **Configure Stryker**
   - Install and configure Stryker for Jest
   - Set up appropriate mutation thresholds (high: 80%, low: 60%, break: 50%)
   - Add mutation testing to the CI/CD pipeline

2. **Baseline Testing**
   - Run initial mutation tests on critical utility functions
   - Document baseline mutation scores
   - Identify areas where tests pass but mutations survive

### Phase 2: Targeted Improvements (2 weeks)

1. **Utility Functions**
   - Improve test quality for core utility functions
   - Aim for mutation score of 80%+

2. **Auth Module**
   - Apply mutation testing to authentication modules
   - Strengthen edge case testing

3. **UI Component Testing**
   - Test critical UI components with mutation testing
   - Focus on components handling business logic

### Phase 3: Full Implementation (Ongoing)

1. **New Feature Development**
   - Include mutation testing in the development workflow for new features
   - Require minimum mutation score for new code

2. **Documentation**
   - Create documentation on interpreting mutation test results
   - Train developers on writing mutation-resistant tests

3. **Regular Auditing**
   - Schedule quarterly mutation testing audits
   - Track improvement in mutation scores over time

### Success Criteria

- Overall mutation score of 70%+ for critical code paths
- No critical components with mutation score below 50%
- All new features include mutation testing as part of development 