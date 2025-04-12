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

# Create and ensure all required directories exist with proper permissions
mkdir -p /app/media /app/static /app/data /app/pyerp/static

# Apply migrations
# Note: We're removing the PG_AVAILABLE check here too, assuming
# migrations should run if DB is configured in Django settings
# However, they are currently manually commented out below.
echo "Skipping database migrations due to known issues with migrations..."
# Comment out the migration commands to avoid issues
# cd /app
# python manage.py makemigrations --noinput
# python manage.py migrate --noinput
# echo "Migrations skipped"

# Function to wait for database to be ready
wait_for_db() {
  echo "Waiting for database to be ready..."

  # Simple wait logic - relies on Django settings to determine actual DB
  # This check might need refinement if SQLite is truly needed as a fallback
  # in some scenarios not covered by environment/1P settings.
  if [ -z "${DB_HOST:-}" ] && [ -z "${DATABASE_URL:-}" ]; then
      echo "Neither DB_HOST nor DATABASE_URL is set, assuming SQLite or other non-networked DB."
      # If using memory DB or local SQLite, no wait is needed.
      # Exporting USE_SQLITE might be needed if other parts of the script rely on it.
      # export USE_SQLITE="true"
      return 0
  fi

  # Determine host/port/user from env vars (might be overridden by 1P later in Django)
  local host=${DB_HOST}
  local port=${DB_PORT:-5432}
  local user=${DB_USER:-postgres}
  export PGPASSWORD="${DB_PASSWORD:-}" # Use password from env if set

  echo "Attempting to check PostgreSQL status at ${host}:${port}..."

  MAX_TRIES=10 # Increased retries
  CURRENT_TRY=0
  while [ $CURRENT_TRY -lt $MAX_TRIES ]; do
    if pg_isready -h "${host}" -p "${port}" -U "${user}" -t 2 >/dev/null 2>&1; then
      echo "PostgreSQL is ready!"
      return 0
    else
      CURRENT_TRY=$((CURRENT_TRY+1))
      echo "Waiting for PostgreSQL... (attempt $CURRENT_TRY of $MAX_TRIES)"
      sleep 2
    fi
  done

  echo "PostgreSQL did not become ready after $MAX_TRIES attempts."
  # Decide if we should exit or continue (e.g., maybe Django will handle it)
  # exit 1 # Optional: Exit if DB is critical for startup
}

# Function to wait for Redis to be ready
wait_for_redis() {
  echo "Waiting for Redis to be ready..."

  # Check if Redis should be skipped explicitly
  if [[ "${USE_MEMORY_BROKER:-false}" == "true" ]]; then
    echo "USE_MEMORY_BROKER is true, using memory broker for Celery"
    export CELERY_BROKER_URL="memory://"
    export CELERY_RESULT_BACKEND="django-db"
    export CELERY_TASK_ALWAYS_EAGER="true"
    return 0
  fi

  # Check if CELERY_BROKER_URL is explicitly set to memory
  if [[ "${CELERY_BROKER_URL:-}" == "memory://"* ]]; then
    echo "CELERY_BROKER_URL is memory://, using memory broker"
    export CELERY_RESULT_BACKEND="django-db"
    export CELERY_TASK_ALWAYS_EAGER="true"
    return 0
  fi

  # Extract host and port from CELERY_BROKER_URL or use defaults
  local redis_url=${CELERY_BROKER_URL:-redis://localhost:6379/0}
  local redis_host=$(echo "${redis_url}" | sed -E 's/redis:\/\/([^:]+).*/\1/' | sed -E 's/:([0-9]+).*//') # Handle host without port
  local redis_port=$(echo "${redis_url}" | sed -E 's/.*:([0-9]+).*/\1/' | grep -E '^[0-9]+$' || echo 6379) # Extract port or default

  if [[ "${redis_host}" == "" || "${redis_host}" == "${redis_url}" ]]; then
      redis_host="localhost" # Default host if extraction failed
  fi

  echo "Attempting to check Redis status at ${redis_host}:${redis_port}..."

  MAX_REDIS_TRIES=5
  CURRENT_REDIS_TRY=0
  while [ $CURRENT_REDIS_TRY -lt $MAX_REDIS_TRIES ]; do
    if redis-cli -h "${redis_host}" -p "${redis_port}" ping 2>/dev/null | grep -q "PONG"; then
      echo "Redis is ready!"
      return 0
    else
      CURRENT_REDIS_TRY=$((CURRENT_REDIS_TRY+1))
      echo "Waiting for Redis... (attempt $CURRENT_REDIS_TRY of $MAX_REDIS_TRIES)"
      sleep 1
    fi
  done

  echo "Redis did not become ready after $MAX_REDIS_TRIES attempts. Celery might fail if configured for Redis."
  # Optionally fall back to memory broker if Redis is expected but unavailable
  # echo "Falling back to memory broker."
  # export CELERY_BROKER_URL="memory://"
  # export CELERY_RESULT_BACKEND="django-db"
  # export CELERY_TASK_ALWAYS_EAGER="true"
}

# Wait for database and Redis to be ready
wait_for_db
wait_for_redis

# Run database migrations (still commented out)
# echo "Running database migrations..."
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
