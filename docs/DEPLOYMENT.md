# pyERP Deployment Guide

This guide provides detailed instructions for deploying the pyERP application in both development and production environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Development Environment](#development-environment)
   - [Unix/Linux Development](#unixlinux-development)
   - [Windows Development](#windows-development)
3. [Production Environment](#production-environment)
4. [Environment Configuration](#environment-configuration)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Database Management](#database-management)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Production Environment (Linux Only)
- Linux OS (Ubuntu 20.04+ recommended)
- Docker Engine 24.0+
- Docker Compose V2
- 4 CPU cores (8+ recommended)
- 8GB RAM (16GB+ recommended)
- 50GB SSD storage (100GB+ recommended)
- Fast internet connection with static IP
- SSL certificate for your domain

### Development Environment
#### Unix/Linux Development with Docker
- Unix-based OS (Linux/macOS)
- Docker Engine 24.0+
- Docker Compose V2
- 4 CPU cores
- 8GB RAM
- 20GB storage

#### Windows Development (Local Mode)
- Windows 10/11
- Python 3.10+
- PostgreSQL 15
- Redis 7
- 4 CPU cores
- 8GB RAM
- 20GB storage

## Development Environment

### Unix/Linux Development

The Docker-based development environment provides a consistent setup with hot-reloading and debugging capabilities.

#### Services
- External PostgreSQL Database (not containerized)
- Redis 7 (Cache & Message Broker)
- Django Development Server
- Celery (Async Task Worker)
- Celery Beat (Task Scheduler)

#### Setup and Running

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/pyerp.git
   cd pyerp
   ```

2. Configure environment variables:
   - Use the environment files in `config/env/` directory
   - For development, use `config/env/.env.dev`
   - For production, use `config/env/.env.prod`
   - Update the variables as needed, especially the external database connection details
   - Set the following environment variables for your external PostgreSQL database:
     ```bash
     export DB_HOST=your_postgres_host
     export DB_PORT=5432
     ```

3. Start the development environment:
   ```bash
   docker compose -f docker/docker-compose.yml up
   ```

4. Access the application:
   - Web application: http://localhost:8050
   - Redis: localhost:6379

### Windows Development

The local development setup runs services directly on Windows without Docker.

#### Prerequisites Installation

1. Install Python 3.10+:
   - Download from python.org
   - Add Python to PATH during installation
   - Verify installation: `python --version`

2. Install PostgreSQL 15:
   - Download from postgresql.org
   - Keep note of the password set during installation
   - Add PostgreSQL bin directory to PATH
   - Verify installation: `psql --version`

3. Install Redis 7:
   - Download Redis for Windows
   - Install as a Windows service
   - Verify installation: `redis-cli --version`

#### Setup and Running

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/pyerp.git
   cd pyerp
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements/local.txt
   ```

4. Configure environment:
   - Copy `.env.example` to `.env`
   - Update database and Redis connection settings
   - Set `DEBUG=True`

5. Initialize database:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Start development server:
   ```bash
   python manage.py runserver 8050
   ```

7. In a new terminal, start Celery worker:
   ```bash
   celery -A pyerp worker -l info
   ```

8. In another terminal, start Celery beat:
   ```bash
   celery -A pyerp beat -l info
   ```

9. Access the application:
   - Web application: http://localhost:8050
   - Database: localhost:5432
   - Redis: localhost:6379

## Production Environment

The production environment is optimized for performance, security, and reliability. Production deployment is supported only on Linux systems.

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Domain name pointing to your server
- SSH access to the server
- Ports 80 and 443 open for web traffic
- Docker and Docker Compose installed
- Git installed
- External PostgreSQL database server

### Deployment Options

#### Option 1: Automated CI/CD Pipeline (Recommended)

The pyERP system includes a CI/CD pipeline that automatically deploys to production when the `dev` branch is merged into the `prod` branch.

1. **Set Up the Deployment Server**:

   Use the provided server setup script to prepare your production server:

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

   The script will:
   - Create a dedicated user for the application
   - Install Docker and Docker Compose
   - Create necessary directories
   - Set up GitHub Container Registry authentication
   - Create a production environment file with values from your source environment

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

If you prefer to deploy manually, follow these steps:

1. Prepare the Linux server:
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install -y curl git software-properties-common
   
   # Install Docker and Docker Compose if not already installed
   curl -fsSL https://get.docker.com | sudo sh
   sudo usermod -aG docker $USER
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/your-org/pyerp.git
   cd pyerp
   ```

3. Configure environment variables:
   - Use the environment files in `config/env/` directory
   - For production, use `config/env/.env.prod`
   - Update all variables with production values:
     - Generate a strong SECRET_KEY
     - Configure external database connection details
     - Configure email settings
     - Update ALLOWED_HOSTS with your domain
     - Configure SSL settings
   - Set the following environment variables for your external PostgreSQL database:
     ```bash
     export DB_HOST=your_postgres_host
     export DB_PORT=5432
     export DB_NAME=pyerp
     export DB_USER=pyerp
     export DB_PASSWORD=your_secure_password
     ```

4. Configure Nginx:
   - Update `nginx/conf.d/default.conf` with your domain
   - Place SSL certificates in `nginx/ssl/` or configure Certbot

5. Start the production environment:
   ```bash
   docker compose -f docker/docker-compose.prod.yml up -d
   ```

6. Initialize the database:
   ```bash
   docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py migrate
   docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py collectstatic --no-input
   docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py createsuperuser
   ```

### Production Environment Features
- Nginx serving static/media files
- SSL/TLS encryption
- External PostgreSQL database
- Redis for caching and Celery
- Celery for background tasks
- Health checks for services
- Automatic database migrations
- Certbot for SSL certificate automation
- CI/CD pipeline for automated deployments

### Required Environment Variables

The deployment requires the following environment variables to be defined in your `.env` file:

- **GitHub Credentials** (required for CI/CD and container registry):
  - `GITHUB_USERNAME`: GitHub username for accessing the container registry
  - `GITHUB_TOKEN`: GitHub personal access token with `read:packages` scope

- **Database Configuration**:
  - `DB_HOST`: Hostname or IP address of your PostgreSQL server
  - `DB_PORT`: Port number (default: 5432)
  - `DB_NAME`: Database name
  - `DB_USER`: Database username
  - `DB_PASSWORD`: Database password

- **Django Settings**:
  - `SECRET_KEY`: Django secret key
  - `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
  - `DEBUG`: Set to False for production

- **Email Settings**:
  - `EMAIL_HOST`: SMTP server hostname
  - `EMAIL_PORT`: SMTP port
  - `EMAIL_HOST_USER`: SMTP username
  - `EMAIL_HOST_PASSWORD`: SMTP password
  - `EMAIL_USE_TLS`: Whether to use TLS
  - `DEFAULT_FROM_EMAIL`: Default sender email

- **Optional Settings**:
  - `DD_API_KEY`: Datadog API key (if using Datadog)
  - `DD_SITE`: Datadog site (default: datadoghq.com)
  - Legacy ERP connection settings (if applicable)

### Monitoring and Maintenance

#### Viewing Logs
```bash
# View all container logs
docker compose -f docker/docker-compose.prod.yml logs -f

# View logs for a specific service
docker compose -f docker/docker-compose.prod.yml logs -f pyerp
```

#### Restarting Services
```bash
# Restart all services
docker compose -f docker/docker-compose.prod.yml restart

# Restart a specific service
docker compose -f docker/docker-compose.prod.yml restart pyerp
```

#### Updating the Application
When using the CI/CD pipeline, updates are automatically deployed when changes are merged to the `prod` branch.

For manual updates:
```bash
# Pull the latest code
git pull origin prod

# Rebuild and restart containers
docker compose -f docker/docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker/docker-compose.prod.yml exec pyerp python manage.py migrate
```

## Environment Configuration

### Unix/Linux Development Environment (`docker.env.dev`)
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
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT:-5432}

# Redis and Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Windows Development Environment (`.env`)
```env
# Key settings
DEBUG=True
SECRET_KEY=dev_secret_key_replace_in_production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pyerp_dev
DB_USER=postgres
DB_PASSWORD=your_local_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Redis and Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Development-specific
DJANGO_SETTINGS_MODULE=pyerp.settings.development
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Windows-specific
PYTHONUNBUFFERED=1
COMPOSE_CONVERT_WINDOWS_PATHS=1
```

### Production Environment (`docker.env.prod`)
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

