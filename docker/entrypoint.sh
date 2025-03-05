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

# Create media and static directories with proper permissions
mkdir -p /app/media /app/static /app/data
chmod -R 755 /app/media /app/static /app/data

# Initialize Vue.js application
if [ -d "/app/frontend" ]; then
    echo "Initializing Vue.js application..."
    /bin/bash /app/docker/vue-entrypoint.sh echo "Vue.js initialization complete"
fi

# Execute command passed to entrypoint
exec "$@"