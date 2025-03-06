"""
Admin configuration for core app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _  # noqa: F401
from .models import AuditLog


@admin.register(AuditLog)


class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for the AuditLog model."""

    list_display = (  # noqa: F841
        'timestamp',
        'event_type',
        'username',
        'ip_address',
        'message_short',
    )
    list_filter = (  # noqa: F841
        'event_type',
        'timestamp',
    )
    search_fields = (  # noqa: F841
        'username',
        'ip_address',
        'message',
    )
    readonly_fields = (  # noqa: F841
        'timestamp',
        'event_type',
        'message',
        'user',
        'username',
        'ip_address',
        'user_agent',
        'content_type',
        'object_id',
        'additional_data',
        'uuid',
    )
    fieldsets = (  # noqa: F841
        (None, {
                 'fields': ('timestamp', 'event_type', 'message', 'uuid')  # noqa: E128
                 }),
                 (_('User Information'), {
                 'fields': ('user', 'username', 'ip_address', 'user_agent')  # noqa: E128
                 }),
                 (_('Related Object'), {
                 'fields': ('content_type', 'object_id'),  # noqa: E128
                 'classes': ('collapse',),
                 }),
                 (_('Additional Data'), {
                 'fields': ('additional_data',),  # noqa: E128
                 'classes': ('collapse',),
                 }),
    )
    date_hierarchy = 'timestamp'  # noqa: F841

    def message_short(self, obj):


        """Return a shortened version of the message for display in list view."""  # noqa: E501
        if len(obj.message) > 50:
            return f"{obj.message[:47]}..."
        return obj.message
    message_short.short_description = _('Message')

    def has_add_permission(self, request):

        """Prevent manual creation of audit logs."""
        return False

    def has_change_permission(self, request, obj=None):

        """Prevent modification of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion only by superusers."""
        return request.user.is_superuser
