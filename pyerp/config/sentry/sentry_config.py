"""
Sentry configuration for error tracking and performance monitoring.
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def initialize_sentry(dsn=None):
    """
    Initialize Sentry for error tracking and performance monitoring.
    
    Args:
        dsn: The Sentry DSN (Data Source Name) to connect to. If None, tries to get it from
             the SENTRY_DSN environment variable.
    """
    if not dsn:
        dsn = os.environ.get("SENTRY_DSN")
    
    if not dsn:
        logger.warning("Sentry DSN not provided. Sentry integration is disabled.")
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.redis import RedisIntegration

        # Get environment and release info
        environment = os.environ.get("PYERP_ENV", "development")
        release = os.environ.get("PYERP_VERSION", "dev")
        
        # Configure Sentry
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                DjangoIntegration(),
                LoggingIntegration(
                    level=logging.INFO,        # Capture info and above as breadcrumbs
                    event_level=logging.ERROR  # Send errors as events
                ),
                RedisIntegration(),
            ],
            environment=environment,
            release=release,
            # Send a sample of performance data (0.1 = 10%)
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            # Send a sample of profiling data (0.01 = 1%)
            profiles_sample_rate=float(os.environ.get("SENTRY_PROFILES_SAMPLE_RATE", "0.01")),
            # Capture all SQL queries as spans for performance monitoring
            _experiments={
                "auto_enabling_integrations": True,
            },
            # Don't send PII data
            send_default_pii=False,
            # Before sending an event to Sentry, this function will be called
            before_send=before_send,
        )
        
        logger.info(f"Sentry initialized: environment={environment}, release={release}")
        return True
    except ImportError:
        logger.warning("sentry_sdk not installed. Sentry integration is disabled.")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False

def before_send(event, hint):
    """
    Filter sensitive information before sending events to Sentry.
    
    Args:
        event: The event dictionary
        hint: A dictionary containing additional information about the event
        
    Returns:
        The modified event or None if the event should be discarded
    """
    # Remove sensitive information from request data if present
    if 'request' in event and 'data' in event['request']:
        # Make a copy so we can modify it
        data = dict(event['request']['data'])
        
        # Filter out sensitive fields
        sensitive_fields = ['password', 'token', 'secret', 'credit_card', 'card_number']
        for field in sensitive_fields:
            if field in data:
                data[field] = '[FILTERED]'
        
        # Update the request data
        event['request']['data'] = data
    
    return event 