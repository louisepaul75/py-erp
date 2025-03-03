# pyERP Deployment Guide

This guide provides detailed instructions for deploying the pyERP application in both development and production environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Development Environment](#development-environment)
3. [Production Environment](#production-environment)
4. [Environment Configuration](#environment-configuration)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Database Management](#database-management)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- 4 CPU cores
- 8GB RAM
- 50GB SSD storage
- Docker Engine 24.0+
- Docker Compose V2

### Recommended Requirements
- 8+ CPU cores
- 16GB+ RAM
- 100GB+ SSD storage
- Docker Engine 24.0+
- Docker Compose V2
- Fast internet connection with static IP (for production)

## Development Environment

The development environment is configured for local development with hot-reloading and debugging capabilities.

### Services
- PostgreSQL 15 (Database)
- Redis 7 (Cache & Message Broker)
- Django Development Server

### Setup and Running

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/pyerp.git
   cd pyerp
   ```

2. Configure environment variables:
   - Copy `docker/docker.env.dev.example` to `docker/docker.env.dev`
   - Update the variables as needed (default values work for local development)

3. Start the development environment:
   ```bash
   docker compose up
   ```

4. Access the application:
   - Web application: http://localhost:8050
   - Database: localhost:5432
   - Redis: localhost:6379

### Development Environment Features
- Live code reloading
- PostgreSQL exposed on port 5432 for local database tools
- Redis exposed on port 6379 for local monitoring
- Console email backend for easy testing
- Django debug toolbar enabled
- Static and media files served by Django

## Production Environment

The production environment is optimized for performance, security, and reliability.

### Services
- PostgreSQL 15 (Database)
- Redis 7 (Cache & Message Broker)
- Django with Gunicorn (Application Server)
- Nginx (Web Server)
- Celery (Async Task Worker)
- Celery Beat (Task Scheduler)

### Setup and Running

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/pyerp.git
   cd pyerp
   ```

2. Configure environment variables:
   - Copy `docker/docker.env.prod.example` to `docker/docker.env.prod`
   - Update all variables with production values:
     - Generate a strong SECRET_KEY
     - Set secure database passwords
     - Configure email settings
     - Update ALLOWED_HOSTS with your domain
     - Configure SSL settings

3. Configure Nginx:
   - Update `nginx/conf.d/default.conf` with your domain
   - Place SSL certificates in `nginx/ssl/` or configure Certbot

4. Start the production environment:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

5. Initialize the database:
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py migrate
   docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
   docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

### Production Environment Features
- Nginx serving static/media files
- SSL/TLS encryption
- PostgreSQL with persistent volume
- Redis for caching and Celery
- Celery for background tasks
- Health checks for all services
- Automatic database migrations
- Certbot for SSL certificate automation

## Environment Configuration

### Development Environment Variables (`docker.env.dev`)
```env
# Key settings
DEBUG=True
SECRET_KEY=dev_secret_key_replace_in_production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pyerp_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis and Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Development-specific
DJANGO_SETTINGS_MODULE=pyerp.settings.development
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production Environment Variables (`docker.env.prod`)
```env
# Key settings
DEBUG=False
SECRET_KEY=your_production_secret_key_here
ALLOWED_HOSTS=your.domain.com

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pyerp
DB_USER=pyerp
DB_PASSWORD=your_secure_password_here
DB_HOST=db
DB_PORT=5432

# Redis and Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Security settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## SSL Certificate Setup

### Using Certbot
1. Initial certificate creation:
   ```bash
   docker compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d your.domain.com
   ```

2. Certificate renewal:
   ```bash
   docker compose -f docker-compose.prod.yml run --rm certbot renew
   ```

### Manual SSL Certificates
1. Place your certificates in `nginx/ssl/`:
   - `nginx/ssl/your.domain.com.crt`
   - `nginx/ssl/your.domain.com.key`

2. Update Nginx configuration accordingly

## Database Management

### Backup
```bash
# Development
docker compose exec db pg_dump -U postgres pyerp_dev > backup_dev.sql

# Production
docker compose -f docker-compose.prod.yml exec db pg_dump -U pyerp pyerp > backup_prod.sql
```

### Restore
```bash
# Development
docker compose exec -T db psql -U postgres pyerp_dev < backup_dev.sql

# Production
docker compose -f docker-compose.prod.yml exec -T db psql -U pyerp pyerp < backup_prod.sql
```

## Monitoring and Maintenance

### Logs
```bash
# View service logs
docker compose -f docker-compose.prod.yml logs -f [service_name]

# Available services: web, db, redis, nginx, celery, celery-beat
```

### Health Checks
All services have built-in health checks. Monitor them with:
```bash
docker compose -f docker-compose.prod.yml ps
```

### Updates
1. Pull latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart services:
   ```bash
   # Development
   docker compose build
   docker compose up -d

   # Production
   docker compose -f docker-compose.prod.yml build
   docker compose -f docker-compose.prod.yml up -d
   ```

## Troubleshooting

### Common Issues

1. Database connection errors:
   - Check if database service is healthy
   - Verify database credentials in environment file
   - Ensure database port is not conflicting

2. Redis connection errors:
   - Check Redis service health
   - Verify Redis URL in environment file
   - Check if Redis port is accessible

3. Static files not serving:
   - Run collectstatic command
   - Check Nginx configuration
   - Verify volume mounts

4. Email not working:
   - Verify email settings in environment file
   - Check email provider access
   - Review email logs

### Debug Commands

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps

# View service logs
docker compose -f docker-compose.prod.yml logs -f service_name

# Check container health
docker inspect container_name | grep Health

# Enter container shell
docker compose -f docker-compose.prod.yml exec service_name bash
```

