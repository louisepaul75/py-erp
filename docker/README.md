# Docker Configuration

This directory contains configuration files for Docker deployment of the pyERP application.

## Environment Files

### Security Warning

**IMPORTANT**: The environment files (`docker.env.dev` and `docker.env.prod`) contain sensitive information 
and should never be committed to version control. These files are included in `.gitignore` to help prevent 
accidental commits.

### Available Files

- `docker.env.dev.example`: Template for development environment settings
- `docker.env.prod.example`: Template for production environment settings
- `docker.env.dev`: Your actual development environment settings (not tracked in Git)
- `docker.env.prod`: Your actual production environment settings (not tracked in Git)

## Setup Instructions

1. Copy the example files to create your actual configuration:
   ```bash
   # For development
   cp docker.env.dev.example docker.env.dev
   
   # For production
   cp docker.env.prod.example docker.env.prod
   ```

2. Edit the environment files with appropriate settings:
   - Development: Edit `docker.env.dev` with development settings
   - Production: Edit `docker.env.prod` with production settings

## Database Configuration

The Docker containers use PostgreSQL for both development and production environments:

1. **Development Database**: 
   - Default credentials in `docker.env.dev`
   - Database exposed on port 5432 for local development tools

2. **Production Database**:
   - Secure credentials required in `docker.env.prod`
   - Database not exposed externally
   - Regular backups recommended

## Example Docker Commands

**Development mode:**
```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# View logs
docker compose logs -f
```

**Production mode:**
```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Execute commands
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

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

For detailed deployment instructions, see:
- [Development Docker Setup](../docs/development/docker_deployment.md#development-mode)
- [Production Docker Setup](../docs/development/docker_deployment.md#production-mode) 