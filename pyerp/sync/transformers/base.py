"""Base classes for data transformation between systems."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


class ValidationError:
    """Container for validation errors."""

    def __init__(
        self,
        field: str,
        message: str,
        error_type: str = "error",
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize validation error.
        
        Args:
            field: Name of the field with error
            message: Error message
            error_type: Type of error (error or warning)
            context: Additional context about the error
        """
        self.field = field
        self.message = message
        self.error_type = error_type
        self.context = context or {}


class BaseTransformer(ABC):
    """Abstract base class for data transformation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the transformer with configuration.
        
        Args:
            config: Dictionary containing transformer configuration
        """
        self.config = config
        self.field_mappings = config.get('field_mappings', {})
        self.custom_transformers = config.get('custom_transformers', [])
        self.validation_rules = config.get('validation_rules', [])
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the transformer configuration.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not isinstance(self.field_mappings, dict):
            raise ValueError("field_mappings must be a dictionary")

        if not isinstance(self.custom_transformers, list):
            raise ValueError("custom_transformers must be a list")

        if not isinstance(self.validation_rules, list):
            raise ValueError("validation_rules must be a list")

    def apply_field_mappings(
        self, source_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply configured field mappings to source record.
        
        Args:
            source_record: Source data record
            
        Returns:
            Transformed record with mapped fields
        """
        transformed = {}
        for source_field, target_field in self.field_mappings.items():
            if source_field in source_record:
                transformed[target_field] = source_record[source_field]
        return transformed

    def apply_custom_transformers(
        self,
        record: Dict[str, Any],
        source_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply custom transformation functions.
        
        Args:
            record: Currently transformed record
            source_record: Original source record
            
        Returns:
            Record with custom transformations applied
        """
        transformed = record.copy()
        for transformer in self.custom_transformers:
            if isinstance(transformer, Callable):
                transformed = transformer(transformed, source_record)
        return transformed

    def validate_record(
        self, record: Dict[str, Any]
    ) -> List[ValidationError]:
        """Validate a transformed record.
        
        Args:
            record: Record to validate
            
        Returns:
            List of validation errors found
        """
        errors = []
        for rule in self.validation_rules:
            field = rule.get('field')
            validator = rule.get('validator')
            error_message = rule.get('error_message', 'Validation failed')
            
            if not field or not validator:
                continue
                
            if field in record and not validator(record[field]):
                errors.append(ValidationError(
                    field=field,
                    message=error_message,
                    context={'value': record.get(field)}
                ))
        return errors

    @abstractmethod
    def transform(
        self, source_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform source data to target format.
        
        Args:
            source_data: List of source records to transform
            
        Returns:
            List of transformed records
            
        Raises:
            ValueError: If source data is invalid
        """
        transformed_records = []
        for record in source_data:
            # Apply field mappings
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(
                transformed, record
            )
            
            transformed_records.append(transformed)
            
        return transformed_records

    def validate(
        self, transformed_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate transformed data.
        
        Args:
            transformed_data: List of transformed records to validate
            
        Returns:
            List of validation errors by record
        """
        validation_results = []
        for record in transformed_data:
            errors = self.validate_record(record)
            if errors:
                validation_results.append({
                    'record': record,
                    'errors': errors
                })
        return validation_results 