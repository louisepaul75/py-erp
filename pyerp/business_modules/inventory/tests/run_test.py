#!/usr/bin/env python
"""
Run tests for the inventory app.
Handles database setup and testing.
"""

import os
import sys
import django
import logging
import psycopg2
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project directory to the sys.path
root_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(root_dir, '../../../..'))
sys.path.insert(0, project_root)

# Load environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.testing')
os.environ.setdefault('PYERP_ENV', 'test')

# Set test-specific environment variables
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'

# Configure Django
django.setup()

# Add required apps to INSTALLED_APPS
if 'products' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ('products',)
if 'inventory' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ('inventory',)
if 'sales' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ('sales',)

# Force close any existing connections to test database
def close_test_db_connections():
    """Force close any existing connections to the test database."""
    try:
        # Get connection parameters from settings
        db_settings = settings.DATABASES['default']
        test_db_name = f"test_{db_settings['NAME']}"
        
        # Connect to postgres database to perform admin operations
        conn = psycopg2.connect(
            host=db_settings['HOST'],
            port=db_settings.get('PORT', 5432),
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            database='postgres'  # Connect to postgres database
        )
        conn.autocommit = True  # Needed for administrative commands
        
        # Create a cursor
        cur = conn.cursor()
        
        # SQL to terminate all connections to the test database
        sql = f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{test_db_name}'
        AND pid <> pg_backend_pid();
        """
        
        # Execute the SQL
        cur.execute(sql)
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
        logger.info(f"Terminated connections to {test_db_name}")
    except Exception as e:
        logger.error(f"Error terminating database connections: {e}")


if __name__ == "__main__":
    """Run the tests."""
    # Close any existing connections to test database
    close_test_db_connections()
    
    # Create the args to pass to Django's test runner
    test_args = ['manage.py', 'test']
    
    # Add any specific test paths from command line
    if len(sys.argv) > 1:
        # Add all arguments after the script name
        test_args.extend(sys.argv[1:])
    else:
        # Default to running all inventory tests
        test_args.append('pyerp.business_modules.inventory.tests')
    
    # Add the no input flag to avoid confirmation prompts
    test_args.append('--noinput')
    
    # Add verbosity if not already specified
    if not any(arg.startswith('-v') for arg in test_args):
        test_args.append('-v1')
    
    # Show what we're running
    logger.info(f"Running tests with arguments: {' '.join(test_args[1:])}")
    
    # Run the tests using Django's test runner
    from django.core.management import execute_from_command_line
    execute_from_command_line(test_args) 