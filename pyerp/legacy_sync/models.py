"""
Models for the legacy_sync app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _  # noqa: F401
import json  # noqa: F401


class SyncStatus(models.TextChoices):
    """
    Status choices for synchronization operations.
    """
    PENDING = 'pending', _('Pending')  # noqa: F841
    IN_PROGRESS = 'in_progress', _('In Progress')  # noqa: F841
  # noqa: F841
    COMPLETED = 'completed', _('Completed')  # noqa: F841
    FAILED = 'failed', _('Failed')  # noqa: F841
  # noqa: F841
    PARTIALLY_COMPLETED = 'partially_completed', _('Partially Completed')  # noqa: F841
  # noqa: F841


class SyncLog(models.Model):
    """
    Log of synchronization operations between the legacy and new systems.
    """
    entity_type = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        help_text=_('Type of entity being synchronized (e.g., product, customer)')  # noqa: E501
    )
    status = models.CharField(  # noqa: F841
        max_length=20,  # noqa: E128
        choices=SyncStatus.choices,  # noqa: F841
  # noqa: F841
        default=SyncStatus.PENDING,  # noqa: F841
        help_text=_('Current status of the synchronization operation')  # noqa: F841
    )
    started_at = models.DateTimeField(  # noqa: F841
        auto_now_add=True,  # noqa: E128
        help_text=_('When the synchronization operation started')  # noqa: F841
    )
    completed_at = models.DateTimeField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('When the synchronization operation completed')  # noqa: F841
    )
    records_processed = models.PositiveIntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of records processed during synchronization')  # noqa: F841
    )
    records_created = models.PositiveIntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of new records created during synchronization')  # noqa: F841
    )
    records_updated = models.PositiveIntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of existing records updated during synchronization')  # noqa: E501
    )
    records_failed = models.PositiveIntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of records that failed to synchronize')  # noqa: F841
    )
    error_message = models.TextField(  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Error message if the synchronization operation failed')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Synchronization Log')  # noqa: F841
        verbose_name_plural = _('Synchronization Logs')  # noqa: F841
        ordering = ['-started_at']  # noqa: F841
        indexes = [  # noqa: F841
            models.Index(fields=['entity_type']),  # noqa: E128
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"{self.entity_type} sync - {self.status} - {self.started_at}"


class EntityMapping(models.Model):
    """
    Mapping between entities in the legacy and new systems.
    """
    entity_type = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        help_text=_('Type of entity being mapped (e.g., product, customer)')  # noqa: F841
    )
    legacy_id = models.CharField(  # noqa: F841
        max_length=100,  # noqa: E128
        help_text=_('ID of the entity in the legacy system')  # noqa: F841
    )
    new_id = models.CharField(  # noqa: F841
        max_length=100,  # noqa: E128
        help_text=_('ID of the entity in the new system')  # noqa: F841
    )
    last_synced_at = models.DateTimeField(  # noqa: F841
  # noqa: F841
        auto_now=True,  # noqa: F841
        help_text=_('When the entity was last synchronized')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Entity Mapping')  # noqa: F841
        verbose_name_plural = _('Entity Mappings')  # noqa: F841
        unique_together = [  # noqa: F841
  # noqa: F841
            ('entity_type', 'legacy_id'),
            ('entity_type', 'new_id'),
        ]
        indexes = [  # noqa: F841
  # noqa: F841
            models.Index(fields=['entity_type', 'legacy_id']),
            models.Index(fields=['entity_type', 'new_id']),
        ]

    def __str__(self):
        return f"{self.entity_type}: {self.legacy_id} -> {self.new_id}"


class EntityMappingConfig(models.Model):
    """
    Configuration for mapping fields between legacy and new entities.

    This model defines how fields from the legacy system map to fields in the new system,  # noqa: E501
    including any transformations that need to be applied.
    """
    entity_type = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        unique=True,  # noqa: F841
        help_text=_('Type of entity being mapped (e.g., product, customer)')  # noqa: F841
    )
    legacy_table = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=100,  # noqa: F841
        help_text=_('Name of the table in the legacy system')  # noqa: F841
    )
    new_model = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=100,  # noqa: F841
        help_text=_('Full path to the model class in the new system (e.g., pyerp.products.models.Product)')  # noqa: E501
    )
    field_mappings = models.JSONField(  # noqa: F841
        help_text=_('JSON mapping of legacy fields to new fields, including transformations')  # noqa: E501
    )
    is_active = models.BooleanField(  # noqa: F841
        default=True,  # noqa: E128
        help_text=_('Whether this mapping configuration is active')  # noqa: F841
    )
    created_at = models.DateTimeField(  # noqa: F841
        auto_now_add=True,  # noqa: E128
        help_text=_('When this mapping configuration was created')  # noqa: F841
    )
    updated_at = models.DateTimeField(  # noqa: F841
        auto_now=True,  # noqa: E128
        help_text=_('When this mapping configuration was last updated')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Entity Mapping Configuration')  # noqa: F841
        verbose_name_plural = _('Entity Mapping Configurations')  # noqa: F841
        ordering = ['entity_type']  # noqa: F841

    def __str__(self):

        return f"Mapping config for {self.entity_type}"

    def get_field_mapping(self, legacy_field):
        """
        Get the mapping configuration for a specific legacy field.

        Args:
            legacy_field: The name of the field in the legacy system.

        Returns:
            A dictionary with the mapping configuration, or None if not found.
        """
        mappings = self.field_mappings
        return mappings.get(legacy_field)

    def transform_legacy_data(self, legacy_data):
        """
        Transform data from the legacy system to the format expected by the new system.  # noqa: E501

        Args:
            legacy_data: A dictionary of data from the legacy system.

        Returns:
            A dictionary of transformed data for the new system.
        """
        new_data = {}

        for legacy_field, mapping in self.field_mappings.items():
            if legacy_field in legacy_data:
                legacy_value = legacy_data[legacy_field]

                # Skip if the legacy value is None and the field is not required  # noqa: E501
                if legacy_value is None and not mapping.get('required', False):
                    continue

                # Apply transformation if specified
                transform_func = mapping.get('transform')
                if transform_func:
                    # This is a placeholder - in a real implementation, you would  # noqa: E501
                    # have a way to dynamically execute the transformation function  # noqa: E501
                    # For example, using a registry of transformation functions
                    # or evaluating a Python expression
                    if transform_func == 'to_uppercase':
                        transformed_value = str(legacy_value).upper()
                    elif transform_func == 'to_lowercase':
                        transformed_value = str(legacy_value).lower()
                    elif transform_func == 'to_boolean':
                        transformed_value = bool(legacy_value)
                    elif transform_func == 'to_int':
                        transformed_value = int(float(legacy_value)) if legacy_value else 0  # noqa: E501
                    elif transform_func == 'to_float':
  # noqa: F841
                        transformed_value = float(legacy_value) if legacy_value else 0.0  # noqa: E501
                    else:
                        # Default: no transformation
                        transformed_value = legacy_value
                else:
                    transformed_value = legacy_value

                # Map to the new field name
                new_field = mapping.get('new_field')
                if new_field:
                    new_data[new_field] = transformed_value

        return new_data


class TransformationFunction(models.Model):
    """
    Custom transformation functions for data mapping.

    This model stores Python code snippets that can be used to transform data
    during the mapping process.
    """
    name = models.CharField(  # noqa: F841
        max_length=100,  # noqa: F841
  # noqa: F841
        unique=True,  # noqa: F841
  # noqa: F841
        help_text=_('Name of the transformation function')  # noqa: F841
    )
    description = models.TextField(  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
  # noqa: F841
        help_text=_('Description of what the transformation function does')  # noqa: F841
    )
    code = models.TextField(  # noqa: F841
        help_text=_('Python code for the transformation function. Should take a single value parameter and return the transformed value.')  # noqa: E501
    )
    is_active = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=True,  # noqa: F841
  # noqa: F841
        help_text=_('Whether this transformation function is active')  # noqa: F841
    )
    created_at = models.DateTimeField(  # noqa: F841
  # noqa: F841
        auto_now_add=True,  # noqa: F841
  # noqa: F841
        help_text=_('When this transformation function was created')  # noqa: F841
    )
    updated_at = models.DateTimeField(  # noqa: F841
  # noqa: F841
        auto_now=True,  # noqa: F841
  # noqa: F841
        help_text=_('When this transformation function was last updated')  # noqa: F841
  # noqa: F841
    )

    class Meta:

        verbose_name = _('Transformation Function')  # noqa: F841
        verbose_name_plural = _('Transformation Functions')  # noqa: F841
  # noqa: F841
        ordering = ['name']  # noqa: F841
  # noqa: F841

    def __str__(self):

        return self.name

    def execute(self, value):
        """
        Execute the transformation function on a value.

        Args:
            value: The value to transform.

        Returns:
            The transformed value.
        """
        # This is a simplified implementation - in a real system, you would want  # noqa: E501
        # to add more security measures and error handling
        try:
            # Create a local namespace for the function
            local_vars = {'value': value}

            # Execute the code in the local namespace
            exec(self.code, {}, local_vars)

            # Return the result
            return local_vars.get('result', value)
        except Exception as e:
            # Log the error and return the original value
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing transformation function {self.name}: {e}")  # noqa: E501
            return value
