#!/bin/bash

set -e

# Ensure the DJANGO_SETTINGS_MODULE is correct
if [[ "${DJANGO_SETTINGS_MODULE:-}" != "pyerp.config.settings.production" ]]; then
    echo "DJANGO_SETTINGS_MODULE was incorrect: ${DJANGO_SETTINGS_MODULE:-none}"
    echo "Setting it to the correct value: pyerp.config.settings.production"
    export DJANGO_SETTINGS_MODULE="pyerp.config.settings.production"
fi

# Environment variables are loaded via --env-file in docker run
# echo "Loading environment from /app/config/env/.env.prod"
# source /app/config/env/.env.prod 2>/dev/null || true # Removed this line

# Print database settings for debugging
echo "Database settings: NAME=$DB_NAME, HOST=$DB_HOST, USER=$DB_USER"
if [ -n "$DB_PASSWORD" ]; then
  echo "Database password is set"
fi

# Network diagnostics
echo "Network diagnostics:"
echo "Checking DNS resolution for $DB_HOST..."
cat /etc/hosts
echo "Running ping test..."
ping -c 1 $DB_HOST || echo "Ping failed but continuing..."
echo "Running IP resolution test..."
getent hosts $DB_HOST || echo "Host resolution failed but continuing..."

# Wait for PostgreSQL
echo "Attempting connection to PostgreSQL at $DB_HOST:$DB_PORT..."
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for PostgreSQL database connection..."
  sleep 2
done
echo "PostgreSQL database is ready!"

# Create log directory
mkdir -p /app/logs
chmod -R 755 /app/logs
echo "Log directories configured with correct permissions"

# Apply Django migrations if needed
python manage.py migrate

# Start all services using supervisord in the foreground (remove exec)
# This might show errors if supervisord itself fails immediately
echo "Starting supervisord..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
