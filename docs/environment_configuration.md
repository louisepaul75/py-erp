# Environment Configuration

This document explains how environment variables are handled in the pyERP project.

## Environment Files

The project uses environment files to store configuration variables:

1. **Source Files**:
   - `config/env/.env.dev` - Development environment variables
   - `config/env/.env.prod` - Production environment variables
   - `config/env/.env.test` - Testing environment variables (if needed)

2. **Loading Mechanism**:
   - The project now uses a centralized environment loading mechanism
   - The environment loader looks for files in this order:
     1. `config/env/.env.<environment>` (primary)
     2. `config/env/.env` (fallback)
     3. `.env` in project root (last resort)

## Environment Determination

The environment is determined in the following order:

1. `PYERP_ENV` environment variable (if set)
2. Based on the `DJANGO_SETTINGS_MODULE` value:
   - `*production*` → "prod" environment
   - `*test*` or `*testing*` → "test" environment
   - Otherwise → "dev" environment

## Setup Instructions

### Development Setup

```bash
# Set up development environment
python scripts/setup_env.py dev
```

### Production Setup

```bash
# Set up production environment
python scripts/setup_env.py prod
```

### Testing Setup

```bash
# Set up testing environment
python scripts/setup_env.py test
```

## Docker Setup

In Docker, the environment is automatically configured:

- Development Docker Compose uses `config/env/.env.dev`
- Production Docker Compose uses `config/env/.env.prod`
- The Docker entrypoint script sets `PYERP_ENV` based on the `DJANGO_SETTINGS_MODULE`

## Manual Configuration

If you need to configure the environment manually:

1. Create a suitable `.env.<environment>` file in `config/env/`
2. Run the setup script or create a symlink manually:
   ```bash
   ln -s config/env/.env.<environment> .env
   ```
3. Set the `PYERP_ENV` environment variable:
   ```bash
   export PYERP_ENV=<environment>
   ```

## Troubleshooting

If environment variables are not loading correctly:

1. Check that the correct environment file exists in `config/env/`
2. Verify the `PYERP_ENV` and `DJANGO_SETTINGS_MODULE` environment variables
3. Run with verbose output to see which files are being loaded:
   ```python
   from pyerp.utils.env_loader import load_environment_variables
   load_environment_variables(verbose=True)
   ```
