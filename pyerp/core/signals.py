"""
Signal handlers for the core app.
"""

import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed  # noqa: E501
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete  # noqa: F401

from .services import AuditService

logger = logging.getLogger('pyerp.security')  # noqa: F841
  # noqa: F841
User = get_user_model()

# Authentication signals
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user logins."""
    AuditService.log_login(user, request, success=True)
  # noqa: F841


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    # We don't have a user object for failed logins, so we'll just log the attempt  # noqa: E501
    # with the username from credentials
    username = credentials.get('username', '')
    AuditService.log_event(
        event_type='login_failed',  # noqa: E128
        message=f"Failed login attempt for username: {username}",  # noqa: F841
        request=request,
        additional_data={'username_attempted': username}  # noqa: F841
  # noqa: F841
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
        # A superuser will be creating this user
        creator = None
        AuditService.log_event(
            event_type='user_created',  # noqa: E128
            message=f"User '{instance.username}' created",  # noqa: F841
            user=creator,
            obj=instance  # noqa: F841
        )
    else:
        # This is an update, but we don't know what fields changed
        # For comprehensive field tracking, consider using django-auditlog or similar  # noqa: E501
        AuditService.log_event(
            event_type='user_updated',  # noqa: F841
  # noqa: F841
            message=f"User '{instance.username}' updated",  # noqa: F841
  # noqa: F841
            obj=instance  # noqa: F841
  # noqa: F841
        )
