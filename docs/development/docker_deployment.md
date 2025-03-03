# Docker Deployment Structure

This document outlines the Docker deployment structure for the pyERP system, which consists of two primary deployment modes: development and production.

## Overview

The pyERP system uses Docker and Docker Compose for containerization, with separate configurations for development and production environments. This separation ensures that development can proceed smoothly with debugging capabilities while production remains secure and optimized for performance.

## Directory Structure

```
docker/
├── Dockerfile.dev           # Development Dockerfile
├── Dockerfile.prod          # Production Dockerfile
├── docker-compose.yml      # Development compose file
├── docker-compose.prod.yml # Production compose file
├── docker.env.dev          # Development environment variables
├── docker.env.prod         # Production environment variables
├── nginx/                  # Nginx configuration for production
│   ├── conf.d/            # Nginx site configurations
│   └── ssl/               # SSL certificates
└── certbot/               # SSL certificate automation
    ├── conf/              # Certbot configuration
    └── www/               # Certbot webroot
```

## Development Mode

### Components
- External PostgreSQL Database (not containerized)
- Redis 7 (Cache & Message Broker)
- Django Development Server
- Celery (Async Task Worker)
- Celery Beat (Task Scheduler)

### Features
- Live code reloading
- Debug mode enabled
- Single container deployment
- Console email backend
- Django debug toolbar
- Development-specific settings
- Connection to external PostgreSQL database

### Configuration
- Uses `docker-compose.yml`
- Environment variables in `docker.env.dev`
- Single volume for application data
- Development-specific Django settings
- External database connection parameters

### Usage
```bash
# Set external database connection environment variables
export DB_HOST=your_postgres_host
export DB_PORT=5432
export DB_NAME=pyerp_dev
export DB_USER=postgres
export DB_PASSWORD=your_password

# Start development environment
docker compose up

# Run migrations
docker compose exec pyerp python manage.py migrate

# Create superuser
docker compose exec pyerp python manage.py createsuperuser
```

## Production Mode

### Components
- External PostgreSQL Database (not containerized)
- Redis 7 (Cache & Message Broker)
- Django with Gunicorn (Application Server)
- Nginx (Web Server)
- Celery (Async Task Worker)
- Celery Beat (Task Scheduler)

### Features
- Optimized for performance
- SSL/TLS encryption
- Health checks for services
- Single container deployment
- Production-grade security settings
- Automated SSL certificate management
- Background task processing
- Connection to external PostgreSQL database

### Configuration
- Uses `docker-compose.prod.yml`
- Environment variables in `docker.env.prod`
- Nginx for reverse proxy and static files
- Celery for background tasks
- SSL certificates via Certbot
- External database connection parameters

### Usage
```bash
# Set external database connection environment variables
export DB_HOST=your_postgres_host
export DB_PORT=5432
export DB_NAME=pyerp
export DB_USER=pyerp
export DB_PASSWORD=your_password

# Start production environment
docker compose -f docker/docker-compose.prod.yml up -d

# Initialize database
docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py migrate
docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py collectstatic --no-input
docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py createsuperuser
```

## Environment Variables

### Development (`docker.env.dev`)
- DEBUG=True
- External database connection parameters
- Local email backend
- Development-specific settings
- Redis configuration

### Production (`docker.env.prod`)
- DEBUG=False
- External database connection parameters
- SMTP email configuration
- SSL/TLS settings
- Security headers
- Production-specific settings
- Redis configuration

## Volumes

### Development
- `pyerp_data`: Application data

### Production
- `pyerp_data`: Application data
- `certbot/conf`: SSL certificates
- `certbot/www`: SSL verification

## Database Configuration

The pyERP system is configured to use an external PostgreSQL database. You must provide the following environment variables:

- `DB_HOST`: Hostname or IP address of your PostgreSQL server
- `DB_PORT`: Port number (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password

These can be set in your environment or in the respective `.env` files.

## Security Considerations

### Development
- Debug mode enabled
- Exposed service ports
- External database connection
- No SSL required

### Production
- Debug mode disabled
- Restricted service access
- Strong passwords required
- SSL/TLS encryption
- Security headers enabled
- Regular security updates
- Proper user permissions
- Secure environment variables
- External database connection with proper security

## Maintenance

### Development
```bash
# View logs
docker compose logs -f

# Rebuild containers
docker compose build
docker compose up -d
```

### Production
```bash
# View logs
docker compose -f docker/docker-compose.prod.yml logs -f

# Rebuild containers
docker compose -f docker/docker-compose.prod.yml build
docker compose -f docker/docker-compose.prod.yml up -d

# SSL certificate renewal
docker compose -f docker/docker-compose.prod.yml run --rm certbot renew
```

## Health Monitoring

The environment includes health checks for critical services:

### Redis
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Web (Production)
```yaml
healthcheck:
  test: curl --fail http://localhost:8050/admin/ || exit 1
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

Monitor service health with:
```bash
# Development
docker compose ps

# Production
docker compose -f docker/docker-compose.prod.yml ps
``` 