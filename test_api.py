#!/usr/bin/env python
"""
Test script for the legacy ERP API connection.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from django.conf import settings
from pyerp.external_api.legacy_erp.client import LegacyERPClient
from pyerp.external_api.legacy_erp.settings import API_ENVIRONMENTS

# Set pandas display options
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

def main():
    """Main test function."""
    # Print environment settings
    print("API Environment settings:")
    for env_name, env_config in API_ENVIRONMENTS.items():
        print(f"  {env_name}:")
        print(f"    base_url: {env_config.get('base_url')}")
        
    print("\nInitializing Legacy ERP client...")
    client = LegacyERPClient(environment="live")
    
    # Print the client's base URL
    print(f"Client base URL: {client.base_url}")
    
    print("\nChecking connection...")
    conn_result = client.check_connection()
    print(f"Connection status: {conn_result}")
    
    try:
        print("\nFetching production orders...")
        production_orders = client.fetch_table(
            table_name="Werksauftraege",
            top=5
        )
        print(f"Result shape: {production_orders.shape}")
        print("\nProduction orders sample:")
        print(production_orders.head())
        
    except Exception as e:
        print(f"\nError fetching data: {e}")
    
    print("\nTest completed")

if __name__ == "__main__":
    main() 