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
from pathlib import Path

from django.conf import settings
from django.db import OperationalError, connections
from django.utils import timezone

from pyerp.monitoring.models import HealthCheckResult

# Import the API clients we'll check
try:
    from pyerp.direct_api.exceptions import (
        DirectAPIError,
        ServerUnavailableError,
    )
    from pyerp.direct_api.scripts.getTable import SimpleAPIClient

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
        connections["default"].ensure_connection()
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
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
    status = HealthCheckResult.STATUS_SUCCESS
    details = "Legacy ERP connection is healthy."

    if not LEGACY_API_AVAILABLE:
        status = HealthCheckResult.STATUS_WARNING
        details = "Legacy ERP API module is not available."
        response_time = 0
    else:
        try:
            # Use SimpleAPIClient instead of DirectAPIClient
            client = SimpleAPIClient()
            
            # Use validate_session instead of _make_request to $info endpoint
            session_valid = client.validate_session()
            
            if not session_valid:
                status = HealthCheckResult.STATUS_WARNING
                details = "Legacy ERP API session validation failed."
                logger.warning(
                    "Legacy ERP health check warning: Failed to validate session"
                )

        except ServerUnavailableError as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Legacy ERP server is unavailable: {e!s}"
            msg = "Legacy ERP health check failed - server unavailable: "
            logger.error(f"{msg}{e!s}")
        except DirectAPIError as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Legacy ERP API error: {e!s}"
            msg = "Legacy ERP health check failed: "
            logger.error(f"{msg}{e!s}")
        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Unexpected error during Legacy ERP check: {e!s}"
            msg = "Legacy ERP health check failed with unexpected error: "
            logger.error(f"{msg}{e!s}")

    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Return the health check result without saving to database
    return {
        "component": HealthCheckResult.COMPONENT_LEGACY_ERP,
        "status": status,
        "details": details,
        "response_time": response_time,
        "timestamp": timezone.now(),
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
            client = ImageAPIClient()

            # Try to fetch a small amount of data to verify connection
            response = client.get_all_images(page=1, page_size=1)

            if not response or "results" not in response:
                status = HealthCheckResult.STATUS_WARNING
                details = "Pictures API returned unexpected response format."

        except Exception as e:
            status = HealthCheckResult.STATUS_ERROR
            details = f"Pictures API connection error: {e!s}"
            logger.error(f"Pictures API health check failed: {e!s}")

    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Return the health check result without saving to database
    return {
        "component": HealthCheckResult.COMPONENT_PICTURES_API,
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
        "connections": {
            "active": 0,
            "idle": 0,
            "total": 0
        },
        "transactions": {
            "committed": 0,
            "rolled_back": 0,
            "active": 0
        },
        "performance": {
            "slow_queries": 0,
            "cache_hit_ratio": 0,
            "avg_query_time": 0
        },
        "disk": {
            "size_mb": 0,
            "index_size_mb": 0
        },
        "queries": {
            "select_count": 0,
            "insert_count": 0,
            "update_count": 0,
            "delete_count": 0
        },
        "timestamp": timezone.now()
    }
    
    try:
        with connections["default"].cursor() as cursor:
            if connections["default"].vendor == "postgresql":
                # Get connection statistics
                cursor.execute("""
                    SELECT state, count(*) 
                    FROM pg_stat_activity 
                    GROUP BY state
                """)
                for state, count in cursor.fetchall():
                    if state == 'active':
                        stats["connections"]["active"] = count
                    elif state == 'idle':
                        stats["connections"]["idle"] = count
                    
                stats["connections"]["total"] = stats["connections"]["active"] + stats["connections"]["idle"]
                
                # Get transaction statistics
                cursor.execute("""
                    SELECT 
                        sum(xact_commit) as committed, 
                        sum(xact_rollback) as rolled_back
                    FROM pg_stat_database
                """)
                result = cursor.fetchone()
                if result:
                    stats["transactions"]["committed"] = result[0] or 0
                    stats["transactions"]["rolled_back"] = result[1] or 0
                
                # Get active transactions
                cursor.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND xact_start IS NOT NULL
                """)
                stats["transactions"]["active"] = cursor.fetchone()[0] or 0
                
                # Get slow queries count (queries taking more than 1 second)
                cursor.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND query_start IS NOT NULL 
                    AND NOW() - query_start > interval '1 second'
                """)
                stats["performance"]["slow_queries"] = cursor.fetchone()[0] or 0
                
                # Get cache hit ratio
                cursor.execute("""
                    SELECT 
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read) + 0.001) * 100 as hit_ratio
                    FROM pg_statio_user_tables
                """)
                stats["performance"]["cache_hit_ratio"] = round(cursor.fetchone()[0] or 0, 2)
                
                # Get database and index size
                cursor.execute("""
                    SELECT 
                        pg_database_size(current_database()) / (1024*1024) as db_size_mb, 
                        (SELECT sum(pg_relation_size(indexrelid)) / (1024*1024) 
                         FROM pg_index) as index_size_mb
                """)
                result = cursor.fetchone()
                if result:
                    stats["disk"]["size_mb"] = round(result[0] or 0, 2)
                    stats["disk"]["index_size_mb"] = round(result[1] or 0, 2)
                
                # Get query counts by type (since database start)
                cursor.execute("""
                    SELECT 
                        sum(n_tup_ins) as inserts, 
                        sum(n_tup_upd) as updates, 
                        sum(n_tup_del) as deletes, 
                        sum(n_live_tup + n_dead_tup) as total_rows
                    FROM pg_stat_user_tables
                """)
                result = cursor.fetchone()
                if result:
                    stats["queries"]["insert_count"] = result[0] or 0
                    stats["queries"]["update_count"] = result[1] or 0
                    stats["queries"]["delete_count"] = result[2] or 0
                    
                # Get select query count (approximation)
                cursor.execute("""
                    SELECT sum(seq_scan + idx_scan) as selects
                    FROM pg_stat_user_tables
                """)
                stats["queries"]["select_count"] = cursor.fetchone()[0] or 0
                
                # Calculate average query time
                cursor.execute("""
                    SELECT extract(epoch from avg(now() - query_start)) as avg_time
                    FROM pg_stat_activity 
                    WHERE state = 'active' AND query_start IS NOT NULL
                """)
                avg_time = cursor.fetchone()[0]
                stats["performance"]["avg_query_time"] = round(avg_time * 1000 if avg_time else 0, 2)  # in ms
                
            else:
                # For non-PostgreSQL databases, provide limited stats
                stats["connections"]["total"] = 1
                stats["connections"]["active"] = 1
    
    except Exception as e:
        logger.error(f"Error fetching database statistics: {e!s}")
    
    return stats


def run_all_health_checks(as_array=True):
    """
    Run all available health checks.

    Args:
        as_array (bool): If True, returns results as an array; otherwise as a dict

    Returns:
        list or dict: Health check results in the specified format
    """
    # Run all health checks
    results = {
        HealthCheckResult.COMPONENT_DATABASE: check_database_connection(),
        HealthCheckResult.COMPONENT_LEGACY_ERP: check_legacy_erp_connection(),
        HealthCheckResult.COMPONENT_PICTURES_API: check_pictures_api_connection(),
    }
    
    # Always add database validation result
    validation_result = validate_database()
    results[HealthCheckResult.COMPONENT_DATABASE_VALIDATION] = validation_result
    
    # Return in the requested format
    if as_array:
        # Convert to array format with component included in each result
        return [
            {
                "component": component,
                **result
            } 
            for component, result in results.items()
        ]
    
    return results
