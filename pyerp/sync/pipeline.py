"""Pipeline orchestration for sync operations."""

from typing import Any, Dict, List, Optional, Type

from django.utils import timezone
from django.db import connection
from pyerp.utils.json_utils import DateTimeEncoder, json_serialize
from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.utils.constants import SyncStatus

from .extractors.base import BaseExtractor
from .transformers.base import BaseTransformer
from .loaders.base import BaseLoader
from .models import (
    SyncLog,
    # SyncLogDetail, # Comment out the problematic import
    SyncMapping,
    SyncState,
)


logger = get_logger(__name__)


class SyncPipeline:
    """
    Orchestrates extraction, transformation, and loading for sync operations.
    """

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
        # Get the next available ID using MAX(id) + 1
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM audit_synclog")
            next_id = cursor.fetchone()[0]

        # Create sync log entry with explicit ID
        start_time = timezone.now()
        self.sync_log = SyncLog.objects.create(
            id=next_id,
            entity_type=self.mapping.entity_type,
            status=SyncStatus.STARTED,
            started_at=start_time,
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            error_message=""
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
            status=SyncStatus.STARTED,
            details={
                "entity_type": self.mapping.entity_type,
                "incremental": incremental,
                "batch_size": batch_size,
            },
        )

        try:
            # Build query parameters
            params = query_params or {}
            if incremental and self.sync_state.last_sync_time:
                # Add timestamp filter for incremental sync
                params["timestamp_filter"] = self.sync_state.last_sync_time

            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=0,
                status=SyncStatus.STARTED,
                details={
                    "entity_type": self.mapping.entity_type,
                    "incremental": incremental,
                    "batch_size": batch_size,
                },
            )

            # Extract data
            with self.extractor:
                source_data = self.extractor.extract(
                    query_params=params,
                    fail_on_filter_error=fail_on_filter_error
                )

            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=len(source_data),
                status=SyncStatus.EXTRACTED,
                details={
                    "entity_type": self.mapping.entity_type,
                    "incremental": incremental,
                },
            )

            # Initialize counts before the loop
            self.sync_log.records_processed = 0
            self.sync_log.records_created = 0
            self.sync_log.records_updated = 0
            self.sync_log.records_failed = 0
            self.sync_log.save(update_fields=['records_processed', 'records_created', 'records_updated', 'records_failed'])

            # Process data in batches
            total_processed = 0
            total_created = 0
            total_updated = 0
            total_failed = 0

            # Process all records in a single batch if batch_size is 0
            if batch_size <= 0:
                batch_size = len(source_data) if source_data else 0

            # Process data in batches
            for i in range(0, len(source_data), batch_size):
                batch = source_data[i:i + batch_size]
                created_count, updated_count, failure_count = self._process_batch(batch)

                total_processed += len(batch)
                total_created += created_count
                total_updated += updated_count
                total_failed += failure_count

                # Update sync log with progress
                self.sync_log.records_processed = total_processed
                self.sync_log.records_created = total_created
                self.sync_log.records_updated = total_updated
                self.sync_log.records_failed = total_failed
                self.sync_log.save()

            # Update sync state on successful completion
            success = total_failed == 0
            self.sync_state.update_sync_completed(success=success)

            # Update final sync log status and completion time
            self.sync_log.status = SyncStatus.COMPLETED if success else SyncStatus.COMPLETED_WITH_ERRORS
            self.sync_log.completed_at = timezone.now()
            self.sync_log.save()

            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=total_processed,
                status=SyncStatus.COMPLETED,
                details={
                    "entity_type": self.mapping.entity_type,
                    "created_count": total_created,
                    "updated_count": total_updated,
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
                self.sync_log.status = SyncStatus.FAILED
                self.sync_log.error_message = error_msg
                self.sync_log.completed_at = timezone.now()
                self.sync_log.save()
            
            # Log the event
            log_data_sync_event(
                source=self.mapping.source.name,
                destination=self.mapping.target.name,
                record_count=0,
                status=SyncStatus.FAILED,
                details={
                    "entity_type": self.mapping.entity_type,
                    "error": error_msg,
                },
            )
            
            # Return the failed log, don't re-raise
            return self.sync_log

    def _process_batch(self, batch: List[Dict[str, Any]]) -> tuple:
        """Process a batch of records.

        Args:
            batch: List of records to process

        Returns:
            tuple: (created_count, updated_count, failure_count)
        """
        created_count = 0
        updated_count = 0
        failure_count = 0
        all_transformed_records = [] # Collect successfully transformed records

        logger.debug("==> [_process_batch] Starting processing for batch of size %s", len(batch))

        for record in batch: # Iterate through each record in the batch
            # Use a consistent way to get ID for logging
            record_id_str = str(record.get("__KEY", record.get("Nummer", "unknown_id")))
            logger.debug("==> [_process_batch] Transforming record ID: %s", record_id_str)
            try:
                # Transform single record - correctly calling with dict
                transformed_record = self.transformer.transform(record)

                # Transformer returns a list; expect 0 or 1 item for a single input record
                if transformed_record: # Check if the list is not empty
                    logger.debug("<== [_process_batch] Successfully transformed record ID: %s", record_id_str)
                    all_transformed_records.append(transformed_record)
                else:
                    # Log or handle transformation failure for this record
                    logger.warning("<== [_process_batch] Transformation returned None for record ID: %s", record_id_str)
                    failure_count += 1
            except Exception as transform_error:
                # Log transformation error for this specific record
                logger.error("<== [_process_batch] Error transforming record ID: %s - Error: %s", record_id_str, transform_error, exc_info=True)
                failure_count += 1

        logger.debug("<== [_process_batch] Finished transforming batch. Transformed %s / Failed %s.", len(all_transformed_records), failure_count)

        # Load all successfully transformed records from the batch at once
        if all_transformed_records:
            logger.debug("==> [_process_batch] Loading %s transformed records...", len(all_transformed_records))
            try:
                load_result = self.loader.load(all_transformed_records) # Load collected records
                logger.debug("<== [_process_batch] Completed loading. Created: %s, Updated: %s, Errors: %s", load_result.created, load_result.updated, load_result.errors)
                created_count = load_result.created
                updated_count = load_result.updated
                # Add any load errors to the failure count
                failure_count += load_result.errors
                # Log details if available and needed (optional)
                # if load_result.errors > 0 and hasattr(load_result, 'error_details'):
                #     logger.warning(f"Loading errors encountered: {load_result.error_details}")
            except Exception as load_error:
                # Log batch loading failure
                logger.error("<== [_process_batch] Error loading batch: %s", load_error, exc_info=True)
                # If loading fails for the whole batch, mark all transformed records as failed
                failure_count += len(all_transformed_records)
                created_count = 0 # Reset counts as load failed
                updated_count = 0
        else:
             logger.debug("[_process_batch] No records transformed successfully, skipping load step.")

        logger.debug("<== [_process_batch] Finished processing batch. Result: (Created: %s, Updated: %s, Failed: %s)", created_count, updated_count, failure_count)
        return created_count, updated_count, failure_count

    def _clean_for_json(self, data):
        """Clean data recursively to ensure it can be JSON serialized.

        Args:
            data: Data to clean

        Returns:
            Cleaned data safe for JSON serialization
        """
        # Use the utility function which handles recursion and types
        return json_serialize(data)

    def fetch_data(self, query_params=None, fail_on_filter_error=False):
        """Fetch data from source without processing it.
        
        This method allows for data to be fetched once and reused across multiple pipelines.
        
        Args:
            query_params: Query parameters for filtering data
            fail_on_filter_error: Whether to fail if filter doesn't work
            
        Returns:
            List of records fetched from the source
        """
        logger.info("Fetching data in extract-only mode...")
        
        # Initialize the extractor
        try:
            # Make sure the extractor is properly initialized
            if hasattr(self.extractor, 'initialize') and callable(self.extractor.initialize):
                self.extractor.initialize()
            
            # Use a context manager to ensure proper connection handling
            with self.extractor:
                # Extract data from source without transforming or loading
                logger.debug("==> [fetch_data] Calling self.extractor.extract() with params: %s", query_params)
                records = self.extractor.extract(
                    query_params=query_params,
                    fail_on_filter_error=fail_on_filter_error
                )
                logger.debug("<== [fetch_data] Returned from self.extractor.extract(). Found %s records.", len(records))
                logger.info(f"Fetched {len(records)} records")
                return records
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
        
    def run_with_data(self, data=None, incremental=True, batch_size=100, query_params=None):
        """Run the pipeline with pre-fetched data.
        
        This method uses provided data instead of extracting it from source.
        
        Args:
            data: Pre-fetched data to use
            incremental: Whether to run in incremental mode
            batch_size: Size of batches to process
            query_params: Original query parameters used for extraction
            
        Returns:
            SyncLog: The sync log for this run
        """
        if not data:
            raise ValueError("No data provided for run_with_data method")
        
        # Apply top limit if specified in query_params
        if query_params and "$top" in query_params and isinstance(data, list):
            top_limit = int(query_params["$top"])
            if len(data) > top_limit:
                logger.info(f"Limiting pre-fetched data to top {top_limit} records (from {len(data)} total)")
                data = data[:top_limit]
        
        logger.info(f"Running pipeline with {len(data)} pre-fetched records")
        
        # Create sync log
        sync_log = self.create_sync_log(incremental=incremental)
        
        # Process in batches
        total_count = len(data)
        processed_count = 0
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        # Process records in batches
        for start_idx in range(0, total_count, batch_size):
            end_idx = min(start_idx + batch_size, total_count)
            batch = data[start_idx:end_idx]
            batch_size_actual = len(batch)
            
            logger.info(f"Processing batch {start_idx//batch_size + 1}: {start_idx} to {end_idx-1}")
            
            try:
                # Process this batch
                created, updated, failed = self._process_batch(batch)
                
                # Update counters
                processed_count += batch_size_actual
                created_count += created
                updated_count += updated
                failed_count += failed
                
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                failed_count += batch_size_actual
                processed_count += batch_size_actual
        
        # Update sync log
        sync_log.records_processed = processed_count
        sync_log.records_created = created_count
        sync_log.records_updated = updated_count
        sync_log.records_failed = failed_count
        sync_log.status = SyncStatus.COMPLETED
        sync_log.completed_at = timezone.now()
        sync_log.save()
        
        return sync_log

    def create_sync_log(self, incremental=True):
        """Create a new sync log entry.
        
        Args:
            incremental: Whether this is an incremental sync
            
        Returns:
            SyncLog: The newly created sync log entry
        """
        # Get the next available ID using MAX(id) + 1
        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM audit_synclog")
            next_id = cursor.fetchone()[0]

        # Create sync log entry with explicit ID
        start_time = timezone.now()
        sync_log = SyncLog.objects.create(
            id=next_id,
            entity_type=self.mapping.entity_type,
            status=SyncStatus.STARTED,
            started_at=start_time,
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            error_message=""
        )
        
        # Update the sync state
        self.sync_state.update_sync_started()
        
        # Log the event
        log_data_sync_event(
            source=self.mapping.source.name,
            destination=self.mapping.target.name,
            record_count=0,
            status=SyncStatus.STARTED,
            details={
                "entity_type": self.mapping.entity_type,
                "incremental": incremental,
            },
        )
        
        return sync_log


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

            # Determine the extractor class
            if extractor_class and isinstance(extractor_class, type):
                extractor_class_instance = extractor_class
            else:
                extractor_class_instance = cls._import_class(
                    # Use provided path string or path from config
                    extractor_class or source_config.get("extractor_class")
                )

            # Extract the inner config values from source_config
            base_extractor_config = source_config.copy() if source_config else {}
            
            # Check if config field exists and extract it
            if "config" in base_extractor_config:
                inner_config = base_extractor_config.pop("config", {})
                merged_extractor_config = inner_config.copy()  # Start with inner config values
                # Add the rest of the source_config fields
                merged_extractor_config.update(base_extractor_config)
            else:
                merged_extractor_config = base_extractor_config.copy()

            # Merge with mapping's extractor_config if present
            if mapping_config and "extractor_config" in mapping_config:
                merged_extractor_config.update(mapping_config["extractor_config"])

            logger.info(f"Extractor config after merging: {merged_extractor_config}")

            # Create the extractor using the merged config
            extractor = cls._create_component(
                extractor_class_instance,
                merged_extractor_config,
            )
            logger.info(
                f"Created extractor: {extractor.__class__.__name__} "
                f"with config: {merged_extractor_config}"
            )

            # Get transformer class
            transformer_instance = None
            if transformer_class and isinstance(transformer_class, type):
                transformer_instance = transformer_class
            else:
                # Determine path from argument or config
                transformer_class_path = (
                    transformer_class  # String path from arg
                    or mapping_config.get("transformer_class")
                    or mapping_config.get("transformation", {}).get(
                        "transformer_class"
                    )
                    or mapping_config.get("transformation", {}).get("class")
                )
                if transformer_class_path:
                    transformer_instance = cls._import_class(
                        transformer_class_path
                    )
                else:
                    # Handle case where no transformer class is defined
                    # You might want a default or raise an error
                    logger.warning(
                        "No transformer class defined for mapping."
                    )
                    # Assign a default pass-through transformer?
                    # from .transformers.base import BaseTransformer
                    # transformer_instance = BaseTransformer
                    raise ValueError(
                        "Transformer class must be provided or "
                        "defined in mapping config."
                    )

            transformer = cls._create_component(
                transformer_instance,
                mapping_config.get("transformation", {}),
            )
            logger.info(
                f"Created transformer: {transformer.__class__.__name__}"
            )

            # Get loader class
            loader_instance = None
            if loader_class and isinstance(loader_class, type):
                loader_instance = loader_class
            else:
                # Determine path from argument or config
                loader_class_path = (
                    loader_class  # String path from arg
                    or target_config.get("loader_class")
                    or mapping_config.get("loader", {}).get("class")
                    # Consider removing default fallback
                    or "pyerp.sync.loaders.django_model.DjangoModelLoader"
                )
                if loader_class_path:
                    loader_instance = cls._import_class(loader_class_path)
                else:
                    raise ValueError(
                        "Loader class must be provided or "
                        "defined in target/mapping config."
                    )

            logger.info(
                f"Using loader class: "
                f"{loader_instance.__name__ if loader_instance else 'None'}"
            )

            # Merge target_config with mapping's loader_config
            merged_loader_config = target_config.copy()
            if mapping_config and "loader_config" in mapping_config:
                merged_loader_config.update(mapping_config["loader_config"])

            loader = cls._create_component(
                loader_instance,
                merged_loader_config,
            )
            logger.info(
                f"Created loader: {loader.__class__.__name__} "
                f"with config: {merged_loader_config}"
            )

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
    def _create_component(
        component_class: Type,
        config: Dict[str, Any]
    ) -> Any:
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
