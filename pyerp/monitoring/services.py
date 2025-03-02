"""
Services for performing system health checks.

This module contains the implementations of various health check services
that monitor critical system components such as database connections,
legacy ERP API integration, and the pictures API.
"""

import time
import logging
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