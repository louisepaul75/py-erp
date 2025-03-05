# Environment Files Consolidation - Team Announcement

## What Changed

We have consolidated all environment files in the pyERP project. Previously, we had two sets of environment files:

1. **Config Environment Files** (`config/env/`): Used by the Django application
2. **Docker Environment Files** (`docker/`): Used by Docker Compose

Now, we have a single source of truth for all environment variables in the `config/env/` directory.

## What You Need to Do

1. **Pull the latest changes** from the repository:
   ```bash
   git pull origin main
   ```

2. **Use the consolidated environment files**:
   - For development: `config/env/.env.dev`
   - For production: `config/env/.env.prod`

3. **Update any local scripts** that might reference the old Docker environment files.

## Benefits

1. **Single Source of Truth**: All environment variables are defined in one place
2. **Reduced Duplication**: No need to maintain two sets of environment files
3. **Simplified Management**: Easier to manage and update environment variables
4. **Consistent Configuration**: Same environment variables used across both Docker and Django
5. **Better Developer Experience**: Developers only need to configure one set of environment files

## Docker Compose Changes

The Docker Compose files have been updated to use the consolidated environment files:

- `docker-compose.yml` now uses `../config/env/.env.dev`
- `docker-compose.prod.yml` now uses `../config/env/.env.prod`

## Documentation

For more details about the consolidation process, see:
- [Environment Consolidation Plan](ENV_CONSOLIDATION.md)

## Questions?

If you have any questions or encounter any issues, please reach out to the DevOps team. 