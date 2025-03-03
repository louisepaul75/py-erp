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
- PostgreSQL 15 (Database)
- Redis 7 (Cache & Message Broker)
- Django Development Server

### Features
- Live code reloading
- Debug mode enabled
- Exposed ports for direct database/Redis access
- Console email backend
- Django debug toolbar
- Development-specific settings

### Configuration
- Uses `docker-compose.yml`
- Environment variables in `docker.env.dev`
- Mounts local code directory for live updates
- Development-specific Django settings

### Usage
```bash
# Start development environment
docker compose up

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser
```

## Production Mode

### Components
- PostgreSQL 15 (Database)
- Redis 7 (Cache & Message Broker)
- Django with Gunicorn (Application Server)
- Nginx (Web Server)
- Celery (Async Task Worker)
- Celery Beat (Task Scheduler)

### Features
- Optimized for performance
- SSL/TLS encryption
- Health checks for all services
- Proper service isolation
- Production-grade security settings
- Automated SSL certificate management
- Background task processing

### Configuration
- Uses `docker-compose.prod.yml`
- Environment variables in `docker.env.prod`
- Nginx for reverse proxy and static files
- Celery for background tasks
- SSL certificates via Certbot

### Usage
```bash
# Start production environment
docker compose -f docker-compose.prod.yml up -d

# Initialize database
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Environment Variables

### Development (`docker.env.dev`)
- DEBUG=True
- Development database credentials
- Local email backend
- Development-specific settings
- Exposed service ports

### Production (`docker.env.prod`)
- DEBUG=False
- Production database credentials
- SMTP email configuration
- SSL/TLS settings
- Security headers
- Production-specific settings

## Volumes

### Development
- `postgres_data_dev`: PostgreSQL data
- `redis_data_dev`: Redis data
- `static_volume_dev`: Static files
- `media_volume_dev`: Media files

### Production
- `postgres_data_prod`: PostgreSQL data
- `redis_data_prod`: Redis data
- `static_volume`: Static files
- `media_volume`: Media files
- `log_volume`: Application logs
- `certbot/conf`: SSL certificates
- `certbot/www`: SSL verification

## Security Considerations

### Development
- Debug mode enabled
- Exposed service ports
- Default credentials acceptable
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

## Maintenance

### Development
```bash
# View logs
docker compose logs -f [service]

# Rebuild containers
docker compose build
docker compose up -d

# Database operations
docker compose exec db pg_dump -U postgres pyerp_dev > backup_dev.sql
docker compose exec -T db psql -U postgres pyerp_dev < backup_dev.sql
```

### Production
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f [service]

# Rebuild containers
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Database operations
docker compose -f docker-compose.prod.yml exec db pg_dump -U pyerp pyerp > backup_prod.sql
docker compose -f docker-compose.prod.yml exec -T db psql -U pyerp pyerp < backup_prod.sql

# SSL certificate renewal
docker compose -f docker-compose.prod.yml run --rm certbot renew
```

## Health Monitoring

Both environments include health checks for critical services:

### Database
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 10s
  timeout: 5s
  retries: 5
```

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
docker compose -f docker-compose.prod.yml ps
``` 