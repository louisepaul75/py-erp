"""Django model loader implementation."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from django.db.models import Model

from .base import BaseLoader


logger = logging.getLogger(__name__)


class DjangoModelLoader(BaseLoader):
    """Loader for Django model data."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.
        
        Returns:
            List of required field names
        """
        return ['app_name', 'model_name', 'unique_field']

    def _get_model_class(self) -> Type[Model]:
        """Get Django model class from configuration.
        
        Returns:
            Django model class
            
        Raises:
            ValueError: If model cannot be found
        """
        try:
            return apps.get_model(
                self.config['app_name'],
                self.config['model_name']
            )
        except Exception as e:
            raise ValueError(
                f"Failed to get model {self.config['app_name']}."
                f"{self.config['model_name']}: {e}"
            )

    def prepare_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare a record for loading into Django model.
        
        Args:
            record: Record to prepare
            
        Returns:
            Tuple of (lookup criteria, prepared record)
            
        Raises:
            ValueError: If record is invalid
        """
        # Get unique field from config
        unique_field = self.config['unique_field']
        if unique_field not in record:
            raise ValueError(
                f"Record missing unique field: {unique_field}"
            )
            
        # Create lookup criteria
        lookup_criteria = {unique_field: record[unique_field]}
        
        # Prepare record data
        prepared_record = record.copy()
        
        # Remove any fields that don't exist on the model
        model_class = self._get_model_class()
        model_fields = {
            f.name: f for f in model_class._meta.get_fields()
        }
        
        for field in list(prepared_record.keys()):
            if field not in model_fields:
                prepared_record.pop(field)
                
        return lookup_criteria, prepared_record

    def load_record(
        self,
        lookup_criteria: Dict[str, Any],
        record: Dict[str, Any],
        update_existing: bool = True
    ) -> Optional[Model]:
        """Load a single record into Django model.
        
        Args:
            lookup_criteria: Criteria to find existing record
            record: Record data to load
            update_existing: Whether to update existing records
            
        Returns:
            Created or updated model instance, or None if skipped
            
        Raises:
            ValueError: If record is invalid
            ValidationError: If model validation fails
        """
        model_class = self._get_model_class()
        
        try:
            with transaction.atomic():
                # Check for existing record
                instance = model_class.objects.filter(
                    **lookup_criteria
                ).first()
                
                if instance:
                    if not update_existing:
                        return None
                        
                    # Update existing instance
                    for field, value in record.items():
                        setattr(instance, field, value)
                else:
                    # Create new instance
                    instance = model_class(**record)
                
                # Validate and save
                try:
                    instance.full_clean()
                except DjangoValidationError as e:
                    raise ValueError(
                        f"Validation failed: {e}"
                    ) from e
                    
                instance.save()
                return instance
                
        except Exception as e:
            if not isinstance(e, ValueError):
                raise ValueError(
                    f"Failed to load record: {e}"
                ) from e
            raise

    def handle_conflicts(
        self,
        existing_record: Model,
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle conflicts between existing and new data.
        
        Args:
            existing_record: Existing model instance
            new_data: New data to apply
            
        Returns:
            Resolved data to apply
            
        This implementation uses a simple "newest wins" strategy by default.
        Override this method to implement custom conflict resolution.
        """
        strategy = self.config.get('conflict_strategy', 'newest_wins')
        
        if strategy == 'newest_wins':
            return new_data
        elif strategy == 'keep_existing':
            return {
                field: getattr(existing_record, field)
                for field in new_data.keys()
            }
        else:
            raise ValueError(f"Unknown conflict strategy: {strategy}")

    def _validate_model_fields(
        self, model_class: Type[Model], data: Dict[str, Any]
    ) -> None:
        """Validate that data matches model field types.
        
        Args:
            model_class: Django model class
            data: Data to validate
            
        Raises:
            ValueError: If data types don't match model fields
        """
        for field_name, value in data.items():
            try:
                field = model_class._meta.get_field(field_name)
                
                # Check if field type matches value type
                if isinstance(field, models.IntegerField):
                    if not isinstance(value, (int, type(None))):
                        raise ValueError(
                            f"Field {field_name} expects int, "
                            f"got {type(value)}"
                        )
                elif isinstance(field, models.FloatField):
                    if not isinstance(value, (float, int, type(None))):
                        raise ValueError(
                            f"Field {field_name} expects float/int, "
                            f"got {type(value)}"
                        )
                elif isinstance(field, models.CharField):
                    if not isinstance(value, (str, type(None))):
                        raise ValueError(
                            f"Field {field_name} expects string, "
                            f"got {type(value)}"
                        )
                        
            except models.FieldDoesNotExist:
                # Field will be removed in prepare_record
                continue 