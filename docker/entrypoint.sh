#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Function to check if PostgreSQL is ready
postgres_ready() {
    python << END
import sys
import psycopg2
import dj_database_url
import os

url = os.environ.get('DATABASE_URL')
if not url:
    sys.exit(1)
    
config = dj_database_url.parse(url)
try:
    conn = psycopg2.connect(
        dbname=config['NAME'],
        user=config['USER'],
        password=config['PASSWORD'],
        host=config['HOST'],
        port=config['PORT'],
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Function to check if Redis is ready
redis_ready() {
    python << END
import sys
import redis
import os

url = os.environ.get('REDIS_URL')
if not url:
    sys.exit(1)
    
try:
    r = redis.from_url(url)
    r.ping()
except redis.exceptions.ConnectionError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready
until postgres_ready; do
  echo >&2 "PostgreSQL is unavailable - waiting..."
  sleep 1
done
echo >&2 "PostgreSQL is up - continuing..."

# Wait for Redis to be ready
until redis_ready; do
  echo >&2 "Redis is unavailable - waiting..."
  sleep 1
done
echo >&2 "Redis is up - continuing..."

# Apply database migrations
echo >&2 "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
if [ "${DJANGO_COLLECT_STATIC:-0}" = "1" ]; then
    echo >&2 "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Create superuser if needed
if [ "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo >&2 "Creating superuser..."
    python manage.py createsuperuser --noinput || true
fi

exec "$@" 