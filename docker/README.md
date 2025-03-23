# Docker Setup for pyERP

This directory contains Docker configuration files for the pyERP system.

## Environment Files

**IMPORTANT UPDATE**: We are consolidating environment files. The Docker-specific environment files (`docker.env.dev` and `docker.env.prod`) are being migrated to the central environment files in `config/env/`. Please refer to the [Environment Consolidation Plan](../docs/ENV_CONSOLIDATION.md) for details.

**IMPORTANT**: The environment files contain sensitive information and should not be committed to version control.

### Environment Files (Legacy - Being Phased Out)
- `docker.env.dev.example`: Template for development environment settings
- `docker.env.prod.example`: Template for production environment settings
- `docker.env.dev`: Your actual development environment settings (not tracked in Git)
- `docker.env.prod`: Your actual production environment settings (not tracked in Git)

### New Environment Files (Consolidated)
- `config/env/.env.dev`: Development environment settings
- `config/env/.env.prod`: Production environment settings

## Setup Instructions

### Initial Setup

```bash
# Copy example environment files (Legacy - use config/env files instead)
cp docker.env.dev.example docker.env.dev
cp docker.env.prod.example docker.env.prod
```

### Configuration

- Development: Edit `config/env/.env.dev` with development settings
- Production: Edit `config/env/.env.prod` with production settings

## Database Configuration

### Development

- Default credentials in `config/env/.env.dev`
- Uses PostgreSQL database

### Production

- Secure credentials required in `config/env/.env.prod`
- Uses PostgreSQL database

## Running Docker Containers

### Development

```bash
docker-compose up
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Included Development Tools

The Docker development environment includes several tools to aid development:

### Testing Tools
- **Jest**: JavaScript testing framework
- **Stryker Mutator (v8.7.1)**: Mutation testing framework for JavaScript
  - Available commands:
    - `npm run test:mutation`: Run mutation tests
    - `npm run test:mutation:report`: View mutation test report

### Viewing Mutation Test Reports

The mutation test reports can be viewed by running:

```bash
# From the frontend-react directory inside the container
npm run test:mutation:report
```

This will serve the HTML report, typically accessible at http://localhost:3000.

## Docker Files

```
docker/
├── Dockerfile.dev         # Development Dockerfile
├── Dockerfile.prod        # Production Dockerfile
├── docker-compose.yml     # Development Docker Compose
├── docker-compose.prod.yml # Production Docker Compose
├── entrypoint.sh          # Container entrypoint script
├── start.sh               # Application startup script
├── supervisord.conf       # Supervisor configuration
├── nginx/                 # Nginx configuration
│   └── conf.d/            # Nginx site configuration
│       └── pyerp.conf     # pyERP Nginx configuration
├── docker.env.dev          # Development environment variables (legacy)
├── docker.env.prod         # Production environment variables (legacy)
└── README.md              # This file
```

## Troubleshooting

If you encounter issues with Docker:

1. Check container logs:
   ```bash
   docker-compose logs
   ```

2. Verify environment variables are set correctly.

3. Ensure PostgreSQL is accessible from the container.

4. Check for port conflicts on the host machine.

## Monitoring

To start the monitoring services (Elasticsearch and Kibana), run:

```bash
cd docker
docker-compose -f docker-compose.monitoring.yml up -d
```

This will start:
- Elasticsearch on port 9200
- Kibana on port 5601

You can access the Kibana UI at http://localhost:5601 to monitor and manage your Elasticsearch instance.

### Stopping Monitoring

To stop the monitoring services, run:

```bash
cd docker
docker-compose -f docker-compose.monitoring.yml down
```
