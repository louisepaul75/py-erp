import os
import json
import logging.config
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def format(self, record):
        logobj = {}
        
        # Standard log record attributes
        logobj['timestamp'] = datetime.utcnow().isoformat()
        logobj['level'] = record.levelname
        logobj['name'] = record.name
        logobj['message'] = record.getMessage()
        
        # Add exception info if available
        if record.exc_info:
            logobj['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields from the record
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'id', 'levelname', 'levelno', 'lineno',
                          'module', 'msecs', 'message', 'msg', 'name', 'pathname',
                          'process', 'processName', 'relativeCreated', 'stack_info',
                          'thread', 'threadName']:
                logobj[key] = value
        
        return json.dumps(logobj)

def configure_logging():
    """
    Configure Django logging to output structured JSON logs that can be easily parsed by Filebeat.
    """
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(os.environ.get('LOG_DIR', '/app/logs'), 'pyerp.log'),
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 10,
                'formatter': 'json',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(os.environ.get('LOG_DIR', '/app/logs'), 'pyerp-error.log'),
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 10,
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['console', 'error_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'pyerp': {
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
        },
    }
    
    logging.config.dictConfig(logging_config)

def get_logger(name):
    """
    Get a logger with the given name, configured for structured logging.
    
    Usage:
        logger = get_logger(__name__)
        
        # Add context to logs
        logger.info("User logged in", extra={
            'user_id': user.id,
            'username': user.username,
            'ip_address': request.META.get('REMOTE_ADDR')
        })
    """
    return logging.getLogger(name) 