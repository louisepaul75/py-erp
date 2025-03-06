"""
System health checks for the Core app.
"""

import logging

from django.core.checks import Warning, register
from django.db import connections
from django.db.utils import DatabaseError, InterfaceError, OperationalError

# Set up logging
logger = logging.getLogger("pyerp.core")


@register()
def check_database_connection(app_configs, **kwargs):
    """
    Check if the database connection is working.
    This check will be run at startup and when Django runs checks.
    It will not prevent the app from starting even if the database is unavailable.  # noqa: E501
    """
    errors = []

    try:
        conn = connections["default"]
        conn.cursor()
    except (OperationalError, InterfaceError, DatabaseError) as e:
        logger.error(f"Database connection check failed: {e!s}")
        errors.append(
            Warning(
                f"Database connection failed: {e!s}",
                hint="The application will still start but database-dependent features will be unavailable.",
                id="pyerp.core.W001",
            ),
        )

    return errors
