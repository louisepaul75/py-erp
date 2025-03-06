# Environment Files Consolidation Plan

## Overview

This document outlines the plan to consolidate environment files in the pyERP project. Currently, we have two sets of environment files:

1. **Config Environment Files** (`config/env/`): Used by the Django application
2. **Docker Environment Files** (`docker/`): Used by Docker Compose

Having two sets of environment files leads to duplication, potential inconsistencies, and maintenance overhead. This plan aims to consolidate these files to have a single source of truth for environment variables.

## Migration Steps

### 1. Update Docker Compose Files

- [x] Update `docker/docker-compose.prod.yml` to use `../config/env/.env.prod` instead of `docker/docker.env.prod`
- [x] Update `docker/docker-compose.yml` to use `../config/env/.env.dev` instead of `docker/docker.env.dev`

### 2. Consolidate Environment Variables

- [x] Ensure all variables from `docker/docker.env.prod` are included in `config/env/.env.prod`
- [x] Ensure all variables from `docker/docker.env.dev` are included in `config/env/.env.dev`
- [x] Update any Docker-specific scripts that reference the Docker environment files

### 3. Update Documentation

- [x] Update README.md to reflect the new environment file structure
- [x] Update any documentation that references the Docker environment files
- [x] Add notes to the Docker README about the environment file consolidation

### 4. Testing

- [x] Test the development environment with the consolidated environment files
- [x] Test the production environment with the consolidated environment files
- [x] Verify that all Docker containers start correctly
- [x] Verify that all Django functionality works correctly

### 5. Cleanup

- [x] Once testing is complete, remove the Docker environment files:
  - [x] `docker/docker.env.prod`
  - [x] `docker/docker.env.dev`
  - [x] `docker/docker.env.prod.example`
  - [x] `docker/docker.env.dev.example`
- [x] Update .gitignore to remove references to the Docker environment files

## Final Checklist Before Removing Docker Environment Files

Before removing the Docker environment files, ensure that:

1. **All Variables Are Migrated**:
   - [x] Verify that all variables from `docker.env.dev` are in `config/env/.env.dev`
   - [x] Verify that all variables from `docker.env.prod` are in `config/env/.env.prod`
   - [x] Check for any Docker-specific variables that might be missing

2. **All References Are Updated**:
   - [x] Docker Compose files reference the new environment files
   - [x] `scripts/docker/run_docker_dev.sh` is updated
   - [x] Documentation in `docs/DEPLOYMENT.md` is updated
   - [x] Any other scripts or documentation that reference Docker environment files

3. **Testing Is Complete**:
   - [x] Development environment works with the new configuration
   - [x] Production environment works with the new configuration
   - [x] All Docker containers start correctly
   - [x] All Django functionality works correctly

4. **Backup**:
   - [x] Create backups of the Docker environment files before deleting them
   - [x] Store backups in a secure location

5. **Team Communication**:
   - [ ] Inform all team members about the change
   - [ ] Provide instructions for using the new environment files
   - [ ] Update any onboarding documentation

## Benefits of Consolidation

1. **Single Source of Truth**: All environment variables are defined in one place
2. **Reduced Duplication**: No need to maintain two sets of environment files
3. **Simplified Management**: Easier to manage and update environment variables
4. **Consistent Configuration**: Same environment variables used across both Docker and Django
5. **Better Developer Experience**: Developers only need to configure one set of environment files

## Potential Issues and Mitigations

### Issue: Docker-specific Variables

Some variables might be specific to Docker and not needed by Django.

**Mitigation**: These variables can still be included in the config environment files. Django will ignore variables it doesn't use.

### Issue: Path References

Docker Compose files use relative paths to reference environment files.

**Mitigation**: Update the paths in Docker Compose files to use `../config/env/` instead of `docker/`.

### Issue: Deployment Workflows

Different deployment workflows might require different environment file handling.

**Mitigation**: Document the new environment file structure and update deployment scripts accordingly.

## Conclusion

Consolidating environment files will simplify the project structure and reduce maintenance overhead. The migration should be straightforward and can be completed with minimal disruption to development workflows.

## Completion Status

✅ **Environment file consolidation is now complete!** The Docker environment files have been removed, and all references have been updated to use the consolidated files in `config/env/`. Backups of the original files are stored in the `backups/docker_env_files/` directory.
