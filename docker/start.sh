#!/bin/bash
set -e

# Import PyMySQL as MySQLdb
python -c "import pymysql; pymysql.install_as_MySQLdb()"

# Check if we should use local environment (for development without external services)
if [ "$USE_LOCAL_ENV" = "true" ]; then
  echo "Using local environment settings..."
  cp /app/.env.local /app/.env
  # Force SQLite for standalone mode
  export DATABASE_URL="sqlite:///app/db.sqlite3"
  echo "Standalone mode: Using SQLite database"
fi

echo "Environment variables:"
env | sort

echo "Checking for Python and pip:"
python --version
pip --version

echo "Listing installed packages:"
pip list

# Check for essential packages and install if missing
for package in drf-yasg django-filter corsheaders pymysql; do
  echo "Checking for $package..."
  python -c "import $package" 2>/dev/null || {
    echo "Installing missing package: $package"
    pip install $package
  }
done

echo "Creating log directory if it doesn't exist..."
mkdir -p /app/logs

echo "Creating a simple Django debug server..."
cat > /app/simple_django_server.py << 'EOF'
"""
A simple Django development server for debugging.
This bypasses Gunicorn to make it easier to see errors.
"""
import os
import sys
import traceback
from pathlib import Path

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'pyerp.settings.production'))

# Debug imports
print("Python path:", sys.path)
print("Current directory:", os.getcwd())

try:
    print("Attempting to import Django...")
    import django
    print(f"Django version: {django.get_version()}")
    
    print("Setting up Django...")
    django.setup()
    
    from django.core.management import execute_from_command_line
    print("Django management commands available")
    
    # Import critical modules to check for issues
    print("Checking imports:")
    
    print("- Checking settings...")
    from django.conf import settings
    print(f"  DJANGO_SETTINGS_MODULE={settings.SETTINGS_MODULE}")
    print(f"  DEBUG={settings.DEBUG}")
    print(f"  DATABASE ENGINE={settings.DATABASES['default']['ENGINE']}")
    
    print("- Checking pyerp...")
    import pyerp
    print("  pyerp module found")
    
    print("- Checking WSGI application...")
    import pyerp.wsgi
    print("  WSGI application found")
    
    print("- Checking INSTALLED_APPS...")
    for app in settings.INSTALLED_APPS:
        try:
            __import__(app)
            print(f"  ✅ {app} loaded successfully")
        except ImportError as e:
            print(f"  ❌ {app} failed to load: {e}")
            
    print("- Checking URLs...")
    import pyerp.urls
    print("  URLs loaded")
    
    print("- Checking database connection...")
    from django.db import connections
    try:
        connection = connections['default']
        connection.ensure_connection()
        print("  Database connection successful")
    except Exception as e:
        print(f"  Database connection failed: {e}")
    
    print("\nAll critical imports successful, ready to run server")
    print("\nStarting Django development server...\n")
    
    # Run a simple Django development server instead of Gunicorn
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
EOF

echo "Starting Django in debug mode instead of Gunicorn..."
exec python /app/simple_django_server.py 