"""Pipeline orchestration for sync operations."""

import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

import math
from django.utils import timezone
from pyerp.utils.logging import get_logger, log_data_sync_event

from .extractors.base import BaseExtractor
from .transformers.base import BaseTransformer
from .loaders.base import BaseLoader
from .models import (
    SyncLog,
    SyncLogDetail,
    SyncMapping,
    SyncState,
)


logger = get_logger(__name__)


class SyncPipeline:
    """Orchestrates extraction, transformation, and loading for sync operations."""

    def __init__(
        self,
        mapping: SyncMapping,
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        loader: BaseLoader,
    ):
        """Initialize the pipeline with components.

        Args:
            mapping: The sync mapping configuration
            extractor: Data extractor instance
            transformer: Data transformer instance
            loader: Data loader instance
        """
        self.mapping = mapping
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader
        self.sync_log = None
        self.sync_state, _ = SyncState.objects.get_or_create(mapping=mapping)

    def run(
        self,
        incremental: bool = True,
        batch_size: int = 100,
        query_params: Optional[Dict[str, Any]] = None,
        fail_on_filter_error: bool = False,
    ) -> SyncLog:
        """Run the sync pipeline.

        Args:
            incremental: If True, only sync records modified since last sync
            batch_size: Number of records to process in each batch
            query_params: Optional additional query parameters
            fail_on_filter_error: If True, fail if filter doesn't work correctly

        Returns:
            SyncLog: The completed sync log record
        """
        try:
            # Initialize sync log
            self.sync_log = SyncLog.objects.create(
                mapping=self.mapping,
                status="started",
                is_full_sync=not incremental,
                sync_params={
                    "incremental": incremental,
                    "batch_size": batch_size,
                    "query_params": query_params or {},
                    "fail_on_filter_error": fail_on_filter_error,
                },
            )

            # Update sync state
            self.sync_state.update_sync_started()

            # Add modified_date filter for incremental sync
            params = query_params or {}
            if incremental and self.sync_state.last_successful_sync_time:
                # Format date according to extractor's requirements
                modified_since = self.sync_state.last_successful_sync_time
                incremental_config = self.mapping.mapping_config.get("incremental", {})
                filter_format = incremental_config.get(
                    "timestamp_filter_format",
                    "'modified_date > '{value}'",  # Default format
                )

                # Handle both string and list formats for timestamp_filter_format
                if isinstance(filter_format, str):
                    params["filter"] = filter_format.format(
                        value=modified_since.strftime("%Y-%m-%d")
                    )
                elif isinstance(filter_format, list):
                    # Handle the list format by constructing a filter query
                    # Assuming the format is [['field', 'operator', 'value_template']]
                    filter_query = []
                    for filter_item in filter_format:
                        if len(filter_item) >= 3:
                            field, operator, value_template = filter_item
                            value = value_template.format(
                                value=modified_since.strftime("%Y-%m-%d")
                            )
                            filter_query.append([field, operator, value])
                    params["filter"] = filter_query
                else:
                    logger.warning(
                        f"Unsupported timestamp_filter_format type: {type(filter_format)}"
                    )

            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=0,
                status="started",
                details={
                    "entity_type": self.mapping.entity_type,
                    "incremental": incremental,
                    "batch_size": batch_size,
                },
            )

            try:
                # Extract data
                with self.extractor:
                    source_data = self.extractor.extract(
                        query_params=params, fail_on_filter_error=fail_on_filter_error
                    )

                log_data_sync_event(
                    source=self.mapping.source.name,
                    destination=self.mapping.target.name,
                    record_count=len(source_data),
                    status="extracted",
                    details={
                        "entity_type": self.mapping.entity_type,
                        "incremental": incremental,
                    },
                )

                # Process data in batches
                total_processed = 0
                total_success = 0
                total_failed = 0

                for i in range(0, len(source_data), batch_size):
                    batch = source_data[i : i + batch_size]
                    logger.info(
                        f"Processing batch {i//batch_size + 1} "
                        f"({len(batch)} records)"
                    )

                    # Process batch
                    batch_success, batch_failed = self._process_batch(batch)

                    total_success += batch_success
                    total_failed += batch_failed
                    total_processed += len(batch)

                    # Update log with progress
                    self.sync_log.records_processed = total_processed
                    self.sync_log.records_succeeded = total_success
                    self.sync_log.records_failed = total_failed
                    self.sync_log.save()

                # Mark sync as completed
                self.sync_log.mark_completed(total_success, total_failed)
                self.sync_state.update_sync_completed(success=total_failed == 0)

                # Log final status
                status = "completed" if total_failed == 0 else "completed_with_errors"
                log_data_sync_event(
                    source=self.mapping.source.name,
                    destination=self.mapping.target.name,
                    record_count=total_processed,
                    status=status,
                    details={
                        "entity_type": self.mapping.entity_type,
                        "succeeded": total_success,
                        "failed": total_failed,
                    },
                )

                return self.sync_log

            except Exception as e:
                logger.exception("Error during sync pipeline execution")
                # Log error and mark sync as failed
                self.sync_log.mark_failed(
                    error_message=str(e), trace=traceback.format_exc()
                )

                # Log failure event
                log_data_sync_event(
                    source=self.mapping.source.name,
                    destination=self.mapping.target.name,
                    record_count=0,
                    status="failed",
                    details={"entity_type": self.mapping.entity_type, "error": str(e)},
                )

                return self.sync_log

        except Exception:
            logger.exception("Error initializing sync pipeline")
            raise

    def _process_batch(self, batch: List[Dict[str, Any]]) -> tuple:
        """Process a batch of records.

        Args:
            batch: List of records to process

        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        try:
            # Transform the batch
            transformed_data = self.transformer.transform(batch)
            if not transformed_data:
                logger.warning("Transformer returned no data for batch")
                for record in batch:
                    failure_count += 1
                    cleaned_record = self._clean_for_json(record)
                    SyncLogDetail.objects.create(
                        sync_log=self.sync_log,
                        record_id=record.get("id", str(record)),
                        status="failed",
                        error_message="Transformation produced no data",
                        record_data={"source": cleaned_record},
                    )
                return success_count, failure_count

            # Load transformed records
            try:
                # Load all transformed records at once
                result = self.loader.load(transformed_data)

                # Log success for each record
                for record, transformed in zip(batch, transformed_data):
                    cleaned_record = self._clean_for_json(record)
                    cleaned_transformed = self._clean_for_json(transformed)
                    cleaned_result = self._clean_for_json(result)
                    SyncLogDetail.objects.create(
                        sync_log=self.sync_log,
                        record_id=record.get("id", str(record)),
                        status="success",
                        record_data={
                            "source": cleaned_record,
                            "transformed": cleaned_transformed,
                            "result": cleaned_result,
                        },
                    )
                    success_count += 1

            except Exception as e:
                # Log failure for each record
                error_msg = str(e)
                logger.error("Failed to load transformed records: {}".format(error_msg))
                for record in batch:
                    failure_count += 1
                    cleaned_record = self._clean_for_json(record)
                    SyncLogDetail.objects.create(
                        sync_log=self.sync_log,
                        record_id=record.get("id", str(record)),
                        status="failed",
                        error_message=f"Loading failed: {error_msg}",
                        record_data={"source": cleaned_record},
                    )

        except Exception as e:
            # Log batch transformation failure
            error_msg = str(e)
            logger.error("Failed to transform batch: {}".format(error_msg))
            for record in batch:
                failure_count += 1
                cleaned_record = self._clean_for_json(record)
                SyncLogDetail.objects.create(
                    sync_log=self.sync_log,
                    record_id=record.get("id", str(record)),
                    status="failed",
                    error_message=f"Batch transformation failed: {error_msg}",
                    record_data={"source": cleaned_record},
                )

        return success_count, failure_count

    def _clean_for_json(self, data):
        """Clean data to ensure it can be JSON serialized.

        Args:
            data: Data to clean

        Returns:
            Cleaned data safe for JSON serialization
        """
        if isinstance(data, dict):
            return {k: self._clean_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_for_json(v) for v in data]
        elif isinstance(data, (datetime, timezone.datetime)):
            return data.isoformat()
        elif isinstance(data, (int, float, str, bool, type(None))):
            # Handle NaN values
            if isinstance(data, float) and math.isnan(data):
                return None
            return data
        elif hasattr(data, "_asdict") and callable(data._asdict):
            # Handle NamedTuple objects like LoadResult
            return self._clean_for_json(data._asdict())
        elif hasattr(data, "to_dict") and callable(data.to_dict):
            # Handle objects with to_dict method like LoadResult from base.py
            return self._clean_for_json(data.to_dict())
        else:
            return str(data)


class PipelineFactory:
    """Factory for creating sync pipelines from configurations."""

    @classmethod
    def create_pipeline(
        cls,
        mapping: SyncMapping,
        extractor_class: Optional[Type[BaseExtractor]] = None,
        transformer_class: Optional[Type[BaseTransformer]] = None,
        loader_class: Optional[Type[BaseLoader]] = None,
    ) -> SyncPipeline:
        """Create a sync pipeline from a mapping configuration.

        Args:
            mapping: SyncMapping instance with configuration
            extractor_class: Optional extractor class override
            transformer_class: Optional transformer class override
            loader_class: Optional loader class override

        Returns:
            SyncPipeline: Configured pipeline instance
        """
        try:
            # Get source and target configs
            source_config = mapping.source.config
            target_config = mapping.target.config
            mapping_config = mapping.mapping_config

            logger.info("Creating pipeline components...")
            logger.info(f"Source config: {source_config}")
            logger.info(f"Target config: {target_config}")
            logger.info(f"Mapping config: {mapping_config}")

            # Import and instantiate components based on config or overrides
            extractor = cls._create_component(
                extractor_class
                or cls._import_class(source_config.get("extractor_class")),
                source_config,
            )
            logger.info(f"Created extractor: {extractor.__class__.__name__}")

            # Get transformer class from mapping config
            transformer = cls._create_component(
                transformer_class
                or cls._import_class(mapping_config.get("transformer_class")),
                mapping_config,
            )
            logger.info(f"Created transformer: {transformer.__class__.__name__}")

            loader = cls._create_component(
                loader_class or cls._import_class(target_config.get("loader_class")),
                target_config,
            )
            logger.info(f"Created loader: {loader.__class__.__name__}")

            return SyncPipeline(mapping, extractor, transformer, loader)

        except Exception:
            logger.exception("Error creating pipeline components")
            raise

    @staticmethod
    def _import_class(class_path: str) -> Type:
        """Import a class from its dotted path.

        Args:
            class_path: Dotted import path to the class

        Returns:
            The imported class
        """
        module_path, class_name = class_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)

    @staticmethod
    def _create_component(component_class: Type, config: Dict[str, Any]) -> Any:
        """Create a component instance from its class and config.

        Args:
            component_class: The component class
            config: Configuration dictionary

        Returns:
            Instantiated component
        """
        # For DjangoModelLoader, ensure required fields are set
        if component_class.__name__ == 'DjangoModelLoader':
            # Extract model path if provided
            model_path = config.get('model_path')
            if model_path and 'app_name' not in config:
                # Extract app_name and model_name from model_path
                path_parts = model_path.split('.')
                if len(path_parts) >= 3:
                    # Extract model_name from last part
                    config['model_name'] = path_parts[-1]  # Last element
                    
                    # Extract app_name 
                    if path_parts[-2] == 'models':
                        # If the path follows the pattern app.models.Model,
                        # then app_name is the part before 'models'
                        if len(path_parts) >= 3:
                            config['app_name'] = path_parts[-3]
                    else:
                        # Otherwise use the second-to-last segment
                        config['app_name'] = path_parts[-2]
            
            # Set a default unique_field if not provided
            if 'unique_field' not in config:
                config['unique_field'] = config.get('key_field') or 'legacy_id'

        return component_class(config)
