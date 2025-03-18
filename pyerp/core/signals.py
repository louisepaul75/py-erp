"""
Signal handlers for the core app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import post_save
from django.dispatch import receiver

from pyerp.utils.logging import get_category_logger
from .services import AuditService

# Use category logger for security-related logs
logger = get_category_logger("security")
User = get_user_model()


# Authentication signals
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user logins."""
    AuditService.log_login(user, request, success=True)


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    username = credentials.get("username", "")
    AuditService.log_event(
        event_type="login_failed",
        message=f"Failed login attempt for username: {username}",
        request=request,
        additional_data={"username_attempted": username},
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logouts."""
    if user:
        AuditService.log_logout(user, request)


# User model signals
@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user creation and updates."""
    if created:
        creator = None
        AuditService.log_event(
            event_type="user_created",
            message=f"User '{instance.username}' created",
            user=creator,
            obj=instance,
        )
    else:
        AuditService.log_event(
            event_type="user_updated",
            message=f"User '{instance.username}' updated",
            obj=instance,
        )
