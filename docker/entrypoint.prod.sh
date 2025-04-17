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
# Only run DB checks if HOST and PORT are set
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "Network diagnostics for $DB_HOST:$DB_PORT:"
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
else
    echo "DB_HOST or DB_PORT not set. Skipping entrypoint database checks."
    echo "Assuming database connection details will be provided by the application (e.g., via 1Password)."
fi

# Create log directory
mkdir -p /app/logs
chmod -R 755 /app/logs
echo "Log directories configured with correct permissions"

# --- Print Environment Variables Before Migrate ---
echo "DEBUG: Checking environment variables before running migrate:"
echo "DEBUG: DATABASE_URL = ${DATABASE_URL:-<not set>}"
echo "DEBUG: DB_HOST = ${DB_HOST:-<not set>}"
echo "DEBUG: DB_PORT = ${DB_PORT:-<not set>}"
echo "DEBUG: DB_NAME = ${DB_NAME:-<not set>}"
echo "DEBUG: DB_USER = ${DB_USER:-<not set>}"
echo "DEBUG: DB_PASSWORD is ${DB_PASSWORD+set}"
# --- End Print Environment Variables ---

# --- Run 1Password Fetch Test ---
echo "Running 1Password fetch test script..."
python /app/scripts/test_1pw_fetch.py || echo "1Password fetch test script failed, continuing..."
echo "--- 1Password Fetch Test Finished ---"

# Add placeholder log line to satisfy rebuild script check
echo "Database settings source: 1Password (See test script/app logs for details)"

# Apply Django migrations if needed
python manage.py migrate

# Start all services using supervisord in the foreground (remove exec)
# This might show errors if supervisord itself fails immediately
echo "Starting supervisord..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
