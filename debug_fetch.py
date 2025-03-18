#!/usr/bin/env python
"""
Debug script for the legacy ERP API fetch_table method.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Configure logging before anything else
logging.basicConfig(level=logging.DEBUG)

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set Django settings module before importing Django modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.local")

# Import Django and initialize
import django
django.setup()

from django.conf import settings
from pyerp.external_api.legacy_erp.client import LegacyERPClient
from pyerp.external_api.legacy_erp.settings import API_ENVIRONMENTS
from pyerp.utils.logging import get_logger
import requests

# Configure logging
logger = get_logger(__name__)

# Store the original request method for Session
original_request = requests.Session.request

def trace_request(self, method, url, **kwargs):
    """Monkey patch to trace request details."""
    print(f"\n==== OUTGOING REQUEST ====")
    print(f"Method: {method}")
    print(f"URL: {url}")
    print(f"Headers: {kwargs.get('headers', 'None')}")
    print(f"Cookies: {kwargs.get('cookies', 'None')}")
    
    response = original_request(self, method, url, **kwargs)
    
    print(f"\n==== RESPONSE DETAILS ====")
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Cookies: {response.cookies}")
    return response

def main():
    """Main debug function."""
    # Monkey patch requests to trace all HTTP requests
    requests.Session.request = trace_request
    
    print("\n==== Initializing Legacy ERP Client ====")
    client = LegacyERPClient(environment="live")
    
    # Print the client's base URL
    print(f"Client base URL: {client.base_url}")
    
    # Check connection first
    print("\n==== Testing Connection ====")
    connection_result = client.check_connection()
    print(f"Connection result: {connection_result}")
    
    # Try to fetch a table
    print("\n==== Testing fetch_table ====")
    try:
        print("Fetching table 'Werksauftraege'...")
        result = client.fetch_table(
            table_name="Werksauftraege",
            top=5
        )
        print(f"Successfully fetched data. Shape: {result.shape}")
        print("Sample data:")
        print(result.head())
    except Exception as e:
        print(f"Error fetching table: {e}")
        print(f"Error type: {type(e)}")
    
    # Restore original requests method
    requests.Session.request = original_request
    
    print("\nDebug completed")

if __name__ == "__main__":
    main() 