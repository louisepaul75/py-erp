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

# Create directories for Elasticsearch and Kibana
mkdir -p /var/lib/elasticsearch /var/log/elasticsearch /app/logs
chown -R root:root /var/lib/elasticsearch /var/log/elasticsearch /app/logs
chmod -R 755 /var/lib/elasticsearch /var/log/elasticsearch /app/logs

# Start Supervisor (which manages Gunicorn, Nginx, Elasticsearch, and Kibana)
exec "$@"
