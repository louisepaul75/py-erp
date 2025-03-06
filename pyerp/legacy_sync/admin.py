"""
Admin interface for the legacy_sync app.
"""

import json

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pyerp.legacy_sync.models import (
    EntityMapping,
    EntityMappingConfig,
    SyncLog,
    TransformationFunction,
)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    """
    Admin interface for SyncLog model.
    """

    list_display = (
        "entity_type",
        "status",
        "started_at",
        "completed_at",
        "records_processed",
        "records_created",
        "records_updated",
        "records_failed",
    )
    list_filter = ("entity_type", "status", "started_at")
    search_fields = ("entity_type", "error_message")
    readonly_fields = (
        "entity_type",
        "status",
        "started_at",
        "completed_at",
        "records_processed",
        "records_created",
        "records_updated",
        "records_failed",
        "error_message",
    )
    fieldsets = (
        (
            None,
            {
                "fields": ("entity_type", "status"),
            },
        ),
        (
            _("Timing"),
            {
                "fields": ("started_at", "completed_at"),
            },
        ),
        (
            _("Statistics"),
            {
                "fields": (
                    "records_processed",
                    "records_created",
                    "records_updated",
                    "records_failed",
                ),
            },
        ),
        (
            _("Error Details"),
            {
                "fields": ("error_message",),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EntityMapping)
class EntityMappingAdmin(admin.ModelAdmin):
    """
    Admin interface for EntityMapping model.
    """

    list_display = ("entity_type", "legacy_id", "new_id", "last_synced_at")
    list_filter = ("entity_type", "last_synced_at")
    search_fields = ("entity_type", "legacy_id", "new_id")
    readonly_fields = ("last_synced_at",)
    fieldsets = (
        (
            None,
            {
                "fields": ("entity_type", "legacy_id", "new_id"),
            },
        ),
        (
            _("Timing"),
            {
                "fields": ("last_synced_at",),
            },
        ),
    )


class EntityMappingConfigForm(forms.ModelForm):
    """
    Form for EntityMappingConfig model with JSON validation.
    """

    field_mappings_raw = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 80}),
        required=False,
        help_text=_(
            "JSON mapping of legacy fields to new fields, including transformations",
        ),
    )

    class Meta:
        model = EntityMappingConfig
        fields = "__all__"
        exclude = ("field_mappings",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and hasattr(self.instance, "field_mappings"):
            self.fields["field_mappings_raw"].initial = json.dumps(
                self.instance.field_mappings,
                indent=2,
            )

    def clean_field_mappings_raw(self):
        """Validate and convert JSON string to Python dict."""
        field_mappings_raw = self.cleaned_data.get("field_mappings_raw")
        if not field_mappings_raw:
            return {}

        try:
            return json.loads(field_mappings_raw)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {e!s}")

    def save(self, commit=True):
        """Save the form and update the field_mappings field."""
        instance = super().save(commit=False)
        instance.field_mappings = self.cleaned_data.get("field_mappings_raw", {})
        if commit:
            instance.save()
        return instance


@admin.register(EntityMappingConfig)
class EntityMappingConfigAdmin(admin.ModelAdmin):
    """
    Admin interface for EntityMappingConfig model.
    """

    form = EntityMappingConfigForm
    list_display = (
        "entity_type",
        "legacy_table",
        "new_model",
        "is_active",
        "updated_at",
    )
    list_filter = ("entity_type", "is_active", "updated_at")
    search_fields = ("entity_type", "legacy_table", "new_model")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": ("entity_type", "legacy_table", "new_model", "is_active"),
            },
        ),
        (
            _("Field Mappings"),
            {
                "fields": ("field_mappings_raw",),
                "description": _(
                    "Define how fields from the legacy system map to fields in the new system. "
                    'Format: {"legacy_field": {"new_field": "new_field_name", "transform": "transformation_name", "required": true/false}}',
                ),
            },
        ),
        (
            _("Timing"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


class TransformationFunctionForm(forms.ModelForm):
    """
    Form for TransformationFunction model with code validation.
    """

    class Meta:
        model = TransformationFunction
        fields = "__all__"

    def clean_code(self):
        """Validate Python code."""
        code = self.cleaned_data.get("code")
        if not code:
            return code

        # Basic validation - try to compile the code
        try:
            compile(code, "<string>", "exec")
            return code
        except SyntaxError as e:
            raise forms.ValidationError(f"Invalid Python code: {e!s}")


@admin.register(TransformationFunction)
class TransformationFunctionAdmin(admin.ModelAdmin):
    """
    Admin interface for TransformationFunction model.
    """

    form = TransformationFunctionForm
    list_display = ("name", "description", "is_active", "updated_at")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("name", "description", "code")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "description", "is_active"),
            },
        ),
        (
            _("Code"),
            {
                "fields": ("code",),
                "description": _(
                    'Python code for the transformation function. The function should set a variable named "result" '
                    'with the transformed value. The input value is available as the variable "value".',
                ),
            },
        ),
        (
            _("Timing"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
