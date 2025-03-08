"""Pipeline orchestration for sync operations."""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union
import math
import json

from django.db import transaction
from django.utils import timezone

from .extractors.base import BaseExtractor
from .transformers.base import BaseTransformer
from .loaders.base import BaseLoader
from .models import SyncLog, SyncLogDetail, SyncMapping, SyncState


logger = logging.getLogger(__name__)


class SyncPipeline:
    """Orchestrates extraction, transformation, and loading for a sync operation."""

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
        query_params: Optional[Dict[str, Any]] = None
    ) -> SyncLog:
        """Run the sync pipeline.
        
        Args:
            incremental: If True, only sync records modified since last sync
            batch_size: Number of records to process in each batch
            query_params: Optional additional query parameters
            
        Returns:
            SyncLog: The completed sync log record
        """
        # Initialize sync log
        self.sync_log = SyncLog.objects.create(
            mapping=self.mapping,
            status='started',
            is_full_sync=not incremental,
            sync_params={
                'incremental': incremental,
                'batch_size': batch_size,
                'query_params': query_params or {}
            }
        )
        
        # Update sync state
        self.sync_state.update_sync_started()
        
        # Add modified_date filter for incremental sync
        params = query_params or {}
        if incremental and self.sync_state.last_successful_sync_time:
            # Format date according to extractor's requirements
            modified_since = self.sync_state.last_successful_sync_time
            params['modified_date'] = {
                'gt': modified_since.isoformat()
            }
        
        try:
            # Extract data
            with self.extractor:
                source_data = self.extractor.extract(query_params=params)
            
            # Process data in batches
            total_processed = 0
            total_success = 0
            total_failed = 0
            
            for i in range(0, len(source_data), batch_size):
                batch = source_data[i:i+batch_size]
                
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
            
            return self.sync_log
            
        except Exception as e:
            # Log error and mark sync as failed
            logger.exception(f"Sync pipeline failed: {str(e)}")
            self.sync_log.mark_failed(
                error_message=str(e),
                trace=traceback.format_exc()
            )
            return self.sync_log

    def _process_batch(self, batch: List[Dict[str, Any]]) -> tuple:
        """Process a batch of records.
        
        Args:
            batch: List of records to process
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0
        
        for record in batch:
            try:
                # Transform the record
                transformed_data = self.transformer.transform(record)
                
                # Load the record
                result = self.loader.load(transformed_data)
                
                # Log success
                cleaned_record = self._clean_for_json(record)
                cleaned_transformed = self._clean_for_json(transformed_data)
                cleaned_result = self._clean_for_json(result)
                SyncLogDetail.objects.create(
                    sync_log=self.sync_log,
                    record_id=record.get('id', str(record)),
                    status='success',
                    record_data={
                        'source': cleaned_record,
                        'transformed': cleaned_transformed,
                        'result': cleaned_result
                    }
                )
                success_count += 1
                
            except Exception as e:
                # Log failure
                logger.error(f"Failed to process record {record.get('id', '')}: {str(e)}")
                cleaned_record = self._clean_for_json(record)
                SyncLogDetail.objects.create(
                    sync_log=self.sync_log,
                    record_id=record.get('id', str(record)),
                    status='failed',
                    error_message=str(e),
                    record_data={'source': cleaned_record}
                )
                failure_count += 1
        
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
            return [self._clean_for_json(item) for item in data]
        elif isinstance(data, float) and math.isnan(data):
            return None  # Replace NaN with None
        elif isinstance(data, (datetime, timezone.datetime)):
            return data.isoformat()  # Convert datetimes to strings
        else:
            return data


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
        """Create a pipeline from a mapping and optional component classes.
        
        Args:
            mapping: The sync mapping configuration
            extractor_class: Optional extractor class override
            transformer_class: Optional transformer class override
            loader_class: Optional loader class override
            
        Returns:
            SyncPipeline: Configured pipeline instance
        """
        # Get source and target configs
        source_config = mapping.source.config
        target_config = mapping.target.config
        mapping_config = mapping.mapping_config
        
        # Import and instantiate components based on config or overrides
        extractor = cls._create_component(
            extractor_class or cls._import_class(source_config.get('extractor_class')),
            source_config
        )
        
        transformer = cls._create_component(
            transformer_class or cls._import_class(mapping_config.get('transformer_class')),
            mapping_config
        )
        
        loader = cls._create_component(
            loader_class or cls._import_class(target_config.get('loader_class')),
            target_config
        )
        
        return SyncPipeline(mapping, extractor, transformer, loader)
    
    @staticmethod
    def _import_class(class_path: str) -> Type:
        """Import a class from its dotted path.
        
        Args:
            class_path: Dotted import path to the class
            
        Returns:
            The imported class
        """
        module_path, class_name = class_path.rsplit('.', 1)
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
        return component_class(config) 