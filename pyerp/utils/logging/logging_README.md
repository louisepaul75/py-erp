# pyERP Centralized Logging System

This document describes the centralized logging system for pyERP and how to use it effectively.

## Overview

The logging system provides a standardized way to log messages across the entire pyERP application. It offers:

- Consistent logging format across all components
- Categorized log files for different types of events
- Automatic log rotation (2MB file size limit with 10 backup files)
- JSON formatting option for machine-readable logs
- Performance tracking for slow operations
- Contextual logging for requests and user activities
- Client-side logging capabilities

## Log Categories

The system defines the following log categories, each with its own log file:

| Category | File | Purpose |
|----------|------|---------|
| app | app.log | General application logs |
| security | security.log | Security-related events (authentication, authorization) |
| performance | performance.log | Performance metrics and slow operations |
| data_sync | data_sync.log | Data synchronization with external systems |
| external_api | external_api.log | External API interactions and responses |
| database | database.log | Database operations and errors |
| user_activity | user_activity.log | User activity and actions |
| business_logic | business_logic.log | Business rules and logic execution |
| errors | errors.log | Critical errors and exceptions |
| audit | audit.log | Audit trail for compliance and record-keeping |

## Basic Usage

### Python Code

```python
# Import the logger
from pyerp.utils.logging import get_logger

# Create a logger instance for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Something unexpected but not critical")
logger.error("Something failed that might require attention")
logger.critical("Something failed that requires immediate attention")

# Add context to log messages
logger.info("User profile updated", extra={"user_id": user.id, "fields": ["name", "email"]})
```

### Special Purpose Logging

```python
from pyerp.utils.logging import (
    log_performance, 
    log_security_event,
    log_api_request,
    log_data_sync_event,
    log_user_activity,
    log_audit_event
)

# Log performance metrics
log_performance("database_query", 250)  # 250ms

# Log security events
log_security_event("login_attempt", user="john", ip_address="192.168.1.1", 
                  details={"status": "failed", "reason": "invalid_password"})

# Log API requests
log_api_request("legacy_erp", "/api/orders", 200, 340)  # 340ms response time

# Log data synchronization
log_data_sync_event("legacy_db", "pyerp", 150, "success", 
                   {"sync_type": "incremental", "batch_id": "abc123"})

# Log user activity
log_user_activity("john.doe", "product_created", 
                 {"product_id": 123, "name": "Widget XYZ"})

# Log audit events
log_audit_event("product", 123, "update", user="admin", 
               {"fields": ["price", "stock"], "reasons": ["price_change"]})
```

## Django Integration

### Middleware

Add the logging middleware to your settings to automatically log all HTTP requests and responses:

```python
# In settings.py
MIDDLEWARE = [
    # ... other middleware
    'pyerp.utils.logging_middleware.RequestLoggingMiddleware',
    # ... other middleware
]
```

### Template Context Processor

Add the logging context processor to enable client-side logging in templates:

```python
# In settings.py
TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ... other context processors
                'pyerp.utils.logging_context.logging_context_processor',
            ],
        },
    },
]
```

### In Templates

Use the context processor in templates:

```html
{{ logging_config }}

<button onclick="{{ log_client_event('button_clicked', {'button_id': 'submit'}) }}">
    Submit
</button>
```

### Application Initialization

Initialize the logging system during Django startup:

```python
# In your AppConfig.ready() method:
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    # ...
    
    def ready(self):
        from pyerp.utils.logging_init import initialize_logging
        initialize_logging()
```

## Configuration

The logging system is configured through Django settings:

```python
# In settings.py

# General log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Use JSON formatting (recommended for production)
JSON_LOGGING = os.environ.get("JSON_LOGGING", "False").lower() == "true"

# Log file size limit in bytes (default: 2MB)
LOG_FILE_SIZE_LIMIT = 2 * 1024 * 1024  # 2MB

# Number of backup files to keep
LOG_BACKUP_COUNT = 10
```

## Best Practices

1. **Always use the centralized logging system** instead of `print()` statements or direct use of Python's `logging` module.

2. **Choose the appropriate log level**:
   - DEBUG: Detailed information, typically of interest only for diagnosing problems
   - INFO: Confirmation that things are working as expected
   - WARNING: Indication that something unexpected happened, but the application is still working
   - ERROR: A more serious problem that prevented a function from working
   - CRITICAL: A serious error indicating that the application itself may be unable to continue running

3. **Include relevant context** using the `extra` parameter to make logs more useful for debugging.

4. **Use structured logging** when possible - prefer passing information as key-value pairs rather than formatting everything into the message string.

5. **Categorize logs appropriately** by using the specific logging functions for each type of event.

6. **Avoid sensitive information** in logs - never log passwords, tokens, or personal identifiable information (PII).

7. **Use request IDs** to correlate logs for a specific request flow.

## Troubleshooting

If logs are not appearing as expected:

1. Check that the logs directory exists and is writable
2. Verify that the log level is set appropriately (e.g., DEBUG logs won't appear if LOG_LEVEL is set to INFO)
3. Make sure the logging system is properly initialized
4. Check for logging configuration in test settings that might override the normal behavior 