#!/usr/bin/env python
"""
Script to manually run the Zebra Day health check.
"""
import os
import sys
import json
import time
import requests
import django
from pathlib import Path

# Add the project root to the path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Set up Django environment with the correct settings path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")

# Force local Zebra Day for testing
os.environ["ZEBRA_DAY_LOCAL"] = "true"

# Load environment variables if available
try:
    from pyerp.utils.env_loader import load_environment_variables
    load_environment_variables(verbose=True)
except ImportError:
    print("Warning: Could not import env_loader, using default settings.")

django.setup()

# Now we can import Django-dependent functions
from django.conf import settings
from django.utils import timezone
from pyerp.monitoring.models import HealthCheckResult
from pyerp.external_api import connection_manager

# Define constants similar to those in the actual service
COMPONENT_ZEBRA_DAY = "Zebra Day API"

def check_zebra_day_manually():
    """
    Manual implementation of the Zebra Day health check.
    
    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_ERROR  # Default to error as fallback
    details = "Zebra Day API check not fully implemented."

    if not connection_manager.is_connection_enabled("zebra_day"):
        status = HealthCheckResult.STATUS_WARNING
        details = f"{COMPONENT_ZEBRA_DAY} connection is disabled."
        print(f"INFO: {COMPONENT_ZEBRA_DAY} connection is disabled in configuration.")
    else:
        try:
            # Get the API URL from settings with fallbacks for both deployment modes
            api_url = getattr(settings, "ZEBRA_DAY_API_URL", None)
            api_key = getattr(settings, "ZEBRA_DAY_API_KEY", None)
            
            # If URL not explicitly configured, determine based on environment
            if not api_url:
                # Check if we're running in Docker
                in_docker = os.environ.get("RUNNING_IN_DOCKER", "false").lower() == "true"
                local_zebra = os.environ.get("ZEBRA_DAY_LOCAL", "false").lower() == "true"
                
                if in_docker and local_zebra:
                    # When running in Docker with local Zebra, use the service name as hostname
                    api_url = "http://zebra-day:8118"
                    print(f"INFO: Using Docker service name for Zebra Day: {api_url}")
                elif local_zebra:
                    # Local Zebra running on host
                    api_url = "http://localhost:8118"
                    print(f"INFO: Using localhost for Zebra Day: {api_url}")
                else:
                    # Remote Zebra Day (default configuration)
                    api_url = "http://192.168.73.65:8118"
                    print(f"INFO: Using remote IP for Zebra Day: {api_url}")

            # Try multiple URLs if needed for testing
            urls_to_try = [api_url]
            if api_url != "http://localhost:8118":
                urls_to_try.append("http://localhost:8118")
            
            # Define multiple possible endpoints to test
            endpoints = [
                "/api/health",
                "/api/status",
                "/health",
                "/status",
                ""  # Base URL
            ]
            
            success = False
            valid_response = False
            final_url = None
            
            for url in urls_to_try:
                if success:
                    break
                    
                for endpoint in endpoints:
                    try:
                        # Prepare headers
                        headers = {}
                        if api_key:
                            headers["Authorization"] = f"Bearer {api_key}"
                        headers["Accept"] = "application/json"
                        
                        full_url = f"{url.rstrip('/')}{endpoint}"
                        print(f"Attempting to connect to Zebra Day at: {full_url}")
                        
                        # Make the request with a timeout
                        response = requests.get(full_url, headers=headers, timeout=5)
                        valid_response = True
                        
                        if response.status_code == 200:
                            status = HealthCheckResult.STATUS_SUCCESS
                            details = f"{COMPONENT_ZEBRA_DAY} is healthy at {full_url}. Response: {response.text[:100]}"
                            print(f"SUCCESS: Zebra Day API responded with status 200")
                            success = True
                            final_url = full_url
                            break
                        else:
                            print(f"INFO: Zebra Day API returned status code {response.status_code} at {full_url}")
                        
                    except requests.RequestException as e:
                        print(f"INFO: Zebra Day API connection error at {full_url}: {str(e)}")
            
            if not success:
                if valid_response:
                    status = HealthCheckResult.STATUS_ERROR
                    details = f"{COMPONENT_ZEBRA_DAY} is accessible but returned non-200 status codes"
                else:
                    status = HealthCheckResult.STATUS_ERROR
                    details = f"{COMPONENT_ZEBRA_DAY} connection failed to all endpoints"
            
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{COMPONENT_ZEBRA_DAY} unexpected error: {str(e)}"
            print(f"ERROR: Zebra Day API check failed with exception: {str(e)}")

    response_time = (time.time() - start_time) * 1000
    return {
        "component": COMPONENT_ZEBRA_DAY,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }

def main():
    """Run the Zebra Day health check and print results."""
    print("Checking if Zebra Day connection is enabled...")
    enabled = connection_manager.is_connection_enabled("zebra_day")
    print(f"Zebra Day connection enabled: {enabled}")
    
    original_status = enabled
    # If Zebra Day is disabled, temporarily enable it
    if not enabled:
        print("\nTemporarily enabling Zebra Day connection for testing...")
        connection_manager.set_connection_status("zebra_day", True)
        print("Zebra Day connection temporarily enabled.")

    try:
        print("\nRunning Zebra Day health check...")
        result = check_zebra_day_manually()
        
        # Format the output for better readability
        print("\nZebra Day Health Check Result:")
        print(f"Status: {result['status']}")
        print(f"Component: {result['component']}")
        print(f"Details: {result['details']}")
        print(f"Response Time: {result['response_time']:.2f} ms")
        print(f"Timestamp: {result['timestamp']}")
        
        # Also print as JSON for completeness
        print("\nJSON format:")
        print(json.dumps(result, default=str, indent=2))
        
        # Return success/error for exit code
        return 0 if result['status'] == HealthCheckResult.STATUS_SUCCESS else 1
    finally:
        # Restore the original connection status
        if not original_status:
            print("\nRestoring Zebra Day connection to disabled state...")
            connection_manager.set_connection_status("zebra_day", False)
            print("Zebra Day connection disabled.")

if __name__ == "__main__":
    sys.exit(main()) 