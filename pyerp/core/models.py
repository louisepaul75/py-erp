"""
Core models for the ERP system.
"""

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Audit logging for security-related and critical system events.
    Part of Phase 1 MVP security implementation.
    """

    class EventType(models.TextChoices):
        LOGIN = "login", _("Login")
        LOGOUT = "logout", _("Logout")
        LOGIN_FAILED = "login_failed", _("Login Failed")
        PASSWORD_CHANGE = "password_change", _("Password Change")
        PASSWORD_RESET = "password_reset", _("Password Reset")
        USER_CREATED = "user_created", _("User Created")
        USER_UPDATED = "user_updated", _("User Updated")
        USER_DELETED = "user_deleted", _("User Deleted")
        PERMISSION_CHANGE = "permission_change", _("Permission Change")
        DATA_ACCESS = "data_access", _("Data Access")
        DATA_CHANGE = "data_change", _("Data Change")
        SYSTEM_ERROR = "system_error", _("System Error")
        OTHER = "other", _("Other")

    # Basic event information
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the event occurred"),
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        help_text=_("Type of event being logged"),
    )
    message = models.TextField(
        help_text=_("Description of the event"),
    )

    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
        help_text=_("User who triggered the event (if applicable)"),
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        help_text=_("Username as a backup if user record is deleted"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("IP address where the event originated"),
    )
    user_agent = models.TextField(
        blank=True,
        help_text=_("User agent/browser information"),
    )

    # Related object (optional)
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Type of object this event relates to"),
    )
    object_id = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("ID of related object"),
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Additional data
    additional_data = models.JSONField(
        null=True,
        blank=True,
        help_text=_("Additional event-specific data stored as JSON"),
    )

    # Unique identifier for the event
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique identifier for this audit event"),
    )

    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["username"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        if self.username:
            return (
                f"{self.get_event_type_display()} - {self.username} - {self.timestamp}"
            )
        return f"{self.get_event_type_display()} - {self.timestamp}"

    def save(self, *args, **kwargs):
        if self.user and not self.username:
            self.username = self.user.username
        super().save(*args, **kwargs)
