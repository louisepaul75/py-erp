"""
System health checks for the Core app.
"""

import logging
from django.core.checks import register, Warning, Error  # noqa: F401
from django.db import connections
from django.db.utils import OperationalError, InterfaceError, DatabaseError

# Set up logging
logger = logging.getLogger('pyerp.core')

@register()
def check_database_connection(app_configs, **kwargs):
    """
    Check if the database connection is working.
    This check will be run at startup and when Django runs checks.
    It will not prevent the app from starting even if the database is unavailable.  # noqa: E501
    """
    errors = []

    try:
        # Try to connect to the database
        conn = connections['default']
        conn.cursor()
    except (OperationalError, InterfaceError, DatabaseError) as e:
        logger.error(f"Database connection check failed: {str(e)}")
        errors.append(
            Warning(  # noqa: E128
                f"Database connection failed: {str(e)}",
                hint="The application will still start but database-dependent features will be unavailable.",  # noqa: E501
  # noqa: E501, F841
                id="pyerp.core.W001",  # noqa: F841
  # noqa: F841
            )
        )

    return errors
