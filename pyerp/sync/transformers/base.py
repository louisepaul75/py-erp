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
            ValueError: If required configuration is missing or invalid
        """
        if not isinstance(self.field_mappings, dict):
            raise ValueError("field_mappings must be a dictionary")

        if not isinstance(self.validation_rules, list):
            raise ValueError("validation_rules must be a list")

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
        result = {}
        # apply field mappings
        for source_field, target_field in self.field_mappings.items():
            if source_field in source_record:
                result[target_field] = source_record[source_field]
        
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
        """
        for field, transformer in self.custom_transformers.items():
            if field in record:
                try:
                    record[field] = transformer(record[field], source_record)
                except Exception as e:
                    logger.error(f"Error applying custom transformer for {field}: {e}")

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
            validator = rule.get("validator")
            error_message = rule.get("error_message", "Validation failed")

            if not field or not validator:
                continue

            if field in record and not validator(record[field]):
                errors.append(
                    ValidationError(
                        field=field,
                        message=error_message,
                        context={"value": record.get(field)},
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
            Tuple of (new_records, existing_records)
        """
        if not existing_keys or not key_field:
            # If no existing keys or key field provided, return all as new
            return source_data, []

        # Determine source field that maps to the key field
        source_field = None
        for target, source in self.field_mappings.items():
            if target == key_field:
                source_field = source
                break

        if not source_field:
            # If no mapping found for key field, return all as new
            return source_data, []

        # Normalize existing keys for more robust comparison
        # Convert all keys to strings and normalize case and whitespace
        normalized_existing_keys = set()
        for key in existing_keys:
            if key is not None:
                # Convert to string, strip whitespace, and convert to lowercase
                normalized_key = str(key).strip().lower()
                normalized_existing_keys.add(normalized_key)

        new_records = []
        existing_records = []

        # Separate records based on whether they exist in the target system
        for record in source_data:
            if source_field in record and record[source_field] is not None:
                # Normalize the source key for comparison
                source_key = str(record[source_field]).strip().lower()
                if source_key in normalized_existing_keys:
                    existing_records.append(record)
                else:
                    new_records.append(record)
            else:
                # If the key field is missing or None, treat as new
                new_records.append(record)

        logger.info(
            f"Prefiltered records: {len(new_records)} new, "
            f"{len(existing_records)} existing"
        )

        return new_records, existing_records

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
            List of validation errors by record
        """
        validation_results = []
        for record in transformed_data:
            errors = self.validate_record(record)
            if errors:
                validation_results.append({"record": record, "errors": errors})
        return validation_results
