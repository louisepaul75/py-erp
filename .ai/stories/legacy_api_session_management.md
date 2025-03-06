# User Story: Legacy API Session Management Enhancement

## Story Overview

**As a** systems developer,
**I want to** improve session management in our Legacy API integration,
**So that** we avoid session-related errors and optimize the stability of our data synchronization processes.

## Background

Our integration with the legacy 4D ERP system relies on proper session management to maintain stable connections. Through extensive development and debugging of the `getTable.py` script, we've identified critical issues and behaviors in the legacy API's session management that need to be addressed to ensure reliable data exchange.

## Key Findings

### Session and Cookie Management

1. **Cookie Handling Issues**:
   - The API requires a single `WASID4D` cookie for authentication
   - Multiple copies of this cookie in requests cause authentication failures
   - The API sometimes returns a secondary cookie `4DSID_WSZ-DB` that can be used as a fallback

2. **Session Limitations**:
   - The server enforces a maximum number of concurrent sessions per user/IP
   - When the limit is reached, the API returns a 402 error with "Maximum number of sessions reached"
   - Sessions should be reused between script runs rather than creating new ones each time

3. **Logout Functionality**:
   - Explicit logout attempts cause issues with session management
   - Sessions should be allowed to expire naturally rather than being forcibly terminated

## Requirements

1. Implement robust cookie management to prevent cookie duplication
2. Create a session persistence mechanism that allows sessions to be reused across script executions
3. Eliminate logout functionality and focus on session reuse
4. Add comprehensive logging for session-related operations to aid debugging
5. Implement automatic retry mechanisms for session-related errors

## Acceptance Criteria

1. The `getTable.py` script should successfully maintain a single session across multiple executions
2. No duplicate cookies should be present in any API request
3. The script should handle "Maximum number of sessions reached" errors gracefully with retry logic
4. Debugging logs should provide clear visibility into session states and transitions
5. No session-related errors should occur during normal operation, even with frequent script executions
6. All session cookies should be properly stored and retrieved between script runs

## Technical Implementation Details

### Session Cookie Management

1. **Clearing and Setting Cookies**:
   ```python
   # Clear any existing cookies to prevent duplicates
   self.session.cookies.clear()

   # Set exactly one cookie with the current session ID
   if self.session_id:
       self.session.cookies.set('WASID4D', self.session_id)
   ```

2. **Cookie Persistence**:
   ```python
   # Save session cookie to file
   cookie_data = {
       'timestamp': datetime.now().isoformat(),
       'value': session_id
   }

   with open(COOKIE_FILE_PATH, 'w') as f:
       json.dump(cookie_data, f)
   ```

3. **Cookie Loading and Validation**:
   ```python
   # Load saved cookie at initialization
   if os.path.exists(COOKIE_FILE_PATH):
       with open(COOKIE_FILE_PATH, 'r') as f:
           cookie_data = json.load(f)
           self.session_id = cookie_data['value']
   ```

### Session Validation and Refresh

1. **Session Validation**:
   ```python
   # Make a simple API request to check if session is valid
   response = self.session.get(f"{self.base_url}/rest/$info")

   # Check if response is successful
   if response.status_code == 200:
       return True
   else:
       return False
   ```

2. **Session Refresh**:
   ```python
   # If validation fails, attempt to get a new session
   self.session.cookies.clear()
   response = self.session.get(f"{self.base_url}/rest/$info")

   # Extract new session cookie
   for cookie in response.cookies:
       if cookie.name == 'WASID4D':
           self.session_id = cookie.value
           self.save_session_cookie()
           return True
   ```

## Testing Plan

1. Test session persistence across multiple script executions
2. Test handling of duplicate cookies
3. Test recovery from session limit errors
4. Test session validation and refresh mechanisms
5. Verify that logs provide adequate debugging information

## Documentation Requirements

1. Update the API integration documentation with session management best practices
2. Document the cookie structure and session lifecycle
3. Add troubleshooting information for common session errors

## Related Documentation

Detailed technical findings and implementation notes are available in:
- [docs/legacy_erp/api/direct_api_integration.md](../../docs/legacy_erp/api/direct_api_integration.md)
