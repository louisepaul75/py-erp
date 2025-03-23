"""Base classes for data transformation between systems."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


logger = logging.getLogger(__name__)


class ValidationError:
    """Container for validation errors."""

    def __init__(
        self,
        field: str,
        message: str,
        error_type: str = "error",
        context: Optional[Dict[str, Any]] = None,
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
        self.field_mappings = config.get("field_mappings", {})
        self.custom_transformers = {}
        self.validation_rules = config.get("validation_rules", [])
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the transformer configuration.

        Raises:
            TransformError: If required configuration is missing or invalid
        """
        from pyerp.sync.exceptions import TransformError
        
        if not isinstance(self.field_mappings, dict):
            raise TransformError("field_mappings must be a dictionary")

        if not isinstance(self.validation_rules, list):
            raise TransformError("validation_rules must be a list")

    def register_custom_transformer(
        self, field: str, transformer: Callable[[Any], Any]
    ) -> None:
        """Register a custom transformer function for a field.

        Args:
            field: Field name to transform
            transformer: Function to transform the field value
        """
        self.custom_transformers[field] = transformer

    def apply_field_mappings(self, source_record: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field mappings to a source record.
        
        Args:
            source_record: Source record to transform
            
        Returns:
            Transformed record with mapped fields
        """
        # Start with a copy of the source record to preserve unmapped fields
        result = source_record.copy()

        # Apply field mappings
        for target_field, source_field in self.field_mappings.items():
            if source_field in source_record:
                result[target_field] = source_record[source_field]
                # Remove the original field if it's different from the target
                if source_field != target_field and source_field in result:
                    del result[source_field]

        return result

    def apply_custom_transformers(
        self, record: Dict[str, Any], source_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply custom transformers to a record.

        Args:
            record: Record to transform
            source_record: Original source record

        Returns:
            Transformed record
        
        Raises:
            TransformError: If a transformer fails
        """
        for field, transformer in self.custom_transformers.items():
            if field in record:
                try:
                    record[field] = transformer(record[field])
                except Exception as e:
                    from pyerp.sync.exceptions import TransformError
                    error_msg = f"Error applying custom transformer for field '{field}': {e}"
                    logger.error(error_msg)
                    raise TransformError(error_msg)

        return record

    def validate_record(self, record: Dict[str, Any]) -> List[ValidationError]:
        """Validate a transformed record.

        Args:
            record: Record to validate

        Returns:
            List of validation errors found
        """
        errors = []
        for rule in self.validation_rules:
            field = rule.get("field")
            check = rule.get("check")
            value_to_check = rule.get("value")
            error_message = rule.get("message", "Validation failed")

            if not field or field not in record:
                continue

            field_value = record[field]
            
            # Perform validation based on the check type
            is_valid = True
            if check == "greater_than" and not field_value > value_to_check:
                is_valid = False
            elif check == "less_than" and not field_value < value_to_check:
                is_valid = False
            elif check == "equals" and not field_value == value_to_check:
                is_valid = False
            
            if not is_valid:
                errors.append(
                    ValidationError(
                        field=field,
                        message=error_message,
                        context={"value": field_value},
                    )
                )
        return errors

    def prefilter_records(
        self,
        source_data: List[Dict[str, Any]],
        existing_keys: Optional[Set[Any]] = None,
        key_field: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Prefilter records to separate new and existing records.

        This method helps optimize processing by separating records that need
        to be created from those that might need updates, based on a key field.

        Args:
            source_data: List of source records to filter
            existing_keys: Set of existing keys in the target system
            key_field: Field name to use as the key (defaults to first field in mappings)

        Returns:
            Tuple of (records_to_update, records_to_create)
        """
        if existing_keys is None:
            existing_keys = set()
        
        if not key_field or not source_data:
            # If no key field provided, return all as to_update
            return source_data, []

        # Create normalized existing keys for comparison
        normalized_existing_keys = {str(k).strip().lower() if k is not None else None for k in existing_keys}
        
        to_update = []
        to_create = []

        # Filter records based on whether their key exists in existing_keys
        for record in source_data:
            if key_field not in record:
                continue
            
            key_value = record[key_field]
            # Check if the key exists in either original or normalized form
            normalized_key = str(key_value).strip().lower() if key_value is not None else None
            
            if key_value in existing_keys or normalized_key in normalized_existing_keys:
                to_update.append(record)
            else:
                to_create.append(record)

        return to_update, to_create

    @abstractmethod
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
            transformed = self.apply_custom_transformers(transformed, record)

            transformed_records.append(transformed)

        return transformed_records

    def validate(self, transformed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate transformed data.

        Args:
            transformed_data: List of transformed records to validate

        Returns:
            List of valid records
        """
        valid_records = []
        for record in transformed_data:
            errors = self.validate_record(record)
            if not errors:
                valid_records.append(record)
        
        return valid_records
