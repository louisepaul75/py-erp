"""
Models for the legacy_sync app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import json


class SyncStatus(models.TextChoices):
    """
    Status choices for synchronization operations.
    """
    PENDING = 'pending', _('Pending')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    PARTIALLY_COMPLETED = 'partially_completed', _('Partially Completed')


class SyncLog(models.Model):
    """
    Log of synchronization operations between the legacy and new systems.
    """
    entity_type = models.CharField(
        max_length=50,
        help_text=_('Type of entity being synchronized (e.g., product, customer)')
    )
    status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING,
        help_text=_('Current status of the synchronization operation')
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the synchronization operation started')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the synchronization operation completed')
    )
    records_processed = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of records processed during synchronization')
    )
    records_created = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of new records created during synchronization')
    )
    records_updated = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of existing records updated during synchronization')
    )
    records_failed = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of records that failed to synchronize')
    )
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if the synchronization operation failed')
    )
    
    class Meta:
        verbose_name = _('Synchronization Log')
        verbose_name_plural = _('Synchronization Logs')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['entity_type']),
            models.Index(fields=['status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.entity_type} sync - {self.status} - {self.started_at}"


class EntityMapping(models.Model):
    """
    Mapping between entities in the legacy and new systems.
    """
    entity_type = models.CharField(
        max_length=50,
        help_text=_('Type of entity being mapped (e.g., product, customer)')
    )
    legacy_id = models.CharField(
        max_length=100,
        help_text=_('ID of the entity in the legacy system')
    )
    new_id = models.CharField(
        max_length=100,
        help_text=_('ID of the entity in the new system')
    )
    last_synced_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When the entity was last synchronized')
    )
    
    class Meta:
        verbose_name = _('Entity Mapping')
        verbose_name_plural = _('Entity Mappings')
        unique_together = [
            ('entity_type', 'legacy_id'),
            ('entity_type', 'new_id'),
        ]
        indexes = [
            models.Index(fields=['entity_type', 'legacy_id']),
            models.Index(fields=['entity_type', 'new_id']),
        ]
    
    def __str__(self):
        return f"{self.entity_type}: {self.legacy_id} -> {self.new_id}"


class EntityMappingConfig(models.Model):
    """
    Configuration for mapping fields between legacy and new entities.
    
    This model defines how fields from the legacy system map to fields in the new system,
    including any transformations that need to be applied.
    """
    entity_type = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Type of entity being mapped (e.g., product, customer)')
    )
    legacy_table = models.CharField(
        max_length=100,
        help_text=_('Name of the table in the legacy system')
    )
    new_model = models.CharField(
        max_length=100,
        help_text=_('Full path to the model class in the new system (e.g., pyerp.products.models.Product)')
    )
    field_mappings = models.JSONField(
        help_text=_('JSON mapping of legacy fields to new fields, including transformations')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this mapping configuration is active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this mapping configuration was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When this mapping configuration was last updated')
    )
    
    class Meta:
        verbose_name = _('Entity Mapping Configuration')
        verbose_name_plural = _('Entity Mapping Configurations')
        ordering = ['entity_type']
    
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
        Transform data from the legacy system to the format expected by the new system.
        
        Args:
            legacy_data: A dictionary of data from the legacy system.
            
        Returns:
            A dictionary of transformed data for the new system.
        """
        new_data = {}
        
        for legacy_field, mapping in self.field_mappings.items():
            if legacy_field in legacy_data:
                legacy_value = legacy_data[legacy_field]
                
                # Skip if the legacy value is None and the field is not required
                if legacy_value is None and not mapping.get('required', False):
                    continue
                
                # Apply transformation if specified
                transform_func = mapping.get('transform')
                if transform_func:
                    # This is a placeholder - in a real implementation, you would
                    # have a way to dynamically execute the transformation function
                    # For example, using a registry of transformation functions
                    # or evaluating a Python expression
                    if transform_func == 'to_uppercase':
                        transformed_value = str(legacy_value).upper()
                    elif transform_func == 'to_lowercase':
                        transformed_value = str(legacy_value).lower()
                    elif transform_func == 'to_boolean':
                        transformed_value = bool(legacy_value)
                    elif transform_func == 'to_int':
                        transformed_value = int(float(legacy_value)) if legacy_value else 0
                    elif transform_func == 'to_float':
                        transformed_value = float(legacy_value) if legacy_value else 0.0
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
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Name of the transformation function')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of what the transformation function does')
    )
    code = models.TextField(
        help_text=_('Python code for the transformation function. Should take a single value parameter and return the transformed value.')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this transformation function is active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this transformation function was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When this transformation function was last updated')
    )
    
    class Meta:
        verbose_name = _('Transformation Function')
        verbose_name_plural = _('Transformation Functions')
        ordering = ['name']
    
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
        # This is a simplified implementation - in a real system, you would want
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
            logger.error(f"Error executing transformation function {self.name}: {e}")
            return value 