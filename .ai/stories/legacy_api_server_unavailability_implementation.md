# Implementation: PYERP-187 - Legacy API Server Unavailability Handling

## Summary
This document describes the implementation of robust server unavailability handling in the pyERP legacy API integration, improving system resilience during legacy ERP outages.

## Status: ✅ Completed

## Implementation Details

### 1. New Exception Types

Added a specialized exception hierarchy for better error handling:

```python
class ServerUnavailableError(ConnectionError):
    """Raised when the server is unavailable or unreachable."""
    def __init__(self, message="The legacy ERP server is currently unavailable", inner_exception=None):
        self.inner_exception = inner_exception
        super().__init__(message)
```

This allows for more specific catching and handling of server unavailability scenarios.

### 2. Enhanced Error Detection

Improved the `_make_request` method in `DirectAPIClient` to detect different types of server unavailability:

```python
# Connection timeout handling
except requests.exceptions.ConnectTimeout as e:
    last_error = e
    logger.warning(f"Connection timeout during API request: {e}")
    # Retry logic here...
    
# Connection refused handling
except requests.exceptions.ConnectionError as e:
    if "Connection refused" in str(e) or "Failed to establish a new connection" in str(e):
        # Server is down handling...
    else:
        # Other connection error handling...
        
# DNS resolution errors
except socket.gaierror as e:
    # DNS failure handling...
```

This differentiation allows for more appropriate handling strategies based on the specific error type.

### 3. Smart Retry Logic

Implemented exponential backoff with context-aware retries:

```python
retries += 1
if retries <= API_MAX_RETRIES:
    backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
    logger.info(f"Retrying request in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
    time.sleep(backoff)
else:
    logger.error(f"Server appears to be unavailable after {retries-1} retries")
    raise ServerUnavailableError(
        f"Legacy ERP server at {self._get_base_url()} is unavailable (connection timeout)",
        inner_exception=last_error
    )
```

This implementation provides increasing delays between retry attempts, avoiding hammering the server during outages.

### 4. Server Availability Tracking

Added availability tracking to the `LegacyAPIClient`:

```python
def __init__(self):
    # ...
    self.server_available = True
    self.last_availability_check = datetime.datetime.now()
    self.availability_check_interval = datetime.timedelta(minutes=5)  # Check every 5 minutes
```

With checking logic at the start of API operations:

```python
if not self.server_available:
    # Check if we should try again based on the time interval
    time_since_last_check = datetime.datetime.now() - self.last_availability_check
    if time_since_last_check < self.availability_check_interval:
        logger.warning(f"Server is currently unavailable, skipping operation")
        return empty_result  # Return appropriate fallback result
```

This prevents repeated connection attempts to unavailable servers and provides automatic recovery after a cooldown period.

### 5. Graceful Error Handling

Modified all API methods to handle server unavailability gracefully:

- `fetch_table()` - Returns empty DataFrame
- `fetch_record()` - Returns empty dictionary
- `push_field()` - Returns False
- `refresh_session()` - Fails silently and marks server as unavailable

Example implementation in `fetch_table()`:

```python
def fetch_table(self, table_name, ...):
    if not self.server_available:
        # ... availability check logic ...
        return pd.DataFrame()  # Return empty DataFrame instead of raising exception
    
    try:
        # ... normal operation ...
    except ServerUnavailableError as e:
        logger.error(f"Server is unavailable during fetch_table for {table_name}: {e}")
        self.server_available = False
        self.last_availability_check = datetime.datetime.now()
        return pd.DataFrame()  # Return empty DataFrame instead of raising exception
```

### 6. Improved Logging

Enhanced logging throughout the codebase for better visibility:

```python
# Log server state changes
logger.error(f"Server is unavailable during operation: {e}")
self.server_available = False
self.last_availability_check = datetime.datetime.now()

# Log retry attempts
logger.info(f"Retrying request in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")

# Log recovery
logger.info("Successfully refreshed session cookie")
self.server_available = True
```

### 7. Testing

Created a comprehensive test script `test_api_server_unavailable.py` that:
- Tests connection to the legacy API
- Demonstrates graceful handling when server is unavailable
- Simulates server becoming unavailable to test recovery
- Shows appropriate retry behavior

The script verifies that:
1. The system initializes with appropriate server availability detection
2. API methods return empty/default results when server is unavailable
3. Cooldown periods prevent repeated connection attempts
4. Automatic retry happens after the cooldown period expires

## Configuration

The implementation is configurable through several settings:

```python
# In settings.py
API_REQUEST_TIMEOUT = 30  # seconds
API_MAX_RETRIES = 3
API_RETRY_BACKOFF_FACTOR = 0.5  # seconds

# In LegacyAPIClient
self.availability_check_interval = datetime.timedelta(minutes=5)
```

## Benefits

The implemented solution:
1. Makes pyERP resilient to temporary legacy ERP outages
2. Prevents cascading failures in dependent systems
3. Follows best practices for API resilience
4. Avoids unnecessary connection attempts to unavailable servers
5. Provides appropriate fallback behavior for critical operations
6. Ensures automatic recovery when the legacy ERP becomes available again

## Documentation

Full documentation of the implementation is available in:
- `README-server-unavailability-improvements.md` - Overview and detailed explanation
- Inline code documentation throughout the implementation
- Updated PRD section 4.8.6 covering Server Unavailability Handling

## Testing Results

All tests pass successfully and verify the resilience of the system under different server unavailability scenarios. The implementation has been verified to gracefully handle:
- Connection timeouts
- Connection refused errors
- DNS resolution failures
- Authentication failures due to server issues 