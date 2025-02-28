# Legacy ERP Direct API Integration

## Overview

This document details our findings and best practices for integrating with the legacy ERP system's direct API. These insights have been gathered through the development and debugging of the `getTable.py` script and other integration efforts.

## API Architecture

The legacy ERP system exposes a REST-like API that follows some OData conventions but with custom extensions specific to the 4D database system. The API allows for direct access to data tables and provides mechanisms for pagination, filtering, and data retrieval.

## Authentication and Session Management

### Session Cookies

The API uses cookie-based authentication with the following characteristics:

- Primary session cookie: `WASID4D`
- Secondary/alternative cookie: `4DSID_WSZ-DB` (used in some responses)
- Session cookies contain an alphanumeric token that must be preserved between requests
- Sessions have a limited lifetime and will expire after a period of inactivity

### Key Findings on Session Management

1. **Session Limits**: The server enforces a maximum number of concurrent sessions per user or IP address. Exceeding this limit results in a 402 error with the message "Maximum number of sessions reached".

2. **Cookie Duplication**: The API is sensitive to duplicate cookies with the same name. Having multiple `WASID4D` cookies in a request can cause authentication failures.

3. **No Reliable Logout**: The API does not provide a reliable mechanism for explicitly ending sessions. Attempts to implement logout functionality caused issues with session management.

4. **Best Practice**: Maintain a single session across script executions by:
   - Storing the session cookie value in a persistent file
   - Clearing all existing cookies before setting the current session cookie
   - Using exactly one `WASID4D` cookie per request

## Request Structure

### Base URL

The API is accessed through a base URL configured in the application settings. The URL structure follows this pattern:

```
{base_url}/rest/{table_name}
```

### Common Parameters

- `$top`: Maximum number of records to return (pagination)
- `$skip`: Number of records to skip (pagination)
- `$filter`: OData-compatible filter expression

### Example Request

```
GET {base_url}/rest/Kunden?$top=1000&$skip=0
```

## Response Format

The API returns data in JSON format with several possible structures:

### Standard OData Format

```json
{
  "value": [
    { /* record 1 */ },
    { /* record 2 */ },
    /* ... */
  ]
}
```

### 4D Specific Format

```json
{
  "__ENTITIES": [
    { /* record 1 */ },
    { /* record 2 */ },
    /* ... */
  ],
  "__COUNT": 1500,
  /* Other metadata */
}
```

### Direct List Response

In some cases, the API may return an array of records directly:

```json
[
  { /* record 1 */ },
  { /* record 2 */ },
  /* ... */
]
```

## Error Handling

### Common Error Codes

- **200**: Success
- **402**: Maximum number of sessions reached
- **403**: Authentication failure
- **404**: Resource not found
- **500**: Server error

### Error Response Format

Error responses typically include descriptive text that can be used to identify the nature of the problem:

```json
{
  "error": "Error description",
  "details": "Additional error information"
}
```

## Best Practices for Integration

Based on our experience with the API, we recommend the following best practices:

1. **Session Management**:
   - Use a persistent session cookie storage mechanism
   - Ensure only one `WASID4D` cookie exists in any request
   - Implement validation to check if the session is still valid before making data requests
   - Be prepared to acquire a new session if validation fails

2. **Pagination Handling**:
   - Always implement pagination for large datasets
   - Use the `__COUNT` field (when available) to determine total records
   - Check for fewer records than requested to identify the end of pagination

3. **Error Recovery**:
   - Implement retry logic for session-related errors
   - Clear cookies and reestablish sessions when authentication issues occur
   - Log detailed error information for troubleshooting

4. **Data Processing**:
   - Be prepared to handle different response formats
   - Verify the structure of the response before attempting to extract data
   - Use defensive programming techniques when processing responses

## Known Limitations

1. The API has a limit on the maximum number of concurrent sessions
2. There is no reliable way to explicitly end a session
3. Response formats may vary between different endpoints or tables
4. Large datasets require careful pagination handling

## Implementation Example

The `pyerp/direct_api/scripts/getTable.py` script provides a reference implementation that demonstrates these best practices. Key features include:

- Cookie management with persistence between script executions
- Session validation and automatic reestablishment
- Handling of different response formats
- Pagination for retrieving large datasets
- Retry logic for session errors

## Conclusion

The legacy ERP's direct API provides valuable access to system data but requires careful handling of sessions and response formats. By following the best practices outlined in this document, integrations can achieve reliable and efficient data exchange with the legacy system. 