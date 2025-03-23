#!/bin/bash

set -e

# Wait for PostgreSQL
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for PostgreSQL database connection..."
  sleep 1
done
echo "PostgreSQL database is ready!"

# Load environment variables
echo "Loading environment from /app/config/env/.env.prod"
source /app/config/env/.env.prod 2>/dev/null || true

# Print database settings for debugging
echo "Database settings: NAME=$DB_NAME, HOST=$DB_HOST, USER=$DB_USER"
if [ -n "$DB_PASSWORD" ]; then
  echo "Database password is set"
fi

# Create log directory
mkdir -p /app/logs
chmod -R 755 /app/logs
echo "Log directories configured with correct permissions"

# Apply database migrations
python manage.py migrate --noinput

# Start Supervisor (which manages Gunicorn, Nginx, and Redis)
exec "$@"
