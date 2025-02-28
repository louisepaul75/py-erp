# Docker Configuration

This directory contains configuration files for Docker deployment of the pyERP application.

## Environment Files

### Security Warning

**IMPORTANT**: The actual environment files (`docker.env` and `docker.local.env`) contain sensitive information 
and should never be committed to version control. These files are included in `.gitignore` to help prevent 
accidental commits.

### Available Files

- `docker.env.example`: Template for production environment settings
- `docker.local.env.example`: Template for local development environment settings
- `docker.env`: Your actual production environment settings (not tracked in Git)
- `docker.local.env`: Your actual local environment settings (not tracked in Git)

## Setup Instructions

1. Copy the example files to create your actual configuration:
   ```bash
   cp docker.env.example docker.env
   cp docker.local.env.example docker.local.env
   ```

2. Edit `docker.env` and `docker.local.env` to include your actual database credentials and other sensitive information.

3. Use these environment files when building/running your Docker containers:
   - For production: The container automatically uses `docker.env`
   - For local development: Run with `-e USE_LOCAL_ENV=true` to use `docker.local.env`

## Database Configuration

The Docker containers use PyMySQL (pure Python MySQL client) to connect to your database.
You can configure it in the following ways:

1. **Production MySQL**: Modify `docker.env` with your actual MySQL credentials

2. **Local Development**: 
   - Default: Uses SQLite for easy standalone testing
   - Optional: Uncomment and configure the MySQL section in `docker.local.env` to use your MySQL server instead

## Example Docker Run Commands

**Production mode with MySQL:**
```bash
docker run -p 8000:8000 pyerp:latest
```

**Local development mode with SQLite:**
```bash
docker run -p 8000:8000 -e USE_LOCAL_ENV=true pyerp:latest
```

**Local development mode with custom environment file:**
```bash
docker run -p 8000:8000 -v /path/to/your/custom.env:/app/.env pyerp:latest
``` 