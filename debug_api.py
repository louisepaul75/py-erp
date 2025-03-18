#!/usr/bin/env python
"""
Debug script for the legacy ERP API connection to diagnose connection issues.
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
from pyerp.external_api import connection_manager
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

def check_session_cookie_file():
    """Check if the session cookie file exists and what it contains."""
    cookie_path = Path(__file__).resolve().parent / "pyerp" / "external_api" / "legacy_erp" / ".global_session_cookie"
    print(f"\n==== Checking Session Cookie File ====")
    print(f"Path: {cookie_path}")
    print(f"Exists: {cookie_path.exists()}")
    
    if cookie_path.exists():
        try:
            with open(cookie_path, "r") as f:
                content = f.read().strip()
                print(f"Content: {content}")
                try:
                    parsed = json.loads(content)
                    print(f"Parsed JSON: {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
        except Exception as e:
            print(f"Error reading file: {e}")

def main():
    """Main debug function."""
    # Monkey patch requests to trace all HTTP requests
    requests.Session.request = trace_request
    
    print("\n==== Environment Variables ====")
    legacy_env_vars = {k: v for k, v in os.environ.items() if "LEGACY" in k}
    for key, value in legacy_env_vars.items():
        print(f"{key}: {value}")

    print("\n==== Django Settings ====")
    print(f"LEGACY_API_BASE_URL: {getattr(settings, 'LEGACY_API_BASE_URL', 'Not found')}")
    print(f"LEGACY_API_TEST_URL: {getattr(settings, 'LEGACY_API_TEST_URL', 'Not found')}")

    print("\n==== API Environment Settings from settings.py ====")
    print(f"API_BASE_URL in settings.py: {API_ENVIRONMENTS.get('live', {}).get('base_url', 'Not found')}")
    
    print("\n==== API Environment Settings from Django ====")
    django_api_environments = getattr(settings, 'LEGACY_API_ENVIRONMENTS', {})
    for env_name, env_config in django_api_environments.items():
        print(f"  {env_name}:")
        print(f"    base_url: {env_config.get('base_url')}")
        
    print("\n==== Connection Manager Status ====")
    enabled = connection_manager.is_connection_enabled("legacy_erp")
    print(f"Legacy ERP connection enabled: {enabled}")
    
    # Check session cookie file before initialization
    check_session_cookie_file()
    
    print("\n==== Initializing Legacy ERP Client ====")
    client = LegacyERPClient(environment="live")
    
    # Print the client's base URL
    print(f"Client base URL: {client.base_url}")
    
    print("\n==== Loading Session Cookie ====")
    cookie_loaded = client.load_session_cookie()
    print(f"Cookie loaded: {cookie_loaded}")
    if cookie_loaded:
        print(f"Session ID: {client.session_id}")
    
    # Check session cookie file after loading
    check_session_cookie_file()
    
    print("\n==== Validating Session ====")
    try:
        valid = client.validate_session()
        print(f"Session valid: {valid}")
    except Exception as e:
        print(f"Validation error: {e}")
    
    # Check session cookie file after validation
    check_session_cookie_file()
    
    print("\n==== Direct Login ====")
    try:
        login_result = client.login()
        print(f"Login result: {login_result}")
    except Exception as e:
        print(f"Login error: {e}")
    
    # Check session cookie file after login
    check_session_cookie_file()
    
    # Restore original requests method
    requests.Session.request = original_request
    
    print("\nDebug completed")

if __name__ == "__main__":
    main() 