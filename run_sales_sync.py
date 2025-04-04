#!/usr/bin/env python
"""
Script to run the sales record sync with specific parameters.
This script is used to overcome the SyncLogDetail import issue.
"""

import os
import sys
import django
import argparse
from datetime import timedelta
from pathlib import Path
import logging

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Function to load environment variables from .env file
def load_env_file(env_path):
    """Load environment variables from .env file."""
    print(f"Checking for environment file at: {env_path}")
    if not os.path.exists(env_path):
        print(f"Environment file not found: {env_path}")
        return False
    
    print(f"Loading environment from {env_path}")
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")
    return True

# Load environment variables from .env.dev
env_file = project_root / "config" / "env" / ".env.dev"
load_env_file(env_file)

# Setup Django environment with the correct settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

# Now import Django models and functions
from django.utils import timezone
from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)


def main():
    """Run sales record sync with days=10 parameter."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run sales record sync')
    parser.add_argument('--days', type=int, default=10, help='Number of days to look back')
    parser.add_argument('--top', type=int, default=0, help='Limit to top N records')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Check if DB_PASSWORD is set
    db_password = os.environ.get("DB_PASSWORD")
    if db_password:
        print(f"Database password is set (length: {len(db_password)})")
    else:
        print("WARNING: Database password is NOT SET")

    print(f"Starting sales record sync with days={args.days} parameter")
    if args.top > 0:
        print(f"Limiting to top {args.top} sales records")
    
    # Calculate date N days ago
    days_ago = args.days
    modified_since = timezone.now() - timedelta(days=days_ago)
    date_str = modified_since.strftime("%Y-%m-%d")
    
    # Create query parameters with date filter for the legacy ERP system
    query_params = {
        "filter_query": [
            ["modified_date", ">", date_str]
        ]
    }
    
    # Add top limit if specified
    if args.top > 0:
        query_params["$top"] = args.top
    
    print(f"Filtering records modified since {date_str} ({days_ago} days ago)")
    logger.info(f"Using query params: {query_params}")
    
    # Get sales record mappings (IDs 3 and 4 based on setup command output)
    try:
        # Get sales record mappings
        sales_record_mapping = SyncMapping.objects.get(id=3)
        sales_record_items_mapping = SyncMapping.objects.get(id=4)
        
        # Process sales records first
        print(f"Processing sales records mapping: {sales_record_mapping}")
        sales_pipeline = PipelineFactory.create_pipeline(sales_record_mapping)
        
        # For top N records, first fetch the records to get their IDs
        if args.top > 0:
            # Extract data only (no transform/load)
            sales_records = sales_pipeline.fetch_data(query_params=query_params)
            print(f"Fetched {len(sales_records)} sales records")
            
            # Extract the parent IDs from the sales records
            parent_ids = [record.get('AbsNr') for record in sales_records if record.get('AbsNr')]
            
            # Get unique IDs to avoid duplicate filters
            unique_parent_ids = list(set(parent_ids))
            print(f"Extracted {len(unique_parent_ids)} unique parent IDs for filtering line items")
            
            # Now run the sales record pipeline with this data
            sales_result = sales_pipeline.run_with_data(
                data=sales_records,
                incremental=True,
                batch_size=100,
                query_params=query_params
            )
            
            # Create item filter format that works with OData
            # Instead of multiple "AbsNr = X" conditions, use a single "AbsNr IN (list)" condition
            # The filter is a list with a single entry that has the format:
            # ["AbsNr", "in", [id1, id2, id3, ...]]
            items_query_params = {
                "filter_query": [
                    ["modified_date", ">", date_str],
                    ["AbsNr", "in", unique_parent_ids]
                ]
            }
            
            # Process sales record items with parent ID filtering
            print(f"Processing sales record items mapping with parent ID filtering: "
                  f"{sales_record_items_mapping}")
            items_pipeline = PipelineFactory.create_pipeline(
                sales_record_items_mapping
            )
            items_result = items_pipeline.run(
                incremental=True,
                batch_size=100,
                query_params=items_query_params
            )
        else:
            # Regular processing without top limit
            sales_result = sales_pipeline.run(
                incremental=True,
                batch_size=100,
                query_params=query_params
            )
            
            # Then process sales record items
            print(f"Processing sales record items mapping: "
                  f"{sales_record_items_mapping}")
            items_pipeline = PipelineFactory.create_pipeline(
                sales_record_items_mapping
            )
            items_result = items_pipeline.run(
                incremental=True,
                batch_size=100,
                query_params=query_params
            )
        
        print(f"Sales records sync result: {sales_result}")
        print(f"Sales record items sync result: {items_result}")
        print("Sales record sync completed successfully")
        
    except SyncMapping.DoesNotExist as e:
        print(f"Error: Mapping not found: {e}")
    except Exception as e:
        print(f"Error during sync: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 