# pyERP CI/CD Pipeline

This directory contains the CI/CD pipeline configuration for the pyERP system. The pipeline is designed to automate testing, building, and deployment processes.

## Workflows

### Deploy Application (`deploy.yml`)

This workflow handles the deployment of the application to different environments:

- **Development**: Automatically deployed when changes are pushed to the `dev` branch
- **Staging**: Automatically deployed when changes are pushed to any `release/*` branch
- **Production**: Automatically deployed when:
  - A new version tag (`v*`) is pushed
  - The `dev` branch is merged into the `prod` branch via a pull request

#### Production Deployment Process

When the `dev` branch is merged into the `prod` branch, the following steps are executed:

1. Code is checked out
2. Linting and tests are run
3. Docker image is built using `docker/Dockerfile.prod`
4. Image is pushed to GitHub Container Registry
5. Deployment to the production server:
   - Docker Compose files and configuration are copied to the server
   - Latest Docker image is pulled
   - Containers are restarted using `docker-compose.prod.yml`
   - Database migrations are applied
   - Static files are collected

#### Required Secrets

For the deployment to work properly, the following secrets must be configured in the GitHub repository:

**Production Environment:**
- `PROD_SSH_PRIVATE_KEY`: SSH private key for connecting to the production server
- `PROD_DEPLOY_HOST`: Hostname or IP address of the production server
- `PROD_DEPLOY_USER`: Username for SSH connection to the production server
- `PROD_DEPLOY_PATH`: Path on the production server where the application should be deployed

**Development/Staging Environment:**
- `DEV_SSH_PRIVATE_KEY`: SSH private key for connecting to the development/staging server
- `DEV_DEPLOY_HOST`: Hostname or IP address of the development/staging server
- `DEV_DEPLOY_USER`: Username for SSH connection to the development/staging server
- `DEV_DEPLOY_PATH`: Path on the development/staging server where the application should be deployed

**Optional:**
- `SLACK_WEBHOOK_URL`: Webhook URL for Slack notifications (if enabled)

## Server Setup

### Automated Server Setup

The project includes a script to automate the setup of deployment servers. The script is located at `scripts/setup_deployment_server.sh` and can be used to prepare a server for deployment.

#### Usage

```bash
# Basic usage (uses default values)
sudo ./scripts/setup_deployment_server.sh

# Custom configuration
sudo ./scripts/setup_deployment_server.sh <app_user> <app_path> <env_file>
```

#### Required Environment Variables

The script requires the following environment variables to be defined in the specified `.env` file:

- `GITHUB_USERNAME`: GitHub username for accessing the container registry
- `GITHUB_TOKEN`: GitHub personal access token with `read:packages` scope

Other environment variables will be used if present, with sensible defaults provided for missing values:

- Database configuration (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- Email settings (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, etc.)
- Datadog configuration (`DD_API_KEY`, `DD_SITE`)
- Legacy ERP connection settings (if applicable)
- Any other custom environment variables

Example `.env` file:

```
# GitHub credentials for container registry (required)
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-github-personal-access-token

# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pyerp
DB_USER=pyerp
DB_PASSWORD=your-secure-password

# Other environment variables...
```

#### What the Script Does

1. Creates a dedicated user for the application
2. Installs Docker and Docker Compose
3. Creates necessary directories for the application
4. Sets up GitHub Container Registry authentication
5. Creates a production environment file with values from the source environment
6. Copies the source environment file for reference

The script intelligently handles environment variables:
- Uses values from the source environment file when available
- Generates secure random values for sensitive fields like `SECRET_KEY` and `DB_PASSWORD` if not provided
- Automatically detects server hostname and IP addresses for `ALLOWED_HOSTS`
- Includes any additional custom environment variables from the source file

After running the script, you'll need to:
1. Review the generated environment file at `<app_path>/config/env/.env.prod`
2. Set up the CI/CD pipeline in your GitHub repository with the appropriate secrets

### Server Setup Requirements

The target deployment servers should have:

1. Docker and Docker Compose installed
2. Proper network configuration to pull images from GitHub Container Registry
3. Sufficient permissions for the deployment user to run Docker commands
4. Environment files properly configured in the `config/env/` directory

## Manual Deployment

If you need to manually deploy the application, you can follow these steps:

1. SSH into the server
2. Navigate to the application directory
3. Pull the latest code: `git pull origin prod`
4. Pull the latest Docker image: `docker pull ghcr.io/[repository]:[tag]`
5. Restart the containers: `docker-compose -f docker/docker-compose.prod.yml up -d`
6. Apply migrations: `docker-compose -f docker/docker-compose.prod.yml exec pyerp python manage.py migrate`
7. Collect static files: `docker-compose -f docker/docker-compose.prod.yml exec pyerp python manage.py collectstatic --noinput` 