#!/usr/bin/env python
"""
Test script for the monitoring system.
Generates different types of logs to test the monitoring setup.
"""
import os
import sys
import time
import random
import logging
import argparse
import traceback
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import pyERP logging configuration
try:
    from pyerp.config.logging_config import configure_logging, get_logger, get_category_logger
    logging_imported = True
except ImportError:
    # Fallback if the pyERP package is not available
    logging_imported = False
    print("Warning: pyERP logging module not found, using basic logging configuration")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join('logs', 'test_monitoring.log'))
        ]
    )

def setup_logging():
    """Set up logging for the test script."""
    if logging_imported:
        configure_logging()
        return get_logger('test_monitoring')
    else:
        return logging.getLogger('test_monitoring')

def generate_logs(count=100, delay=0.1, include_errors=True):
    """
    Generate a series of log messages of different levels.
    
    Args:
        count: Number of log messages to generate
        delay: Delay between log messages in seconds
        include_errors: Whether to include error and exception logs
    """
    logger = setup_logging()
    security_logger = get_category_logger('security') if logging_imported else logging.getLogger('security')
    performance_logger = get_category_logger('performance') if logging_imported else logging.getLogger('performance')
    
    # Log levels and their corresponding methods
    log_levels = [
        (logger.debug, "Debug message"),
        (logger.info, "Info message"),
        (logger.warning, "Warning message"),
    ]
    
    if include_errors:
        log_levels.extend([
            (logger.error, "Error message"),
            (logger.critical, "Critical message"),
        ])
    
    # User IDs for testing
    user_ids = [f"user_{i}" for i in range(1, 11)]
    
    # Request paths for testing
    request_paths = [
        "/api/users/",
        "/api/products/",
        "/api/orders/",
        "/api/inventory/",
        "/api/reports/",
        "/dashboard/",
        "/admin/users/",
        "/admin/settings/",
    ]
    
    print(f"Generating {count} log messages...")
    
    for i in range(count):
        # Select a random log level
        log_func, message_prefix = random.choice(log_levels)
        
        # Generate a random message with context
        message = f"{message_prefix} #{i+1}"
        
        # Add random context data
        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': random.choice(user_ids),
            'request_id': f"req-{random.randint(10000, 99999)}",
            'ip_address': f"192.168.1.{random.randint(1, 255)}",
            'path': random.choice(request_paths),
        }
        
        # Log the message
        log_func(message, extra=context)
        
        # Occasionally log security events
        if random.random() < 0.2:
            security_event = random.choice([
                "Login attempt",
                "Password changed",
                "Access denied",
                "Permission granted",
                "User created",
                "User deleted",
            ])
            security_logger.info(
                f"Security event: {security_event}",
                extra={
                    'user_id': random.choice(user_ids),
                    'ip_address': f"192.168.1.{random.randint(1, 255)}",
                    'event_type': security_event.lower().replace(' ', '_'),
                    'success': random.choice([True, False]),
                }
            )
        
        # Occasionally log performance metrics
        if random.random() < 0.2:
            duration_ms = random.uniform(10, 5000)
            category = 'normal'
            if duration_ms > 1000:
                category = 'slow'
            if duration_ms > 3000:
                category = 'very_slow'
                
            performance_logger.info(
                f"Request performance: {random.choice(request_paths)}",
                extra={
                    'path': random.choice(request_paths),
                    'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                    'duration_ms': duration_ms,
                    'status_code': random.choice([200, 201, 400, 403, 404, 500]),
                    'category': category,
                }
            )
        
        # Occasionally generate an exception
        if include_errors and random.random() < 0.05:
            try:
                # Generate a random exception
                exceptions = [
                    ValueError("Invalid value provided"),
                    KeyError("Missing required key"),
                    TypeError("Type mismatch"),
                    IndexError("Index out of range"),
                    RuntimeError("Runtime failure"),
                ]
                raise random.choice(exceptions)
            except Exception as e:
                logger.error(
                    f"Exception occurred: {str(e)}",
                    exc_info=True,
                    extra=context
                )
        
        # Add a delay between logs
        if delay > 0:
            time.sleep(delay)
    
    print(f"Generated {count} log messages.")

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Test the monitoring system by generating logs.')
    parser.add_argument('--count', type=int, default=100, help='Number of log messages to generate')
    parser.add_argument('--delay', type=float, default=0.1, help='Delay between log messages in seconds')
    parser.add_argument('--no-errors', action='store_true', help='Skip error and exception logs')
    
    args = parser.parse_args()
    
    # Generate logs
    generate_logs(
        count=args.count,
        delay=args.delay,
        include_errors=not args.no_errors
    ) 