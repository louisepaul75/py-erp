"""
Signal handlers for user-related events.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from pyerp.utils.logging import get_category_logger

# Set up logger for security events
logger = get_category_logger("security")

User = get_user_model()


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    """Log when a user logs in successfully."""
    logger.info(f"User {user.username} logged in successfully")

    # You can add additional functionality here, like:
    # - Update last login tracking
    # - Check for security policies (password expiration, etc.)
    # - Record IP address and user agent


@receiver(user_logged_out)
def handle_user_logged_out(sender, request, user, **kwargs):
    """Log when a user logs out."""
    if user:
        logger.info(f"User {user.username} logged out")


@receiver(user_login_failed)
def handle_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    # Be careful not to log passwords
    username = credentials.get("username", "unknown")
    logger.warning(f"Failed login attempt for user {username}")

    # In a real implementation, you might:
    # - Increment a counter for failed attempts
    # - Lock accounts after X failures
    # - Alert admins of brute force attempts


@receiver(pre_save, sender=User)
def handle_password_change(sender, instance, **kwargs):
    """
    Track when a user's password is changed.
    This helps enforce password expiration policies.
    """
    if instance.pk:  # Only for existing users, not new ones
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if instance.password != old_instance.password:
                # Password has changed
                instance.last_password_change = timezone.now()
                logger.info(f"Password changed for user {instance.username}")
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    """Log and handle user creation and updates."""
    if created:
        logger.info(f"New user created: {instance.username}")
        # You could trigger welcome emails or other onboarding here
    else:
        logger.info(f"User updated: {instance.username}")
        # Handle status changes or other important updates

    # You can add additional user setup tasks here
