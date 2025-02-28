# Docker Management Scripts

This directory contains scripts for managing Docker containers in the pyERP project across different environments.

## Linux Usage

1. First, make the scripts executable:

   ```bash
   chmod +x scripts/docker_rebuild.sh
   chmod +x scripts/docker_rebuild_with_nginx.sh
   ```

2. Run the appropriate script from the project root directory:

   ```bash
   # For standard Docker setup
   ./scripts/docker_rebuild.sh

   # For setup with separate Nginx container
   ./scripts/docker_rebuild_with_nginx.sh
   ```

### Linux Script Features

The Linux scripts now include:

- **Automatic Docker Compose file detection**: The scripts will search for `docker-compose.yml` in common locations
- **Interactive mode**: If no Docker Compose file is found, you'll be prompted to enter the path
- **Nginx detection**: The scripts can determine if Nginx is in a separate compose file
- **Error handling**: Clear error messages with appropriate exit codes
- **Network configuration**: Automatic Docker network setup for container communication

## Windows Usage

1. For PowerShell (recommended):

   ```powershell
   # For standard Docker setup
   .\scripts\docker_rebuild.ps1

   # For setup with separate Nginx container
   .\scripts\docker_rebuild_with_nginx.ps1
   ```

2. For Command Prompt:

   ```cmd
   scripts\docker_rebuild.bat
   ```

## Troubleshooting

If you encounter issues after rebuilding the containers:

1. Check the [Docker HTTPS Troubleshooting Guide](docker_https_troubleshooting.md) for solutions to common HTTPS-related issues.

2. Check the Docker logs:

   ```bash
   # Linux/Mac/PowerShell
   docker logs pyerp-web
   docker logs pyerp-nginx

   # Or follow the logs live
   docker logs -f pyerp-web
   ```

3. Ensure the containers are on the same Docker network:

   ```bash
   docker network inspect pyerp-network
   ```

4. If you still have the "too many redirects" error:
   - Clear your browser cache and cookies completely
   - Try using an incognito/private browser window
   - Verify the Nginx configuration has `proxy_set_header X-Forwarded-Proto https;`
   - Check that Django has imported the HTTPS settings correctly

## Script Descriptions

- `docker_rebuild.sh` / `docker_rebuild.ps1` / `docker_rebuild.bat`: Basic rebuild scripts that stop containers, pull latest code, rebuild, and restart.

- `docker_rebuild_with_nginx.sh` / `docker_rebuild_with_nginx.ps1`: Advanced scripts that handle separate Django and Nginx containers, with proper networking setup.

- `docker_https_troubleshooting.md`: Comprehensive guide for troubleshooting HTTPS-related issues. 