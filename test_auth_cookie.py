#!/usr/bin/env python
"""
test_auth_cookie.py - Test script to get a new auth cookie and examine it

This script tests the auth module's cookie handling by:
1. Invalidating any existing session
2. Getting a new session
3. Printing the cookie information

Usage:
    python test_auth_cookie.py [--debug]
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the direct_api module
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir.parent.parent))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
import django
django.setup()

# Import needed modules
from pyerp.direct_api.auth import get_session, invalidate_session
from pyerp.direct_api.client import DirectAPIClient

# Path to the cookie file - Fix the path to point to the correct location
COOKIE_FILE = os.path.join(script_dir, 'pyerp', 'direct_api', '.global_session_cookie')
print(f"Using cookie file path: {COOKIE_FILE}")

def print_cookie_file():
    """Print the contents of the cookie file."""
    print("\n===== COOKIE FILE CONTENT =====")
    
    if not os.path.exists(COOKIE_FILE):
        print(f"Cookie file not found: {COOKIE_FILE}")
        return
    
    try:
        with open(COOKIE_FILE, 'r') as f:
            content = f.read()
            print(f"Raw content: {content}")
            try:
                data = json.loads(content)
                print("\nParsed JSON:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
                
                # If there's a value field that contains the cookie
                if 'value' in data:
                    # Check what cookie names are present
                    cookie_value = data['value']
                    print("\nCookie names found:")
                    if '4DSID_WSZ-DB=' in cookie_value:
                        print("  - 4DSID_WSZ-DB (FOUND)")
                    else:
                        print("  - 4DSID_WSZ-DB (NOT FOUND)")
                        
                    if 'WASID4D=' in cookie_value:
                        print("  - WASID4D (FOUND)")
                    else:
                        print("  - WASID4D (NOT FOUND)")
            except:
                print("Failed to parse as JSON")
    except Exception as e:
        print(f"Error reading cookie file: {e}")

def test_auth_cookie(environment='live', debug=False):
    """
    Test the auth module's cookie handling.
    
    Args:
        environment: The environment to use
        debug: Enable debug logging
    """
    if debug:
        # Enable debug logging
        logging.getLogger().setLevel(logging.DEBUG)
        for log_name in logging.Logger.manager.loggerDict:
            if 'direct_api' in log_name:
                logging.getLogger(log_name).setLevel(logging.DEBUG)
    
    print(f"\n----- Testing auth cookie for environment: {environment} -----")
    
    # First, invalidate any existing session
    print("\n1. Invalidating existing session...")
    invalidate_session(environment)
    
    # Show cookie file after invalidation
    print("\n2. Cookie file after invalidation:")
    print_cookie_file()
    
    # Get a new session
    print("\n3. Getting new session...")
    session = get_session(environment)
    cookie = session.get_cookie()
    print(f"Got cookie: {cookie[:50]}..." if len(cookie) > 50 else f"Got cookie: {cookie}")
    
    # Show cookie file after getting new session
    print("\n4. Cookie file after getting new session:")
    print_cookie_file()
    
    # Check for WASID4D cookie in headers
    print("\n5. Checking response headers for WASID4D cookie...")
    # Make a request to get the response headers
    import requests
    try:
        # Use the base_url from the client configuration
        base_url = DirectAPIClient(environment=environment)._get_base_url()
        info_url = f"{base_url}/$info"
        print(f"Making request to: {info_url}")
        
        # Make a direct request without any cookies to get a fresh response
        response = requests.get(info_url)
        print(f"Response status: {response.status_code}")
        
        # Print all cookies from the response
        print("Response cookies:")
        for name, value in response.cookies.items():
            print(f"  {name}: {value}")
        
        # Print response headers
        print("Response headers:")
        for header, value in response.headers.items():
            if header.lower() in ('set-cookie', 'cookie'):
                print(f"  {header}: {value}")
                
                # Check if header contains WASID4D
                if 'WASID4D' in value:
                    print("  >> WASID4D found in response cookie!")
                
                # Check if header contains 4DSID_WSZ-DB
                if '4DSID_WSZ-DB' in value:
                    print("  >> 4DSID_WSZ-DB found in response cookie!")
    except Exception as e:
        print(f"Error checking headers: {e}")
    
    # Test client cookie usage
    print("\n6. Testing client with the new session...")
    client = DirectAPIClient(environment=environment)
    # Make a simple request to retrieve table list or info
    print("Creating client and testing API connectivity...")
    try:
        # Try to fetch a small table or table info
        response = client._make_request('GET', 'Info')
        print(f"API test response status: {response.status_code}")
        
        # If we got cookies back, show them
        if 'Set-Cookie' in response.headers:
            cookie_header = response.headers['Set-Cookie']
            print(f"Server returned Set-Cookie: {cookie_header}")
            
            # Check cookie name
            if 'WASID4D' in cookie_header:
                print("  >> WASID4D found in response cookie!")
            
            if '4DSID_WSZ-DB' in cookie_header:
                print("  >> 4DSID_WSZ-DB found in response cookie!")
    except Exception as e:
        print(f"API test failed: {e}")
    
    # Final cookie file state
    print("\n7. Final cookie file state:")
    print_cookie_file()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test auth cookie handling')
    parser.add_argument('--env', default='live', help='Environment to use (default: live)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    test_auth_cookie(args.env, args.debug) 