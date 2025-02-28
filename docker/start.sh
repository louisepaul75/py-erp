#!/bin/bash
set -e

# Check if we should use local environment (for development without external services)
if [ "$USE_LOCAL_ENV" = "true" ]; then
  echo "Using local environment settings..."
  cp /app/.env.local /app/.env
fi

echo "Environment variables:"
env | sort

echo "Checking for Python and pip:"
python --version
pip --version

echo "Listing installed packages:"
pip list

echo "Testing Django configuration..."
python -c "import sys; print(sys.path)"
python -c "import django; print(\"django module found\")"

# Test database URL parsing
echo "Checking database URL..."
python -c "import dj_database_url; db_url='${DATABASE_URL:-postgres://postgres:postgres@db:5432/pyerp}'; parsed = dj_database_url.parse(db_url); print(f'Database config: {parsed}');" || echo "Database URL parsing failed, but continuing..."

# Check if redis is available (if not, print warning but continue)
echo "Checking Redis connection..."
python -c "import redis; r = redis.from_url('${REDIS_URL:-redis://redis:6379/0}'); try: r.ping(); print('Redis connection successful'); except Exception as e: print(f'Redis connection failed: {e}')" || echo "Redis check failed, but continuing..."

# Attempt to import the application module with better error handling
echo "Checking application imports..."
python -c "
try:
    import pyerp
    print('pyerp module found')
    import pyerp.wsgi
    print('wsgi module found')
    import celery
    print('celery module found')
    from django.conf import settings
    print(f'DJANGO_SETTINGS_MODULE={settings.SETTINGS_MODULE}')
except Exception as e:
    print(f'Error importing application modules: {e}')
    import traceback
    traceback.print_exc()
"

# Test database connectivity with retries
echo "Testing database connectivity..."
MAX_RETRIES=5  # Reduced for local testing
RETRY_INTERVAL=2
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  python -c "
try:
    import dj_database_url
    import psycopg2
    db_url = '${DATABASE_URL:-postgres://postgres:postgres@db:5432/pyerp}'
    db_config = dj_database_url.parse(db_url)
    print(f'Attempting to connect to database: {db_config}')
    # This will raise an exception if connection fails
    conn = psycopg2.connect(
        host=db_config['HOST'], 
        port=db_config['PORT'],
        dbname=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD']
    )
    print('Database connection successful')
    conn.close()
    exit(0)
except Exception as e:
    print(f'Database connection error: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"
  
  if [ $? -eq 0 ]; then
    echo "Database connection established!"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "Failed to connect to database. Retry $RETRY_COUNT of $MAX_RETRIES..."
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
      echo "Waiting $RETRY_INTERVAL seconds before retry..."
      sleep $RETRY_INTERVAL
    else
      echo "Database connection not available. This is normal when running locally or in CI."
      echo "For a complete deployment, ensure the database is available and correctly configured."
      break
    fi
  fi
done

# Optionally run migrations, but only if database is available
if (python -c "
try:
    import psycopg2
    db_url = '${DATABASE_URL:-postgres://postgres:postgres@db:5432/pyerp}'
    import dj_database_url
    db_config = dj_database_url.parse(db_url)
    conn = psycopg2.connect(
        host=db_config['HOST'], 
        port=db_config['PORT'],
        dbname=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD']
    )
    conn.close()
    exit(0)
except:
    exit(1)
"); then
    echo "Database available, running migrations..."
    python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE --noinput || echo "Migrations failed, but continuing..."
else
    echo "Skipping migrations as database is not available."
fi

echo "Running Django checks..."
python manage.py check --settings=$DJANGO_SETTINGS_MODULE || echo "Django checks failed, but continuing..."

echo "Starting Gunicorn..."
exec gunicorn pyerp.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level debug 