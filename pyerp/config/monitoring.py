import os
from pyerp.config.logging_config import configure_logging

def setup_monitoring(settings):
    """
    Set up monitoring for the Django application.
    This function should be called from the Django settings file.
    
    Args:
        settings: The Django settings module
    """
    # Configure logging
    configure_logging()
    
    # Configure Sentry if available
    try:
        from pyerp.config.sentry.sentry_config import initialize_sentry
        sentry_dsn = os.environ.get('SENTRY_DSN')
        initialize_sentry(dsn=sentry_dsn)
    except ImportError:
        # Sentry is not installed or configured
        pass
    
    # Add middleware for monitoring if not already present
    if 'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE:
        # Add request ID middleware before CommonMiddleware
        middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
        if 'pyerp.middleware.request_id.RequestIDMiddleware' not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.insert(middleware_index, 'pyerp.middleware.request_id.RequestIDMiddleware')
    
    return settings 