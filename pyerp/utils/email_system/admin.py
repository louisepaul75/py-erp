from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import EmailLog, EmailEvent


class EmailEventInline(admin.TabularInline):
    model = EmailEvent
    extra = 0
    readonly_fields = ("event_type", "timestamp", "data", "user_agent", "ip_address")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "to_email_display",
        "status",
        "created_at",
        "sent_at",
        "opens",
        "clicks",
    )
    list_filter = ("status", "created_at", "sent_at", "esp")
    search_fields = ("subject", "to_email", "from_email", "message_id")
    readonly_fields = (
        "message_id",
        "esp_message_id",
        "created_at",
        "updated_at",
        "sent_at",
        "delivered_at",
        "opens",
        "clicks",
        "html_preview",
    )
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "message_id",
                    "subject",
                    "from_email",
                    "to_email",
                    "cc_email",
                    "bcc_email",
                )
            },
        ),
        (_("Content"), {"fields": ("body_text", "html_preview")}),
        (_("Status"), {"fields": ("status", "error_message")}),
        (_("ESP Information"), {"fields": ("esp", "esp_message_id")}),
        (_("Tracking"), {"fields": ("opens", "clicks")}),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at", "sent_at", "delivered_at")},
        ),
    )
    inlines = [EmailEventInline]

    def to_email_display(self, obj):
        """Display truncated to_email field with tooltip for full content."""
        if len(obj.to_email) > 40:
            return format_html(
                '<span title="{}">{}&hellip;</span>', obj.to_email, obj.to_email[:40]
            )
        return obj.to_email

    to_email_display.short_description = _("To Email")

    def html_preview(self, obj):
        """Display HTML content in an iframe."""
        if obj.body_html:
            return format_html(
                '<iframe src="data:text/html;charset=utf-8,{}" width="100%" height="300px"></iframe>',
                obj.body_html.replace('"', "&quot;"),
            )
        return _("No HTML content")

    html_preview.short_description = _("HTML Preview")


@admin.register(EmailEvent)
class EmailEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "email_subject", "timestamp", "ip_address")
    list_filter = ("event_type", "timestamp")
    search_fields = ("email_log__subject", "email_log__to_email", "ip_address")
    readonly_fields = (
        "email_log",
        "event_type",
        "timestamp",
        "data",
        "user_agent",
        "ip_address",
    )

    def email_subject(self, obj):
        """Display the subject of the related email."""
        return obj.email_log.subject

    email_subject.short_description = _("Email Subject")

    def has_add_permission(self, request):
        return False
