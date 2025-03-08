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

# Check PostgreSQL connection but don't wait indefinitely
echo "Checking PostgreSQL connection..."
export PGPASSWORD="${DB_PASSWORD:-postgres}"

# Try to connect to PostgreSQL but don't fail if unavailable
MAX_TRIES=3
CURRENT_TRY=0
PG_AVAILABLE=false

while [ $CURRENT_TRY -lt $MAX_TRIES ]; do
  if pg_isready -h "${DB_HOST}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" > /dev/null 2>&1; then
    PG_AVAILABLE=true
    echo >&2 "PostgreSQL is up - continuing..."
    break
  else
    CURRENT_TRY=$((CURRENT_TRY+1))
    echo >&2 "PostgreSQL is unavailable (attempt $CURRENT_TRY of $MAX_TRIES)"
    if [ $CURRENT_TRY -eq $MAX_TRIES ]; then
      echo >&2 "PostgreSQL unavailable after $MAX_TRIES attempts - will use SQLite fallback"
    else
      sleep 1
    fi
  fi
done

# Create and ensure all required directories exist with proper permissions
mkdir -p /app/media /app/static /app/data /app/pyerp/static

# Initialize Vue.js application
if [ -d "/app/frontend" ]; then
    echo "Initializing Vue.js application..."
    cd /app/frontend && npm install
    echo "Vue.js initialization complete"
fi

# Apply migrations for development only if PostgreSQL is available
if $PG_AVAILABLE; then
  echo "Applying database migrations..."
  # First make migrations to ensure all models are up to date
  cd /app
  python manage.py makemigrations --noinput
  python manage.py migrate --noinput
  echo "Migrations applied"
else
  echo "Skipping migrations since PostgreSQL is unavailable"
fi

# Execute the command passed to docker run
exec "$@"
