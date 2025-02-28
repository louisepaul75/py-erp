#!/bin/bash
set -e

# Import PyMySQL as MySQLdb
python -c "import pymysql; pymysql.install_as_MySQLdb()"

# Check if we should use local environment (for development without external services)
if [ "$USE_LOCAL_ENV" = "true" ]; then
  echo "Using local environment settings..."
  cp /app/.env.local /app/.env
  # Force SQLite for standalone mode
  export DATABASE_URL="sqlite:///app/db.sqlite3"
  echo "Standalone mode: Using SQLite database"
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
python -c "import dj_database_url; db_url='${DATABASE_URL:-sqlite:///app/db.sqlite3}'; parsed = dj_database_url.parse(db_url); print(f'Database config: {parsed}');" || echo "Database URL parsing failed, but continuing..."

# Check if redis is available (if not, print warning but continue)
echo "Checking Redis connection..."
python -c "
import redis
import os

try:
    redis_url = os.environ.get('REDIS_URL', 'memory://')
    # Handle memory:// as a special case - this is not a valid Redis URL but used for local environment
    if redis_url == 'memory://':
        print('Using in-memory Redis substitute (for local development)')
    else:
        r = redis.from_url(redis_url)
        r.ping()
        print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
    print('This is normal in local development mode - continuing anyway')
" || echo "Redis check failed, but continuing..."

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
    # Check for CORS headers
    import corsheaders
    print('corsheaders module found')
    # Check for Swagger docs
    try:
        import drf_yasg
        print('drf_yasg module found')
    except ImportError:
        print('WARNING: drf_yasg module not found, Swagger docs will not work')
    # Check if sales module exists
    try:
        import pyerp.core
        print('pyerp.core module found')
        print('NOTE: pyerp.sales module might be configured but not present - application may still work')
    except ImportError as e:
        print(f'Error importing pyerp.core: {e}')
except Exception as e:
    print(f'Error importing application modules: {e}')
    import traceback
    traceback.print_exc()
"

# Test database connectivity with retries
echo "Testing database connectivity..."
MAX_RETRIES=3  # Reduced for local testing
RETRY_INTERVAL=2
RETRY_COUNT=0

# Get database engine type
DB_ENGINE=$(python -c "import dj_database_url; db_url='${DATABASE_URL:-sqlite:///app/db.sqlite3}'; parsed = dj_database_url.parse(db_url); print(parsed['ENGINE'])")
echo "Database engine: $DB_ENGINE"

# Skip connection test for SQLite
if [[ $DB_ENGINE == *sqlite* ]]; then
  echo "SQLite database configured - no connection test needed"
elif [[ $DB_ENGINE == *postgresql* ]]; then
  # PostgreSQL connection test
  echo "PostgreSQL detected - testing connection..."
  # Try to install psycopg2-binary if not already installed
  pip install psycopg2-binary || echo "Failed to install psycopg2-binary, continuing anyway"
  
  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    python -c "
try:
    import dj_database_url
    import psycopg2
    db_url = '${DATABASE_URL}'
    db_config = dj_database_url.parse(db_url)
    print(f'Attempting to connect to PostgreSQL: {db_config}')
        
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
      echo "Failed to connect to PostgreSQL. Retry $RETRY_COUNT of $MAX_RETRIES..."
      if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "Waiting $RETRY_INTERVAL seconds before retry..."
        sleep $RETRY_INTERVAL
      else
        # If we're using local ENV and couldn't connect to PostgreSQL, switch to SQLite
        if [ "$USE_LOCAL_ENV" = "true" ]; then
          echo "Couldn't connect to PostgreSQL in local mode, switching to SQLite..."
          export DATABASE_URL="sqlite:///app/db.sqlite3"
          break
        else
          echo "PostgreSQL connection not available. This is normal when running locally or in CI."
          echo "For a complete deployment, ensure the database is available and correctly configured."
          break
        fi
      fi
    fi
  done
else
  # MySQL connection test (for completeness)
  echo "MySQL detected - testing connection..."
  while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    python -c "
try:
    import dj_database_url
    import pymysql
    # Make sure PyMySQL is installed as MySQLdb
    pymysql.install_as_MySQLdb()
    import MySQLdb as Database
    
    db_url = '${DATABASE_URL}'
    db_config = dj_database_url.parse(db_url)
    print(f'Attempting to connect to MySQL: {db_config}')
        
    # This will raise an exception if connection fails
    conn = Database.connect(
        host=db_config['HOST'], 
        port=int(db_config['PORT']),
        db=db_config['NAME'],
        user=db_config['USER'],
        passwd=db_config['PASSWORD']
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
      echo "Failed to connect to MySQL. Retry $RETRY_COUNT of $MAX_RETRIES..."
      if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "Waiting $RETRY_INTERVAL seconds before retry..."
        sleep $RETRY_INTERVAL
      else
        # If we're using local ENV and couldn't connect to MySQL, switch to SQLite
        if [ "$USE_LOCAL_ENV" = "true" ]; then
          echo "Couldn't connect to MySQL in local mode, switching to SQLite..."
          export DATABASE_URL="sqlite:///app/db.sqlite3"
          break
        else
          echo "Database connection not available. This is normal when running locally or in CI."
          echo "For a complete deployment, ensure the database is available and correctly configured."
          break
        fi
      fi
    fi
  done
fi

# Run migrations for SQLite
if [[ $DB_ENGINE == *sqlite* ]]; then
  echo "Creating SQLite database directory if needed..."
  mkdir -p $(dirname "${DATABASE_URL#sqlite:///}")
  echo "Running migrations for SQLite..."
  python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE --noinput || echo "Migrations failed, but continuing..."
elif [[ $DB_ENGINE == *postgresql* || $DB_ENGINE == *mysql* ]]; then
  # Database migration check
  echo "Checking if database is available for migrations..."
  python -c "
try:
    from django.db import connections
    from django.db.utils import OperationalError
    conn = connections['default']
    conn.cursor()
    print('Database available, will run migrations')
    exit(0)
except OperationalError:
    print('Database not available for migrations')
    exit(1)
except Exception as e:
    print(f'Error checking database: {e}')
    exit(1)
"

  if [ $? -eq 0 ]; then
      echo "Running migrations..."
      python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE --noinput || echo "Migrations failed, but continuing..."
  else
      echo "Skipping migrations as database is not available."
  fi
else
  echo "Unknown database engine: $DB_ENGINE. Skipping migrations."
fi

echo "Running Django checks..."
python manage.py check --settings=$DJANGO_SETTINGS_MODULE || echo "Django checks failed, but continuing..."

# Test WSGI application directly before launching gunicorn
echo "Testing WSGI application directly..."
python -c "
try:
    import pyerp.wsgi
    print('WSGI application imported successfully')
    app = pyerp.wsgi.application
    print('WSGI application created successfully')
except Exception as e:
    print(f'Error importing WSGI application: {e}')
    import traceback
    traceback.print_exc()
"

echo "Starting Gunicorn with detailed error logging..."
exec gunicorn pyerp.wsgi:application --bind 0.0.0.0:8000 --workers 2 --log-level debug --timeout 120 --capture-output --enable-stdio-inheritance 