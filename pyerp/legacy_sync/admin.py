"""
Admin interface for the legacy_sync app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _  # noqa: F401
from django import forms
import json

from pyerp.legacy_sync.models import SyncLog, EntityMapping, EntityMappingConfig, TransformationFunction  # noqa: E501


@admin.register(SyncLog)


class SyncLogAdmin(admin.ModelAdmin):
    """
    Admin interface for SyncLog model.
    """
    list_display = (  # noqa: F841
        'entity_type',  # noqa: E128
        'status',
        'started_at',
        'completed_at',
        'records_processed',
        'records_created',
        'records_updated',
        'records_failed',
    )
    list_filter = ('entity_type', 'status', 'started_at')  # noqa: F841
    search_fields = ('entity_type', 'error_message')  # noqa: F841
    readonly_fields = (  # noqa: F841
        'entity_type',  # noqa: E128
        'status',
        'started_at',
        'completed_at',
        'records_processed',
        'records_created',
        'records_updated',
        'records_failed',
        'error_message',
    )
    fieldsets = (  # noqa: F841
        (None, {  # noqa: E128
            'fields': ('entity_type', 'status')
        }),
        (_('Timing'), {
            'fields': ('started_at', 'completed_at')  # noqa: E128
        }),
        (_('Statistics'), {
            'fields': (  # noqa: E128
                'records_processed',
                'records_created',
                'records_updated',
                'records_failed',
            )
        }),
        (_('Error Details'), {
            'fields': ('error_message',),  # noqa: E128
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):

        return False

    def has_change_permission(self, request, obj=None):
  # noqa: F841
        return False


@admin.register(EntityMapping)


class EntityMappingAdmin(admin.ModelAdmin):
    """
    Admin interface for EntityMapping model.
    """
    list_display = ('entity_type', 'legacy_id', 'new_id', 'last_synced_at')  # noqa: F841
    list_filter = ('entity_type', 'last_synced_at')  # noqa: F841
    search_fields = ('entity_type', 'legacy_id', 'new_id')  # noqa: F841
    readonly_fields = ('last_synced_at',)  # noqa: F841
    fieldsets = (  # noqa: F841
        (None, {  # noqa: E128
            'fields': ('entity_type', 'legacy_id', 'new_id')
        }),
        (_('Timing'), {
            'fields': ('last_synced_at',)  # noqa: E128
        }),
    )


class EntityMappingConfigForm(forms.ModelForm):
    """
    Form for EntityMappingConfig model with JSON validation.
    """
    field_mappings_raw = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}),  # noqa: F841
  # noqa: F841
        required=False,  # noqa: F841
        help_text=_('JSON mapping of legacy fields to new fields, including transformations')  # noqa: E501
  # noqa: E501, F841
    )

    class Meta:

        model = EntityMappingConfig  # noqa: F841
        fields = '__all__'  # noqa: F841
        exclude = ('field_mappings',)  # noqa: F841
  # noqa: F841

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # Convert field_mappings to JSON string for editing
        if self.instance.pk and hasattr(self.instance, 'field_mappings'):
            self.fields['field_mappings_raw'].initial = json.dumps(
  # noqa: F841
                self.instance.field_mappings, indent=2
  # noqa: F841
            )

    def clean_field_mappings_raw(self):
        """Validate and convert JSON string to Python dict."""
        field_mappings_raw = self.cleaned_data.get('field_mappings_raw')
        if not field_mappings_raw:
            return {}

        try:
            return json.loads(field_mappings_raw)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {str(e)}")

    def save(self, commit=True):
        """Save the form and update the field_mappings field."""
        instance = super().save(commit=False)
        instance.field_mappings = self.cleaned_data.get('field_mappings_raw', {})  # noqa: E501
        if commit:
            instance.save()
        return instance


@admin.register(EntityMappingConfig)


class EntityMappingConfigAdmin(admin.ModelAdmin):
    """
    Admin interface for EntityMappingConfig model.
    """
    form = EntityMappingConfigForm  # noqa: F841
    list_display = ('entity_type', 'legacy_table', 'new_model', 'is_active', 'updated_at')  # noqa: E501
    list_filter = ('entity_type', 'is_active', 'updated_at')  # noqa: F841
    search_fields = ('entity_type', 'legacy_table', 'new_model')  # noqa: F841
    readonly_fields = ('created_at', 'updated_at')  # noqa: F841
    fieldsets = (  # noqa: F841
        (None, {  # noqa: E128
            'fields': ('entity_type', 'legacy_table', 'new_model', 'is_active')
        }),
        (_('Field Mappings'), {
            'fields': ('field_mappings_raw',),  # noqa: E128
            'description': _(
                'Define how fields from the legacy system map to fields in the new system. '  # noqa: E501
                'Format: {"legacy_field": {"new_field": "new_field_name", "transform": "transformation_name", "required": true/false}}'  # noqa: E501
            )
        }),
        (_('Timing'), {
            'fields': ('created_at', 'updated_at'),  # noqa: E128
            'classes': ('collapse',),
        }),
    )


class TransformationFunctionForm(forms.ModelForm):
    """
    Form for TransformationFunction model with code validation.
    """
    class Meta:

        model = TransformationFunction  # noqa: F841
        fields = '__all__'  # noqa: F841

    def clean_code(self):
        """Validate Python code."""
        code = self.cleaned_data.get('code')
        if not code:
            return code

        # Basic validation - try to compile the code
        try:
            compile(code, '<string>', 'exec')
            return code
        except SyntaxError as e:
            raise forms.ValidationError(f"Invalid Python code: {str(e)}")


@admin.register(TransformationFunction)


class TransformationFunctionAdmin(admin.ModelAdmin):
    """
    Admin interface for TransformationFunction model.
    """
    form = TransformationFunctionForm  # noqa: F841
    list_display = ('name', 'description', 'is_active', 'updated_at')  # noqa: F841
  # noqa: F841
    list_filter = ('is_active', 'created_at', 'updated_at')  # noqa: F841
  # noqa: F841
    search_fields = ('name', 'description', 'code')  # noqa: F841
  # noqa: F841
    readonly_fields = ('created_at', 'updated_at')  # noqa: F841
  # noqa: F841
    fieldsets = (  # noqa: F841
  # noqa: F841
        (None, {
            'fields': ('name', 'description', 'is_active')  # noqa: E128
        }),
        (_('Code'), {
            'fields': ('code',),  # noqa: E128
            'description': _(
                'Python code for the transformation function. The function should set a variable named "result" '  # noqa: E501
                'with the transformed value. The input value is available as the variable "value".'  # noqa: E501
            )
        }),
        (_('Timing'), {
            'fields': ('created_at', 'updated_at'),  # noqa: E128
            'classes': ('collapse',),
        }),
    )
