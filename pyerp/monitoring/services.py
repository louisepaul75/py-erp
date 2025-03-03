"""
Services for performing system health checks.

This module contains the implementations of various health check services
that monitor critical system components such as database connections,
legacy ERP API integration, and the pictures API.
"""

import time
import logging
import subprocess
import sys
import json
from pathlib import Path
from django.db import connections, OperationalError
from django.conf import settings

from pyerp.monitoring.models import HealthCheckResult

# Import the API clients we'll check
try:
    from pyerp.direct_api.client import DirectAPIClient
    from pyerp.direct_api.exceptions import DirectAPIError, ServerUnavailableError
    LEGACY_API_AVAILABLE = True
except ImportError:
    LEGACY_API_AVAILABLE = False

try:
    from pyerp.products.image_api import ImageAPIClient
    PICTURES_API_AVAILABLE = True
except ImportError:
    PICTURES_API_AVAILABLE = False

logger = logging.getLogger(__name__)


def check_database_connection():
    """
    Check if the database connection is working properly.
    
    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_SUCCESS
    details = "Database connection is healthy."
    
    try:
        # Try to get a connection to the database and execute a simple query
        connections['default'].ensure_connection()
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except OperationalError as e:
        status = HealthCheckResult.STATUS_ERROR
        details = f"Failed to connect to database: {str(e)}"
        logger.error(f"Database health check failed: {str(e)}")
    except Exception as e:
        status = HealthCheckResult.STATUS_ERROR
        details = f"Unexpected error during database check: {str(e)}"
        logger.error(f"Database health check failed with unexpected error: {str(e)}")
    
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Create and return the health check result
    result = HealthCheckResult.objects.create(
        component=HealthCheckResult.COMPONENT_DATABASE,
        status=status,
        details=details,
        response_time=response_time
    )
    
    return {
        'component': HealthCheckResult.COMPONENT_DATABASE,
        'status': status,
        'details': details,
        'response_time': response_time,
        'timestamp': result.timestamp
    }


def check_legacy_erp_connection():
    """
    Check if the connection to the legacy ERP API is working properly.
    
    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_SUCCESS
    details = "Legacy ERP connection is healthy."
    
    if not LEGACY_API_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Legacy ERP API module is not available."
        response_time = 0
    else:
        try:
            # Try to connect to the legacy ERP API
            client = DirectAPIClient()
            
            # Try to fetch a small amount of data to verify connection
            response = client._make_request(
                'GET',
                'tables',
                params={'$top': 1}
            )
            
            if response.status_code != 200:
                status = HealthCheckResult.STATUS_WARNING
                details = f"Legacy ERP API returned non-200 status: {response.status_code}"
                
        except ServerUnavailableError as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Legacy ERP server is unavailable: {str(e)}"
            logger.error(f"Legacy ERP health check failed - server unavailable: {str(e)}")
        except DirectAPIError as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Legacy ERP API error: {str(e)}"
            logger.error(f"Legacy ERP health check failed: {str(e)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Unexpected error during Legacy ERP check: {str(e)}"
            logger.error(f"Legacy ERP health check failed with unexpected error: {str(e)}")
    
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Create and return the health check result
    result = HealthCheckResult.objects.create(
        component=HealthCheckResult.COMPONENT_LEGACY_ERP,
        status=status,
        details=details,
        response_time=response_time
    )
    
    return {
        'component': HealthCheckResult.COMPONENT_LEGACY_ERP,
        'status': status,
        'details': details,
        'response_time': response_time,
        'timestamp': result.timestamp
    }


def check_pictures_api_connection():
    """
    Check if the connection to the pictures API is working properly.
    
    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_SUCCESS
    details = "Pictures API connection is healthy."
    
    if not PICTURES_API_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Pictures API module is not available."
        response_time = 0
    else:
        try:
            # Try to connect to the pictures API
            client = ImageAPIClient()
            
            # Try to fetch a small amount of data to verify connection
            response = client.get_all_images(page=1, page_size=1)
            
            if not response or 'results' not in response:
                status = HealthCheckResult.STATUS_WARNING
                details = "Pictures API returned unexpected response format."
                
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Pictures API connection error: {str(e)}"
            logger.error(f"Pictures API health check failed: {str(e)}")
    
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Create and return the health check result
    result = HealthCheckResult.objects.create(
        component=HealthCheckResult.COMPONENT_PICTURES_API,
        status=status,
        details=details,
        response_time=response_time
    )
    
    return {
        'component': HealthCheckResult.COMPONENT_PICTURES_API,
        'status': status,
        'details': details,
        'response_time': response_time,
        'timestamp': result.timestamp
    }


def validate_database():
    """
    Run the comprehensive database validation script and return the results.
    
    Returns:
        dict: Validation result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_SUCCESS
    details = "Database validation completed successfully. No issues found."
    
    try:
        # Get the path to the validation script
        script_path = Path(settings.BASE_DIR) / 'scripts' / 'db_validation.py'
        
        if not script_path.exists():
            status = HealthCheckResult.STATUS_ERROR
            details = f"Database validation script not found at {script_path}"
            logger.error(details)
        else:
            # Run the validation script with the --verbose flag
            cmd = [sys.executable, str(script_path), '--verbose', '--json']
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            # Check if the script ran successfully
            if result.returncode != 0:
                status = HealthCheckResult.STATUS_ERROR
                details = f"Database validation failed with exit code {result.returncode}.\n\n"
                details += f"Error: {result.stderr}\n\n"
                details += f"Output: {result.stdout}"
                logger.error(f"Database validation failed: {result.stderr}")
            else:
                # Try to parse the JSON output
                try:
                    # Extract just the JSON part from the output
                    json_start = result.stdout.find('{')
                    if json_start >= 0:
                        json_output = result.stdout[json_start:]
                        validation_results = json.loads(json_output)
                        
                        # Check for issues
                        issues_found = validation_results.get('issues_found', 0)
                        warnings_found = validation_results.get('warnings_found', 0)
                        
                        if issues_found > 0:
                            status = HealthCheckResult.STATUS_ERROR
                            details = f"Database validation found {issues_found} issues.\n\n"
                            details += validation_results.get('summary', '')
                        elif warnings_found > 0:
                            status = HealthCheckResult.STATUS_WARNING
                            details = f"Database validation found {warnings_found} warnings.\n\n"
                            details += validation_results.get('summary', '')
                        else:
                            details = "Database validation completed successfully. No issues found.\n\n"
                            details += validation_results.get('summary', '')
                    else:
                        details = f"Database validation completed, but output format is not recognized:\n\n{result.stdout}"
                except json.JSONDecodeError:
                    # If JSON parsing fails, use the raw output
                    if 'Issues found: 0' in result.stdout:
                        details = f"Database validation completed successfully. Raw output:\n\n{result.stdout}"
                    else:
                        status = HealthCheckResult.STATUS_WARNING
                        details = f"Database validation completed with possible issues. Raw output:\n\n{result.stdout}"
    except Exception as e:
        status = HealthCheckResult.STATUS_ERROR
        details = f"Error running database validation: {str(e)}"
        logger.error(f"Database validation failed with unexpected error: {str(e)}")
    
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Create and return the health check result
    result = HealthCheckResult.objects.create(
        component=HealthCheckResult.COMPONENT_DATABASE_VALIDATION,
        status=status,
        details=details,
        response_time=response_time
    )
    
    return {
        'component': HealthCheckResult.COMPONENT_DATABASE_VALIDATION,
        'status': status,
        'details': details,
        'response_time': response_time,
        'timestamp': result.timestamp
    }


def run_all_health_checks():
    """
    Run all available health checks.
    
    Returns:
        dict: Dictionary containing all health check results
    """
    results = {
        'database': check_database_connection(),
        'legacy_erp': check_legacy_erp_connection(),
        'pictures_api': check_pictures_api_connection(),
    }
    
    return results 