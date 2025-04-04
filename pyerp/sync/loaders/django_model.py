"""Django model loader implementation."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from django.db.models import Model

from .base import BaseLoader, LoadResult


logger = logging.getLogger(__name__)


class DjangoModelLoader(BaseLoader):
    """Loader for Django model data."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the loader and cache the model class."""
        super().__init__(config)
        # Validate required fields early
        self._validate_config()
        # Load and cache the model class upon initialization
        self._model_class: Optional[Type[Model]] = None
        self._model_class = self._load_model_class()

    @staticmethod
    def _import_class(class_path: str) -> Type:
        """Import a class from its dotted path."""
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError, ValueError) as e:
            raise ImportError(f"Could not import class '{class_path}': {e}") from e

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.

        Returns:
            List of required field names
        """
        return ["app_name", "model_name", "unique_field"]

    def _load_model_class(self) -> Type[Model]:
        """Get Django model class from configuration.

        This method attempts to load the class and should only be called once
        during initialization.

        Returns:
            Django model class

        Raises:
            ValueError: If model cannot be found
        """
        model_path = self.config.get('model')
        app_name = self.config.get('app_name')
        model_name = self.config.get('model_name')

        if model_path:
            logger.info(f"Attempting to load model directly from path: {model_path}")
            try:
                model_class = self._import_class(model_path)
                logger.info(f"Successfully loaded model {model_class.__name__} from path.")
                return model_class
            except ImportError as e:
                logger.warning(f"Failed to load model from path '{model_path}': {e}. Falling back to app/model name.")
        
        if app_name and model_name:
            logger.info(f"Attempting to load model using app_name='{app_name}' and model_name='{model_name}'")
            try:
                model_class = apps.get_model(app_name, model_name)
                logger.info(f"Successfully loaded model {model_class.__name__} using app/model name.")
                return model_class
            except LookupError as e:
                 raise ValueError(f"Failed to get model {app_name}.{model_name}: {e}") from e

        raise ValueError("Loader configuration must provide either 'model' path or 'app_name' and 'model_name'")

    def _get_model_class(self) -> Type[Model]:
        """Return the cached model class."""
        if self._model_class is None:
            # This should not happen if __init__ ran correctly
            logger.error("Model class was not loaded during initialization!")
            raise ValueError("Model class not loaded")
        return self._model_class

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
        unique_field = self.config["unique_field"]
        if unique_field not in record:
            raise ValueError(f"Record missing unique field: {unique_field}")

        # Create lookup criteria
        lookup_criteria = {unique_field: record[unique_field]}

        # Prepare record data
        prepared_record = record.copy()

        # Remove any fields that don't exist on the model or are auto-managed
        model_class = self._get_model_class()
        model_fields = {f.name: f for f in model_class._meta.get_fields()}

        for field in list(prepared_record.keys()):
            # Skip if field doesn't exist or is auto-managed
            if field not in model_fields:
                prepared_record.pop(field)
                continue

            field_obj = model_fields[field]
            is_pk = getattr(field_obj, "primary_key", False)  # Primary key
            is_auto = getattr(field_obj, "auto_created", False)  # Auto-created

            if is_pk or is_auto:
                prepared_record.pop(field)

        return lookup_criteria, prepared_record

    def load_record(
        self,
        lookup_criteria: Dict[str, Any],
        record: Dict[str, Any],
        update_existing: bool = True,
        create_new: bool = True,
    ) -> Optional[Model]:
        """Load a single record into Django model.

        Args:
            lookup_criteria: Criteria to find existing record
            record: Record data to load
            update_existing: Whether to update existing records
            create_new: Whether to create new records

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
                instance = model_class.objects.filter(**lookup_criteria).first()

                if instance:
                    if not update_existing:
                        return None

                    # Update existing instance
                    for field, value in record.items():
                        setattr(instance, field, value)
                else:
                    if not create_new:
                        return None

                    # Create new instance - exclude auto-managed fields
                    model_fields = {f.name: f for f in model_class._meta.get_fields()}
                    filtered_record = {}
                    for field, value in record.items():
                        # Explicitly exclude 'id' field
                        if field == "id":
                            continue

                        if field not in model_fields:
                            continue

                        field_obj = model_fields[field]
                        is_pk = getattr(field_obj, "primary_key", False)
                        is_auto = getattr(field_obj, "auto_created", False)

                        if not (is_pk or is_auto):
                            filtered_record[field] = value

                    # Log the filtered record for debugging
                    logger.debug(
                        f"Creating new {model_class.__name__} "
                        f"with data: {filtered_record}"
                    )

                    instance = model_class(**filtered_record)

                # Validate and save
                try:
                    instance.full_clean()
                except DjangoValidationError as e:
                    raise ValueError(f"Validation failed: {e}") from e

                instance.save()
                return instance

        except Exception as e:
            if not isinstance(e, ValueError):
                raise ValueError(f"Failed to load record: {e}") from e
            raise

    def load(
        self, records: List[Dict[str, Any]], update_existing: bool = True
    ) -> LoadResult:
        """Load records into target system with optimized batch processing.

        This implementation overrides the base loader's method to optimize
        database operations by fetching existing records in bulk.

        Args:
            records: List of records to load
            update_existing: Whether to update existing records
                (ignored if update_strategy is set)

        Returns:
            LoadResult containing operation statistics
        """
        # Check update_strategy from config
        update_strategy = self.config.get("update_strategy", "update_or_create")
        if update_strategy == "update":
            # Only update existing records, don't create new ones
            update_existing = True
            create_new = False
        elif update_strategy == "create":
            # Only create new records, don't update existing ones
            update_existing = False
            create_new = True
        else:  # "update_or_create" (default)
            # Update existing records and create new ones
            update_existing = True
            create_new = True

        result = LoadResult()
        if not records:
            return result

        model_class = self._get_model_class()
        unique_field = self.config["unique_field"]

        # Step 1: Prepare all records and collect unique values
        prepared_records = []
        unique_values = []
        # Map unique values to original records for error reporting
        record_map = {}

        for record in records:
            try:
                lookup_criteria, prepared_record = self.prepare_record(record)
                unique_value = prepared_record[unique_field]
                prepared_records.append((unique_value, prepared_record))
                unique_values.append(unique_value)
                record_map[unique_value] = record
            except Exception as e:
                result.add_error(
                    record=record, error=e, context={"stage": "preparation"}
                )
                logger.error(f"Error preparing record: {e}", extra={"record": record})

        if not prepared_records:
            return result

        # Step 2: Bulk fetch all existing records in one query
        existing_records = {}
        try:
            query_filter = {f"{unique_field}__in": unique_values}
            for record in model_class.objects.filter(**query_filter):
                existing_records[getattr(record, unique_field)] = record
        except Exception as e:
            logger.error(f"Error fetching existing records: {e}")
            # Fall back to individual processing if bulk fetch fails
            return super().load(records, update_existing)

        # Step 3: Process each record individually
        for unique_value, prepared_record in prepared_records:
            try:
                lookup_dict = {unique_field: unique_value}
                instance = self.load_record(
                    lookup_dict,
                    prepared_record,
                    update_existing=update_existing,
                    create_new=create_new,
                )

                if instance is None:
                    result.skipped += 1
                elif instance._state.adding:
                    result.created += 1
                else:
                    result.updated += 1
            except Exception as e:
                original_record = record_map.get(unique_value, prepared_record)
                result.add_error(
                    record=original_record, error=e, context={"stage": "load"}
                )
                logger.error(
                    f"Error loading record: {e}", extra={"record": prepared_record}
                )

        return result

    def handle_conflicts(
        self, existing_record: Model, new_data: Dict[str, Any]
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
        strategy = self.config.get("conflict_strategy", "newest_wins")

        if strategy == "newest_wins":
            return new_data
        elif strategy == "keep_existing":
            return {field: getattr(existing_record, field) for field in new_data.keys()}
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
                            f"Field {field_name} expects int, " f"got {type(value)}"
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
                            f"Field {field_name} expects string, " f"got {type(value)}"
                        )

            except models.FieldDoesNotExist:
                # Field will be removed in prepare_record
                continue
