# Server Unavailability Handling in Legacy API Integration

This document outlines the improvements made to the pyERP system to gracefully handle server unavailability when interacting with the legacy ERP system API.

## Problem Statement

The legacy ERP API connection was not properly handling server unavailability, leading to:

1. Unhandled exceptions when the server was down or unreachable
2. Lack of retry mechanisms with appropriate backoff
3. No differentiation between different types of connection errors
4. No temporary caching or fallback for critical operations
5. Repeated connection attempts even when the server was known to be down

## Implemented Solutions

### 1. New Exception Types

Added a more specific exception type for server unavailability:

```python
class ServerUnavailableError(ConnectionError):
    """Raised when the server is unavailable or unreachable."""
    def __init__(self, message="The legacy ERP server is currently unavailable", inner_exception=None):
        self.inner_exception = inner_exception
        super().__init__(message)
```

### 2. Improved Error Detection

Enhanced the API client to detect various server unavailability scenarios:

- Connection timeouts
- Connection refused errors
- DNS resolution failures
- Authentication failures due to server issues

### 3. Smart Retry Logic

Implemented an intelligent retry mechanism with:

- Exponential backoff between retries
- Maximum retry count to prevent endless retries
- Context-aware retrying based on error type

### 4. Server Availability Tracking

Added server availability tracking in the `LegacyAPIClient`:

```python
def __init__(self):
    # ...
    self.server_available = True
    self.last_availability_check = datetime.datetime.now()
    self.availability_check_interval = datetime.timedelta(minutes=5)
```

- Tracks when the server becomes unavailable
- Prevents repeated connection attempts for a configurable period
- Automatically retries after the waiting period

### 5. Graceful Error Handling

Modified all API methods to handle server unavailability gracefully:

- `fetch_table()` - Returns empty DataFrame instead of raising exception
- `fetch_record()` - Returns empty dictionary instead of raising exception
- `push_field()` - Returns False instead of raising exception
- `refresh_session()` - Fails silently and sets availability flag

### 6. Improved Logging

Enhanced logging to provide better visibility into server issues:

- Log server availability state changes
- Log retry attempts with counts and backoff times
- Provide detailed error messages for different error types

## Testing

A test script (`test_api_server_unavailable.py`) was created to verify these improvements:

- Tests connection to the legacy API server
- Demonstrates graceful handling when server is unavailable
- Simulates server becoming unavailable to test recovery
- Shows appropriate retry behavior

## Configuration

The following configuration options are available to tune the server unavailability handling:

- `API_REQUEST_TIMEOUT` - Timeout for API requests (default: 30 seconds)
- `API_MAX_RETRIES` - Maximum number of retry attempts (default: 3)
- `API_RETRY_BACKOFF_FACTOR` - Backoff factor between retries (default: 0.5)
- `availability_check_interval` - Time to wait before retrying server connection (default: 5 minutes)

## Conclusion

These improvements make the pyERP system more resilient when the legacy ERP API is unavailable. The system now:

1. Handles server unavailability gracefully without crashing
2. Provides appropriate fallbacks and empty results when needed
3. Implements smart retry logic with backoff
4. Avoids excessive connection attempts to unavailable servers
5. Automatically recovers when the server becomes available again

This ensures that the pyERP system remains operational even when the legacy ERP system is temporarily down or unreachable.
