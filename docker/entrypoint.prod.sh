#!/bin/bash

set -e

# Wait for PostgreSQL
until nc -z -v -w30 $DB_HOST $DB_PORT
do
  echo "Waiting for PostgreSQL database connection..."
  sleep 1
done
echo "PostgreSQL database is ready!"

# Apply database migrations
python manage.py migrate --noinput

# Start Supervisor (which manages Gunicorn and Nginx)
exec "$@"
