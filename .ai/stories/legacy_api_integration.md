# User Story: Legacy API Integration - Replace External WSZ_api with Internal Implementation

## Story Overview

**As a** systems developer,  
**I want to** replace the external WSZ_api package with a properly implemented internal module,  
**So that** we have better control over the integration with the legacy system, improved session management, and increased reliability.

## Background

The application currently depends on an external Python package called WSZ_api that provides integration with a legacy 4D-based ERP system. This package is loaded from a hardcoded external path and has several issues, including problematic session management, limited error handling, and no test coverage.

The WSZ_api package provides three main functionalities:
1. Session management and authentication with the legacy system
2. Data retrieval from tables in the legacy system
3. Data updates to the legacy system

## Requirements

1. Create an internal implementation that maintains full API compatibility with the existing WSZ_api package
2. Improve session management to be thread-safe and process-isolated
3. Configure the module through Django settings instead of hardcoded paths
4. Provide comprehensive error handling and logging
5. Ensure all functionality is covered by automated tests
6. Document the new implementation thoroughly

## Acceptance Criteria

1. The new implementation should be a proper Django module within the pyERP project
2. All hardcoded paths should be replaced with configurable settings
3. Session management should use Django's cache framework instead of a local config file
4. The API should maintain backward compatibility with the existing implementation
5. All code should be covered by unit tests and integration tests
6. Documentation should explain the architecture and usage

## Technical Implementation Details

### Phase 1: Internal Implementation

1. **Create Module Structure**
   - Create a new module at `pyerp/legacy_api/`
   - Implement the core components: auth, client, getters, setters, and utilities

2. **Session Management**
   - Use Django's cache framework to store and retrieve session information
   - Implement proper session validation and automatic refresh
   - Make the session handling thread-safe and suitable for distributed environments

3. **Configuration**
   - Add configuration options in Django settings
   ```python
   # settings.py
   LEGACY_API = {
       'ENVIRONMENTS': {
           'test': {
               'hostname': 'http://192.168.73.26:8090',
           },
           'live': {
               'hostname': 'http://192.168.73.28:8080',
           }
       },
       'DEFAULT_ENVIRONMENT': 'live',
       'TIMEOUT': 60,  # seconds
       'RETRIES': 3,
       'SESSION_TIMEOUT': 3500,  # seconds (just under 1 hour)
   }
   ```

4. **Error Handling**
   - Define custom exception classes
   ```python
   class LegacyAPIError(Exception):
       """Base exception for all legacy API errors."""
       pass
   
   class LegacyAPIConnectionError(LegacyAPIError):
       """Error connecting to the legacy API."""
       pass
   
   class LegacyAPIAuthenticationError(LegacyAPIError):
       """Authentication error with the legacy API."""
       pass
   
   class LegacyAPIDataError(LegacyAPIError):
       """Error processing data from the legacy API."""
       pass
   ```

### Phase 2: Compatibility Layer

1. **Create Compatibility Module**
   - Create a compatibility layer that mimics the external WSZ_api package
   - Implement the same function signatures as the original

2. **Update References**
   - Update `pyerp/legacy_sync/api_client.py` to use the new implementation
   - Update command scripts that directly import WSZ_api

3. **Testing**
   - Write comprehensive unit tests
   - Create integration tests for the API client
   - Test backward compatibility with existing code

### Phase 3: Enhanced Features

1. **Caching**
   - Implement caching for frequently accessed data
   - Add cache invalidation mechanisms

2. **Performance Improvements**
   - Implement bulk operations where appropriate
   - Add connection pooling

3. **Monitoring**
   - Add metrics collection for API performance
   - Create monitoring dashboards

## Implementation Tasks

### Phase 1 Tasks

1. [ ] Create basic module structure
2. [ ] Implement session management using Django cache
3. [ ] Implement environment configuration
4. [ ] Create core API client with error handling
5. [ ] Implement data retrieval functions
6. [ ] Implement data update functions
7. [ ] Write unit tests for all components
8. [ ] Document the module design and API

### Phase 2 Tasks

1. [ ] Create compatibility layer
2. [ ] Update references in legacy_sync/api_client.py
3. [ ] Update command scripts
4. [ ] Write integration tests
5. [ ] Document migration process

### Phase 3 Tasks

1. [ ] Implement data caching
2. [ ] Add bulk operations
3. [ ] Implement connection pooling
4. [ ] Add metrics collection
5. [ ] Create monitoring dashboards
6. [ ] Document advanced features

## Dependencies

- Django 5.1+
- Django's cache framework
- Requests library

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking changes in API | Extensive test coverage and compatibility layer |
| Session management issues | Use Django's cache framework and comprehensive testing |
| Performance degradation | Benchmarking before and after implementation |
| Data inconsistency | Transaction support and validation |

## Definition of Done

- All code is written, tested, and documented
- All unit tests pass
- Integration tests with the legacy system pass
- Code review is complete
- Documentation is complete
- No breaking changes to existing functionality 