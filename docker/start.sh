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
python -c "import pyerp; print(\"pyerp module found\")"
python -c "import pyerp.wsgi; print(\"wsgi module found\")"
python -c "import django; print(\"django module found\")"
python -c "from django.conf import settings; print(f\"DJANGO_SETTINGS_MODULE={settings.SETTINGS_MODULE}\")"

echo "Running Django checks..."
python manage.py check --settings=$DJANGO_SETTINGS_MODULE

echo "Starting Gunicorn..."
exec gunicorn pyerp.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level debug 