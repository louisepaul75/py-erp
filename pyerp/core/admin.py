"""
Admin configuration for core app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AuditLog, UserPreference, Tag, TaggedItem


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for the AuditLog model."""

    list_display = (
        "timestamp",
        "event_type",
        "username",
        "ip_address",
        "message_short",
    )
    list_filter = (
        "event_type",
        "timestamp",
    )
    search_fields = (
        "username",
        "ip_address",
        "message",
    )
    readonly_fields = (
        "timestamp",
        "event_type",
        "message",
        "user",
        "username",
        "ip_address",
        "user_agent",
        "content_type",
        "object_id",
        "additional_data",
        "uuid",
    )
    fieldsets = (
        (
            None,
            {
                "fields": ("timestamp", "event_type", "message", "uuid"),
            },
        ),
        (
            _("User Information"),
            {
                "fields": ("user", "username", "ip_address", "user_agent"),
            },
        ),
        (
            _("Related Object"),
            {
                "fields": ("content_type", "object_id"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Additional Data"),
            {
                "fields": ("additional_data",),
                "classes": ("collapse",),
            },
        ),
    )
    date_hierarchy = "timestamp"

    def message_short(self, obj):
        """Return a shortened version of the message for display in list view."""
        if len(obj.message) > 50:
            return f"{obj.message[:47]}..."
        return obj.message

    message_short.short_description = _("Message")

    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent modification of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion only by superusers."""
        return False


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for the UserPreference model."""
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Dashboard Configuration'), {'fields': ('dashboard_config',), 'classes': ('collapse',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for the Tag model."""
    list_display = ('name', 'slug', 'description', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    """Admin interface for the TaggedItem model."""
    list_display = ('tag', 'content_type', 'object_id', 'created_at')
    list_filter = ('tag', 'content_type')
    search_fields = ('tag__name', 'content_type__app_label', 'content_type__model', 'object_id')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('tag',)
