"""
Core services for the ERP system.
"""

import logging
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

logger = logging.getLogger('pyerp.security')


class AuditService:
    """
    Service for creating audit logs for security-related events.
    """
    
    @classmethod
    def log_event(cls, event_type, message, user=None, request=None, 
                  obj=None, additional_data=None):
        """
        Create an audit log entry.
        
        Args:
            event_type (str): Type of event from AuditLog.EventType
            message (str): Description of the event
            user (User, optional): User who triggered the event
            request (HttpRequest, optional): The request that triggered the event
            obj (Model, optional): Related object
            additional_data (dict, optional): Additional data to store with the event
        
        Returns:
            AuditLog: The created audit log entry
        """
        try:
            # Get IP and user agent if request is provided
            ip_address = None
            user_agent = ''
            
            if request:
                ip_address = cls._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # Use authenticated user from request if not explicitly provided
                if user is None and request.user.is_authenticated:
                    user = request.user
            
            # Create content type reference if object is provided
            content_type = None
            object_id = ''
            
            if obj:
                content_type = ContentType.objects.get_for_model(obj)
                object_id = str(obj.pk)
            
            # Create the log entry
            log_entry = AuditLog.objects.create(
                event_type=event_type,
                message=message,
                user=user,
                username=user.username if user else '',
                ip_address=ip_address,
                user_agent=user_agent,
                content_type=content_type,
                object_id=object_id,
                additional_data=additional_data
            )
            
            # Also log to the security logger
            logger.info(
                f"AUDIT: {event_type} - {message}",
                extra={
                    'event_type': event_type,
                    'username': log_entry.username,
                    'ip_address': str(ip_address) if ip_address else None,
                }
            )
            
            return log_entry
            
        except Exception as e:
            # If something goes wrong, log the error but don't raise
            # This ensures audit logging failures don't disrupt normal operation
            logger.error(f"Error creating audit log: {str(e)}")
            return None
    
    @classmethod
    def log_login(cls, user, request, success=True):
        """Log a user login attempt."""
        event_type = AuditLog.EventType.LOGIN if success else AuditLog.EventType.LOGIN_FAILED
        message = f"User login {'successful' if success else 'failed'}"
        return cls.log_event(event_type, message, user, request)
    
    @classmethod
    def log_logout(cls, user, request):
        """Log a user logout."""
        return cls.log_event(AuditLog.EventType.LOGOUT, "User logged out", user, request)
    
    @classmethod
    def log_password_change(cls, user, request):
        """Log a password change."""
        return cls.log_event(
            AuditLog.EventType.PASSWORD_CHANGE,
            "User changed password",
            user,
            request
        )
    
    @classmethod
    def log_password_reset(cls, user, request):
        """Log a password reset."""
        return cls.log_event(
            AuditLog.EventType.PASSWORD_RESET,
            "User reset password",
            user,
            request
        )
    
    @classmethod
    def log_user_created(cls, created_user, creator, request=None):
        """Log user creation."""
        return cls.log_event(
            AuditLog.EventType.USER_CREATED,
            f"User '{created_user.username}' created",
            creator,
            request,
            created_user
        )
    
    @classmethod
    def log_user_updated(cls, updated_user, updater, request=None, changed_fields=None):
        """Log user update."""
        fields_str = ", ".join(changed_fields) if changed_fields else "fields"
        return cls.log_event(
            AuditLog.EventType.USER_UPDATED,
            f"User '{updated_user.username}' updated ({fields_str})",
            updater,
            request,
            updated_user,
            {'changed_fields': changed_fields}
        )
    
    @classmethod
    def log_permission_change(cls, user, target_user, request=None, 
                             permissions=None, added=None, removed=None):
        """Log permission changes."""
        return cls.log_event(
            AuditLog.EventType.PERMISSION_CHANGE,
            f"Permissions changed for '{target_user.username}'",
            user,
            request,
            target_user,
            {
                'permissions': permissions,
                'added': added,
                'removed': removed
            }
        )
    
    @classmethod
    def log_data_access(cls, user, obj, request=None, action=None):
        """Log sensitive data access."""
        model_name = obj._meta.model_name.capitalize()
        return cls.log_event(
            AuditLog.EventType.DATA_ACCESS,
            f"{model_name} ({obj.pk}) accessed {action or ''}",
            user,
            request,
            obj
        )
    
    @classmethod
    def _get_client_ip(cls, request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP in case of proxy chains
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 