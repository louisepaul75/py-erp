# MySQL Setup for Development Environment

## Overview

This document provides instructions for setting up the MySQL connection for the pyERP development environment. We are migrating from SQLite to MySQL to ensure consistency between development and production environments.

## Connection to Existing MySQL Server

The project is configured to connect to an existing MySQL server at IP address `192.168.73.64`. This server is already set up and running, so there's no need to install MySQL locally.

### Environment Configuration

1. Ensure your `.env` file contains the following settings:
   ```
   DB_NAME=pyerp_testing
   DB_USER=admin
   DB_PASSWORD=admin123
   DB_HOST=192.168.73.64
   DB_PORT=3306
   ```

2. Verify that `pyerp/settings/development.py` is configured to use MySQL:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': os.environ.get('DB_NAME', 'pyerp_testing'),
           'USER': os.environ.get('DB_USER', 'admin'),
           'PASSWORD': os.environ.get('DB_PASSWORD', 'admin123'),
           'HOST': os.environ.get('DB_HOST', '192.168.73.64'),
           'PORT': os.environ.get('DB_PORT', '3306'),
       }
   }
   ```

## Database Setup

If the `pyerp_testing` database doesn't already exist on the MySQL server, you'll need to create it:

1. Connect to the MySQL server:
   ```
   mysql -h 192.168.73.64 -u admin -p
   ```
   Enter the password when prompted.

2. Create the database if it doesn't exist:
   ```sql
   CREATE DATABASE IF NOT EXISTS pyerp_testing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. Exit MySQL:
   ```sql
   EXIT;
   ```

## Running Migrations

After configuring the connection to the MySQL server, you need to run migrations to create the necessary tables:

```
python manage.py migrate
```

## Migrating Data from SQLite

If you have existing data in SQLite that you want to migrate to MySQL:

1. Create a JSON dump of your SQLite data:
   ```
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_dump.json
   ```

2. Apply migrations to the MySQL database:
   ```
   python manage.py migrate
   ```

3. Load the data into MySQL:
   ```
   python manage.py loaddata data_dump.json
   ```

## Verification

To verify that your MySQL connection is working correctly:

1. Run the Django development server:
   ```
   python manage.py runserver
   ```

2. Access the admin interface and check if you can view and edit data

3. Run the test suite:
   ```
   python manage.py test
   ```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Verify network connectivity to the MySQL server:
   ```
   ping 192.168.73.64
   ```

2. Check if you can connect to the MySQL server using the MySQL client:
   ```
   mysql -h 192.168.73.64 -u admin -p
   ```

3. Ensure the user has the correct privileges:
   ```sql
   SHOW GRANTS FOR 'admin'@'%';
   ```

4. Check if the MySQL server allows remote connections:
   - The MySQL server must be configured to accept connections from your IP address
   - The user must be allowed to connect from your host (`'admin'@'%'` or `'admin'@'your-ip'`)

### Migration Issues

If you encounter issues with migrations:

1. Reset migrations if necessary:
   ```
   python manage.py migrate --fake zero
   python manage.py migrate --fake
   ```

2. For specific app issues, try:
   ```
   python manage.py migrate app_name --fake-initial
   ```

## Additional Resources

- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Django Database Documentation](https://docs.djangoproject.com/en/stable/ref/databases/)
- [MySQL Python Connector Documentation](https://dev.mysql.com/doc/connector-python/en/) 