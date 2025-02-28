# Security Features in pyERP

This document provides an overview of the security features implemented in the pyERP system. Our security architecture is being rolled out in phases as described in the Product Requirements Document (PRD).

## Current Implementation Status

| Feature | Status | Documentation |
|---------|--------|---------------|
| Basic User Authentication | ✓ Implemented | Built-in Django |
| JWT Authentication for API | ✓ Implemented | Via JWT Package |
| Core Role Definitions | ⚠ Partially Implemented | Django Permissions |
| Basic Audit Logging | ✓ Implemented | [Audit Logging](audit_logging.md) |
| Extended User Profile | 🚧 Planned (Phase 2) | - |
| Complete RBAC | 🚧 Planned (Phase 2) | - |
| Field-level Permissions | 🚧 Planned (Phase 2) | - |
| Multi-factor Authentication | 🚧 Planned (Phase 3) | - |
| Advanced Segregation of Duties | 🚧 Planned (Phase 3) | - |
| LDAP/Active Directory Integration | 🚧 Planned (Phase 3) | - |

## Security Components

### 1. Audit Logging System

The [Audit Logging System](audit_logging.md) provides comprehensive tracking of security-related events. Key features include:

- Recording of authentication events (login, logout, failed attempts)
- Tracking of user creation and management
- Permissions change logging
- Tamper-evident history for compliance and investigation

### 2. Authentication System

The authentication system is built on Django's framework with the following enhancements:

- JWT tokens for API authentication
- Custom password validation rules
- Session management controls

### 3. Authorization System

The authorization system leverages Django's built-in permissions framework with:

- User groups for role-based access
- Object-level permissions (partially implemented)
- View-level permission checks

## Security Guidelines for Developers

### Authentication Best Practices

Always use the authentication decorators and mixins provided by Django:

```python
# Function-based views
from django.contrib.auth.decorators import login_required

@login_required
def secure_view(request):
    # Your secured view logic

# Class-based views
from django.contrib.auth.mixins import LoginRequiredMixin

class SecureView(LoginRequiredMixin, View):
    # Your secured view logic
```

### Authorization Best Practices

Use permission decorators for function-based views:

```python
from django.contrib.auth.decorators import permission_required

@permission_required('app.change_model')
def edit_model(request):
    # Secure editing logic
```

For class-based views, use permission mixins:

```python
from django.contrib.auth.mixins import PermissionRequiredMixin

class EditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'app.change_model'
    # View logic
```

### Audit Logging Guidelines

Always log security-sensitive operations using the AuditService:

```python
from pyerp.core.services import AuditService

# In your views or services
AuditService.log_event(
    event_type='custom_event',
    message="Important security action performed",
    user=request.user,
    request=request
)
```

## Future Security Roadmap

See the [Product Requirements Document](../../.ai/prd.md) for detailed information about upcoming security features in Phase 2 and Phase 3 of the implementation. 