# Direct API Module

## Overview

The `direct_api` module provides a robust interface for connecting to and interacting with the legacy 4D-based ERP system's REST API. This module replaces the previous external `WSZ_api` package with a properly implemented, tested, and maintained internal solution.

## Components

### DirectAPIClient

The `DirectAPIClient` class (`client.py`) serves as the main interface for making requests to the legacy API. It handles:

- Session management and authentication
- Constructing properly formatted URLs
- Making HTTP requests with error handling and retries
- Processing responses and converting data to usable formats (e.g., pandas DataFrames)
- Field updates for individual records

### Authentication

The `auth.py` module handles authentication with the legacy API, including:

- Session creation and storage
- Session validation and refresh
- Secure credential management

### Settings

The `settings.py` module provides configuration settings for the API client, with default values that can be overridden in Django settings:

- API endpoints
- Authentication credentials
- Timeout and retry settings
- Environment configurations (test, live)
- Pagination and response format settings

### Exceptions

The `exceptions.py` module defines custom exception classes for handling various error scenarios:

- `DirectAPIError`: Base exception for all API-related errors
- `ConnectionError`: Network or connection issues
- `ResponseError`: Errors in API responses
- `AuthenticationError`: Authentication failures
- `DataError`: Issues with data processing
- And more specialized exceptions

### Compatibility Layer

The `compatibility.py` module provides backward compatibility with the old `WSZ_api` package, ensuring a smooth transition to the new implementation.

## Usage Examples

### Basic Usage

```python
from pyerp.direct_api.client import DirectAPIClient

# Create a client for the live environment
client = DirectAPIClient(environment='live')

# Fetch data from a table
products_df = client.fetch_table('products', top=100)

# Fetch a specific record
product = client.fetch_record('products', 123)

# Update a field
success = client.push_field('products', 123, 'name', 'New Product Name')
```

### Using the Compatibility Layer

```python
from pyerp.direct_api.compatibility import fetch_data_from_api, push_data

# Fetch data (compatibility with old WSZ_api)
products_df = fetch_data_from_api(
    table_name='products',
    top=100,
    new_data_only=True
)

# Update data (compatibility with old WSZ_api)
success = push_data(
    table='products',
    column='name',
    key=123,
    value='New Product Name'
)
```

## Testing

The `direct_api` module includes comprehensive tests for all components:

### Client Tests (`test_client.py`)

- ✅ **Initialization Tests**: 
  - `test_init`: Verify client initialization with default and custom parameters
  - `test_init_invalid_environment`: Test error handling for invalid environments

- ✅ **URL Building Tests**:
  - `test_build_url`: Ensure proper URL construction for various endpoint formats

- ✅ **Session Management Tests**:
  - `test_get_base_url`: Verify base URL retrieval
  - `test_get_session`: Test session management

- ✅ **Request Handling Tests**:
  - `test_make_request_success`: Verify successful requests
  - `test_make_request_auth_error_retry`: Test session refresh on auth errors
  - `test_make_request_error_response`: Test error response handling
  - `test_make_request_connection_error`: Test connection error handling

- ✅ **Data Fetching Tests**:
  - `test_fetch_table_success`: Test basic table data retrieval
  - `test_fetch_table_with_filters`: Test filtering capabilities
  - `test_fetch_table_pagination`: Test pagination handling
  - `test_fetch_table_json_error`: Test JSON parsing error handling
  - `test_fetch_table_unexpected_format`: Test unexpected data format handling
  - `test_fetch_record_success`: Test single record retrieval
  - `test_fetch_record_json_error`: Test record JSON parsing errors
  - `test_fetch_record_error`: Test record retrieval errors

- ✅ **Data Update Tests**:
  - `test_push_field_success`: Test field update success
  - `test_push_field_error`: Test field update error handling

### Running the Tests

```bash
# Run all tests for the direct_api module
python -m pytest pyerp/direct_api/tests/ -v

# Run specific tests
python -m pytest pyerp/direct_api/tests/test_client.py::TestDirectAPIClient::test_fetch_table_pagination -v
```

## Installation and Dependencies

The `direct_api` module is included in the main pyERP project and requires:

- Python 3.8+
- Django 3.2+
- requests
- pandas
- urllib3

## Contributing

When contributing to the `direct_api` module:

1. Ensure all code changes include corresponding tests
2. Maintain backward compatibility with existing code
3. Follow the established error handling patterns
4. Document any changes to the API surface

## Future Improvements

Planned improvements for the `direct_api` module include:

1. Enhanced caching for frequently accessed data
2. Performance optimizations for large dataset handling
3. Improved monitoring and logging
4. Bulk operations for data updates 