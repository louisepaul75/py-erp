"""
Centralized Logging Module for pyERP

This module provides a centralized configuration for logging across the pyERP system.
It sets up different loggers based on application components and configures
handlers with a rotating file system.

Usage:
    from pyerp.utils.logging import get_logger

    # Get a logger for a specific module
    logger = get_logger(__name__)
    
    # Or get a specific category logger
    from pyerp.utils.logging import get_category_logger
    logger = get_category_logger('security')
"""

import logging
import os
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path

from django.conf import settings
from pythonjsonlogger.jsonlogger import JsonFormatter

# Base directory for log files
LOG_DIR = Path(settings.BASE_DIR) / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log categories based on the codebase analysis
LOG_CATEGORIES = {
    "app": {
        "file": "app.log",
        "level": settings.LOG_LEVEL,
        "description": "General application logs",
    },
    "security": {
        "file": "security.log",
        "level": "INFO",
        "description": "Security-related logs including authentication",
    },
    "performance": {
        "file": "performance.log",
        "level": "INFO",
        "description": "Performance metrics and slow operations",
    },
    "data_sync": {
        "file": "data_sync.log",
        "level": "INFO",
        "description": "Data synchronization with external systems",
    },
    "external_api": {
        "file": "external_api.log",
        "level": "INFO",
        "description": "External API interactions and responses",
    },
    "database": {
        "file": "database.log",
        "level": "WARNING",
        "description": "Database operations and errors",
    },
    "user_activity": {
        "file": "user_activity.log",
        "level": "INFO",
        "description": "User activity and actions",
    },
    "business_logic": {
        "file": "business_logic.log",
        "level": "INFO",
        "description": "Business rules and logic execution",
    },
    "errors": {
        "file": "errors.log",
        "level": "ERROR",
        "description": "Critical errors and exceptions",
    },
    "audit": {
        "file": "audit.log",
        "level": "INFO",
        "description": "Audit trail for compliance and record-keeping",
    },
}

# Get log file size limit from settings (default 2MB)
LOG_FILE_SIZE_LIMIT = getattr(settings, "LOG_FILE_SIZE_LIMIT", 2 * 1024 * 1024)

# Configure JSON logging based on settings
JSON_LOGGING = getattr(settings, "JSON_LOGGING", False)


def get_formatter():
    """Return the appropriate formatter based on settings."""
    if JSON_LOGGING:
        return JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
            },
        )
    return logging.Formatter(
        "{levelname} {asctime} {module} {process:d} {thread:d} {message}", style="{"
    )


def create_file_handler(log_file, log_level):
    """Create a rotating file handler for the given log file."""
    handler = RotatingFileHandler(
        LOG_DIR / log_file,
        maxBytes=LOG_FILE_SIZE_LIMIT,  # 2MB file size
        backupCount=10,  # Keep 10 backup files
        encoding="utf-8",
    )
    handler.setLevel(log_level)
    handler.setFormatter(get_formatter())
    return handler


def create_console_handler(log_level=logging.INFO):
    """Create a console handler for logs."""
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(get_formatter())
    return handler


@lru_cache(maxsize=128)
def get_logger(name):
    """
    Get a logger instance for the given name.
    Uses LRU cache to avoid creating multiple instances for the same name.

    Args:
        name: The logger name (typically __name__ from the calling module)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if this is the first time we're creating this logger
    if not logger.handlers:
        # Determine the category based on the module name
        category = "app"  # Default category

        if "security" in name or "auth" in name:
            category = "security"
        elif "sync" in name or "etl" in name:
            category = "data_sync"
        elif "external_api" in name or "api" in name:
            category = "external_api"
        elif "performance" in name or "metrics" in name:
            category = "performance"
        elif "db" in name or "database" in name or "model" in name:
            category = "database"
        elif "user" in name or "activity" in name:
            category = "user_activity"
        elif "business" in name or "logic" in name or "rule" in name:
            category = "business_logic"

        # Get the settings for this category
        category_config = LOG_CATEGORIES.get(category, LOG_CATEGORIES["app"])

        # Add handlers based on the category
        logger.addHandler(
            create_file_handler(
                category_config["file"], getattr(logging, category_config["level"])
            )
        )

        # Add console handler for non-production environments
        if settings.DEBUG or os.environ.get("ENVIRONMENT", "").lower() != "production":
            logger.addHandler(create_console_handler())

        # Errors go to the errors log regardless of category
        if category != "errors":
            error_handler = create_file_handler(
                LOG_CATEGORIES["errors"]["file"], logging.ERROR
            )
            error_handler.setLevel(logging.ERROR)  # Only log errors and above
            logger.addHandler(error_handler)

        # Set the overall logger level
        logger.setLevel(getattr(logging, category_config["level"]))

        # Don't propagate to parent loggers to avoid duplicate logs
        logger.propagate = True

    return logger


@lru_cache(maxsize=32)
def get_category_logger(category):
    """
    Get a logger specifically for a category.

    Args:
        category: One of the predefined LOG_CATEGORIES

    Returns:
        A configured logger for the specified category
    """
    if category not in LOG_CATEGORIES:
        valid_cats = ", ".join(LOG_CATEGORIES.keys())
        raise ValueError(
            f"Unknown log category: {category}. " f"Valid categories are: {valid_cats}"
        )

    # Create a logger with a standard prefix for the category
    return get_logger(f"pyerp.{category}")


def configure_django_loggers():
    """
    Configure Django's built-in loggers to use our handlers.
    This is useful to call during Django startup to ensure all Django logs
    use our centralized configuration.
    """
    # Configure Django's default loggers
    django_loggers = [
        "django",
        "django.server",
        "django.request",
        "django.db.backends",
        "django.security",
    ]

    for name in django_loggers:
        logger = logging.getLogger(name)

        # Clear existing handlers to avoid duplicates
        logger.handlers = []

        # Determine appropriate category and level
        if name == "django.security":
            category = "security"
            level = "INFO"
        elif name == "django.request":
            category = "errors"
            level = "ERROR"
        elif name == "django.db.backends":
            category = "database"
            level = "WARNING"
        else:
            category = "app"
            level = "INFO"

        # Add appropriate handlers
        logger.addHandler(
            create_file_handler(
                LOG_CATEGORIES[category]["file"], getattr(logging, level)
            )
        )

        # Add console handler for non-production environments
        if settings.DEBUG or os.environ.get("ENVIRONMENT", "").lower() != "production":
            logger.addHandler(create_console_handler())

        # Set the logger level
        logger.setLevel(getattr(logging, level))
        logger.propagate = False


# Convenience functions for common logging tasks
def log_performance(name, duration_ms, extra_context=None):
    """Log a performance metric with standardized format."""
    logger = get_category_logger("performance")
    context = {"operation": name, "duration_ms": duration_ms}
    if extra_context:
        context.update(extra_context)
    logger.info(f"Performance: {name} took {duration_ms}ms", extra=context)


def log_security_event(event_type, user=None, ip_address=None, details=None):
    """Log a security event with standardized format."""
    logger = get_category_logger("security")
    context = {"event_type": event_type}
    if user:
        context["user"] = str(user)
    if ip_address:
        context["ip_address"] = ip_address
    if details:
        context.update(details)
    logger.info(f"Security: {event_type}", extra=context)


def log_api_request(
    api_name, endpoint, status_code, response_time_ms, extra_context=None
):
    """Log an API request with standardized format."""
    logger = get_category_logger("external_api")
    context = {
        "api": api_name,
        "endpoint": endpoint,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
    }
    if extra_context:
        context.update(extra_context)
    msg = f"API: {api_name} {endpoint} {status_code} ({response_time_ms}ms)"
    logger.info(msg, extra=context)


def log_data_sync_event(source, destination, record_count, status, details=None):
    """Log a data synchronization event with standardized format."""
    logger = get_category_logger("data_sync")
    context = {
        "source": source,
        "destination": destination,
        "record_count": record_count,
        "status": status,
    }
    if details:
        context.update(details)
    msg = f"Sync: {source} → {destination} [{status}] {record_count} records"
    logger.info(msg, extra=context)


def log_user_activity(user, action, details=None):
    """Log a user activity with standardized format."""
    logger = get_category_logger("user_activity")
    context = {"user": str(user), "action": action}
    if details:
        context.update(details)
    logger.info(f"User: {user} - {action}", extra=context)


def log_audit_event(resource_type, resource_id, action, user=None, details=None):
    """Log an audit event with standardized format."""
    logger = get_category_logger("audit")
    context = {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "action": action,
    }
    if user:
        context["user"] = str(user)
    if details:
        context.update(details)
    msg = f"Audit: {action} {resource_type} {resource_id}"
    logger.info(msg, extra=context)
