#!/bin/bash

# Setup PostgreSQL database adapter
echo "Setting up PostgreSQL database adapter..."
if python -c "import psycopg2" 2>/dev/null; then
    echo "psycopg2 found and working"
else
    echo "WARNING: psycopg2 is not available"
    echo "Will continue but PostgreSQL database connections may fail"
fi

# Create required directories
echo "Creating required directories..."
mkdir -p /app/logs
mkdir -p /app/media
mkdir -p /app/static
mkdir -p /app/data

# Install Python dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Install development dependencies if requirements-dev.txt exists
if [ -f requirements-dev.txt ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Check for missing dependencies
echo "Checking for missing dependencies..."
for package in drf-yasg django-filter corsheaders rest_framework_simplejwt django_redis; do
    if ! python -c "import $package" 2>/dev/null; then
        echo "Installing missing package: $package"
        pip install $package
    fi
done

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Start the application
echo "Starting the application..."
exec "$@" 