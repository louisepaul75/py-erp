"""
Core models for the ERP system.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _  # noqa: F401
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid


class AuditLog(models.Model):
    """
    Audit logging for security-related and critical system events.
    Part of Phase 1 MVP security implementation.
    """

    class EventType(models.TextChoices):

        LOGIN = 'login', _('Login')  # noqa: F841
        LOGOUT = 'logout', _('Logout')  # noqa: F841
        LOGIN_FAILED = 'login_failed', _('Login Failed')  # noqa: F841
        PASSWORD_CHANGE = 'password_change', _('Password Change')  # noqa: F841
        PASSWORD_RESET = 'password_reset', _('Password Reset')  # noqa: F841
        USER_CREATED = 'user_created', _('User Created')  # noqa: F841
        USER_UPDATED = 'user_updated', _('User Updated')  # noqa: F841
        USER_DELETED = 'user_deleted', _('User Deleted')  # noqa: F841
        PERMISSION_CHANGE = 'permission_change', _('Permission Change')  # noqa: F841
        DATA_ACCESS = 'data_access', _('Data Access')  # noqa: F841
        DATA_CHANGE = 'data_change', _('Data Change')  # noqa: F841
        SYSTEM_ERROR = 'system_error', _('System Error')  # noqa: F841
        OTHER = 'other', _('Other')  # noqa: F841

 # Basic event information
    timestamp = models.DateTimeField(  # noqa: F841
        auto_now_add=True,  # noqa: F841
        help_text=_('When the event occurred')  # noqa: F841
    )
    event_type = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        choices=EventType.choices,  # noqa: F841
        help_text=_('Type of event being logged')  # noqa: F841
    )
    message = models.TextField(  # noqa: F841
        help_text=_('Description of the event')  # noqa: F841
    )

 # User information
    user = models.ForeignKey(  # noqa: F841
        settings.AUTH_USER_MODEL,  # noqa: E128
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        on_delete=models.SET_NULL,  # noqa: F841
        related_name='audit_logs',  # noqa: F841
        help_text=_('User who triggered the event (if applicable)')  # noqa: F841
    )
    username = models.CharField(  # noqa: F841
        max_length=150,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Username as a backup if user record is deleted')  # noqa: F841
    )
    ip_address = models.GenericIPAddressField(  # noqa: F841
        null=True,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('IP address where the event originated')  # noqa: F841
    )
    user_agent = models.TextField(  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('User agent/browser information')  # noqa: F841
    )

 # Related object (optional)
    content_type = models.ForeignKey(  # noqa: F841
        ContentType,  # noqa: E128
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        on_delete=models.SET_NULL,  # noqa: F841
        help_text=_('Type of object this event relates to')  # noqa: F841
    )
    object_id = models.CharField(  # noqa: F841
        max_length=255,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('ID of related object')  # noqa: F841
    )
    content_object = GenericForeignKey('content_type', 'object_id')  # noqa: F841

 # Additional data
    additional_data = models.JSONField(  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Additional event-specific data stored as JSON')  # noqa: F841
    )

 # Unique identifier for the event
    uuid = models.UUIDField(
        default=uuid.uuid4,  # noqa: F841
        editable=False,  # noqa: F841
        unique=True,  # noqa: F841
        help_text=_('Unique identifier for this audit event')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Audit Log')  # noqa: F841
        verbose_name_plural = _('Audit Logs')  # noqa: F841
        ordering = ['-timestamp']  # noqa: F841
        indexes = [  # noqa: F841
                   models.Index(fields=['timestamp']),
                   models.Index(fields=['event_type']),
                   models.Index(fields=['username']),
                   models.Index(fields=['ip_address']),
                   models.Index(fields=['content_type', 'object_id']),
                   # noqa: F841
        ]

    def __str__(self):

        if self.username:
            return f"{self.get_event_type_display()} - {self.username} - {self.timestamp}"  # noqa: E501
        return f"{self.get_event_type_display()} - {self.timestamp}"

    def save(self, *args, **kwargs):
        if self.user and not self.username:
            self.username = self.user.username
        super().save(*args, **kwargs)
