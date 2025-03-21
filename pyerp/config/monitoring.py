import os
import logging
from pyerp.config.logging_config import configure_logging

logger = logging.getLogger(__name__)

def setup_monitoring(settings):
    """
    Set up monitoring for the Django application.
    This function should be called from the Django settings file.
    
    Args:
        settings: The Django settings module
        
    Returns:
        The updated settings module
    """
    # Configure logging
    configure_logging()
    
    # Get monitoring mode from environment
    monitoring_mode = os.environ.get('MONITORING_MODE', 'integrated')
    logger.info(f"Setting up monitoring in {monitoring_mode} mode")
    
    # Configure Sentry if available
    try:
        from pyerp.config.sentry.sentry_config import initialize_sentry
        sentry_dsn = os.environ.get('SENTRY_DSN')
        if initialize_sentry(dsn=sentry_dsn):
            logger.info("Sentry initialized successfully")
        else:
            logger.warning("Sentry initialization failed")
    except ImportError:
        # Sentry is not installed or configured
        logger.warning("Sentry import failed, error tracking disabled")
    
    # Add middleware for monitoring if not already present
    if 'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE:
        # Add request ID middleware before CommonMiddleware
        middleware_index = settings.MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
        
        # Add request ID middleware
        if 'pyerp.middleware.request_id.RequestIDMiddleware' not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.insert(middleware_index, 'pyerp.middleware.request_id.RequestIDMiddleware')
            logger.info("Added RequestIDMiddleware")
            
        # Add performance monitoring middleware
        if 'pyerp.middleware.performance.PerformanceMonitoringMiddleware' not in settings.MIDDLEWARE:
            settings.MIDDLEWARE.insert(middleware_index + 1, 'pyerp.middleware.performance.PerformanceMonitoringMiddleware')
            logger.info("Added PerformanceMonitoringMiddleware")
    
    # Configure monitoring-specific settings based on mode
    if monitoring_mode == 'integrated':
        # All monitoring components are in the same container
        settings.ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
        settings.ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT', '9200')
        settings.KIBANA_HOST = os.environ.get('KIBANA_HOST', 'localhost')
        settings.KIBANA_PORT = os.environ.get('KIBANA_PORT', '5601')
    elif monitoring_mode == 'separate':
        # Monitoring components are in separate containers
        settings.ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'pyerp-elasticsearch')
        settings.ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT', '9200')
        settings.KIBANA_HOST = os.environ.get('KIBANA_HOST', 'pyerp-kibana')
        settings.KIBANA_PORT = os.environ.get('KIBANA_PORT', '5601')
    elif monitoring_mode == 'remote':
        # Monitoring components are on a remote server
        settings.ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', '192.168.73.65')
        settings.ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT', '9200')
        settings.KIBANA_HOST = os.environ.get('KIBANA_HOST', '192.168.73.65')
        settings.KIBANA_PORT = os.environ.get('KIBANA_PORT', '5601')
    
    logger.info(f"Configured Elasticsearch: {settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}")
    logger.info(f"Configured Kibana: {settings.KIBANA_HOST}:{settings.KIBANA_PORT}")
    
    return settings 