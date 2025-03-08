#!/usr/bin/env python
"""Simple test for the sync system with real legacy API."""

import os
import sys
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.config.settings.base')
import django
django.setup()

# Import after Django setup
from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor
from pyerp.external_api.legacy_erp.client import SimpleAPIClient


def run_simple_test():
    """Test direct extraction from legacy API."""
    try:
        # Create a direct client
        environment = "live"
        table_name = "Artikel_Familie"  # Parent products
        
        logger.info(f"Testing direct legacy API connection to {table_name} table")
        
        # Create and configure the extractor
        extractor = LegacyAPIExtractor(config={
            'environment': environment,
            'table_name': table_name,
            'page_size': 10,
            'modified_date_field': 'Modified'
        })
        
        # Connect to legacy API
        extractor.connect()
        
        # Extract data (no date filtering)
        records = extractor.extract()
        
        # Print some statistics
        logger.info(f"Successfully extracted {len(records)} records from {table_name}")
        
        if records:
            # Show first record keys and some sample values
            first_record = records[0]
            logger.info(f"Record keys: {list(first_record.keys())[:10]}...")
            
            # Show some common fields if they exist
            for field in ['Bezeichnung', 'UID', 'created_date', 'modified_date']:
                if field in first_record:
                    logger.info(f"Sample field '{field}': {first_record[field]}")
        
        # Try an incremental extraction with date filter
        one_week_ago = datetime.now() - timedelta(days=7)
        logger.info(f"\nAttempting date-filtered extraction (since {one_week_ago.strftime('%Y-%m-%d')})")
        
        # Extract with date filter
        filtered_records = extractor.extract(query_params={
            'modified_date': {
                'gt': one_week_ago.isoformat()
            }
        })
        
        logger.info(f"Extracted {len(filtered_records)} records with date filter")
        
        logger.info("\nTest completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_simple_test() 