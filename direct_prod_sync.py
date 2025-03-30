#!/usr/bin/env python
"""
Direct script to sync production data with days parameter.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

from django.utils import timezone
from pyerp.external_api.legacy_erp import LegacyERPClient
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)

def run_production_sync():
    """Run production sync directly using the legacy ERP client."""
    # Get command line arguments
    days = 1  # Default to 1 day
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days value: {sys.argv[1]}. Using default of 1.")

    # Create date filter
    modified_since = timezone.now() - timedelta(days=days)
    date_filter = modified_since.strftime('%Y-%m-%d')
    print(f"Filtering for records modified since: {date_filter}")

    # Initialize legacy client
    client = LegacyERPClient(environment='live')
    
    # First fetch some production orders without filters to see what's available
    print("Fetching recent production orders without filters...")
    werksauftraege_recent = client.fetch_table(
        table_name='Werksauftraege',
        top=10
    )
    
    print(f"Recent production orders found: {len(werksauftraege_recent)}")
    if not werksauftraege_recent.empty:
        print("Available columns:")
        for col in werksauftraege_recent.columns:
            print(f"  - {col}")
    
    # Try to get records using date filter on the correct field (if available)
    # Look for fields like "Termin", "eingestellt", "mod_date" or "timestamp" 
    date_field = "eingestellt"  # This is creation_date in the mapping
    if date_field in werksauftraege_recent.columns:
        print(f"\nFetching production orders modified since {date_filter} using {date_field} field...")
        werksauftraege = client.fetch_table(
            table_name='Werksauftraege',
            top=100,
            filter_query=[[date_field, ">", date_filter]]
        )
        
        print(f"Production orders found: {len(werksauftraege)}")
        if not werksauftraege.empty:
            print(werksauftraege.head(2))
    
    # Similarly check for production order items
    print("\nFetching recent production order items without filters...")
    werksauftrpos_recent = client.fetch_table(
        table_name='WerksauftrPos',
        top=10
    )
    
    print(f"Recent production order items found: {len(werksauftrpos_recent)}")
    if not werksauftrpos_recent.empty:
        print("Available columns:")
        for col in werksauftrpos_recent.columns:
            print(f"  - {col}")
    
    date_field_items = "Datum_begin"  # This is start_date in the mapping
    if date_field_items in werksauftrpos_recent.columns:
        print(f"\nFetching production order items modified since {date_filter} using {date_field_items} field...")
        werksauftrpos = client.fetch_table(
            table_name='WerksauftrPos',
            top=100,
            filter_query=[[date_field_items, ">", date_filter]]
        )
        
        print(f"Production order items found: {len(werksauftrpos)}")
        if not werksauftrpos.empty:
            print(werksauftrpos.head(2))
    
    return 0

if __name__ == "__main__":
    sys.exit(run_production_sync()) 