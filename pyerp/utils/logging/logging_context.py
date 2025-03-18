"""
Template context processor for client-side logging

This module provides a Django context processor that adds
logging-related functions to all templates.
"""

import json
from functools import wraps
from django.utils.safestring import mark_safe

from pyerp.utils.logging import get_logger

logger = get_logger(__name__)


def log_to_server(level, message, context=None):
    """
    Log a message from the client side.

    Args:
        level: Logging level (debug, info, warning, error, critical)
        message: The log message
        context: Optional context dictionary
    """
    context = context or {}
    context["source"] = "client"

    log_method = getattr(logger, level.lower(), logger.info)
    log_method(f"CLIENT: {message}", extra=context)


def json_script_wrap(func):
    """
    Decorator to wrap a function's output in a JSON script tag for use in templates.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            # Convert to JSON and include in a script tag
            json_data = json.dumps(result)
            return mark_safe(
                f'<script id="logging-config" type="application/json">'
                f"{json_data}"
                f"</script>"
            )
        return result

    return wrapper


@json_script_wrap
def get_logging_config():
    """
    Generate the configuration for client-side logging.

    Returns:
        Dictionary with logging configuration that will be converted to JSON
        and included in templates.
    """
    # This can be adjusted based on environment
    from django.conf import settings

    # Default to INFO in production, DEBUG in development
    client_log_level = "INFO" if not settings.DEBUG else "DEBUG"

    return {
        "enabled": True,
        "level": client_log_level,
        "appName": "pyERP",
        "version": getattr(settings, "APP_VERSION", "unknown"),
        "environment": getattr(settings, "ENVIRONMENT", "development"),
        "serverEndpoint": "/api/logs/",  # Endpoint to send logs to
        "includeContext": True,
        "consoleOutput": settings.DEBUG,  # Show logs in console in development
    }


def logging_context_processor(request):
    """
    Context processor that adds logging functions to templates.

    Args:
        request: The HttpRequest object

    Returns:
        Dictionary with logging-related functions to be added to the template context
    """
    # Generate a request ID if not already present
    request_id = getattr(request, "id", None)

    def log_client_event(event_type, data=None):
        """Log a client-side event."""
        context = {"request_id": request_id, "event_type": event_type}
        if data:
            context.update(data)
        log_to_server("info", f"Client event: {event_type}", context)

        # Return a JavaScript snippet to execute client-side logging
        safe_event = event_type.replace("'", "\\'")
        return mark_safe(
            f"window.pyerpLogger && "
            f"window.pyerpLogger.logEvent('{safe_event}', {json.dumps(data or {})});"
        )

    # Return the context dictionary
    return {
        "logging_config": get_logging_config(),
        "log_client_event": log_client_event,
        "request_id": request_id,
    }
