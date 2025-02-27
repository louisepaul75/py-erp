# Dependency Management Guide

## Overview

This guide explains the dependency management approach used in the pyERP project. We use pip-tools and Docker to create reproducible and consistent development and production environments.

## Requirements Structure

We organize our dependencies into three categories:

1. **Base Dependencies** (`requirements/base.in`): Core dependencies used in all environments
2. **Production Dependencies** (`requirements/production.in`): Dependencies needed specifically for production
3. **Development Dependencies** (`requirements/development.in`): Additional dependencies needed for development and testing

These are compiled into corresponding `.txt` files using pip-tools.

## Adding Dependencies

### Step 1: Add to the appropriate .in file

Choose the appropriate file based on where the dependency will be used:

```bash
# For core dependencies (Django, database clients, etc.)
requirements/base.in

# For production-only dependencies (Gunicorn, monitoring tools, etc.)
requirements/production.in

# For development-only dependencies (debugging tools, testing frameworks, etc.)
requirements/development.in
```

Add the dependency with a loose version constraint:

```
# Example: Add Django Debug Toolbar to development.in
django-debug-toolbar>=4.2.0,<4.3.0
```

### Step 2: Compile the requirements

Run the dependency update script:

```bash
# From inside the Docker development container
python scripts/update_dependencies.py
```

Or manually compile using pip-compile:

```bash
# Compile the base requirements
pip-compile requirements/base.in --output-file=requirements/base.txt

# Compile production requirements
pip-compile requirements/production.in --output-file=requirements/production.txt

# Compile development requirements
pip-compile requirements/development.in --output-file=requirements/development.txt
```

### Step 3: Rebuild your Docker environment

```bash
# Rebuild to include new dependencies
docker-compose build
docker-compose up -d
```

## Updating Dependencies

We use a scheduled approach to dependency updates:

1. Weekly automated checks for updates (via GitHub Actions or a similar CI tool)
2. Security patches should be applied immediately
3. Major version upgrades should be carefully tested

### Manual Update Process

To manually update all dependencies:

```bash
# Run the update script
python scripts/update_dependencies.py
```

The script will:
1. Upgrade all dependencies to their latest compatible versions
2. Generate a summary of changes

### Security Scanning

We regularly scan dependencies for security vulnerabilities using the Safety package:

```bash
# Run the security scan
python scripts/security_scan.py
```

## Development Environment

Our development environment is Docker-based to ensure consistent dependencies across all developer machines.

### Setup

```bash
# Build and start the development environment
docker-compose up -d
```

### Troubleshooting

If you encounter issues with dependencies:

1. **Dependency conflict**: Check the output of pip-compile for conflicts
2. **Missing dependency**: Ensure you've added it to the correct `.in` file and recompiled
3. **Docker caching issues**: Try rebuilding without cache: `docker-compose build --no-cache`

## Production Deployment

We use a multi-stage build process to create optimized and secure Docker images for production:

```bash
# Build the production image
docker-compose -f docker/docker-compose.prod.yml build

# Start the production services
docker-compose -f docker/docker-compose.prod.yml up -d
```

## Best Practices

1. **Version Constraints**: Always use version constraints in `.in` files
2. **Minimize Production Dependencies**: Keep production containers lean
3. **Security First**: Run security scans regularly
4. **Documentation**: Document why non-obvious dependencies are included
5. **License Compliance**: Verify license compatibility for all dependencies 