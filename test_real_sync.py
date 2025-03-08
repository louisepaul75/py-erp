#!/usr/bin/env python
"""Test the sync system with the real legacy API."""

import os
import sys
import logging
import django
import json
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import math
import pandas as pd
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.config.settings.base')
django.setup()

# Import after Django setup
from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.sync.pipeline import PipelineFactory
from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor
from pyerp.sync.transformers.base import BaseTransformer
from pyerp.sync.loaders.base import BaseLoader
from pyerp.external_api.legacy_erp.client import SimpleAPIClient
from pyerp.sync.pipeline import SyncPipeline


def verify_legacy_api_connection():
    """Test connection to the legacy API."""
    source = SyncSource.objects.get(name='Legacy System')
    config = source.config
    environment = config.get('environment', 'live')
    
    logger.info(f"Testing legacy API connection with environment: {environment}")
    
    try:
        client = SimpleAPIClient(environment=environment)
        logger.info("Legacy API client initialized")
        
        # Test connection to API
        table_name = "Artikel_Familie"
        result = client.fetch_table(
            table_name=table_name, 
            top=5,
            skip=0
        )
        
        if isinstance(result, pd.DataFrame) and not result.empty:
            logger.info(f"Successfully connected to legacy API!")
            logger.info(f"Retrieved {len(result)} records from {table_name}")
            logger.info(f"Columns: {list(result.columns)}")
            return True
        else:
            logger.error("Failed to retrieve data from legacy API")
            return False
    
    except Exception as e:
        logger.error(f"Error connecting to legacy API: {str(e)}")
        return False


class SimpleTransformer(BaseTransformer):
    """Simple transformer for testing."""
    
    def transform(self, record):
        """Transform a record from source to target format."""
        # Simple pass-through with minimal transformation
        transformed = {
            'external_id': record.get('__KEY', '') or record.get('UID', ''),
            'name': record.get('Bezeichnung', ''),
            'active': record.get('Varianten_aktiv', True),
            'sync_data': clean_json_data(record),  # Store full record data for reference
        }
        
        return transformed


def clean_json_data(data):
    """Clean data to ensure it can be serialized to JSON.
    
    Handles:
    - NaN/inf values in pd.DataFrame records
    - Complex objects that aren't JSON serializable
    """
    if data is None:
        return None
    
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items()}
    
    if isinstance(data, list):
        return [clean_json_data(item) for item in data]
    
    # Convert numpy/pandas NaN, infinity to None/null
    if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return None
    
    # Handle numpy numeric types
    if isinstance(data, (np.integer, np.floating)):
        return data.item()
    
    # Convert datetime objects to ISO format strings
    if isinstance(data, datetime):
        return data.isoformat()
    
    return data


class LoggingLoader(BaseLoader):
    """Simple loader that just logs the records."""
    
    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields."""
        return []
    
    def prepare_record(self, record: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare a record for loading.
        
        Args:
            record: The transformed record to load
            
        Returns:
            Tuple of (lookup criteria, prepared record)
        """
        # Use external_id for lookup
        lookup = {
            'external_id': record.get('external_id', '')
        }
        
        # Return lookup criteria and the record itself
        return lookup, record
    
    def load_record(
        self,
        lookup_criteria: Dict[str, Any],
        record: Dict[str, Any],
        update_existing: bool = True
    ) -> Optional[Any]:
        """Load a single record into the target system.
        
        Args:
            lookup_criteria: Criteria to find existing record
            record: The record data to load
            update_existing: Whether to update if record exists
            
        Returns:
            The loaded/updated record or None if error
        """
        # Just log the record for testing purposes
        external_id = lookup_criteria.get('external_id', 'unknown')
        
        logger.info(f"Would load record: {external_id}")
        logger.info(f"  Name: {record.get('name', '')}")
        logger.info(f"  Active: {record.get('active', False)}")
        
        # Return a dummy "loaded" record
        return {
            'id': 123,
            'external_id': external_id,
            'status': 'logged'
        }
    
    def load(self, data):
        """Load a batch of records into the target system."""
        loaded_records = []
        errors = []
        
        for record in data:
            try:
                # Prepare the record
                lookup, prepared_record = self.prepare_record(record)
                
                # Load the record and track result
                result = self.load_record(lookup, prepared_record)
                
                if result:
                    loaded_records.append(result)
                else:
                    errors.append({'record': record, 'error': 'Failed to load'})
            
            except Exception as e:
                errors.append({'record': record, 'error': str(e)})
        
        return loaded_records, errors


def setup_test_environment(successful_env, table_name):
    """Set up the test environment with necessary sync components."""
    # Get or create the sync source
    source, _ = SyncSource.objects.get_or_create(
        name='Legacy System',
        defaults={
            'description': 'Legacy 4D database system',
            'config': {
                'environment': successful_env,
                'extractor_class': 'pyerp.sync.extractors.legacy_api.LegacyAPIExtractor'
            }
        }
    )
    
    # Update the environment if different
    if source.config.get('environment') != successful_env:
        source.config['environment'] = successful_env
        source.save()
    
    # Get or create the sync target
    target, _ = SyncTarget.objects.get_or_create(
        name='Test Logger',
        defaults={
            'description': 'Test logging target that just logs records',
            'config': {
                'loader_class': 'test_real_sync.LoggingLoader'
            }
        }
    )
    
    # Get or create the sync mapping
    mapping, _ = SyncMapping.objects.get_or_create(
        source=source,
        target=target,
        entity_type=table_name,
        defaults={
            'mapping_config': {
                'transformer_class': 'test_real_sync.SimpleTransformer',
                'page_size': 20,
                'modified_date_field': 'modified_date'  # Use the correct field name
            }
        }
    )
    
    # Update the mapping config if needed
    if mapping.mapping_config.get('modified_date_field') != 'modified_date':
        mapping.mapping_config['modified_date_field'] = 'modified_date'
        mapping.mapping_config['page_size'] = 20
        mapping.save()
    
    # Create the extractor
    extractor = LegacyAPIExtractor({
        'environment': source.config['environment'],
        'table_name': table_name,
        'page_size': mapping.mapping_config.get('page_size', 20),
        'modified_date_field': mapping.mapping_config.get('modified_date_field', 'modified_date')
    })
    
    # Create the transformer
    transformer = SimpleTransformer({})
    
    # Create the loader
    loader = LoggingLoader({})
    
    # Create the pipeline
    pipeline = SyncPipeline(
        mapping=mapping,
        extractor=extractor,
        transformer=transformer,
        loader=loader
    )
    
    return pipeline


def run_real_sync_test():
    """Run a test of the sync system using the real legacy API."""
    # First check basic API connection
    if not verify_legacy_api_connection():
        logger.error("Failed to connect to legacy API. Exiting.")
        return False
    
    # Set up the environment for testing with Artikel_Familie
    try:
        pipeline = setup_test_environment('live', 'Artikel_Familie')
        
        # Run the sync with date filtering if you want to test incremental sync
        # Use a date a week ago for testing
        sync_date = datetime.now() - timedelta(days=7)
        
        # Run the sync pipeline
        result = pipeline.run(
            incremental=True,
            query_params={
                'modified_date': {
                    'gt': sync_date.isoformat()
                }
            }
        )
        
        logger.info(f"Sync completed with status: {result.status}")
        logger.info(f"Records processed: {result.records_processed}")
        logger.info(f"Records succeeded: {result.records_succeeded}")
        logger.info(f"Records failed: {result.records_failed}")
        
        if result.error_message:
            logger.error(f"Error: {result.error_message}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error running sync test: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    run_real_sync_test() 