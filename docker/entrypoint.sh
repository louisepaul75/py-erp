#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Set the PYERP_ENV environment variable based on DJANGO_SETTINGS_MODULE
if [[ "${DJANGO_SETTINGS_MODULE:-}" == *"production"* ]]; then
    export PYERP_ENV="prod"
elif [[ "${DJANGO_SETTINGS_MODULE:-}" == *"test"* ]]; then
    export PYERP_ENV="test"
else
    export PYERP_ENV="dev"
fi
echo "PYERP_ENV set to: $PYERP_ENV"

# Create log directories
mkdir -p /app/logs

# Check PostgreSQL connection
echo "Checking PostgreSQL connection..."
export PGPASSWORD="${DB_PASSWORD:-postgres}"
until pg_isready -h "${DB_HOST}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}"; do
  echo >&2 "PostgreSQL is unavailable - waiting..."
  sleep 1
done
echo >&2 "PostgreSQL is up - continuing..."

# Create and ensure all required directories exist with proper permissions
mkdir -p /app/media /app/static /app/data /app/pyerp/static /var/www/static /var/www/media
chmod -R 755 /app/media /app/static /app/data /app/pyerp/static /var/www/static /var/www/media

# Create symbolic links for Nginx to access static and media files
ln -sf /app/staticfiles/* /var/www/static/ 2>/dev/null || true
ln -sf /app/media/* /var/www/media/ 2>/dev/null || true

# Initialize Vue.js application
if [ -d "/app/frontend" ]; then
    echo "Initializing Vue.js application..."
    /bin/bash /app/docker/vue-entrypoint.sh
    echo "Vue.js initialization complete"
fi

# Collect static files for production
if [[ "$PYERP_ENV" == "prod" ]]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    echo "Static files collected"
    
    # Apply migrations
    echo "Applying database migrations..."
    # First make migrations to ensure all models are up to date
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    echo "Migrations applied"
    
    # Create superuser if it doesn't exist
    echo "Checking for superuser..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'pyerp.settings.production'))
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')).exists():
    print('Creating superuser...')
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi

# Update Nginx configuration to point to the correct directories
if [ -f "/etc/nginx/conf.d/pyerp.conf" ]; then
    sed -i 's|alias /var/www/static/;|alias /app/staticfiles/;|g' /etc/nginx/conf.d/pyerp.conf
    sed -i 's|alias /var/www/media/;|alias /app/media/;|g' /etc/nginx/conf.d/pyerp.conf
fi

# Start supervisord to manage all services
echo "Starting supervisord..."
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf