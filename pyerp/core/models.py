"""
Core models for the ERP system.
"""

import uuid
import json
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


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


class UserPreference(models.Model):
    """
    Store user preferences including dashboard configuration.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )
    dashboard_config = models.JSONField(
        default=dict, help_text="JSON configuration of user's dashboard layout"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"

    def get_dashboard_modules(self):
        """
        Returns the user's dashboard module configuration.
        If none exists, returns the default configuration.
        """
        if not self.dashboard_config or "modules" not in self.dashboard_config:
            return self.get_default_dashboard_modules()
        return self.dashboard_config.get("modules", [])

    def get_dashboard_grid_layout(self):
        """
        Returns the user's dashboard grid layout configuration.
        If none exists, returns the default grid layout.
        """
        if not self.dashboard_config or "grid_layout" not in self.dashboard_config:
            return self.get_default_dashboard_grid_layout()
        return self.dashboard_config.get("grid_layout", {})

    def get_default_dashboard_modules(self):
        """
        Returns the default dashboard modules configuration.
        """
        return [
            {
                "id": "users-permissions",
                "title": "Benutzer & Berechtigungen",
                "type": "users-permissions",
                "position": 0,
                "enabled": True,
                "settings": {"show_stats": True, "show_recent_users": True},
            },
            {
                "id": "quick-access",
                "title": "Schnellzugriff",
                "type": "quick-access",
                "position": 1,
                "enabled": True,
                "settings": {},
            },
            {
                "id": "recent-orders",
                "title": "Bestellungen nach Liefertermin",
                "type": "recent-orders",
                "position": 2,
                "enabled": True,
                "settings": {},
            },
            {
                "id": "important-links",
                "title": "Wichtige Links",
                "type": "important-links",
                "position": 3,
                "enabled": True,
                "settings": {},
            },
            {
                "id": "news-board",
                "title": "Interne Pinnwand",
                "type": "news-board",
                "position": 4,
                "enabled": True,
                "settings": {},
            },
        ]

    def get_default_dashboard_grid_layout(self):
        """
        Returns the default dashboard grid layout configuration.
        This is used when no user-specific layout is available.
        """
        # Default grid layout
        return {
            "lg": [
                {"w": 8, "h": 11, "x": 2, "y": 0, "i": "menu-tiles", "moved": False, "static": False},
                {"w": 4, "h": 12, "x": 2, "y": 11, "i": "quick-links", "moved": False, "static": False},
                {"w": 4, "h": 12, "x": 6, "y": 11, "i": "news-pinboard", "moved": False, "static": False}
            ],
            "md": [
                {"i": "menu-tiles", "x": 0, "y": 8, "w": 12, "h": 12, "title": "Menü"},
                {"i": "quick-links", "x": 0, "y": 20, "w": 6, "h": 6, "title": "Schnellzugriff"},
                {"i": "news-pinboard", "x": 6, "y": 20, "w": 6, "h": 6, "title": "Pinnwand"}
            ],
            "sm": [
                {"i": "menu-tiles", "x": 0, "y": 8, "w": 12, "h": 14, "title": "Menü"},
                {"i": "quick-links", "x": 0, "y": 22, "w": 12, "h": 6, "title": "Schnellzugriff"},
                {"i": "news-pinboard", "x": 0, "y": 28, "w": 12, "h": 6, "title": "Pinnwand"}
            ]
        }

    def save_dashboard_config(self, modules=None, grid_layout=None):
        """
        Save the dashboard configuration.
        Can update modules, grid layout, or both.
        """
        if not self.dashboard_config:
            self.dashboard_config = {}
        
        if modules is not None:
            self.dashboard_config['modules'] = modules
            
        if grid_layout is not None:
            self.dashboard_config['grid_layout'] = grid_layout
            
        self.save()
        return self.dashboard_config
