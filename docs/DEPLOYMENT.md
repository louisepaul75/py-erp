# pyERP Deployment Guide

This guide provides detailed instructions for deploying the pyERP application in both development and production environments, starting from a blank Windows VM.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Server Setup](#initial-server-setup)
3. [Installing Docker and Docker Compose](#installing-docker-and-docker-compose)
4. [Setting Up Portainer for Container Management](#setting-up-portainer-for-container-management)
5. [Development Environment Deployment](#development-environment-deployment)
6. [Production Environment Deployment](#production-environment-deployment)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Database Management](#database-management)
9. [Backup and Restore Procedures](#backup-and-restore-procedures)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Troubleshooting](#troubleshooting)
12. [Updating the Application](#updating-the-application)

## System Requirements

### Minimum Requirements
- Windows Server 2019 or Windows 10/11 Pro/Enterprise
- 4 CPU cores
- 8GB RAM
- 100GB SSD storage
- Internet connection

### Recommended Requirements
- Windows Server 2022 or Windows 11 Pro/Enterprise
- 8+ CPU cores
- 16GB+ RAM
- 250GB+ SSD storage
- Fast internet connection with static IP

## Initial Server Setup

1. **Windows Updates**:
   ```powershell
   # Check for Windows updates
   Get-WindowsUpdate
   
   # Install all available updates
   Install-WindowsUpdate -AcceptAll
   ```

2. **Install Required Windows Features**:
   ```powershell
   # Install Hyper-V (required for Docker)
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   
   # Install Containers feature
   Enable-WindowsOptionalFeature -Online -FeatureName Containers -All
   ```

3. **Configure Firewall**:
   ```powershell
   # Allow HTTP/HTTPS traffic
   New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
   New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
   
   # Allow Portainer access (if exposed externally)
   New-NetFirewallRule -DisplayName "Allow Portainer" -Direction Inbound -Protocol TCP -LocalPort 9000 -Action Allow
   ```

4. **Create Service Account** (optional but recommended):
   ```powershell
   # Create a new user for running services
   New-LocalUser -Name "pyerp-service" -Description "Service account for pyERP" -Password (ConvertTo-SecureString "YourStrongPassword" -AsPlainText -Force) -PasswordNeverExpires
   
   # Add to appropriate groups
   Add-LocalGroupMember -Group "Users" -Member "pyerp-service"
   ```

## Installing Docker and Docker Compose

1. **Install Docker Desktop on Windows**:
   - Download Docker Desktop from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
   - Run the installer and follow the installation wizard
   - During installation, ensure "Use WSL 2 instead of Hyper-V" is selected if you'll be using WSL
   - Complete the installation and restart if prompted
   - Start Docker Desktop from the Start menu

2. **Verify Docker Installation**:
   ```powershell
   # Check Docker version
   docker --version
   
   # Check Docker Compose version (included with Docker Desktop)
   docker-compose --version
   
   # Verify Docker is running correctly
   docker run hello-world
   ```

3. **Configure Docker**:
   ```powershell
   # Create default network for your containers
   docker network create pyerp-network
   
   # Set Docker to start automatically
   Set-Service -Name docker -StartupType Automatic
   ```

## Setting Up Portainer for Container Management

Since you'll be managing multiple Docker containers in production, Portainer is an excellent web-based management UI for Docker environments.

1. **Create Volumes for Portainer**:
   ```powershell
   docker volume create portainer_data
   ```

2. **Deploy Portainer**:
   ```powershell
   # For a single server deployment
   docker run -d -p 9000:9000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
   
   # If you need to manage multiple Docker hosts, use Portainer with agents
   docker run -d -p 9000:9000 -p 8000:8000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
   ```

3. **Access Portainer**:
   - Open a browser and navigate to `http://your-server-ip:9000`
   - Create an admin user with a strong password
   - Select "Local" environment during initial setup

4. **Configure Portainer Security**:
   - Set up HTTPS with a valid SSL certificate
   - Consider putting Portainer behind a reverse proxy
   - Enable IP access control if needed

5. **Set Up Portainer Stacks for pyERP**:
   - In Portainer, go to "Stacks" and click "Add stack"
   - For each environment (dev, prod), create a separate stack
   - Upload or paste the corresponding docker-compose.yml file
   - Set environment variables or link to .env file
   - Deploy the stack

## Development Environment Deployment

1. **Clone Repository**:
   ```powershell
   # Create a directory for your project
   mkdir C:\Projects
   cd C:\Projects
   
   # Clone the repository
   git clone https://github.com/Wilhelm-Schweizer/pyERP
   cd pyERP
   ```

2. **Configure Environment Variables**:
   ```powershell
   # Create development environment file
   copy .env.dev.example .env.dev
   
   # Edit the file with appropriate values for development
   notepad .env.dev
   ```

   Required variables for development:
   ```
   DJANGO_SETTINGS_MODULE=pyerp.settings.development
   DJANGO_DEBUG=True
   SECRET_KEY=your_development_secret_key
   DATABASE_URL=postgres://postgres:postgres@db:5432/pyerp_dev
   REDIS_URL=redis://redis:6379/0
   
   # Legacy system connection (if needed)
   LEGACY_API_HOST=your-legacy-erp-host
   LEGACY_API_PORT=8080
   LEGACY_API_USERNAME=your-username
   LEGACY_API_PASSWORD=your-password
   ```

3. **Deploy Development Environment**:
   ```powershell
   # Navigate to the docker directory
   cd docker
   
   # Start the development environment
   docker-compose up -d
   ```

   Alternatively, use Portainer:
   - In Portainer, create a new stack named "pyerp-dev"
   - Upload the docker/docker-compose.yml file
   - Set environment variables or link to .env.dev file
   - Deploy the stack

4. **Initialize Development Database**:
   ```powershell
   # Run migrations
   docker-compose exec web python manage.py migrate
   
   # Create a superuser
   docker-compose exec web python manage.py createsuperuser
   
   # Load any initial data if needed
   docker-compose exec web python manage.py loaddata initial_data
   ```

5. **Accessing Development Environment**:
   - Django Admin: http://localhost:8000/admin/
   - Main application: http://localhost:8000/

## Production Environment Deployment

1. **Prepare Production Server**:
   - Ensure Docker and Portainer are installed and running
   - Create appropriate data directories with secure permissions
   
   ```powershell
   # Create directories for persistent storage
   mkdir -p C:\pyERP\data\postgres
   mkdir -p C:\pyERP\data\redis
   mkdir -p C:\pyERP\data\static
   mkdir -p C:\pyERP\data\media
   mkdir -p C:\pyERP\data\logs
   mkdir -p C:\pyERP\nginx\ssl
   ```

2. **Clone Repository**:
   ```powershell
   # Create a directory for your project
   mkdir C:\Projects
   cd C:\Projects
   
   # Clone the repository
   git clone https://github.com/Wilhelm-Schweizer/pyERP
   cd pyERP
   
   # Checkout the appropriate release tag or branch
   git checkout v1.0.0  # Replace with your version
   ```

3. **Configure Production Environment Variables**:
   ```powershell
   # Create production environment file
   copy .env.prod.example .env.prod
   
   # Edit the file with appropriate values for production
   notepad .env.prod
   ```

   Required variables for production:
   ```
   DJANGO_SETTINGS_MODULE=pyerp.settings.production
   DJANGO_DEBUG=False
   SECRET_KEY=your_very_secure_production_secret_key
   POSTGRES_USER=pyerp_user
   POSTGRES_PASSWORD=your_secure_db_password
   POSTGRES_DB=pyerp_production
   
   # SMTP settings for email
   EMAIL_HOST=your_smtp_server
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email_user
   EMAIL_HOST_PASSWORD=your_email_password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   
   # Legacy system connection (if needed)
   LEGACY_API_HOST=your-legacy-erp-host
   LEGACY_API_PORT=8080
   LEGACY_API_USERNAME=your-username
   LEGACY_API_PASSWORD=your-password
   ```

4. **Configure SSL Certificates**:
   - Place your SSL certificates in the `docker/nginx/ssl/` directory:
     - `server.crt`: SSL certificate
     - `server.key`: SSL private key
   - If you don't have certificates, generate self-signed ones (not recommended for true production):
   
   ```powershell
   cd docker/nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
   ```

5. **Deploy Production Environment**:
   
   Using Docker Compose directly:
   ```powershell
   # Navigate to the docker directory
   cd docker
   
   # Start the production environment
   docker-compose -f docker-compose.prod.yml up -d
   ```
   
   Using Portainer (recommended):
   - In Portainer, create a new stack named "pyerp-prod"
   - Upload the docker/docker-compose.prod.yml file
   - Set environment variables or link to .env.prod file
   - Deploy the stack

6. **Initialize Production Database**:
   ```powershell
   # Run migrations
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   
   # Create a superuser
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   
   # Collect static files
   docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   ```

7. **Accessing Production Environment**:
   - Main application: https://yourdomain.com/
   - Django Admin: https://yourdomain.com/admin/

## SSL Certificate Setup

For a production environment, proper SSL certificates are essential:

1. **Using Let's Encrypt (recommended for public servers)**:
   
   Add a Certbot container to your production stack:
   
   ```yaml
   certbot:
     image: certbot/certbot
     volumes:
       - ./nginx/ssl:/etc/letsencrypt
       - ./nginx/webroot:/var/www/certbot
     command: certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d yourdomain.com
   ```
   
   Then modify your Nginx configuration to use Let's Encrypt certificates.

2. **Using Purchased SSL Certificates**:
   - Place your certificate files in `docker/nginx/ssl/`
   - Update the Nginx configuration to point to these files

3. **Self-signed Certificates (for internal/testing only)**:
   ```powershell
   cd docker/nginx/ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
   ```

## Database Management

1. **Backup Production Database**:
   ```powershell
   # Create a backup directory
   mkdir -p C:\pyERP\backups
   
   # Backup the database
   docker-compose -f docker/docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > C:\pyERP\backups\pyerp_$(Get-Date -Format "yyyyMMdd").sql
   ```

2. **Schedule Automated Backups**:
   Create a PowerShell script for backups and schedule it using Task Scheduler:
   
   ```powershell
   # backup_database.ps1
   $backupDir = "C:\pyERP\backups"
   $dateStr = Get-Date -Format "yyyyMMdd_HHmmss"
   $backupFile = "$backupDir\pyerp_$dateStr.sql"
   
   # Run the backup command
   docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml exec -T db pg_dump -U pyerp_user pyerp_production > $backupFile
   
   # Compress the backup
   Compress-Archive -Path $backupFile -DestinationPath "$backupFile.zip"
   
   # Remove the uncompressed file
   Remove-Item $backupFile
   
   # Delete backups older than 30 days
   Get-ChildItem -Path $backupDir -Filter "*.zip" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item
   ```

3. **Restore Database from Backup**:
   ```powershell
   # Stop the services that use the database
   docker-compose -f docker/docker-compose.prod.yml stop web celery celery-beat
   
   # Restore the database
   Get-Content C:\pyERP\backups\your_backup_file.sql | docker-compose -f docker/docker-compose.prod.yml exec -T db psql -U $POSTGRES_USER $POSTGRES_DB
   
   # Restart the services
   docker-compose -f docker/docker-compose.prod.yml start web celery celery-beat
   ```

## Backup and Restore Procedures

1. **Complete System Backup**:
   
   Create a comprehensive backup script:
   
   ```powershell
   # full_backup.ps1
   $backupDir = "C:\pyERP\backups\full_$(Get-Date -Format "yyyyMMdd")"
   New-Item -ItemType Directory -Force -Path $backupDir
   
   # Backup PostgreSQL database
   docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml exec -T db pg_dump -U pyerp_user pyerp_production > "$backupDir\database.sql"
   
   # Backup environment files
   Copy-Item C:\Projects\pyERP\.env.prod "$backupDir\.env.prod.bak"
   
   # Backup media files
   Copy-Item -Recurse C:\pyERP\data\media "$backupDir\media"
   
   # Backup Nginx config and SSL certificates
   Copy-Item -Recurse C:\Projects\pyERP\docker\nginx "$backupDir\nginx"
   
   # Compress the entire backup
   Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
   
   # Remove the uncompressed directory
   Remove-Item -Recurse -Force $backupDir
   ```

2. **System Restore**:
   
   ```powershell
   # Extract backup
   Expand-Archive C:\pyERP\backups\full_20240501.zip -DestinationPath C:\pyERP\restore
   
   # Restore environment files
   Copy-Item C:\pyERP\restore\full_20240501\.env.prod.bak C:\Projects\pyERP\.env.prod
   
   # Stop services
   docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml down
   
   # Restore media files
   Copy-Item -Recurse C:\pyERP\restore\full_20240501\media\* C:\pyERP\data\media
   
   # Restore Nginx configuration and SSL certificates
   Copy-Item -Recurse C:\pyERP\restore\full_20240501\nginx\* C:\Projects\pyERP\docker\nginx
   
   # Start services
   docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml up -d db
   
   # Wait for database to start
   Start-Sleep -Seconds 30
   
   # Restore database
   Get-Content C:\pyERP\restore\full_20240501\database.sql | docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml exec -T db psql -U pyerp_user pyerp_production
   
   # Start remaining services
   docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml up -d
   ```

## Monitoring and Maintenance

1. **Monitoring with Portainer**:
   - Use Portainer's dashboard to monitor container status
   - Set up email alerts for container failures
   - Configure resource usage monitoring

2. **Log Monitoring**:
   - Access container logs through Portainer
   - Set up centralized logging with ELK Stack or similar (optional)
   
   ```powershell
   # View logs from specific container
   docker-compose -f docker/docker-compose.prod.yml logs web
   
   # Follow logs in real-time
   docker-compose -f docker/docker-compose.prod.yml logs -f web
   ```

3. **Regular Maintenance Tasks**:
   
   Create a maintenance script to run weekly:
   
   ```powershell
   # maintenance.ps1
   
   # Prune unused Docker resources
   docker system prune -f
   
   # Check for container updates
   docker-compose -f C:\Projects\pyERP\docker\docker-compose.prod.yml pull
   
   # Backup the database
   & C:\Scripts\backup_database.ps1
   
   # Clean up old log files
   Get-ChildItem -Path C:\pyERP\data\logs -File | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item
   
   # Report system status
   Send-MailMessage -From "system@yourdomain.com" -To "admin@yourdomain.com" -Subject "Weekly maintenance completed" -Body "System maintenance tasks have been completed successfully." -SmtpServer your-smtp-server
   ```

## Troubleshooting

1. **Container Won't Start**:
   
   Check logs for errors:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml logs web
   ```
   
   Check if it's a port conflict:
   ```powershell
   netstat -ano | findstr "8000"
   ```
   
   Check environment variables:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml config
   ```

2. **Database Connection Issues**:
   
   Check database container is running:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml ps db
   ```
   
   Check database logs:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml logs db
   ```
   
   Test database connection:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml exec web python -c "import psycopg2; conn = psycopg2.connect(database='pyerp_production', user='pyerp_user', password='your_password', host='db', port='5432'); print('Connection successful')"
   ```

3. **Nginx/Web Server Issues**:
   
   Check Nginx logs:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml logs nginx
   ```
   
   Test Nginx configuration:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -t
   ```
   
   Reload Nginx after configuration changes:
   ```powershell
   docker-compose -f docker/docker-compose.prod.yml exec nginx nginx -s reload
   ```

## Updating the Application

1. **Development Environment Updates**:
   
   ```powershell
   # Navigate to the repository
   cd C:\Projects\pyERP
   
   # Pull latest changes
   git pull
   
   # Update and restart containers
   cd docker
   docker-compose down
   docker-compose up -d
   
   # Apply migrations
   docker-compose exec web python manage.py migrate
   ```

2. **Production Environment Updates**:
   
   Create an update script:
   
   ```powershell
   # update_production.ps1
   
   # Backup before updating
   & C:\Scripts\backup_database.ps1
   
   # Navigate to the repository
   Set-Location C:\Projects\pyERP
   
   # Pull latest changes
   git pull
   
   # Checkout the specific version/tag to deploy
   git checkout v1.1.0  # Replace with your version
   
   # Update and restart containers
   Set-Location docker
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d
   
   # Apply migrations
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   
   # Collect static files
   docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   
   # Test if the application is running
   $response = Invoke-WebRequest -Uri https://yourdomain.com/health/ -UseBasicParsing
   if ($response.StatusCode -eq 200) {
       Write-Host "Update successful!"
   } else {
       Write-Host "Update failed! Rolling back..."
       # Roll back logic here
   }
   ```

