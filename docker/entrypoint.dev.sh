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

# Create and ensure all required directories exist with proper permissions
mkdir -p /app/media /app/static /app/data /app/pyerp/static

# Initialize Vue.js application
if [ -d "/app/frontend" ]; then
    echo "Initializing Vue.js application..."
    cd /app/frontend && npm install
    echo "Vue.js initialization complete"
fi

# Apply migrations for development
echo "Applying database migrations..."
# First make migrations to ensure all models are up to date
cd /app
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "Migrations applied"

# Execute the command passed to docker run
exec "$@"
