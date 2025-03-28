"""Pipeline orchestration for sync operations."""

import json
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

import math
import pandas as pd
from django.utils import timezone
from pyerp.utils.json_utils import DateTimeEncoder, json_serialize
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
            incremental: Whether to perform an incremental sync
            batch_size: Number of records to process in each batch
            query_params: Additional query parameters for the extractor
            fail_on_filter_error: Whether to fail if filter query fails

        Returns:
            SyncLog: The sync log entry for this run
        """
        # Create sync log entry
        self.sync_log = SyncLog.objects.create(
            mapping=self.mapping,
            status="started",
            is_full_sync=not incremental,
            sync_params={
                "batch_size": batch_size,
                "query_params": query_params or {},
            },
        )

        # Update sync state
        self.sync_state.update_sync_started()

        # Build query parameters
        params = query_params or {}
        if incremental and self.sync_state.last_sync_time:
            # Add timestamp filter for incremental sync
            params["timestamp_filter"] = self.sync_state.last_sync_time

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

            # Process all records in a single batch if batch_size is 0
            if batch_size <= 0:
                batch_size = len(source_data)

            # Process data in batches
            for i in range(0, len(source_data), batch_size):
                batch = source_data[i:i + batch_size]
                success_count, failure_count = self._process_batch(batch)

                total_processed += len(batch)
                total_success += success_count
                total_failed += failure_count

                # Update sync log with progress
                self.sync_log.records_processed = total_processed
                self.sync_log.records_succeeded = total_success
                self.sync_log.records_failed = total_failed
                self.sync_log.save()

            # Update sync state on successful completion
            self.sync_state.update_sync_completed(success=True)

            # Update final sync log status
            self.sync_log.status = "completed"
            self.sync_log.save()

            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=total_processed,
                status="completed",
                details={
                    "entity_type": self.mapping.entity_type,
                    "success_count": total_success,
                    "failure_count": total_failed,
                },
            )

            return self.sync_log

        except Exception as e:
            # Log the error
            logger.exception("Error in sync pipeline")
            error_msg = str(e)

            # Update sync state
            self.sync_state.update_sync_completed(success=False)
            
            # Update error in sync log
            if self.sync_log:
                self.sync_log.status = "failed"
                self.sync_log.error_message = error_msg
                
                # Ensure all fields are JSON serializable
                if hasattr(self.sync_log, 'sync_params') and self.sync_log.sync_params:
                    self.sync_log.sync_params = json_serialize(self.sync_log.sync_params)
                
                try:
                    self.sync_log.save()
                except Exception as save_error:
                    logger.error(f"Error saving sync log: {save_error}")
            
            # Log the event
            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=0,
                status="failed",
                details={
                    "entity_type": self.mapping.entity_type,
                    "error": error_msg,
                },
            )
            
            # Re-raise the exception
            raise

    def _process_batch(self, batch: List[Dict[str, Any]]) -> tuple:
        """Process a batch of records.

        Args:
            batch: List of records to process

        Returns:
            tuple: (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        try:
            # Transform batch
            transformed_records = self.transformer.transform(batch)

            # Load transformed records
            load_result = self.loader.load(transformed_records)
            
            # Process load results - LoadResult is an object, not a dictionary
            # Count the successes and failures
            success_count = load_result.created + load_result.updated
            failure_count = load_result.errors
            
            # Create log entries for errors
            for error_detail in load_result.error_details:
                SyncLogDetail.objects.create(
                    sync_log=self.sync_log,
                    record_id=str(error_detail.get("record", {}).get("id", "unknown")),
                    status="failed",
                    error_message=error_detail.get("error", "Unknown error"),
                    record_data={
                        "source": self._clean_for_json(error_detail.get("record", {})),
                    },
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
        return json_serialize(data)


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
            transformer_class_path = (
                transformer_class
                or mapping_config.get("transformer_class")
                or mapping_config.get("transformation", {}).get("transformer_class")
                or mapping_config.get("transformation", {}).get("class")
            )
            transformer = cls._create_component(
                cls._import_class(transformer_class_path),
                mapping_config.get("transformation", {}),
            )
            logger.info(f"Created transformer: {transformer.__class__.__name__}")

            # Get loader class from config
            loader_class_path = None
            if loader_class:
                loader_class_path = loader_class
            else:
                # Try multiple possible locations for the loader class
                loader_class_path = (
                    target_config.get("loader_class")
                    or mapping_config.get("loader", {}).get("class")
                    or "pyerp.sync.loaders.django_model.DjangoModelLoader"  # Default fallback
                )
            
            logger.info(f"Using loader class: {loader_class_path}")
            
            loader = cls._create_component(
                cls._import_class(loader_class_path),
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
