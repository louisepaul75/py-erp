#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Create log directories
mkdir -p /var/log/supervisor /var/log/nginx /var/log/redis

# Start Redis service
echo "Starting Redis service..."
redis-server --daemonize yes
sleep 2  # Give Redis time to start

# Function to check if Redis is ready
redis_ready() {
    redis-cli ping > /dev/null 2>&1
}

# Wait for Redis to be ready
until redis_ready; do
  echo >&2 "Redis is unavailable - waiting..."
  sleep 1
done
echo >&2 "Redis is up - continuing..."

# Check PostgreSQL connection
echo "Checking PostgreSQL connection..."
export PGPASSWORD="${DB_PASSWORD:-postgres}"
until pg_isready -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}"; do
  echo >&2 "PostgreSQL is unavailable - waiting..."
  sleep 1
done
echo >&2 "PostgreSQL is up - continuing..."

# Apply database migrations
echo >&2 "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo >&2 "Collecting static files..."
python manage.py collectstatic --noinput

# Create media and static directories with proper permissions
mkdir -p /app/media /app/static /app/data
chmod -R 755 /app/media /app/static /app/data

# Create superuser if needed
if [ "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo >&2 "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser may already exist"
fi

# Execute command passed to entrypoint
exec "$@"