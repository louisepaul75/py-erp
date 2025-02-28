# Legacy API Client for 4D ERP System

This module provides a robust implementation for accessing the legacy 4D ERP system directly via its REST API.

## Key Features

- **Single-Session Management**: Maintains a single session with the legacy system to prevent server overload
- **Environment Configuration**: Supports test and live environments
- **Data Access**: Retrieve data from any table in the legacy system
- **Data Updates**: Ability to update field values in legacy records
- **Robust Connection Handling**: Properly manages cookies and sessions for reliable connections

## Session Management

The most important feature of this implementation is proper session handling. The 4D server creates a new session for each request by default, which can lead to server overload with multiple clients. Our implementation ensures that a single session is maintained throughout the client's lifecycle:

1. We manually extract the initial session cookie (`WASID4D`) provided by the server
2. We bypass the default session cookie handling of the requests library
3. For each request, we explicitly include the session cookie in the request headers
4. This approach ensures the same server-side session is used for all operations
5. We monitor for new cookies from the server to detect any session changes

## Usage Example

```python
from direct_legacy_access import DirectLegacyAccess

# Create client instance
legacy = DirectLegacyAccess(environment='live')

# Get information about current session
session_info = legacy.get_session_info()
print(f"Session established: {session_info['established']}")
print(f"Session expires at: {session_info['expires_at']}")

# Retrieve data from a table
df = legacy.fetch_table_data("ArtikelGruppe", top=10)
print(df)

# Get a list of available tables
tables = legacy.list_available_tables()
print(f"Found {len(tables)} tables")

# Update a record
success = legacy.push_field_update("ArtikelGruppe", 123, "Bezeichnung", "New Name")

# Always close the session when done
legacy.close()
```

## Implementation Details

The client uses the `requests` library for HTTP communication but adds these key enhancements:

1. **Manual Cookie Management**: Rather than relying on `requests.Session` cookie handling, we manually extract and provide the session cookie
2. **Direct Request Control**: Uses direct `requests.get/post/put` calls with explicit cookie headers
3. **Session Validation**: Checks if the session is valid before making requests
4. **Error Handling**: Comprehensive error handling and logging
5. **Cookie Monitoring**: Logs warnings if the server tries to issue a new session cookie

## Advantages Over WSZ_api Module

This implementation offers several advantages over the existing WSZ_api module:

1. **No File-Based Session Storage**: Sessions are managed in memory, not in configuration files
2. **Thread Safety**: Each client instance maintains its own session, avoiding conflicts
3. **Process Isolation**: No shared global state between different processes
4. **Proper Resource Management**: Sessions are properly closed when no longer needed
5. **Single Session Per Client**: Prevents server overload by strictly maintaining a single session

## Legacy System API Notes

The legacy 4D system has these notable behaviors:

1. By default, it creates a new session for each request
2. Sessions can be preserved by explicitly passing the session cookie with each request
3. The system uses the `WASID4D` cookie to track sessions
4. The server doesn't prevent multiple sessions from being created
5. Some endpoints (like `$info` and `$catalog`) work without authentication
6. The server doesn't have a dedicated authentication endpoint 

## Legacy ERP API Direct Access

This module provides direct access to the legacy ERP system's REST API without using the WSZ_api module. It includes support for session management, data retrieval, and data updates.

### Features

- **Session Management**: 
  - Properly maintains a single session with the legacy API
  - Reuses session cookies across requests to prevent creating multiple server sessions
  - Includes session cache to share cookies across processes/instances
  - Automatically validates and refreshes sessions when needed

- **Data Retrieval**:
  - Fetches data from tables with support for pagination
  - Handles filtering and sorting
  - Converts responses to pandas DataFrames for easier data manipulation

- **Data Updates**:
  - Updates field values for specific records

### Usage

```python
from direct_legacy_access import DirectLegacyAccess

# Create a client instance
client = DirectLegacyAccess(environment='live')  # or 'test'

# Get session information
session_info = client.get_session_info()
print(f"Session cookie: {session_info['session_cookie']}")

# Get API information
api_info = client.get_info()
print(f"Cache size: {api_info['cacheSize']}")

# Fetch data from a table
df = client.fetch_table_data("ArtikelGruppe", top=10)
print(df)

# List available tables
tables = client.list_available_tables()
print(f"Found {len(tables)} tables")

# Update a field value
success = client.push_field_update(
    table_name="ArtikelGruppe", 
    record_id=1, 
    field_name="Bezeichnung", 
    field_value="New Value"
)

# Close the session when done
client.close()
```

### Session Cookie Caching

This implementation includes a session cookie caching mechanism to share sessions across multiple client instances, reducing the number of server-side sessions created:

```python
# First client instance
client1 = DirectLegacyAccess(environment='live')
# ... operations ...
client1.close()  # Cookie remains cached

# Second client instance will reuse the same server session
client2 = DirectLegacyAccess(environment='live')  # Automatically uses cached cookie
```

The cookie cache implementation:
1. Automatically stores valid session cookies in a cache
2. Reuses cached cookies for new client instances
3. Validates cookies before reusing them
4. Falls back to creating a new session if the cached cookie is invalid
5. Works with Django's cache framework if available, or uses a thread-safe in-memory cache

### Implementation Details

This implementation features several improvements:

1. **Session Sharing**: Using the cookie cache, multiple processes or instances can share the same server-side session
2. **Manual Cookie Management**: Rather than relying on the requests library's cookie handling, we manually manage cookies to ensure consistent behavior
3. **Direct Request Control**: Making direct requests with explicit headers rather than using session mechanics
4. **Session Validation**: Validating sessions before use to ensure they're still valid
5. **Error Handling**: Comprehensive error handling throughout all operations
6. **Cookie Monitoring**: Monitoring changes to cookies to detect when the server issues a new session

### Notes on Legacy System API Behavior

The legacy ERP system's REST API has some specific behaviors that this implementation accounts for:

1. **Session Creation**: By default, the API creates a new session for each request that doesn't include a session cookie
2. **Session Cookies**: The system uses a cookie named `WASID4D` to track sessions
3. **Session Timeout**: Sessions timeout after inactivity (default is 60 minutes)
4. **No Logout Endpoint**: The API doesn't provide a standard endpoint to explicitly terminate sessions

Due to these behaviors, the implementation focuses on ensuring proper session reuse to minimize the number of concurrent sessions on the server. 