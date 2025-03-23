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

# Disable Datadog APM for Elasticsearch and Kibana
export DD_TRACE_ENABLED=false
export DD_PROFILING_ENABLED=false
echo "Disabled Datadog APM tracing for Elasticsearch and Kibana"

# Apply database migrations
python manage.py migrate --noinput

# Create directories for Elasticsearch and Kibana
mkdir -p /var/lib/elasticsearch /var/log/elasticsearch /app/logs
chown -R elasticsearch:elasticsearch /var/lib/elasticsearch /var/log/elasticsearch
chmod -R 755 /var/lib/elasticsearch /var/log/elasticsearch /app/logs
echo "Elasticsearch directories configured with correct permissions"

# Start Supervisor (which manages Gunicorn, Nginx, Elasticsearch, and Kibana)
exec "$@"
