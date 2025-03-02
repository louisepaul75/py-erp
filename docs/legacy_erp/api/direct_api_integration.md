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

## Filtering Capabilities

The API supports OData-style filtering through the `$filter` parameter. Our testing has revealed the following filter types and behaviors:

### Supported Filter Types

1. **Equality Filters**
   ```
   $filter="Artikel_Nr = '115413'"
   ```
   Exact match for a specific value. String values must be enclosed in single quotes.

2. **Text Search with LIKE**
   ```
   $filter="Bezeichnung LIKE '%Test%'"
   ```
   Case-insensitive text search using the LIKE operator with wildcards.

3. **Numeric Comparisons**
   ```
   $filter="Preis > 10"
   ```
   Supports standard comparison operators: `>`, `<`, `>=`, `<=`, `=`, `<>`.

4. **Boolean Filters**
   ```
   $filter="aktiv = true"
   ```
   Boolean values should be specified as `true` or `false` (lowercase).

5. **Date Filters**
   ```
   $filter="CREATIONDATE >= '2023-01-01'"
   ```
   Dates should be formatted as 'YYYY-MM-DD' and enclosed in single quotes.

6. **Combined Filters with AND**
   ```
   $filter="Preis > 5 AND aktiv = true"
   ```
   Multiple conditions can be combined with the AND operator.

7. **Combined Filters with OR**
   ```
   $filter="Artikel_Nr = '115413' OR Artikel_Nr = '115414'"
   ```
   Multiple conditions can be combined with the OR operator.

### Important Notes on Filtering

1. **Filter Quoting**
   - The entire filter expression must be enclosed in double quotes in the URL parameter
   - String values within the filter must be enclosed in single quotes
   - Example: `$filter="Artikel_Nr = '115413'"`

2. **Table-Specific Support**
   - Not all tables support all filter types
   - Some tables may have different field names than expected
   - Testing is recommended to determine which filters work with specific tables

3. **Error Handling**
   - The API may return errors for invalid filters rather than empty results
   - Implementing a fallback mechanism to retry without filters is recommended
   - Example approach:
     ```python
     try:
         # Try with filter
         response = session.get(url, params=params)
         
         # Check for filter-related errors
         if response.status_code != 200 and '$filter' in params:
             # Remove the filter and try again
             params_without_filter = params.copy()
             params_without_filter.pop('$filter', None)
             response = session.get(url, params=params_without_filter)
     ```

4. **Field Names**
   - Field names in filters are case-sensitive
   - Common fields include:
     - `Artikel_Nr` - Article/product number
     - `Bezeichnung` - Description/name
     - `Preis` - Price
     - `aktiv` - Active status (boolean)
     - `CREATIONDATE` - Creation date

5. **Performance Considerations**
   - Filters are processed on the server side and can improve performance by reducing data transfer
   - Complex filters may increase server processing time
   - Combining filters with pagination is recommended for large datasets

### Testing Filter Support

To test which filters are supported by a specific table, you can use the `test_filter.py` script:

```bash
python pyerp/direct_api/scripts/test_filter.py --env live --table Kunden --verbose
```

This script tests various filter types and reports which ones work with the specified table.

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