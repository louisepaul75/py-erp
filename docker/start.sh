#!/bin/bash
set -e

echo "Environment variables:"
env | sort

echo "Checking for Python and pip:"
python --version
pip --version

echo "Listing installed packages:"
pip list

echo "Testing Django configuration..."
python -c "import sys; print(sys.path)"
python -c "import django; print(\"django module found\")"

# Check if redis is available (if not, print warning but continue)
echo "Checking Redis connection..."
python -c "import redis; r = redis.from_url('${REDIS_URL:-redis://redis:6379/0}'); try: r.ping(); print('Redis connection successful'); except Exception as e: print(f'Redis connection failed: {e}')" || echo "Redis check failed, but continuing..."

# Attempt to import the application module with better error handling
echo "Checking application imports..."
python -c "try:
    import pyerp
    print('pyerp module found')
    import pyerp.wsgi
    print('wsgi module found')
    import celery
    print('celery module found')
    from django.conf import settings
    print(f'DJANGO_SETTINGS_MODULE={settings.SETTINGS_MODULE}')
except Exception as e:
    print(f'Error importing application modules: {e}')
    import traceback
    traceback.print_exc()
"

echo "Running Django checks..."
python manage.py check --settings=$DJANGO_SETTINGS_MODULE

echo "Starting Gunicorn..."
exec gunicorn pyerp.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level debug 