"""
Services for performing system health checks.

This module contains the implementations of various health check services
that monitor critical system components such as database connections,
legacy ERP API integration, and the pictures API.
"""

import json
import logging
import subprocess
import sys
import time
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from pathlib import Path

from django.conf import settings
from django.db import OperationalError, connections
from django.utils import timezone

from pyerp.monitoring.models import HealthCheckResult
from pyerp.external_api import connection_manager

# Import the API clients from the new structure
try:
    from pyerp.external_api.images_cms import ImageAPIClient

    IMAGES_CMS_AVAILABLE = True
except ImportError:
    IMAGES_CMS_AVAILABLE = False

try:
    from pyerp.external_api.legacy_erp import LegacyERPClient

    LEGACY_ERP_AVAILABLE = True
except ImportError:
    LEGACY_ERP_AVAILABLE = False

logger = logging.getLogger(__name__)

# Maximum time to wait for each health check (in seconds)
HEALTH_CHECK_TIMEOUT = 15
# Maximum time to wait for individual component checks
COMPONENT_CHECK_TIMEOUT = 14

# Define component names (consider moving to models.py or a constants file)
COMPONENT_DATABASE = "Database"
COMPONENT_LEGACY_ERP = "Legacy ERP API"
COMPONENT_IMAGES_CMS = "Images CMS API"
COMPONENT_DATABASE_VALIDATION = "Database Validation"
COMPONENT_ZEBRA_DAY = "Zebra Day API"
COMPONENT_KIBANA_ELASTIC = "Kibana/Elastic Monitoring"
COMPONENT_BUCHHALTUNGSBUTTLER = "Buchhaltungsbutler API"
COMPONENT_FRANKFURTER_API = "Frankfurter API"


def check_database_connection():
    """
    Check if the database connection is working properly.

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    # Default to error since we're using SQLite fallback
    status = HealthCheckResult.STATUS_ERROR
    details = "Using SQLite fallback - primary database connection is not available"

    try:
        db_engine = connections["default"].vendor
        if db_engine == "sqlite":
            # We're using SQLite fallback, which means primary DB is not available
            status = HealthCheckResult.STATUS_ERROR
            details = (
                "Using SQLite fallback - primary database connection is not available"
            )
            logger.error("Database health check: Using SQLite fallback")
        else:
            # Check the actual database connection
            connections["default"].ensure_connection()
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            status = HealthCheckResult.STATUS_SUCCESS
            details = "Database connection is healthy."
    except OperationalError as e:
        status = HealthCheckResult.STATUS_ERROR
        details = f"Failed to connect to database: {e!s}"
        logger.error(f"Database health check failed: {e!s}")
    except Exception as e:
        status = HealthCheckResult.STATUS_ERROR
        details = f"Unexpected error during database check: {e!s}"
        logger.error(
            f"Database health check failed with unexpected error: {e!s}",
        )

    # Convert to milliseconds
    response_time = (time.time() - start_time) * 1000

    # Return the health check result without saving to database
    return {
        "component": COMPONENT_DATABASE, # Use defined constant
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }


def check_legacy_erp_connection():
    """
    Check if the connection to the legacy ERP API is working properly.

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_ERROR
    details = "Legacy ERP API connection is not available"
    response_time = (time.time() - start_time) * 1000 # Calculate time even if disabled/unavailable

    # First check if the connection is enabled
    if not connection_manager.is_connection_enabled("legacy_erp"):
        status = HealthCheckResult.STATUS_WARNING
        details = "Legacy ERP API connection is disabled"
        logger.info("Legacy ERP health check: Connection is disabled")
    elif not LEGACY_ERP_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Legacy ERP API module is not available"
        logger.warning("Legacy ERP health check: Module not available")
    else:
        try:
            # Create client and check connection
            client = LegacyERPClient()
            client.check_connection() # Assuming this raises an exception on failure
            status = HealthCheckResult.STATUS_SUCCESS
            details = "Legacy ERP API connection is healthy"
            response_time = (time.time() - start_time) * 1000
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Legacy ERP API error: {e!s}"
            logger.error(f"Legacy ERP health check failed: {e!s}")
            response_time = (time.time() - start_time) * 1000

    # Return the health check result without saving to database
    return {
        "component": COMPONENT_LEGACY_ERP, # Use defined constant
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }


def check_images_cms_connection():
    """
    Check if the connection to the images CMS API is working properly.

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_SUCCESS
    details = "Images CMS API connection is healthy"
    response_time = (time.time() - start_time) * 1000 # Calculate time even if disabled/unavailable

    # First check if the connection is enabled
    if not connection_manager.is_connection_enabled("images_cms"):
        status = HealthCheckResult.STATUS_WARNING
        details = "Images CMS API connection is disabled"
        logger.info("Images CMS health check: Connection is disabled")
    elif not IMAGES_CMS_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Images CMS API module is not available"
        logger.warning("Images CMS health check: Module not available")
    else:
        try:
            # Log the API URL being used for debugging
            api_url = settings.IMAGE_API.get("BASE_URL")
            logger.debug(f"Images CMS API URL from settings: {api_url}")

            # Create client and check connection
            client = ImageAPIClient()
            client.check_connection() # Assuming this raises an exception on failure
            status = HealthCheckResult.STATUS_SUCCESS
            details = "Images CMS API connection is healthy"
            response_time = (time.time() - start_time) * 1000

        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Images CMS API error: {e!s}"
            logger.error(f"Images CMS API health check failed: {e!s}")
            response_time = (time.time() - start_time) * 1000

    # Return the health check result without saving to database
    return {
        "component": COMPONENT_IMAGES_CMS, # Use defined constant
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
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
        script_path = Path(settings.BASE_DIR) / "scripts" / "db_validation.py"

        if not script_path.exists():
            status = HealthCheckResult.STATUS_ERROR
            details = f"Database validation script not found at {script_path}"
            logger.error(details)
        else:
            cmd = [sys.executable, str(script_path), "--verbose", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            # Check if the script ran successfully
            if result.returncode != 0:
                status = HealthCheckResult.STATUS_ERROR
                details = f"Database validation failed with exit code {result.returncode}.\n\n"
                details += f"Error: {result.stderr}\n\n"
                details += f"Output: {result.stdout}"
                logger.error(f"Database validation failed: {result.stderr}")
            else:
                try:
                    json_start = result.stdout.find("{")
                    if json_start >= 0:
                        json_output = result.stdout[json_start:]
                        validation_results = json.loads(json_output)

                        # Check for issues
                        issues_found = validation_results.get("issues_found", 0)
                        warnings_found = validation_results.get("warnings_found", 0)

                        if issues_found > 0:
                            status = HealthCheckResult.STATUS_ERROR
                            details = (
                                f"Database validation found {issues_found} issues.\n\n"
                            )
                            details += validation_results.get("summary", "")
                        elif warnings_found > 0:
                            status = HealthCheckResult.STATUS_WARNING
                            details = f"Database validation found {warnings_found} warnings.\n\n"
                            details += validation_results.get("summary", "")
                        else:
                            details = "Database validation completed successfully. No issues found.\n\n"
                            details += validation_results.get("summary", "")
                    else:
                        details = f"Database validation completed, but output format is not recognized:\n\n{result.stdout}"
                except json.JSONDecodeError:
                    if "Issues found: 0" in result.stdout:
                        details = f"Database validation completed successfully. Raw output:\n\n{result.stdout}"
                    else:
                        status = HealthCheckResult.STATUS_WARNING
                        details = f"Database validation completed with possible issues. Raw output:\n\n{result.stdout}"
                except Exception as e:
                    status = HealthCheckResult.STATUS_ERROR
                    details = f"Error running database validation: {e!s}"
                    logger.error(
                        f"Database validation failed with unexpected error: {e!s}",
                    )
    except Exception as e:
        status = HealthCheckResult.STATUS_ERROR
        details = f"Error running database validation: {e!s}"
        logger.error(f"Database validation failed with unexpected error: {e!s}")

    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Create and return the health check result
    result = HealthCheckResult.objects.create(
        component=COMPONENT_DATABASE_VALIDATION, # Use defined constant
        status=status,
        details=details,
        response_time=response_time,
    )

    return {
        "component": COMPONENT_DATABASE_VALIDATION, # Use defined constant
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": result.timestamp,
    }


def get_database_statistics():
    """
    Get detailed statistics about database performance and usage.

    Returns:
        dict: Detailed database statistics including connections, transactions, and performance metrics
    """
    stats = {
        "connections": {"active": 0, "idle": 0, "total": 0},
        "transactions": {"committed": 0, "rolled_back": 0, "active": 0},
        "performance": {"slow_queries": 0, "cache_hit_ratio": 0, "avg_query_time": 0},
        "disk": {"size_mb": 0, "index_size_mb": 0},
        "queries": {
            "select_count": 0,
            "insert_count": 0,
            "update_count": 0,
            "delete_count": 0,
        },
        "timestamp": timezone.now(),
    }

    try:
        with connections["default"].cursor() as cursor:
            if connections["default"].vendor == "postgresql":
                # Get connection statistics
                cursor.execute(
                    """
                    SELECT state, count(*) 
                    FROM pg_stat_activity 
                    GROUP BY state
                """
                )
                for state, count in cursor.fetchall():
                    if state == "active":
                        stats["connections"]["active"] = count
                    elif state == "idle":
                        stats["connections"]["idle"] = count

                stats["connections"]["total"] = (
                    stats["connections"]["active"] + stats["connections"]["idle"]
                )

                # Get transaction statistics
                cursor.execute(
                    """
                    SELECT 
                        sum(xact_commit) as committed, 
                        sum(xact_rollback) as rolled_back
                    FROM pg_stat_database
                """
                )
                result = cursor.fetchone()
                if result:
                    stats["transactions"]["committed"] = result[0] or 0
                    stats["transactions"]["rolled_back"] = result[1] or 0

                # Get active transactions
                cursor.execute(
                    """
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND xact_start IS NOT NULL
                """
                )
                stats["transactions"]["active"] = cursor.fetchone()[0] or 0

                # Get slow queries count (queries taking more than 1 second)
                cursor.execute(
                    """
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND query_start IS NOT NULL 
                    AND NOW() - query_start > interval '1 second'
                """
                )
                stats["performance"]["slow_queries"] = cursor.fetchone()[0] or 0

                # Get cache hit ratio
                cursor.execute(
                    """
                    SELECT 
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read) + 0.001) * 100 as hit_ratio
                    FROM pg_statio_user_tables
                """
                )
                stats["performance"]["cache_hit_ratio"] = round(
                    cursor.fetchone()[0] or 0, 2
                )

                # Get database and index size
                cursor.execute(
                    """
                    SELECT 
                        pg_database_size(current_database()) / (1024*1024) as db_size_mb, 
                        (SELECT sum(pg_relation_size(indexrelid)) / (1024*1024) 
                         FROM pg_index) as index_size_mb
                """
                )
                result = cursor.fetchone()
                if result:
                    stats["disk"]["size_mb"] = round(result[0] or 0, 2)
                    stats["disk"]["index_size_mb"] = round(result[1] or 0, 2)

                # Get query counts by type (since database start)
                cursor.execute(
                    """
                    SELECT 
                        sum(n_tup_ins) as inserts, 
                        sum(n_tup_upd) as updates, 
                        sum(n_tup_del) as deletes, 
                        sum(n_live_tup + n_dead_tup) as total_rows
                    FROM pg_stat_user_tables
                """
                )
                result = cursor.fetchone()
                if result:
                    stats["queries"]["insert_count"] = result[0] or 0
                    stats["queries"]["update_count"] = result[1] or 0
                    stats["queries"]["delete_count"] = result[2] or 0

                # Get select query count (approximation)
                cursor.execute(
                    """
                    SELECT sum(seq_scan + idx_scan) as selects
                    FROM pg_stat_user_tables
                """
                )
                stats["queries"]["select_count"] = cursor.fetchone()[0] or 0

                # Calculate average query time
                cursor.execute(
                    """
                    SELECT extract(epoch from avg(now() - query_start)) as avg_time
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND query_start IS NOT NULL
                """
                )
                avg_time = cursor.fetchone()[0]
                stats["performance"]["avg_query_time"] = round(
                    avg_time * 1000 if avg_time else 0, 2
                )  # in ms

            else:
                # For non-PostgreSQL databases, provide limited stats
                stats["connections"]["total"] = 1
                stats["connections"]["active"] = 1

    except Exception as e:
        logger.error(f"Error fetching database statistics: {e!s}")

    return stats


def run_all_health_checks(as_array=True):
    """
    Run all health checks concurrently and return the results.

    Args:
        as_array (bool): If True, returns results as a list of dictionaries.
                         If False, returns results as a dictionary keyed by component name.

    Returns:
        list or dict: List or dictionary containing the results of each health check
    """
    start_time = time.time()
    logger.info("Starting all health checks...")

    # List of functions to call for health checks
    health_check_functions = [
        check_database_connection,
        check_legacy_erp_connection,
        check_images_cms_connection,
        validate_database, # Assuming this runs fast enough or handled internally
        check_zebra_day,
        check_kibana_elastic,
        check_buchhaltungsbutler,
        check_frankfurter_api,
    ]

    results_list = []
    timed_out_checks = []

    with ThreadPoolExecutor(max_workers=len(health_check_functions)) as executor:
        # Submit all health check functions to the executor
        future_to_func = {
            executor.submit(func): func for func in health_check_functions
        }

        # Process results as they complete
        for future in as_completed(future_to_func, timeout=HEALTH_CHECK_TIMEOUT):
            func = future_to_func[future]
            component_name = func.__name__.replace("check_", "").replace("_", " ").title() # Derive name for logging

            try:
                # Get the result, applying the component check timeout
                result = future.result(timeout=COMPONENT_CHECK_TIMEOUT)
                results_list.append(result)
                logger.debug(f"Health check completed: {result['component']}")
            except TimeoutError:
                # Individual check timed out
                logger.error(
                    f"Health check timed out for component: {component_name} "
                    f"(> {COMPONENT_CHECK_TIMEOUT}s)"
                )
                timed_out_checks.append(component_name)
                results_list.append({
                    "component": component_name, # Best guess for component name
                    "status": HealthCheckResult.STATUS_ERROR,
                    "details": f"Check timed out after {COMPONENT_CHECK_TIMEOUT} seconds.",
                    "response_time": COMPONENT_CHECK_TIMEOUT * 1000,
                    "timestamp": timezone.now(),
                })
            except Exception as exc:
                # An unexpected error occurred during the check execution
                logger.exception(
                    f"Health check failed with exception for component: {component_name}: {exc!s}"
                )
                results_list.append({
                    "component": component_name, # Best guess for component name
                    "status": HealthCheckResult.STATUS_ERROR,
                    "details": f"Check failed with exception: {exc!s}",
                    "response_time": (time.time() - start_time) * 1000, # Time until failure
                    "timestamp": timezone.now(),
                })

    # Handle checks that might not have completed if the overall timeout was hit
    # (though as_completed with timeout should handle this)
    if len(results_list) < len(health_check_functions):
        logger.warning(
            f"Overall health check timeout ({HEALTH_CHECK_TIMEOUT}s) may have been reached. "
            f"Completed {len(results_list)} out of {len(health_check_functions)} checks."
        )
        # Potentially identify which ones are missing if needed

    total_duration = (time.time() - start_time) * 1000
    logger.info(
        f"All health checks finished in {total_duration:.2f} ms. "
        f"Timed out checks: {timed_out_checks if timed_out_checks else 'None'}"
    )

    # Format results based on the 'as_array' parameter
    if as_array:
        return results_list
    else:
        # Convert list of dicts to dict keyed by component name
        results_dict = {result["component"]: result for result in results_list}
        return results_dict


def get_host_resources():
    """
    Collect host resource metrics including CPU, memory, and disk usage.

    Returns:
        dict: A dictionary containing host resource metrics
    """
    import psutil
    import platform
    from datetime import datetime

    try:
        # Get CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        # Get memory information
        memory = psutil.virtual_memory()

        # Get disk information
        disk = psutil.disk_usage("/")

        # Get system information
        system_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "uptime": int(time.time() - psutil.boot_time()),
        }

        # Get network information
        net_io = psutil.net_io_counters()

        # Format the results
        result = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else None,
                    "min": (
                        cpu_freq.min if cpu_freq and hasattr(cpu_freq, "min") else None
                    ),
                    "max": (
                        cpu_freq.max if cpu_freq and hasattr(cpu_freq, "max") else None
                    ),
                },
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            },
            "system": system_info,
        }

        return result
    except Exception as e:
        logger.error(f"Error collecting host resources: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


def check_zebra_day():
    """
    Check if the connection to the Zebra Day API is working properly.
    
    Zebra Day can run either:
    1. Locally (when started with --with-zebra) at http://localhost:8118
    2. Remotely (default) at IP 192.168.73.65:8118

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_UNKNOWN
    details = "Zebra Day API check not fully implemented."
    component_name = COMPONENT_ZEBRA_DAY

    if not connection_manager.is_connection_enabled("zebra_day"):
        status = HealthCheckResult.STATUS_WARNING
        details = f"{component_name} connection is disabled."
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
                    logger.info(f"Using Docker service name for Zebra Day: {api_url}")
                elif local_zebra:
                    # Local Zebra running on host
                    api_url = "http://localhost:8118"
                    logger.info(f"Using localhost for Zebra Day: {api_url}")
                else:
                    # Remote Zebra Day (default configuration)
                    api_url = "http://192.168.73.65:8118"
                    logger.info(f"Using remote IP for Zebra Day: {api_url}")

            # Prepare headers
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            headers["Accept"] = "application/json"
            
            # Use health or status endpoint if available
            # Note: Adjust endpoint based on actual Zebra Day API structure
            health_endpoint = f"{api_url.rstrip('/')}/api/health"
            
            # Make the request with a timeout
            response = requests.get(health_endpoint, headers=headers, timeout=5)
            
            if response.status_code == 200:
                status = HealthCheckResult.STATUS_SUCCESS
                details = f"{component_name} API is healthy at {api_url}. Response: {response.text[:100]}"
            else:
                status = HealthCheckResult.STATUS_ERROR
                details = f"{component_name} API at {api_url} returned status code {response.status_code}: {response.text[:100]}"
                logger.error(f"{component_name} API error: {response.status_code} - {response.text[:200]}")
        except requests.RequestException as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} API connection error: {str(e)}"
            logger.error(f"{component_name} API connection error: {str(e)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} API unexpected error: {str(e)}"
            logger.exception(f"{component_name} API check failed with exception")

    response_time = (time.time() - start_time) * 1000
    return {
        "component": component_name,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }


def check_kibana_elastic():
    """
    Check if the connection to Kibana/Elastic monitoring is working properly.
    
    Configuration options:
    - ELASTICSEARCH_URL: Base URL for Elasticsearch (default: http://localhost:9200)
    - ELASTICSEARCH_USERNAME: Optional auth username
    - ELASTICSEARCH_PASSWORD: Optional auth password
    
    When running in Docker with --with-monitoring flag, the service is accessible 
    via the container name 'pyerp-elastic-kibana' on port 9200.

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_UNKNOWN
    details = "Kibana/Elastic check not fully implemented."
    component_name = COMPONENT_KIBANA_ELASTIC

    if not connection_manager.is_connection_enabled("kibana_elastic"):
        status = HealthCheckResult.STATUS_WARNING
        details = f"{component_name} connection is disabled."
    else:
        try:
            # Get the Elasticsearch URL with fallbacks for different environments
            es_url = getattr(settings, "ELASTICSEARCH_URL", None)
            es_username = getattr(settings, "ELASTICSEARCH_USERNAME", None)
            es_password = getattr(settings, "ELASTICSEARCH_PASSWORD", None)
            
            # If URL not explicitly configured, determine based on environment
            if not es_url:
                # Check if we're running in Docker
                in_docker = os.environ.get("RUNNING_IN_DOCKER", "false").lower() == "true"
                with_monitoring = os.environ.get("WITH_MONITORING", "false").lower() == "true"
                
                if in_docker and with_monitoring:
                    # When running in Docker with monitoring, use the service name
                    es_url = "http://pyerp-elastic-kibana:9200"
                    logger.info(f"Using Docker service name for Elasticsearch: {es_url}")
                else:
                    # Default to localhost
                    es_url = "http://localhost:9200"
                    logger.info(f"Using localhost for Elasticsearch: {es_url}")
            
            # Construct auth tuple if credentials are provided
            auth = None
            if es_username and es_password:
                auth = (es_username, es_password)
            
            # Use Elasticsearch's cluster health endpoint
            health_endpoint = f"{es_url.rstrip('/')}/_cluster/health"
            logger.debug(f"Checking Elasticsearch health at: {health_endpoint}")
            
            # Make the request with a timeout
            response = requests.get(health_endpoint, auth=auth, timeout=5)
            
            if response.status_code == 200:
                # Parse the response
                health_data = response.json()
                cluster_status = health_data.get("status", "unknown")
                
                # Map Elasticsearch status to our health check status
                if cluster_status == "green":
                    status = HealthCheckResult.STATUS_SUCCESS
                    details = "Elasticsearch cluster health is green. All shards allocated."
                elif cluster_status == "yellow":
                    status = HealthCheckResult.STATUS_WARNING
                    details = "Elasticsearch cluster health is yellow. Some replica shards not allocated."
                else:  # red or unknown
                    status = HealthCheckResult.STATUS_ERROR
                    details = (
                        f"Elasticsearch cluster health is {cluster_status}. "
                        "Some primary shards not allocated."
                    )
                
                # Add more details
                node_count = health_data.get("number_of_nodes", 0)
                details += f" Nodes: {node_count}."
            else:
                status = HealthCheckResult.STATUS_ERROR
                details = (
                    f"Elasticsearch at {es_url} returned status code {response.status_code}: "
                    f"{response.text[:100]}"
                )
                logger.error(
                    f"Elasticsearch API error: {response.status_code} - "
                    f"{response.text[:200]}"
                )
        except requests.RequestException as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Elasticsearch connection error: {str(e)}"
            logger.error(f"Elasticsearch connection error: {str(e)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Elasticsearch unexpected error: {str(e)}"
            logger.exception("Elasticsearch check failed with exception")

    response_time = (time.time() - start_time) * 1000
    return {
        "component": component_name,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }


def check_buchhaltungsbutler():
    """
    Check if the connection to the Buchhaltungsbutler API is working properly.
    
    Configuration options:
    - BUCHHALTUNGSBUTLER_API_URL: Base URL for the API
    - BUCHHALTUNGSBUTLER_API_KEY: Authentication key
    
    The connection manager uses 'buchhaltungs_buttler' as the key.

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_UNKNOWN
    details = "Buchhaltungsbutler API check not fully implemented."
    component_name = COMPONENT_BUCHHALTUNGSBUTTLER

    if not connection_manager.is_connection_enabled("buchhaltungs_buttler"):
        status = HealthCheckResult.STATUS_WARNING
        details = f"{component_name} connection is disabled."
    else:
        try:
            # Get the API settings from Django settings
            api_url = getattr(settings, "BUCHHALTUNGSBUTLER_API_URL", None)
            api_key = getattr(settings, "BUCHHALTUNGSBUTLER_API_KEY", None)
            
            if not api_url:
                status = HealthCheckResult.STATUS_ERROR
                details = f"{component_name} API URL not configured in settings."
                logger.error(f"{component_name} API URL missing from settings")
            elif not api_key:
                status = HealthCheckResult.STATUS_ERROR
                details = f"{component_name} API key not configured in settings."
                logger.error(f"{component_name} API key missing from settings")
            else:
                # Prepare headers with authentication
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                
                # Call a lightweight endpoint (adjust based on actual API structure)
                endpoint = f"{api_url.rstrip('/')}/api/v1/status"
                logger.debug(f"Checking {component_name} health at: {endpoint}")
                
                # Make the request with a timeout
                response = requests.get(endpoint, headers=headers, timeout=5)
                
                if response.status_code in (200, 201, 204):
                    status = HealthCheckResult.STATUS_SUCCESS
                    details = (
                        f"{component_name} API is healthy. "
                        f"Response status: {response.status_code}."
                    )
                    
                    # Add more details if available
                    try:
                        if (response.text and 
                            response.headers.get("content-type", "").startswith("application/json")):
                            response_data = response.json()
                            if isinstance(response_data, dict):
                                api_status = response_data.get("status", "unknown")
                                api_version = response_data.get("version", "unknown")
                                details += f" API status: {api_status}, version: {api_version}."
                    except ValueError:
                        pass  # Not JSON or parsing failed
                else:
                    status = HealthCheckResult.STATUS_ERROR
                    details = (
                        f"{component_name} API returned status code {response.status_code}: "
                        f"{response.text[:100]}"
                    )
                    logger.error(
                        f"{component_name} API error: {response.status_code} - "
                        f"{response.text[:200]}"
                    )
        except requests.RequestException as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} API connection error: {str(e)}"
            logger.error(f"{component_name} API connection error: {str(e)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} API unexpected error: {str(e)}"
            logger.exception(f"{component_name} API check failed with exception")

    response_time = (time.time() - start_time) * 1000
    return {
        "component": component_name,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }


def check_frankfurter_api():
    """
    Check if the connection to the Frankfurter API is working properly.
    This is a free currency exchange rates API.
    
    Default API URL: https://api.frankfurter.app
    Can be overridden with FRANKFURTER_API_URL setting.

    Returns:
        dict: Health check result with status, details, and response time
    """
    start_time = time.time()
    status = HealthCheckResult.STATUS_UNKNOWN
    details = "Frankfurter API check not fully implemented."
    component_name = COMPONENT_FRANKFURTER_API

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
            logger.debug(f"Using Frankfurter API URL: {api_url}")
            
            # Use the /latest endpoint which returns current exchange rates
            endpoint = f"{api_url.rstrip('/')}/latest?from=EUR"
            
            # Make the request with a timeout
            logger.debug(f"Checking Frankfurter API health at: {endpoint}")
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
                logger.error(
                    f"{component_name} API error: {response.status_code} - "
                    f"{response.text[:200]}"
                )
        except requests.RequestException as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} connection error: {str(e)}"
            logger.error(f"{component_name} connection error: {str(e)}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"{component_name} unexpected error: {str(e)}"
            logger.exception(f"{component_name} check failed with exception")

    response_time = (time.time() - start_time) * 1000
    return {
        "component": component_name,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
    }
