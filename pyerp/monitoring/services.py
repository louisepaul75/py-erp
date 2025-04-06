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
HEALTH_CHECK_TIMEOUT = 15  # Reduced from 120 seconds

# Maximum time to wait for individual component checks
COMPONENT_CHECK_TIMEOUT = 10 # Reduced from 60 seconds


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
        "component": HealthCheckResult.COMPONENT_DATABASE,
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

    # First check if the connection is enabled
    if not connection_manager.is_connection_enabled("legacy_erp"):
        status = HealthCheckResult.STATUS_WARNING
        details = "Legacy ERP API connection is disabled"
        logger.info("Legacy ERP health check: Connection is disabled")
        response_time = 0
    elif not LEGACY_ERP_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Legacy ERP API module is not available"
        logger.warning("Legacy ERP health check: Module not available")
        response_time = 0
    else:
        try:
            # Create client and check connection
            client = LegacyERPClient()
            client.check_connection()
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
        "component": HealthCheckResult.COMPONENT_LEGACY_ERP,
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

    # First check if the connection is enabled
    if not connection_manager.is_connection_enabled("images_cms"):
        status = HealthCheckResult.STATUS_WARNING
        details = "Images CMS API connection is disabled"
        logger.info("Images CMS health check: Connection is disabled")
        response_time = 0
    elif not IMAGES_CMS_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Images CMS API module is not available"
        response_time = 0
        logger.warning("Images CMS health check: Module not available")
    else:
        try:
            # Log the API URL being used for debugging
            api_url = settings.IMAGE_API.get("BASE_URL")
            logger.debug(f"Images CMS API URL from settings: {api_url}")

            # Create client and check connection
            client = ImageAPIClient()
            client.check_connection()
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
        "component": HealthCheckResult.COMPONENT_IMAGES_CMS,
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
        component=HealthCheckResult.COMPONENT_DATABASE_VALIDATION,
        status=status,
        details=details,
        response_time=response_time,
    )

    return {
        "component": HealthCheckResult.COMPONENT_DATABASE_VALIDATION,
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
    Run all health checks concurrently using ThreadPoolExecutor.

    Args:
        as_array (bool): If True, returns results as an array; otherwise as dict

    Returns:
        list or dict: Health check results in the specified format
    """
    logger.info("Starting health checks concurrently")
    start_time = time.time()

    health_checks = {
        HealthCheckResult.COMPONENT_DATABASE: check_database_connection,
        HealthCheckResult.COMPONENT_LEGACY_ERP: check_legacy_erp_connection,
        HealthCheckResult.COMPONENT_IMAGES_CMS: check_images_cms_connection,
    }

    results = {}
    futures = {}

    executor = ThreadPoolExecutor(max_workers=len(health_checks))
    try:
        for component, check_func in health_checks.items():
            logger.debug(f"Submitting health check for: {component}")
            futures[executor.submit(check_func)] = component

        # Process completed futures with overall timeout
        completed_count = 0
        try:
            for future in as_completed(futures, timeout=HEALTH_CHECK_TIMEOUT):
                component = futures[future]
                completed_count += 1
                try:
                    # Get result with individual component timeout
                    result = future.result(timeout=COMPONENT_CHECK_TIMEOUT)
                    results[component] = result
                    logger.debug(f"Health check completed for {component}: {result['status']}")
                except TimeoutError:
                    error_msg = f"Health check timed out for {component} after {COMPONENT_CHECK_TIMEOUT} seconds"
                    logger.warning(error_msg)
                    results[component] = {
                        "component": component,
                        "status": HealthCheckResult.STATUS_ERROR,
                        "details": error_msg,
                        "response_time": COMPONENT_CHECK_TIMEOUT * 1000,
                        "timestamp": timezone.now(),
                    }
                except Exception as e:
                    error_msg = f"Health check failed for {component}: {e!s}"
                    logger.exception(error_msg)
                    results[component] = {
                        "component": component,
                        "status": HealthCheckResult.STATUS_ERROR,
                        "details": error_msg,
                        "response_time": 0,  # Or calculate time until exception?
                        "timestamp": timezone.now(),
                    }
        except TimeoutError:
            unfinished_count = len(futures) - completed_count
            logger.warning(
                f"Overall health check timed out after {HEALTH_CHECK_TIMEOUT} seconds. "\
                f"{unfinished_count} (of {len(futures)}) futures unfinished."
            )
            # Don't wait for hanging futures - this is crucial to avoid Gunicorn timeout
            # Note: cancel_futures=True is Py 3.9+
            executor.shutdown(wait=False, cancel_futures=True)

        # Check for any components that didn't get a result recorded
        # This handles futures that timed out in the as_completed loop
        # or any other unexpected missing results.
        for component in health_checks.keys():
            if component not in results:
                error_msg = f"Health check result missing for {component} (likely timed out or cancelled)"
                logger.error(error_msg)
                results[component] = {
                    "component": component,
                    "status": HealthCheckResult.STATUS_ERROR,
                    "details": error_msg,
                    "response_time": HEALTH_CHECK_TIMEOUT * 1000,
                    "timestamp": timezone.now(),
                }

    finally:
        # Ensure shutdown happens even if no timeout occurred in as_completed
        # but do it without waiting to prevent hangs if a future completed
        # but somehow got stuck during shutdown.
        if not executor._shutdown:
            executor.shutdown(wait=False, cancel_futures=True)

    total_time = time.time() - start_time
    logger.info(f"All health checks processed concurrently in {total_time:.2f} seconds")

    # Return in the requested format
    if as_array:
        # Ensure order matches the original definition for consistency
        ordered_results = []
        for component in health_checks.keys():
            # results dict is guaranteed to have all components now
            result_data = results[component]
            # Ensure 'component' key exists, even if the check failed early
            if 'component' not in result_data:
                result_data['component'] = component
            ordered_results.append(result_data)
        return ordered_results

    # Return as dictionary (already guaranteed to have all components)
    return results


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
