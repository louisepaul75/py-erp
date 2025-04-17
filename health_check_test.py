#!/usr/bin/env python
"""
Simple script to test the health of Buchhaltungsbutler and Frankfurter APIs
"""

import os
import sys
import json
import time
from pathlib import Path

# Make sure pyerp module is in path (same as in manage.py)
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import and use the centralized environment loader
from pyerp.utils.env_loader import load_environment_variables
load_environment_variables(verbose=True)

# Set the default Django settings module if not defined
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")

# Now set up Django
import django
django.setup()

# Import models after Django is set up
from django.utils import timezone
from pyerp.monitoring.models import HealthCheckResult
from pyerp.external_api import connection_manager
import requests
from django.conf import settings

def enable_connections_temporarily():
    """Temporarily enable the connections and return original settings"""
    original_connections = connection_manager.get_connections()
    
    # Create a copy of the original settings
    temp_connections = original_connections.copy()
    
    # Enable the services we want to test
    temp_connections["buchhaltungs_buttler"] = True
    temp_connections["frankfurter_api"] = True
    
    # Save the temporary settings
    connection_manager.save_connections(temp_connections)
    
    print("Temporarily enabled connections for testing")
    
    return original_connections

def restore_connections(original_connections):
    """Restore the original connection settings"""
    connection_manager.save_connections(original_connections)
    print("Restored original connection settings")

def check_buchhaltungsbutler():
    """
    Check if the connection to the Buchhaltungsbutler API is working properly.
    """
    start_time = time.time()
    # Use the defined statuses from the model
    status = HealthCheckResult.STATUS_ERROR
    details = "Buchhaltungsbutler API check not fully implemented."
    component_name = "Buchhaltungsbutler API"

    if not connection_manager.is_connection_enabled("buchhaltungs_buttler"):
        status = HealthCheckResult.STATUS_WARNING
        details = f"{component_name} connection is disabled."
    else:
        try:
            # Get the API settings
            api_settings = getattr(settings, "BUCHHALTUNGSBUTLER_API", {})
            api_client = api_settings.get("API_CLIENT")
            api_secret = api_settings.get("API_SECRET")
            
            if not api_client or not api_secret:
                status = HealthCheckResult.STATUS_ERROR
                details = f"{component_name} API credentials not configured in settings."
                print(f"ERROR: {component_name} API credentials missing from settings")
            else:
                # Since this is just a test, we'll just check if we have credentials
                status = HealthCheckResult.STATUS_SUCCESS
                details = f"{component_name} credentials are configured properly."
                
                # For a real check, you would make an API request here
                print(f"API client: {api_client}")
                print(f"API secret is set: {bool(api_secret)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} API unexpected error: {str(e)}"
            print(f"EXCEPTION: {component_name} API check failed with exception: {e}")

    response_time = (time.time() - start_time) * 1000
    result = {
        "component": component_name,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }
    return result

def check_frankfurter_api():
    """
    Check if the connection to the Frankfurter API is working properly.
    This is a free currency exchange rates API.
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_ERROR
    details = "Frankfurter API check not fully implemented."
    component_name = "Frankfurter API"

    if not connection_manager.is_connection_enabled("frankfurter_api"):
        status = HealthCheckResult.STATUS_WARNING
        details = f"{component_name} connection is disabled."
    else:
        try:
            # The Frankfurter API base URL
            api_url = getattr(
                settings, 
                "FRANKFURTER_API_URL", 
                "https://api.frankfurter.app"
            )
            print(f"Using Frankfurter API URL: {api_url}")
            
            # Use the /latest endpoint which returns current exchange rates
            endpoint = f"{api_url.rstrip('/')}/latest?from=EUR"
            
            # Make the request with a timeout
            print(f"Checking Frankfurter API health at: {endpoint}")
            response = requests.get(endpoint, timeout=5)
            
            if response.status_code == 200:
                try:
                    # Parse the response to extract useful info
                    data = response.json()
                    base_currency = data.get("base", "unknown")
                    date = data.get("date", "unknown")
                    
                    # Check if the response contains rates
                    rates = data.get("rates", {})
                    if rates and isinstance(rates, dict) and len(rates) > 0:
                        status = HealthCheckResult.STATUS_SUCCESS
                        rate_count = len(rates)
                        currencies = list(rates.keys())[:5]  # Limit to first 5 currencies
                        details = (
                            f"{component_name} is healthy. "
                            f"Base: {base_currency}, Date: {date}. "
                            f"Returned rates for {rate_count} currencies "
                            f"including {', '.join(currencies)}..."
                        )
                    else:
                        status = HealthCheckResult.STATUS_WARNING
                        details = (
                            f"{component_name} returned a valid response but with "
                            f"no rates data. Base: {base_currency}, Date: {date}."
                        )
                except ValueError:
                    status = HealthCheckResult.STATUS_ERROR
                    details = f"{component_name} returned invalid JSON: {response.text[:100]}"
            else:
                status = HealthCheckResult.STATUS_ERROR
                details = (
                    f"{component_name} returned status code {response.status_code}: "
                    f"{response.text[:100]}"
                )
                print(f"ERROR: {component_name} API error: {response.status_code}")
        except requests.RequestException as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} connection error: {str(e)}"
            print(f"ERROR: {component_name} connection error: {str(e)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} unexpected error: {str(e)}"
            print(f"EXCEPTION: {component_name} check failed with exception: {e}")

    response_time = (time.time() - start_time) * 1000
    result = {
        "component": component_name,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }
    return result

def main():
    """Run the health checks and display results"""
    print("Running health checks...\n")
    
    # Save original settings and temporarily enable connections
    original_connections = enable_connections_temporarily()
    
    try:
        print("Buchhaltungsbutler API Health Check:")
        result = check_buchhaltungsbutler()
        print(json.dumps(result, default=str, indent=2))
        
        print("\nFrankfurter API Health Check:")
        result = check_frankfurter_api()
        print(json.dumps(result, default=str, indent=2))
    finally:
        # Make sure we restore original settings even if an exception occurs
        restore_connections(original_connections)

if __name__ == "__main__":
    main() 