#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Ensure the DJANGO_SETTINGS_MODULE is correct
if [[ "${DJANGO_SETTINGS_MODULE:-}" != "pyerp.config.settings.development" ]]; then
    echo "DJANGO_SETTINGS_MODULE was incorrect: ${DJANGO_SETTINGS_MODULE:-none}"
    echo "Setting it to the correct value: pyerp.config.settings.development"
    export DJANGO_SETTINGS_MODULE="pyerp.config.settings.development"
fi

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

# Check if PostgreSQL environment variables are set
if [ -n "${DB_HOST:-}" ] && [ -n "${DB_USER:-}" ]; then
    echo "PostgreSQL environment variables found, checking connection..."
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
else
    echo "No PostgreSQL environment variables found - will use SQLite"
    PG_AVAILABLE=false
fi

# Create and ensure all required directories exist with proper permissions
mkdir -p /app/media /app/static /app/data /app/pyerp/static

# Initialize React application
# Removed the initial npm install from here - moved to just before supervisord starts
# if [ -d \"/app/frontend-react\" ]; then
#     echo \"Initializing React application...\"
#     cd /app/frontend-react && npm install --legacy-peer-deps
#     echo \"React initialization complete\"
# fi

# Apply migrations for development only if PostgreSQL is available
if $PG_AVAILABLE; then
  echo "Skipping database migrations due to known issues with migrations..."
  # Comment out the migration commands to avoid issues
  # cd /app
  # python manage.py makemigrations --noinput
  # python manage.py migrate --noinput
  echo "Migrations skipped"
else
  echo "Skipping migrations since PostgreSQL is unavailable"
fi

# Function to wait for database to be ready
wait_for_db() {
  echo "Waiting for database to be ready..."
  
  # Check if we're using SQLite fallback
  if [ "$PG_AVAILABLE" = false ]; then
    echo "Using SQLite fallback - no need to wait for database"
    export USE_SQLITE="true"
    return 0
  fi
  
  # For PostgreSQL
  if [ -z "${DB_HOST}" ]; then
    echo "DB_HOST not set, skipping PostgreSQL check"
  else
    while ! pg_isready -h "${DB_HOST}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" >/dev/null 2>&1; do
      echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT:-5432}..."
      sleep 1
    done
    echo "PostgreSQL is ready!"
  fi
}

# Function to wait for Redis to be ready
wait_for_redis() {
  # No PostgreSQL available means we're in SQLite fallback mode
  if [ "$PG_AVAILABLE" = false ]; then
    echo "SQLite fallback mode detected - using memory broker for Celery"
    export USE_MEMORY_BROKER="true"
    export USE_SQLITE="true"
    export CELERY_BROKER_URL="memory://"
    export CELERY_RESULT_BACKEND="django-db"
    export CELERY_TASK_ALWAYS_EAGER="true"
    return 0
  fi
  
  # Check if Redis should be used
  if [[ "${USE_MEMORY_BROKER:-false}" == "true" ]]; then
    echo "Using memory broker for Celery, skipping Redis check"
    # Set environment variables for memory broker
    export CELERY_BROKER_URL="memory://"
    export CELERY_RESULT_BACKEND="django-db"
    export CELERY_TASK_ALWAYS_EAGER="true"
    return 0
  fi
  
  # If using SQLite fallback and no explicit Redis URL, use memory backend
  if [[ "${USE_SQLITE:-false}" == "true" && -z "${CELERY_BROKER_URL}" ]]; then
    echo "SQLite fallback mode detected with no Redis config, using memory broker"
    export CELERY_BROKER_URL="memory://"
    export CELERY_RESULT_BACKEND="django-db"
    export CELERY_TASK_ALWAYS_EAGER="true"
    return 0
  fi

  echo "Waiting for Redis to be ready..."
  # Extract host and port from CELERY_BROKER_URL or use defaults
  REDIS_HOST=$(echo "${CELERY_BROKER_URL:-redis://localhost:6379/0}" | sed -E 's/redis:\/\/([^:]+):.*/\1/')
  REDIS_PORT=$(echo "${CELERY_BROKER_URL:-redis://localhost:6379/0}" | sed -E 's/redis:\/\/[^:]+:([0-9]+).*/\1/')
  
  MAX_REDIS_TRIES=3
  CURRENT_REDIS_TRY=0
  
  while [ $CURRENT_REDIS_TRY -lt $MAX_REDIS_TRIES ]; do
    if redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping 2>/dev/null | grep -q "PONG"; then
      echo "Redis is ready at ${REDIS_HOST}:${REDIS_PORT}!"
      return 0
    else
      CURRENT_REDIS_TRY=$((CURRENT_REDIS_TRY+1))
      echo "Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}... (attempt $CURRENT_REDIS_TRY of $MAX_REDIS_TRIES)"
      
      if [ $CURRENT_REDIS_TRY -eq $MAX_REDIS_TRIES ]; then
        echo "Redis unavailable after $MAX_REDIS_TRIES attempts - falling back to memory broker"
        export CELERY_BROKER_URL="memory://"
        export CELERY_RESULT_BACKEND="django-db"
        export CELERY_TASK_ALWAYS_EAGER="true"
        return 0
      fi
      
      sleep 1
    fi
  done
}

# Wait for database and Redis to be ready
wait_for_db
wait_for_redis

# Run database migrations
echo "Skipping migrations due to known issues..."
# cd /app
# python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
cd /app
python /app/manage.py collectstatic --noinput

# Create a superuser if needed
if [[ "${DJANGO_SUPERUSER_USERNAME:-}" != "" && "${DJANGO_SUPERUSER_PASSWORD:-}" != "" && "${DJANGO_SUPERUSER_EMAIL:-}" != "" ]]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || echo "Superuser already exists or creation failed."
fi

# Create necessary directories for supervisor
echo "Ensuring supervisor directories exist..."
mkdir -p /var/run /var/log/supervisor
chmod 755 /var/run /var/log/supervisor

# Explicitly export NEXT_PUBLIC_API_URL if it exists
if [ -n "${NEXT_PUBLIC_API_URL:-}" ]; then
    export NEXT_PUBLIC_API_URL
    echo "Exported NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}"
fi

# Ensure frontend dependencies are installed BEFORE starting supervisord
if [ -d "/app/frontend-react" ]; then
    echo "Ensuring frontend dependencies are fully installed..."
    cd /app/frontend-react && npm install --legacy-peer-deps
    echo "Frontend dependencies installation complete."
    cd /app # Change back to the main app directory
fi

# Start supervisord
echo "Starting supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
