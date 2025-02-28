#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Create log directories
mkdir -p /var/log/supervisor /var/log/nginx /var/log/mysql /var/log/redis

# Initialize MySQL data directory if it doesn't exist
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo "Initializing MySQL data directory..."
    mkdir -p /var/lib/mysql
    chown -R mysql:mysql /var/lib/mysql
    mysqld --initialize-insecure --user=mysql || echo "MySQL data directory already initialized"
fi

# Start MariaDB service
echo "Starting MariaDB service..."
mkdir -p /run/mysqld
chown mysql:mysql /run/mysqld
/etc/init.d/mariadb start || mysqld_safe &
sleep 10  # Give MariaDB more time to start

# Setup MySQL database
echo "Setting up MySQL database..."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME:-pyerp_testing};" || echo "Database already exists"
mysql -u root -e "CREATE USER IF NOT EXISTS '${DB_USER:-admin}'@'localhost' IDENTIFIED BY '${DB_PASSWORD:-password}';" || echo "User already exists"
mysql -u root -e "GRANT ALL PRIVILEGES ON ${DB_NAME:-pyerp_testing}.* TO '${DB_USER:-admin}'@'localhost';" || echo "Privileges already granted"
mysql -u root -e "FLUSH PRIVILEGES;" || echo "Failed to flush privileges"

# Start Redis service
echo "Starting Redis service..."
service redis-server start || redis-server &
sleep 2  # Give Redis time to start

# Function to check if MySQL is ready
mysql_ready() {
    # Try both socket and TCP connection methods
    mysqladmin ping -h localhost -u root > /dev/null 2>&1 || \
    mysql -h localhost -u root -e "SELECT 1;" > /dev/null 2>&1
}

# Function to check if Redis is ready
redis_ready() {
    redis-cli ping > /dev/null 2>&1
}

# Wait for MySQL to be ready
until mysql_ready; do
  echo >&2 "MySQL is unavailable - waiting..."
  sleep 1
done
echo >&2 "MySQL is up - continuing..."

# Wait for Redis to be ready
until redis_ready; do
  echo >&2 "Redis is unavailable - waiting..."
  sleep 1
done
echo >&2 "Redis is up - continuing..."

# Setup PyMySQL to work with Django
python -c "import pymysql; pymysql.install_as_MySQLdb()" || echo "Failed to setup PyMySQL"

# Apply database migrations
echo >&2 "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo >&2 "Collecting static files..."
python manage.py collectstatic --noinput

# Create media and static directories with proper permissions
mkdir -p /app/media /app/static /var/www/static /var/www/media
chmod -R 755 /app/media /app/static /var/www/static /var/www/media

# Copy static files to Nginx static directory
cp -r /app/static/* /var/www/static/ || echo "No static files to copy"

# Create superuser if needed
if [ "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    echo >&2 "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser may already exist"
fi

# Configure Nginx to use the correct hostname
if [ -n "${NGINX_HOST:-}" ]; then
    echo "Configuring Nginx for host: ${NGINX_HOST}"
    sed -i "s/server_name localhost;/server_name ${NGINX_HOST};/g" /etc/nginx/conf.d/pyerp.conf
fi

# Start supervisord
echo "Starting all services with supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf