#!/bin/bash

set -e

# Handle debug mode
if [ "$DEBUG_MODE" = "true" ]; then
  echo "Running in DEBUG MODE - special configuration for local development"
  # Load debug environment instead of prod
  ENV_FILE="/app/config/env/.env.prod.local"
else
  ENV_FILE="/app/config/env/.env.prod"
fi

# Wait for PostgreSQL
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for PostgreSQL database connection..."
  sleep 1
done
echo "PostgreSQL database is ready!"

# Load environment variables
echo "Loading environment from $ENV_FILE"
source $ENV_FILE 2>/dev/null || true

# Print database settings for debugging
echo "Database settings: NAME=$DB_NAME, HOST=$DB_HOST, USER=$DB_USER"
if [ -n "$DB_PASSWORD" ]; then
  echo "Database password is set"
fi

# Create log directory
mkdir -p /app/logs
chmod -R 755 /app/logs
echo "Log directories configured with correct permissions"

# Apply Django migrations if needed
python manage.py migrate

# Start all services using supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
