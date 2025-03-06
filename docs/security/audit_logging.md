# Audit Logging System

This document describes the implementation and usage of the audit logging system in pyERP, which provides comprehensive logging of security-related events and critical actions.

## Overview

The audit logging system records important security events in a central database table, providing a tamper-evident history of actions that affect security, user access, or sensitive data. This functionality supports security monitoring, incident investigation, and compliance requirements.

## Technical Architecture

### Core Components

1. **AuditLog Model**
   - Located in `pyerp/core/models.py`
   - Stores comprehensive information about security events
   - Contains fields for user data, timestamps, IP addresses, and event details

2. **AuditService**
   - Located in `pyerp/core/services.py`
   - Service layer for creating consistent audit log entries
   - Provides utility methods for common security events

3. **Signal Handlers**
   - Located in `pyerp/core/signals.py`
   - Automatically captures authentication events (login, logout, login failures)
   - Records user creation and modification events

4. **Admin Interface**
   - Located in `pyerp/core/admin.py`
   - Provides a searchable, filterable view of the audit logs for administrators
   - Enforces log integrity by preventing modifications

## Data Model

The `AuditLog` model includes the following key fields:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | DateTimeField | When the event occurred |
| `event_type` | CharField | Type of event (login, logout, etc.) |
| `message` | TextField | Human-readable description of the event |
| `user` | ForeignKey | Reference to the user who performed the action |
| `username` | CharField | Backup of username in case user record is deleted |
| `ip_address` | GenericIPAddressField | IP address where the event originated |
| `user_agent` | TextField | Browser/client information |
| `content_type` | ForeignKey | Content type of related object (optional) |
| `object_id` | CharField | ID of related object (optional) |
| `additional_data` | JSONField | Custom JSON data specific to the event |
| `uuid` | UUIDField | Unique identifier for the audit event |

## Event Types

The system supports the following event types:

- `LOGIN`: Successful user login
- `LOGOUT`: User logout
- `LOGIN_FAILED`: Failed login attempt
- `PASSWORD_CHANGE`: Password change
- `PASSWORD_RESET`: Password reset request
- `USER_CREATED`: New user creation
- `USER_UPDATED`: User profile or settings update
- `USER_DELETED`: User deletion
- `PERMISSION_CHANGE`: Change to user permissions or roles
- `DATA_ACCESS`: Access to sensitive data
- `DATA_CHANGE`: Modification of critical data
- `SYSTEM_ERROR`: Security-related system error
- `OTHER`: Other security-relevant event

## Usage Guidelines

### Automatic Logging

The following events are automatically logged:

- User login (successful and failed)
- User logout
- User creation and updates

### Manual Logging

For other events, developers can use the `AuditService` to create audit logs:

```python
from pyerp.core.services import AuditService

# Log a simple event
AuditService.log_event(
    event_type='data_access',
    message="User accessed sensitive customer data",
    user=request.user,
    request=request
)

# Log access to a specific object
AuditService.log_data_access(
    user=request.user,
    obj=customer_record,
    request=request,
    action="viewed payment information"
)

# Log permission changes
AuditService.log_permission_change(
    user=request.user,
    target_user=affected_user,
    permissions=["can_approve_orders"],
    added=["can_approve_orders"],
    removed=["can_view_reports"]
)
```

### Adding Custom Event Types

To add a new event type, update the `EventType` class in `pyerp/core/models.py`:

```python
class EventType(models.TextChoices):
    # ... existing types ...
    NEW_EVENT_TYPE = 'new_event_type', _('New Event Type')
```

## Viewing Audit Logs

Audit logs can be viewed in the Django admin interface under the Core section. The interface provides:

- Filtering by event type, date, and username
- Search functionality
- Detailed view of individual events

## Security Considerations

- Audit logs cannot be modified through the admin interface
- Only superusers can delete audit logs (should be rare)
- The system stores username separately to maintain the record even if a user is deleted
- Additional information is logged to the security.log file for redundancy

## Future Enhancements

In Phase 2 of the security implementation, the following enhancements are planned:

- Enhanced UI for audit log review outside of the admin interface
- Advanced filtering and reporting capabilities
- Export functionality for compliance reporting
- Aggregated security metrics and dashboards

## Integration with Other Systems

The audit logging system is designed to complement other security features:

- **Authentication System**: Logs all authentication events
- **User Management**: Tracks changes to user accounts and permissions
- **Data Access Controls**: Records access to sensitive data

## Compliance Considerations

The audit logging system helps meet the following compliance requirements:

- Record keeping of security events
- User access monitoring
- Change tracking for sensitive data
- Accountability and non-repudiation
