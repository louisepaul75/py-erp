"""
Core models for the ERP system.
"""

import uuid
# import json  # Removed unused import
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from datetime import datetime

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
                f"{self.get_event_type_display()} - {self.username} - "
                f"{self.timestamp}"
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
    dashboard_layouts = models.JSONField(
        default=dict, 
        help_text="JSON configuration of user's saved dashboard layouts"
    )
    active_layout_id = models.CharField(
        max_length=100, null=True, blank=True, 
        help_text="ID of the currently active dashboard layout"
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
        Returns the grid layout configuration for the dashboard.
        If no configuration exists, returns the default grid layout.
        """
        # If the user has an active layout, use that one
        if self.active_layout_id and self.dashboard_layouts:
            layouts = self.dashboard_layouts.get('layouts', {})
            active_layout = next((
                layout for layout in layouts 
                if layout.get('id') == self.active_layout_id), None
            )
            # Use .get() for safer access
            if active_layout and active_layout.get('grid_layout'):
                return active_layout.get('grid_layout')
        
        # Fallback to the main dashboard_config, use .get()
        if self.dashboard_config and self.dashboard_config.get('grid_layout'):
            return self.dashboard_config.get('grid_layout')
        
        # If no layout found, return the default
        return self.get_default_dashboard_grid_layout()

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
                {"w": 8, "h": 11, "x": 2, "y": 0, "i": "menu-tiles", 
                 "moved": False, "static": False},
                {"w": 4, "h": 12, "x": 2, "y": 11, "i": "quick-links", 
                 "moved": False, "static": False},
                {"w": 4, "h": 12, "x": 6, "y": 11, "i": "news-pinboard", 
                 "moved": False, "static": False}
            ],
            "md": [
                {"i": "menu-tiles", "x": 0, "y": 8, "w": 12, "h": 12, 
                 "title": "Menü"},
                {"i": "quick-links", "x": 0, "y": 20, "w": 6, "h": 6, 
                 "title": "Schnellzugriff"},
                {"i": "news-pinboard", "x": 6, "y": 20, "w": 6, "h": 6, 
                 "title": "Pinnwand"}
            ],
            "sm": [
                {"i": "menu-tiles", "x": 0, "y": 8, "w": 12, "h": 14, 
                 "title": "Menü"},
                {"i": "quick-links", "x": 0, "y": 22, "w": 12, "h": 6, 
                 "title": "Schnellzugriff"},
                {"i": "news-pinboard", "x": 0, "y": 28, "w": 12, "h": 6, 
                 "title": "Pinnwand"}
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
        
    def get_saved_layouts(self):
        """
        Returns all saved dashboard layouts for the user.
        """
        if not self.dashboard_layouts or 'layouts' not in self.dashboard_layouts:
            # Initialize with the default layout
            default_layout = {
                'id': 'default',
                'name': 'Default Layout',
                'grid_layout': self.get_default_dashboard_grid_layout(),
                'created_at': datetime.now().isoformat()
            }
            self.dashboard_layouts = {'layouts': [default_layout]}
            self.active_layout_id = 'default'
            self.save()
        
        return self.dashboard_layouts.get('layouts', [])
    
    def save_layout(self, layout_id, name, grid_layout):
        """
        Save a named dashboard layout.
        If layout_id exists, updates that layout, otherwise creates a new one.
        """
        if not self.dashboard_layouts:
            self.dashboard_layouts = {'layouts': []}
        
        layouts = self.dashboard_layouts.get('layouts', [])
        
        # Check if layout already exists
        layout_index = next((
            i for i, layout in enumerate(layouts) 
            if layout.get('id') == layout_id), None
        )
        
        if layout_index is not None:
            # Update existing layout
            layouts[layout_index].update({
                'name': name,
                'grid_layout': grid_layout,
                'updated_at': datetime.now().isoformat()
            })
        else:
            # Create new layout
            new_layout = {
                'id': layout_id,
                'name': name,
                'grid_layout': grid_layout,
                'created_at': datetime.now().isoformat()
            }
            layouts.append(new_layout)
        
        self.dashboard_layouts['layouts'] = layouts
        self.save()
        return self.dashboard_layouts
    
    def delete_layout(self, layout_id):
        """
        Delete a saved dashboard layout by ID.
        """
        if not self.dashboard_layouts or 'layouts' not in self.dashboard_layouts:
            return
        
        layouts = self.dashboard_layouts.get('layouts', [])
        self.dashboard_layouts['layouts'] = [
            layout for layout in layouts if layout.get('id') != layout_id
        ]
        
        # If we deleted the active layout, set active to None
        if self.active_layout_id == layout_id:
            self.active_layout_id = None
            
            # If we have other layouts, set the first one as active
            if self.dashboard_layouts['layouts']:
                self.active_layout_id = (
                    self.dashboard_layouts['layouts'][0]['id']
                )
        
        self.save()
        return self.dashboard_layouts
    
    def set_active_layout(self, layout_id):
        """
        Set the active dashboard layout.
        """
        layouts = self.get_saved_layouts()
        
        # Check if layout exists
        layout_exists = any(
            layout.get('id') == layout_id for layout in layouts
        )
        
        if layout_exists:
            self.active_layout_id = layout_id
            self.save()
            return True
        
        return False


# --- Tagging System ---

class Tag(models.Model):
    """
    Generic Tag model for categorizing various entities.
    Moved from products module.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Tag name")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("URL-friendly tag name"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Tag description"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Creation timestamp"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp"),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]
        # Ensure the table name remains consistent during the move,
        # or handle renaming explicitly in migrations later.
        # db_table = 'products_tag'  # Temporarily uncomment if needed for migration

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TaggedItem(models.Model):
    """
    Associates a Tag with any other model instance using GenericForeignKey.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tagged_items",
        help_text=_("The tag being applied")
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text=_("Content type of the tagged object")
    )
    object_id = models.PositiveIntegerField(
        db_index=True,  # Add index for faster lookups
        help_text=_("Primary key of the tagged object")
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Timestamp when the tag was applied")
    )

    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")
        # Ensure a tag is applied only once to a specific object
        unique_together = ('tag', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        # Use try-except for potentially missing content_object 
        # during deletion phases
        try:
            content_obj_str = str(self.content_object)
        except AttributeError:
            # Fallback representation
            content_obj_str = f"{self.content_type}({self.object_id})"
        return f"'{self.tag}' tag on {content_obj_str}"

# --- End Tagging System ---

class Notification(models.Model):
    """
    Represents a notification sent to a user.
    Can be system-generated, a direct message, or a to-do item.
    """
    class NotificationType(models.TextChoices):
        SYSTEM = 'system', _('System')
        DIRECT_MESSAGE = 'direct_message', _('Direct Message')
        TODO = 'todo', _('To-Do')  # Add the new TODO type

    class PriorityLevel(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Recipient User'),
        help_text=_("The user who will receive the notification."),
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Keep notification even if sender deleted
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name=_('Sender User (if applicable)'),
        help_text=_("The user who sent the notification (if applicable)."),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title'),
        help_text=_("The title of the notification."),
    )
    content = models.TextField(
        verbose_name=_('Content'),
        blank=True,  # Keeping blank=True as per original
        help_text=_("The main content/body of the notification."),
    )
    type = models.CharField(
        max_length=20,  # Adjusted length if needed
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,  # Keep default or change if needed
        db_index=True,  # Keep index
        verbose_name=_('Notification Type'),
        help_text=_( # Updated help text
            "Category of the notification (e.g., 'system', "
            "'direct_message', 'todo')."
        ), 
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,  # Keep index
        verbose_name=_('Is Read'),
        help_text=_("Indicates if the user has read the notification."),
    )
    # --- New fields for To-Do type ---
    is_completed = models.BooleanField(
        default=False,
        null=True,  # Allow null for non-todo types
        blank=True,
        verbose_name=_('Is Completed (for To-Do)'),
        help_text=_( # Help text
            "Indicates if the to-do item has been completed "
            "(only applies to 'todo' type)."
        )
    )
    priority = models.CharField(
        max_length=10,
        choices=PriorityLevel.choices,
        null=True,  # Allow null for non-todo types
        blank=True,
        verbose_name=_('Priority (for To-Do)'),
        help_text=_( # Help text
             "Priority level for the to-do item "
             "(only applies to 'todo' type)."
        )
    )
    # --- End new fields ---
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # Keep index
        verbose_name=_('Created At'),
        help_text=_("Timestamp when the notification was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        help_text=_("Timestamp when the notification was last updated."),
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Combined existing and potential new indexes
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["user", "type", "is_read", "-created_at"]),
            models.Index( # Index for ToDo filtering
                fields=["user", "type", "is_completed", "priority"]
            ), 
            models.Index( # Index on created_at alone might be redundant
                fields=["created_at"]
            ), 
        ]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        read_status = 'Read' if self.is_read else 'Unread'
        if self.type == self.NotificationType.TODO:
            completed_status = 'Completed' if self.is_completed else 'Pending'
            priority_display = self.get_priority_display() or 'N/A'
            return (
                f"ToDo for {self.user.username}: {self.title} "
                f"({completed_status}, Priority: {priority_display})"
            )
        else:
            return (
                f"{self.get_type_display()} for {self.user.username}: "
                f"{self.title} ({read_status})"
            )


class Device(models.Model):
    """
    Represents a network device, potentially a printer or other hardware.
    """
    class DeviceType(models.TextChoices):
        PRINTER = 'PRINTER', _('Printer')
        SCANNER = 'SCANNER', _('Scanner')
        COMPUTER = 'COMPUTER', _('Computer')
        NETWORK_GEAR = 'NETWORK_GEAR', _('Network Gear')
        OTHER = 'OTHER', _('Other')

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier for the device"),
    )
    name = models.CharField(
        max_length=255,
        help_text=_(
            "Human-readable name for the device (e.g., 'Lab CA Printer')"
        ),
    )
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.OTHER,
        help_text=_("Type of the device"),
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        unique=True,  # Assuming IP should be unique for active devices
        help_text=_("IP address of the device"),
        db_index=True,
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text=_(
            "Physical or logical location (e.g., 'Lab CA', 'Office Wing B')"
        ),
        db_index=True,
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Device model designation (e.g., 'Zebra ZD420')"),
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        unique=True,  # Serial numbers should ideally be unique
        null=True,  # Allow null if serial is unknown initially
        help_text=_("Device serial number"),
    )
    label_zpl_styles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text=_(
            "List of ZPL label styles supported/configured (for printers)"
        ),
    )
    # Add other common fields as needed, e.g., MAC address, purchase date, etc.
    mac_address = models.CharField(
        max_length=17,  # XX:XX:XX:XX:XX:XX
        blank=True,
        null=True,
        unique=True,
        help_text=_("MAC address of the device"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Is the device currently active and in use?"),
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = ['location', 'name']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['device_type']),
            models.Index(fields=['is_active']),
            # For quicker lookups of active IPs
            models.Index(fields=['ip_address', 'is_active']),
        ]
        # Consider a unique constraint if needed, e.g., (location, name)
        # unique_together = (('location', 'name'),)

    def __str__(self):
        location_str = self.location or 'No Location'
        ip_str = self.ip_address or 'No IP'
        return f"{self.name} ({location_str}) - {ip_str}"
