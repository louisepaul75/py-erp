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
- CI/CD pipeline for automated deployments

### Deployment Options

#### Option 1: Automated CI/CD Pipeline (Recommended)

The pyERP system includes a CI/CD pipeline that automatically deploys to production when the `dev` branch is merged into the `prod` branch.

1. **Set Up the Deployment Server**:

   ```bash
   # Copy the setup script to your server
   scp scripts/setup_deployment_server.sh user@your-server-ip:/tmp/

   # Copy your environment file to the server
   scp config/env/.env user@your-server-ip:/tmp/

   # SSH into your server
   ssh user@your-server-ip

   # Run the setup script
   cd /tmp
   chmod +x setup_deployment_server.sh
   sudo ./setup_deployment_server.sh pyerp /opt/pyerp /tmp/.env
   ```

2. **Configure GitHub Repository Secrets**:

   Add the following secrets to your GitHub repository:

   - `PROD_SSH_PRIVATE_KEY`: SSH private key for connecting to your production server
   - `PROD_DEPLOY_HOST`: Hostname or IP address of your production server
   - `PROD_DEPLOY_USER`: Username created by the setup script (default: `pyerp`)
   - `PROD_DEPLOY_PATH`: Path where the application is deployed (default: `/opt/pyerp`)

3. **Deploy to Production**:

   To deploy to production, simply merge your `dev` branch into the `prod` branch:

   ```bash
   git checkout prod
   git merge dev
   git push origin prod
   ```

   The CI/CD pipeline will automatically:
   - Run linting and tests
   - Build the Docker image
   - Push the image to GitHub Container Registry
   - Deploy to your production server

#### Option 2: Manual Deployment

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
- GitHub credentials for container registry:
  - `GITHUB_USERNAME`: GitHub username
  - `GITHUB_TOKEN`: GitHub personal access token with `read:packages` scope

## Automated Server Setup

The project includes a script (`scripts/setup_deployment_server.sh`) to automate the setup of deployment servers.

### What the Script Does

1. Creates a dedicated user for the application
2. Installs Docker and Docker Compose
3. Creates necessary directories for the application
4. Sets up GitHub Container Registry authentication
5. Creates a production environment file with values from the source environment
6. Copies the source environment file for reference

### Required Environment Variables

The script requires the following environment variables to be defined in the specified `.env` file:

- `GITHUB_USERNAME`: GitHub username for accessing the container registry
- `GITHUB_TOKEN`: GitHub personal access token with `read:packages` scope

Other environment variables will be used if present, with sensible defaults provided for missing values:

- Database configuration (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- Email settings (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, etc.)
- Datadog configuration (`DD_API_KEY`, `DD_SITE`)
- Legacy ERP connection settings (if applicable)
- Any other custom environment variables

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
